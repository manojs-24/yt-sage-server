from urllib.parse import urlparse
from pydantic import HttpUrl

def is_valid_youtube_url(url: HttpUrl) -> bool:
    try:
        # print(f"Validating YouTube URL: {url}")
        parsed_url = urlparse(url)
        # print(f"Parsed url: {parsed_url}")
        return parsed_url.netloc in ["www.youtube.com", "youtube.com", "youtu.be"]
    except Exception:
        return False
