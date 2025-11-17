import json
from types import SimpleNamespace
from typing import Optional, Dict, Any, List

from AudioBookShelfClient.__rest_client import RestClient, RestException
from AudioBookShelfClient.libraries import Libraries


class Collections:

    def __init__(self, url, api_key, library_id: str = None, libs: Libraries = None):
        self.cache = None
        self.base_url = url
        self.api_key = api_key
        self.library_id = library_id
        self.libraries = libs

    def __load_collections(self):
        if self.cache is None:
            url = f"{self.base_url.rstrip('/')}/api/collections"

            try:
                response_raw = RestClient.get_raw(url, self.api_key)
                response = json.loads(response_raw.text, object_hook=lambda d: SimpleNamespace(**d))
                if not response or not hasattr(response, 'collections'):
                    raise ValueError("No collections found")

                if self.library_id:
                    self.cache = [item for item in response.collections if item.libraryId == self.library_id]
                else:
                    self.cache = response.collections
            except RestException as e:
                if e.status_code == 404:
                    raise ValueError("No collections found") from e
                raise

    def get_all(self) -> Optional[List[SimpleNamespace]]:
        self.__load_collections()
        return self.cache


    def get_all_summary(self) -> Optional[List[Dict[str, Any]]]:
        collections = self.get_all()
        if collections:
            library_name = self.libraries.get_by_id(self.library_id).name if self.library_id else None
            return [{'name': item.name, 'id': item.id, 'library': library_name or self.libraries.get_by_id(item.libraryId).name} for item in collections]
        return None

    def exists(self, name: str) -> bool:
        collections = self.get_all()
        return any(c.name == name for c in collections)

    def get(self, name: str) -> Optional[SimpleNamespace]:
        collections = self.get_all()
        return next((c for c in collections if c.name == name), None)

    def create(self, name: str, description: str, library_id: str, items: List[Dict[str, Any]], dryrun: bool = False):
        if dryrun:
            return

        url = f"{self.base_url.rstrip('/')}/api/collections"
        data = {
            "name": name,
            "libraryId": library_id,
            "description": description,
            "books": [item.get('id') for item in items]
        }
        try:
            RestClient.post(url, self.api_key, payload=data)
        except RestException as e:
            if e.status_code == 409:
                raise ValueError(f"Collection '{name}' already exists") from e
            raise

    def update(self, name: str, description: str, library_id: str, items: List[Dict[str, Any]], dryrun: bool = False):
        collection = self.get(name)
        if not collection:
            self.create(name, description, library_id, items)
            return items

        books = [item.get('id') for item in items]
        existing = [c.id for c in collection.books]
        added = set(books) - set(existing)

        if not added:
            return None

        if not dryrun:
            url = f"{self.base_url.rstrip('/')}/api/collections/{collection.id}/batch/add"
            data = {
                "books": [*added]
            }
            try:
                RestClient.post(url, self.api_key, payload=data)
            except RestException as e:
                if e.status_code == 409:
                    raise ValueError(f"Collection '{name}' already exists") from e
                raise
        return [item for item in items if item.get('id') in added]