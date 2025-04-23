from dotenv import load_dotenv

load_dotenv()

from flashcrawler.tasks.oneoff import get_archive_results
from flashcrawler.tasks.regular import get_games_details


if __name__ == "__main__":
    import asyncio

    asyncio.run(
        get_games_details.task.run(
            headless=False,
            workers=4
        )
    )