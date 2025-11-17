import json
import sys
from pathlib import Path


class Config:

    def __init__(self, config_file: str):
        self._base_url = None
        self._api_key = None
        self.config_file = config_file
        self.__load_config()

    def __load_config(self):
        # Load from the config file in the user's config directory
        config_dir = Path.home() / '.config' / 'abscli'

        # Ensure config has .json extension
        if not self.config_file.endswith('.json'):
            self.config_file = f"{self.config_file}.json"

        config_file_path = config_dir / self.config_file

        if not config_file_path.exists():
            print(f"\nConfig file not found: {config_file_path}", file=sys.stderr)
            print(f"Create a config file at {config_file_path} and add the following:", file=sys.stderr)
            print(f"  {{", file=sys.stderr)
            print(f"    \"base_url\": \"https://<your-audiobookshelf-server>\",", file=sys.stderr)
            print(f"    \"api_key\": \"<your-api-key>\"", file=sys.stderr)
            print(f"  }}", file=sys.stderr)
            print(f"Then run the command again.\n", file=sys.stderr)
            sys.exit(1)

        try:
            with open(config_file_path, 'r') as f:
                config_data = json.load(f)

            self._base_url = config_data.get('base_url')
            self._api_key = config_data.get('api_key')

            if not self._base_url:
                raise ValueError(f"Config file missing 'base_url': {config_file_path}")
            if not self._api_key:
                raise ValueError(f"Config file missing 'api_key': {config_file_path}")

        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in config file {config_file_path}: {e}")

    @property
    def url(self):
        return self._base_url

    @property
    def api_key(self):
        return self._api_key