import logging

import requests
from typing import List, Dict, Optional

from config.settings.base import env

logger = logging.getLogger(__name__)


def api_news_desk_posts(per_page: int = 1) -> List[Dict]:
    """
        Fetch news posts from the Infinite News Desk API.

        Args:
            per_page (int): The number of posts to fetch. Defaults to 1.

        Returns:
            List[Dict]: A list of dictionaries containing post-details with title, link, and image source URL.
    """

    url = env("NEWS_DESK_API_END_POINT")
    endpoint = f"{url}?per_page={per_page}"
    headers = {}

    posts = []
    try:
        response = requests.get(endpoint, headers=headers)
        response.raise_for_status()
        data = response.json()
        for item in data:
            post = {
                'title': item.get('title', {}).get('rendered', {}),
                'link': item.get("link")
            }
            featured_media_links = item.get("_links", {}).get("wp:featuredmedia", [])
            if featured_media_links:
                media_endpoint = featured_media_links[0].get("href")
                image_url = api_new_desk_post_image_url(media_endpoint)
                if image_url:
                    post['image_source_link'] = image_url
            posts.append(post)

    except requests.RequestException as e:
        logger.error(f"Error fetching Infinite News Desk news posts: {e}")
    except (ValueError, KeyError, IndexError) as e:
        logger.error(f"Error processing Infinite News Desk news posts data: {e}")

    return posts


def api_new_desk_post_image_url(media_endpoint: str) -> Optional[str]:
    """
        Fetch the source URL of the image from the media endpoint.

        Args:
            media_endpoint (str): The API endpoint to fetch media details.

        Returns:
            Optional[str]: The source URL of the large image, or None if not available.
    """
    headers = {}
    try:
        response = requests.get(media_endpoint, headers=headers)
        response.raise_for_status()
        data = response.json()
        media_details = data.get("media_details", {})
        sizes = media_details.get("sizes", {})
        large_image = sizes.get("large", {})
        return large_image.get("source_url")
    except requests.RequestException as e:
        logger.error(f"Error fetching Infinite News Desk news post Image url: {e}")
    except (ValueError, KeyError) as e:
        logger.error(f"Error processing News Desk news post Image url media details: {e}")
    return None
