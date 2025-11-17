from typing import List, Dict, Any, Optional

import duckdb
import pandas as pd

from .__rest_client import RestClient, RestException

class DataException(Exception):
    def __init__(self, message):
        self.message = message

class BookCache:
    def __init__(self, library_id: str, url: str, api_key: str):
        """
        Initialize BookCache and load books from the API.

        Args:
            library_id: ID of the library to fetch books from

        Raises:
            ValueError: If library_id is not provided or an API request fails
        """
        self.restclient = RestClient()
        self.base_url = url
        self.api_key = api_key
        self.genres_cache = None

        self.conn = duckdb.connect(':memory:', read_only=False)
        self._load_books(library_id)

    def _load_books(self, library_id: str):
        """Fetch books from API and load into DuckDB."""
        url = f"{self.base_url.rstrip('/')}/api/libraries/{library_id}/items"

        try:
            response = RestClient.get(url, self.api_key)
        except RestException as e:
            if e.status_code == 404:
                raise ValueError(f"Library with ID '{library_id}' not found") from e
            raise

        if not response or 'results' not in response:
            raise ValueError("Invalid response from API")

        books_list = response['results']

        if not books_list:
            # Create an empty table with schema
            raise DataException("No books found")
        else:
            con = self.conn
            df = pd.json_normalize(books_list)
            con.register("books_list_df", df)
            # Let DuckDB infer schema from the book data
            con.execute("""
                  CREATE TABLE books AS
                  SELECT * 
                  FROM books_list_df
            """)
        #print(self.conn.execute("DESCRIBE books").fetchdf())

    def get_columns(self) -> Optional[List[str]]:
        cols = self.conn.execute("DESCRIBE books").fetchdf()
        return [item.get('column_name') for item in cols.to_dict(orient='records')]

    def count(self) -> int:
        return self.conn.execute("SELECT COUNT(*) FROM books").fetchone()[0]

    def query(self, sql: str) -> List[Dict[str, Any]]:
        """
        Execute a SQL query on the books database.

        Args:
            sql: SQL query string

        Returns:
            List of dictionaries containing query results
        """
        result = self.conn.execute(sql).fetchall()
        columns = [desc[0] for desc in self.conn.description]
        return [dict(zip(columns, row)) for row in result]

    def get_all(self) -> List[Dict[str, Any]]:
        """
        Get all books from the cache.

        Returns:
            List of all books as dictionaries
        """
        return self.query("""SELECT * FROM books ORDER BY "media.metadata.title" ASC""")

    def get_book_by_id(self, book_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific book by ID.

        Args:
            book_id: The book ID to retrieve

        Returns:
            Dictionary containing book data or None if not found
        """
        result = self.conn.execute(
            "SELECT * FROM books WHERE id = ?",
            [book_id]
        ).fetchone()

        if result:
            return {'id': result[0], 'data': result[1]}
        return None

    def close(self):
        """Close the database connection."""
        self.conn.close()