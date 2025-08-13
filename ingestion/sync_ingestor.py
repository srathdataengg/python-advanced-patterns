import requests
from ingestion.base import BaseIngestor
from ingestion.base import BaseIngestor
from utils.retry import retry
from utils.logger import logger


class SyncIngestor(BaseIngestor):
    """
    Synchronous ingestor that fetches data via HTTP GET requests
    and processes the JSON response.
    """

    API_URL = "https://jsonplaceholder.typicode.com/posts"

    @retry(max_attempts=3, delay_seconds=2,exceptions=(requests.exceptions.RequestException,))
    def fetch(self, url):
        """
        Fetch the data from the API endpoint synchronously.

        :return: List of JSON objects fetched from the API.

        """

        response = requests.get(url)
        response.raise_for_status()  # Raise error for bad status
        return response.json()

    def process(self, raw_data):
        """
        Process raw JSON data by filtering or transforming as needed(here we just pass through)
        :param raw_data: List of json objects from API
        :return: Processed data(list)
        """

        # For demo, simply return as-is
        return raw_data


if __name__ == '__main__':

    ingestor = SyncIngestor()
    try:
        data = ingestor.fetch(SyncIngestor.API_URL)
        print(data)

    except Exception as e:
        print(f"Final failure after retries: {e}")
