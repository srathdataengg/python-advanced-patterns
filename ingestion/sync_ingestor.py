import requests
from ingestion.base import BaseIngestor


class SyncIngestor(BaseIngestor):
    """
    Synchronous ingestor that fetches data via HTTP GET requests
    and processes the JSON response.
    """

    API_URL = "https://jsonplaceholder.typicode.com/posts"

    def fetch(self):
        """
        Fetch the data from the API endpoint synchronously.

        :return: List of JSON objects fetched from the API.

        """

        response = requests.get(self.API_URL, timeout=10)
        response.raise_for_status()      # Raise error for bad status
        return response.json()

    def process(self, raw_data):
        """
        Process raw JSON data by filtering or transforming as needed(here we just pass through)
        :param raw_data: List of json objects from API
        :return: Processed data(list)
        """

        # For demo, simply return as-is
        return  raw_data


