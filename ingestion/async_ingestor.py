import asyncio
import aiohttp
from utils.logger import logger  # Using your existing logger


class AsyncIngestor:
    def __init__(self, urls):
        self.urls = urls

    async def fetch(self, session, url):
        """
        Fetch a single url asynchronously.
        :param self:
        :param session:
        :param url:
        :return:
        """

        try:
            async with session.get(url, ssl = False) as response:
                data = await  response.json()
                logger.info(f"Success: {url}")
                return data
        except Exception as e:
            logger.exception(f"X Error fetching {url}: {e}")
            return None

    async def run(self):
        """
        Create tasks for all URLs and run them concurrently.
        """

        async with aiohttp.ClientSession() as session:
            tasks = [self.fetch(session, url) for url in self.urls]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            return results


if __name__ == "__main__":
    urls = [f"https://jsonplaceholder.typicode.com/posts/{i}" for i in range(1, 21)]
    ingestor = AsyncIngestor(urls)
    results = asyncio.run(ingestor.run())
    logger.info(f"Fetched {len([r for r in results if r])} successful responses.")
