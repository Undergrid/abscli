from typing import Optional, Dict, Any, List

from certifi import where

from AudioBookShelfClient.__rest_client import RestClient, RestException


class Filters:

    def __init__(self, url, api_key, library_id: str):
        self.cache = None
        self.base_url = url
        self.api_key = api_key
        self.library_id = library_id

    def __load_filters(self):
        if self.cache is None:
            url = f"{self.base_url.rstrip('/')}/api/libraries/{self.library_id}"
            params = {
                "include": "filterdata"
            }

            try:
                response = RestClient.get(url, self.api_key, params=params)
                self.cache = response['filterdata']
            except RestException as e:
                if e.status_code == 404:
                    raise ValueError(f"Library with ID '{self.library_id}' not found")
                else:
                    raise e
    def get(self, name: str) -> Optional[List[Dict[str, Any]]]:
        self.__load_filters()
        return self.cache.get(name)

    def get_genres(self) -> Optional[List[Dict[str, Any]]]:
        self.__load_filters()
        #return self.cache.get('genres')
        return [{'name': item} for item in self.cache.get('genres')]

    def get_series(self) -> Optional[List[Dict[str, Any]]]:
        self.__load_filters()
        return self.cache.get('series')

    def search(self, query: str, exact: bool) -> Optional[List[Dict[str, Any]]]:
        self.__load_filters()
        if exact:
            return [item for item in self.cache if query == item.get('name')]
        else:
            return [item for item in self.cache if query in item.get('name')]