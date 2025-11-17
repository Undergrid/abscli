import json
from types import SimpleNamespace
from typing import Optional, Dict, Any, List

from AudioBookShelfClient.__rest_client import RestClient, RestException

class Library:
    def __init__(self, name: str, id: Optional[str] = None):
        self._name = name
        self._id = id

    @property
    def id(self) -> str | None:
        return self._id

    @property
    def name(self) -> str:
        return self._name

class Libraries:

    def __init__(self, url, api_key):
        self.cache = None
        self.cache_objects = None
        self.base_url = url
        self.api_key = api_key

    def __load_libraries(self):
        if self.cache is None:
            url = f"{self.base_url.rstrip('/')}/api/libraries"

            try:
                response_raw = RestClient.get_raw(url, self.api_key)
                response = json.loads(response_raw.text, object_hook=lambda d: SimpleNamespace(**d))
                if not response or not hasattr(response, 'libraries'):
                    raise ValueError("No libraries found")
                self.cache = response.libraries
            except RestException as e:
                if e.status_code == 404:
                    raise ValueError("No libraries found") from e
                raise

    def get_all(self) -> Optional[List[Any]]:
        self.__load_libraries()
        return self.cache

    def get_all_summary(self) -> Optional[List[Dict[str, Any]]]:
        libraries = self.get_all()
        if libraries:
            return [{'name': lib.name, 'id': lib.id} for lib in libraries]
        return None

    def get_by_name(self, name: str) -> Optional[Library]:
        if not name:
            return None

        libraries = self.get_all()
        if libraries:
            return next((lib for lib in libraries if lib.name == name), None)
        return None

    def get_by_id(self, id: str) -> Optional[Library]:
        if not id:
            return None

        libraries = self.get_all();
        if libraries:
            return next((lib for lib in libraries if lib.id == id), None)
        return None

    def refresh(self):
        self.cache = None
        self.__load_libraries()
