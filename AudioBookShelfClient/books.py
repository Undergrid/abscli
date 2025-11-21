from typing import Optional, Dict, Any, List

from AudioBookShelfClient import Utils
from AudioBookShelfClient.__book_cache import BookCache, DataException

class NoBooksException(Exception):
    def __init__(self, message):
        self.message = message

class Books:

    def __init__(self, url, api_key, library_id: str = None):
        self.__bookCache = None
        self.base_url = url
        self.api_key = api_key
        self.library_id = library_id

    def __load_books(self, library_id: str):
        try:
            if self.__bookCache is None:#
                self.__bookCache = BookCache(library_id, self.base_url, self.api_key)
        except DataException as e:
            raise NoBooksException(f"Library with ID '{library_id}': {e.message}")

    def get_fields(self) -> Optional[List[str]]:
        self.__load_books(self.library_id)
        return self.__bookCache.get_columns()

    def get_all(self) -> Optional[List[Dict[str, Any]]]:
        self.__load_books(self.library_id)
        return self.__bookCache.get_all()

    def get_all_summary(self) -> Optional[List[Dict[str, Any]]]:
        self.__load_books(self.library_id)
        books = self.__bookCache.get_all()
        if books:
            return [{'name': item.get('media.metadata.title'), 'id': item.get('id')} for item in books]
        return None

    def query(self, query: str) -> Optional[List[Dict[str, Any]]]:
        self.__load_books(self.library_id)
        return self.__bookCache.query(query)

    def where(self, where: str, order: str = None) -> Optional[List[Dict[str, Any]]]:
        if Utils.has_keywords(where):
            raise ValueError(
                "Disallowed SQL Keyword in WHERE clause.'"
            )

        self.__load_books(self.library_id)
        query = f"""
            SELECT * FROM books WHERE {where}
        """
        if order:
            query += f" ORDER BY {order}"
        return self.__bookCache.query(query)
