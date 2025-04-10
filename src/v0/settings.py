import os
import sys


class Settings:
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    SCRAPER_DIR = r"PATH_TO_REPO\plug-and-crawl"

    def __init__(self) -> None:
        sys.path.append(self.BASE_DIR)
        sys.path.append(self.SCRAPER_DIR)


settings = Settings()