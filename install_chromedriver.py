import os

import requests
from requests import Response

from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.download_manager import WDMDownloadManager
from webdriver_manager.core.http import HttpClient
from webdriver_manager.core.logger import log
from selenium.webdriver.chrome.service import Service

class CustomHttpClient(HttpClient):

    def get(self, url, params=None, **kwargs) -> Response:
        """
        Add you own logic here like session or proxy etc.
        """
        log("The call will be done with custom HTTP client")
        return requests.get(url, params, **kwargs)


def test_can_get_chrome_driver_with_custom_http_client():
    http_client = CustomHttpClient()
    download_manager = WDMDownloadManager(http_client)
    path = ChromeDriverManager(download_manager=download_manager).install()
    assert os.path.exists(path)
    return path

def get_service():
    path = test_can_get_chrome_driver_with_custom_http_client()
    service = Service(path)
    return service

if __name__ == "__main__":
    test_can_get_chrome_driver_with_custom_http_client()