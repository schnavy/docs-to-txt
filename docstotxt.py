#!/usr/bin/env python3
import argparse
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import re

def sanitize_filename(s):
    # Replace non-alphanumeric characters to create a safe filename.
    return re.sub(r'[^a-zA-Z0-9_\-\.]', '-', s)

def get_internal_links(html, base_url, links_selector):
    soup = BeautifulSoup(html, "html.parser")
    container = soup.select_one(links_selector)
    if container is None:
        print(f"No container found for selector: {links_selector}")
        return []
    links = []
    base_netloc = urlparse(base_url).netloc
    for a in container.find_all("a", href=True):
        full_url = urljoin(base_url, a["href"])
        if urlparse(full_url).netloc == base_netloc:
            links.append(full_url)
    return links

def extract_text(html, content_selector=None):
    soup = BeautifulSoup(html, "html.parser")
    if content_selector:
        element = soup.select_one(content_selector)
        if element:
            return element.get_text(separator="\n", strip=True)
        else:
            print(f"No element found for content selector: {content_selector}. Using full page text.")
    # Default to full page text if no valid content_selector provided.
    return soup.get_text(separator="\n", strip=True)

def main():
    parser = argparse.ArgumentParser(
        description="Download text content from a URL and its internal links within a container."
    )
    parser.add_argument("url", help="The base URL to download")
    parser.add_argument("links_selector", help="CSS selector for the container with links")
    parser.add_argument("content_selector", nargs="?", default=None,
                        help="Optional CSS selector for text extraction (if omitted, the full page text is used)")
    args = parser.parse_args()

    base_url = args.url
    links_selector = args.links_selector
    content_selector = args.content_selector

    netloc = sanitize_filename(urlparse(base_url).netloc)
    safe_links_selector = sanitize_filename(links_selector)
    if content_selector:
        safe_content_selector = sanitize_filename(content_selector)
        filename = f"{netloc}_{safe_links_selector}_{safe_content_selector}.txt"
    else:
        filename = f"{netloc}_{safe_links_selector}.txt"

    try:
        response = requests.get(base_url)
        response.raise_for_status()
        base_text = extract_text(response.text, content_selector)
        with open(filename, "w", encoding="utf-8") as f:
            f.write(base_text)
        print(f"Saved text content from {base_url} to {filename}")

        links = get_internal_links(response.text, base_url, links_selector)
        print(f"Found {len(links)} internal link(s) in the container.")

        with open(filename, "a", encoding="utf-8") as f:
            for link in links:
                try:
                    link_resp = requests.get(link)
                    link_resp.raise_for_status()
                    link_text = extract_text(link_resp.text, content_selector)
                    f.write(f"\n\n<!-- Content from {link} -->\n\n")
                    f.write(link_text)
                    print(f"Appended text content from {link}")
                except Exception as e:
                    print(f"Error retrieving {link}: {e}")
    except Exception as e:
        print(f"Error retrieving {base_url}: {e}")

if __name__ == "__main__":
    main()