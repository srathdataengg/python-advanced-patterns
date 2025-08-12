from abc import ABC, abstractmethod


class BaseIngestor(ABC):
    """
    Abstract base class for ingestion pipelines.

    This class defines the contract that all concrete ingestors
    must follow by implementing the 'fetch' and 'process' methods.

    Provides a common 'run' method to execute the ingestion workflow:
    fetch raw data and then process it

    """

    def __init__(self):
        """ Initialise any shared resources or configuration here if needed """
        pass

    @abstractmethod
    def fetch(self):
        """
        Fetch data from the source.

        Must be implemented subclasses.

        :return: raw data fetched from the source (format may vary)

        """
        pass

    @abstractmethod
    def process(self, raw_data):
        """
        Process the raw data fetched  from the source.

        Must be implemented by subclasses.

        :param raw_data: The raw data returned by fetch.

        :return: Processed and cleaned data ready for downstream use.

        """
        pass

    def run(self):
        """
        Runs the ingestion pipeline by fetching data and then processing it
        :return: The final processed data
        """
        raw_data = self.fetch()
        processed_data = self.process(raw_data)
        return processed_data
