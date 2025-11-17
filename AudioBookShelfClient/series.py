from typing import List

from .__book_cache import BookCache


class Series:
    def __init__(self, cache: BookCache):
        self.book_cache = cache
        self.series_cache = None

    def __load_series(self):
        query = """
            WITH series_split AS (
               SELECT
                   UNNEST(string_split("media.metadata.seriesName", ',')) AS series_raw
               FROM books
               WHERE "media.metadata.seriesName" IS NOT NULL
            ),
            cleaned_series AS (
               SELECT
                   TRIM(
                       regexp_replace(series_raw, ' #[0-9]+$', '')
                   ) AS series
               FROM series_split
            )
            SELECT DISTINCT
                  series
            FROM cleaned_series
            WHERE series <> ''
            ORDER BY series;
        """
        data = self.book_cache.query(query)
        self.series_cache = [item.get('series') for item in data]

    def get_all(self) -> List[str]:
        self.__load_series()
        return self.series_cache

    def refresh(self):
        self.series_cache = None
        self.__load_series()
