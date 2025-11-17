import json
from types import SimpleNamespace

import requests
from typing import Optional, Dict, Any

from requests import Response


class RestException(Exception):
    def __init__(self, message, status_code):
        self.message = message
        self.status_code = status_code

class RestClient:

    @staticmethod
    def __get(url: str, api_key: str, headers=None, params=None, payload=None) -> Optional[Response]:
        """
        Make a GET request to the AudioBookShelf API.

        :param url: The URL to request
        :param api_key: The API key to use for authentication
        :param headers: Optional headers
        :param params: Optional query parameters
        :param payload: Optional JSON payload
        :param raw: If True, return the raw response object instead of parsing JSON
        :return: Response data
        """
        my_headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        if headers:
            my_headers.update(headers)

        try:
            response = requests.get(url, headers=my_headers, params=params, json=payload, timeout=30)
            response.raise_for_status()
            return response

        except requests.exceptions.HTTPError as e:
            if response.status_code == 401:
                raise ValueError("Authentication failed. Check your API key")
            elif response.status_code == 403:
                raise ValueError("Access forbidden. Check your permissions")
            elif response.status_code == 404:
                raise RestException("404", 404)
            elif response.status_code == 400:
                raise ValueError(f"Bad request: {response.text}")
            elif response.status_code == 429:
                raise ValueError("Too many requests. Please try again later.")
            elif response.status_code == 500:
                raise ValueError("Internal server error. Please try again later.")
            elif response.status_code == 503:
                raise ValueError("Service unavailable. Please try again later.")
            else:
                raise requests.exceptions.HTTPError(f"HTTP error occurred: {e}")
        except requests.exceptions.JSONDecodeError:
            raise ValueError("Invalid JSON response from server")
        except requests.exceptions.Timeout:
            raise requests.exceptions.Timeout("Request timed out after 30 seconds")
        except requests.exceptions.RequestException as e:
            raise requests.exceptions.RequestException(f"Request failed: {e}")

    @staticmethod
    def get_raw(url, api_key, headers=None, params=None, payload=None) -> Optional[Response]:
        return RestClient.__get(url, api_key, headers, params, payload)

    @staticmethod
    def get(url, api_key, headers=None, params=None, payload=None) -> Optional[Dict[str, Any]]:
        response = RestClient.__get(url, api_key, headers, params, payload)
        return response.json()

    @staticmethod
    def get_text(url, api_key, headers=None, params=None, payload=None) -> Optional[str]:
        response = RestClient.__get(url, api_key, headers, params, payload)
        return response.text

    @staticmethod
    def get_auto(url, api_key, headers=None, params=None, payload=None) -> Optional[Any]:
        response = RestClient.__get(url, api_key, headers, params, payload)
        return json.loads(response.text, object_hook=lambda d: SimpleNamespace(**d))

    @staticmethod
    def post(url, api_key, headers=None, payload=None) -> Optional[Dict[str, Any]]:
        """
        Make a POST request to the AudioBookShelf API.

        :param url: The URL to request
        :param api_key: The API key to use for authentication
        :param headers: Optional headers
        :param payload: Optional JSON payload
        :return: Response data
        """

        my_headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        if headers:
            my_headers.update(headers)

        try:
            response = requests.post(url, headers=my_headers, json=payload, timeout=30)
            response.raise_for_status()
            data = response.json()
            return data

        except requests.exceptions.HTTPError as e:
            if response.status_code == 401:
                raise ValueError("Authentication failed. Check your API key")
            elif response.status_code == 403:
                raise ValueError("Access forbidden. Check your permissions")
            elif response.status_code == 404:
                raise RestException("404", 404)
            elif response.status_code == 400:
                raise ValueError(f"Bad request: {response.text}")
            elif response.status_code == 429:
                raise ValueError("Too many requests. Please try again later.")
            elif response.status_code == 500:
                raise ValueError("Internal server error. Please try again later.")
            elif response.status_code == 503:
                raise ValueError("Service unavailable. Please try again later.")
            else:
                raise requests.exceptions.HTTPError(f"HTTP error occurred: {e}")
        except requests.exceptions.JSONDecodeError:
            raise ValueError("Invalid JSON response from server")
        except requests.exceptions.Timeout:
            raise requests.exceptions.Timeout("Request timed out after 30 seconds")
        except requests.exceptions.RequestException as e:
            raise requests.exceptions.RequestException(f"Request failed: {e}")

    @staticmethod
    def patch(url, api_key, headers=None, payload=None) -> Optional[Dict[str, Any]]:
        """
        Make a PATCH request to the AudioBookShelf API.

        :param url: The URL to request
        :param api_key: The API key to use for authentication
        :param headers: Optional headers
        :param payload: Optional JSON payload
        :return: Response data
        """

        my_headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        if headers:
            my_headers.update(headers)

        try:
            response = requests.patch(url, headers=my_headers, json=payload, timeout=30)
            response.raise_for_status()
            data = response.json()
            return data

        except requests.exceptions.HTTPError as e:
            if response.status_code == 401:
                raise ValueError("Authentication failed. Check your API key")
            elif response.status_code == 403:
                raise ValueError("Access forbidden. Check your permissions")
            elif response.status_code == 404:
                raise RestException("404", 404)
            elif response.status_code == 400:
                raise ValueError(f"Bad request: {response.text}")
            elif response.status_code == 429:
                raise ValueError("Too many requests. Please try again later.")
            elif response.status_code == 500:
                raise ValueError("Internal server error. Please try again later.")
            elif response.status_code == 503:
                raise ValueError("Service unavailable. Please try again later.")
            else:
                raise requests.exceptions.HTTPError(f"HTTP error occurred: {e}")
        except requests.exceptions.JSONDecodeError:
            raise ValueError("Invalid JSON response from server")
        except requests.exceptions.Timeout:
            raise requests.exceptions.Timeout("Request timed out after 30 seconds")
        except requests.exceptions.RequestException as e:
            raise requests.exceptions.RequestException(f"Request failed: {e}")