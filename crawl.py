from urllib import parse
import asyncio
import aiohttp
from bs4 import BeautifulSoup

def normalize_url(url):
    parsed_url = parse.urlparse(url)
    normalized_url = parsed_url.netloc + parsed_url.path
    if normalized_url.endswith("/"):
        normalized_url = normalized_url[:-1]
    return normalized_url

def get_heading_from_html(html):
    soup = BeautifulSoup(html, "html.parser")
    heading = soup.find("h1")
    if heading:
        return heading.get_text()
    return None

def get_first_paragraph_from_html(html):
    soup = BeautifulSoup(html, "html.parser")
    paragraph = soup.find("p")
    if paragraph:
        return paragraph.get_text()
    return None

def get_urls_from_html(html, base_url):
    soup = BeautifulSoup(html, "html.parser")
    urls = []
    for link in soup.find_all("a"):
        href = link.get("href")
        if href:
            absolute_url = parse.urljoin(base_url, href)
            urls.append(absolute_url)
    return urls

def get_images_from_html(html, base_url):
    soup = BeautifulSoup(html, "html.parser")
    images = []
    for img in soup.find_all("img"):
        src = img.get("src")
        if src:
            absolute_url = parse.urljoin(base_url, src)
            images.append(absolute_url)
    return images

def extract_page_data(html, page_url):
    heading = get_heading_from_html(html)
    first_paragraph = get_first_paragraph_from_html(html)
    outgoing_links = get_urls_from_html(html, page_url)
    image_urls = get_images_from_html(html, page_url)
    return {
        "url": normalize_url(page_url),
        "heading": heading,
        "first_paragraph": first_paragraph,
        "outgoing_links": outgoing_links,
        "image_urls": image_urls
    }

class AsyncCrawler:
    def __init__(self, base_url, max_concurrency=3, max_pages=50):
        self.base_url = base_url
        self.base_domain = parse.urlparse(base_url).netloc
        self.page_data = {}
        self.lock = asyncio.Lock()
        self.max_concurrency = max_concurrency
        self.max_pages = max_pages
        self.should_stop = False
        self.all_tasks = set()
        self.semaphore = asyncio.Semaphore(max_concurrency)
        self.session = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.close()

    async def add_page_visit(self, normalized_url):
        async with self.lock:
            if self.should_stop:
                return False

            if len(self.page_data) >= self.max_pages:
                self.should_stop = True
                print("Reached maximum number of pages to crawl.")
                for task in list(self.all_tasks):
                    task.cancel()
                return False

            if normalized_url in self.page_data:
                return False

            # Reserve this URL immediately so concurrent tasks don't duplicate work.
            # Keep a placeholder dict so every visited page can be reported.
            self.page_data[normalized_url] = {
                "url": normalized_url,
                "heading": None,
                "first_paragraph": None,
                "outgoing_links": [],
                "image_urls": [],
            }
            return True

    async def get_html(self, url):
        if self.session is None:
            raise RuntimeError("Crawler session is not initialized")

        async with self.session.get(url, headers={"User-Agent": "BootCrawler/1.0"}) as response:
            response.raise_for_status()

            content_type = response.headers.get("content-type", "").lower()
            if "text/html" not in content_type:
                raise ValueError(f"Expected text/html, got {content_type}")

            return await response.text()

    async def crawl_page(self, current_url=None):
        if self.should_stop:
            return

        if current_url is None:
            current_url = self.base_url

        current_domain = parse.urlparse(current_url).netloc
        if current_domain != self.base_domain:
            return

        normalized_current_url = normalize_url(current_url)
        first_visit = await self.add_page_visit(normalized_current_url)
        if not first_visit:
            return

        print(f"crawling: {current_url}")

        try:
            async with self.semaphore:
                html = await self.get_html(current_url)
                extracted_data = extract_page_data(html, current_url)

                async with self.lock:
                    self.page_data[normalized_current_url] = extracted_data

                discovered_urls = get_urls_from_html(html, current_url)
        except Exception as e:
            print(f"error crawling {current_url}: {e}")
            return

        tasks = []
        for url in discovered_urls:
            task = asyncio.create_task(self.crawl_page(url))
            self.all_tasks.add(task)
            tasks.append(task)

        if tasks:
            try:
                await asyncio.gather(*tasks)
            except asyncio.CancelledError:
                return
            finally:
                for task in tasks:
                    self.all_tasks.discard(task)

    async def crawl(self):
        await self.crawl_page(self.base_url)
        return self.page_data


async def crawl_site_async(base_url, max_concurrency=3, max_pages=50):
    async with AsyncCrawler(
        base_url,
        max_concurrency=max_concurrency,
        max_pages=max_pages,
    ) as crawler:
        return await crawler.crawl()