import os
import urllib
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


def download_html(url, file_path):
    """
    Downloads the HTML content from the given URL and saves it to a specified file path.

    Args:
        url (str): The URL to download the HTML content from.
        file_path (str): The file path to save the downloaded HTML content.

    Returns:
        int: Returns 1 if the download was successful, otherwise returns 0.
    """
    response = requests.get(url)
    if response.status_code == 200:
        print(f"URL: {url}")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(response.text)
        print(f"SUCCESS DOWNLOADED from {url}!")
        return 1
    else:
        print(f"URL: {url}")
        print("ERROR!")
        return 0


def get_all_doc_links(base_url):
    """
    Retrieves all documentation links from the base URL.

    Args:
        base_url (str): The base URL to scrape for documentation links.

    Returns:
        list: A list of full URLs to the documentation pages.
    """
    response = requests.get(base_url)
    soup = BeautifulSoup(response.text, "html.parser")

    # Find all links to the documentation pages
    doc_links = []
    for link in soup.find_all("a", href=True):
        href = link["href"]
        if "tutorials/" in href:
            full_url = urljoin(base_url, href)
            doc_links.append(full_url)

    return doc_links


def main():
    """
    Main function to scrape documentation links from the base URL,
    download each HTML page, and save them to a specified directory.
    """
    base_url = "https://python.langchain.com/v0.2/docs/tutorials/"
    output_dir = "../data"
    os.makedirs(output_dir, exist_ok=True)

    doc_links = get_all_doc_links(base_url)
    num_docs = len(doc_links)
    count = 0

    for url in doc_links:
        file_name = url.split("/")[-2] + ".html"
        file_path = os.path.join(output_dir, file_name)
        print(file_path)
        if download_html(url=url, file_path=file_path):
            count += 1
        print("\n")
        print("#" * 50)

    print(f"Successfully downloaded {count}/{num_docs} documents!")


if __name__ == "__main__":
    main()
