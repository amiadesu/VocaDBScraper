import asyncio
import dotenv
import os

from scrapers.vocaDBScraper import VocaDBScraper

dotenv.load_dotenv()

acceptable_services = [
    "Youtube",
    "NicoNicoDouga",
    "Bilibili"
]
    
async def main():
    """
    This function will only scrape data from VocaDB API, it won't restore views for it.
    For restoring views use views.ipynb 
    """
    scraper = VocaDBScraper(os.environ["DB_URL"])

    await scraper.run()

if __name__ == "__main__":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())