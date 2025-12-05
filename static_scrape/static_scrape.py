import os
import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from hashlib import sha1
from collections import deque

BASE_URL = "https://aws.amazon.com/sagemaker/"
DOMAIN = "aws.amazon.com"
DOWNLOAD_IMAGES = True

IMG_DIR = "images"
OUT_FILE = "data.jsonl"

visited = set()
queue = deque([BASE_URL])


def fetch(url):
    r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    r.raise_for_status()
    return r.text


def save_image(url):
    os.makedirs(IMG_DIR, exist_ok=True)
    ext = os.path.splitext(urlparse(url).path)[-1]
    fname = sha1(url.encode()).hexdigest() + ext
    path = os.path.join(IMG_DIR, fname)

    try:
        r = requests.get(url, stream=True, timeout=10)
        if r.ok:
            with open(path, "wb") as f:
                for chunk in r.iter_content(1024):
                    f.write(chunk)
            return path
    except:
        pass
    return None


def parse(url, html):
    soup = BeautifulSoup(html, "lxml")

    
    text = " ".join(
        t.get_text(strip=True) for t in soup.select("p, h1, h2, h3, section")
    )

    
    images = []
    for tag in soup.find_all("img"):
        src = tag.get("src") or tag.get("data-src")
        if not src:
            continue
        img_url = urljoin(url, src)
        local = save_image(img_url) if DOWNLOAD_IMAGES else None
        images.append({"url": img_url, "local": local, "alt": tag.get("alt")})

    
    links = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        full = urljoin(url, href)
        parsed = urlparse(full)

        if DOMAIN in parsed.netloc and "/bedrock" in parsed.path:
            links.append(full)

    return {"url": url, "text": text, "images": images, "links": links}


def save_record(record):
    with open(OUT_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def crawl():
    while queue:
        url = queue.popleft()
        if url in visited:
            continue

        visited.add(url)
        print("Scraping:", url)

        try:
            html = fetch(url)
        except Exception as e:
            print("Failed:", url, e)
            continue

        data = parse(url, html)
        save_record(data)

        
        for link in data["links"]:
            if link not in visited:
                queue.append(link)


def main():
    
    if os.path.exists(OUT_FILE):
        os.remove(OUT_FILE)

    crawl()
    print("\nDone. Pages scraped:", len(visited))


if __name__ == "__main__":
    main()