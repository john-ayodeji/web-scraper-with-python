import asyncio
import sys
from crawl import crawl_site_async
from json_report import write_json_report

async def main_async():
    if len(sys.argv) < 4:
        print("usage: python main.py URL max_concurrency max_pages")
        exit(1)
    elif len(sys.argv) > 4:
        print("too many arguments provided")
        exit(1)
    else:
        base_url = sys.argv[1]
        try:
            max_concurrency = int(sys.argv[2])
            max_pages = int(sys.argv[3])
        except ValueError:
            print("max_concurrency and max_pages must be integers")
            exit(1)

        if max_concurrency < 1:
            print("max_concurrency must be at least 1")
            exit(1)

        if max_pages < 1:
            print("max_pages must be at least 1")
            exit(1)

        print(f"starting crawl of: {base_url}")
        print(f"max concurrency: {max_concurrency}, max pages: {max_pages}")
        page_data = await crawl_site_async(
            base_url,
            max_concurrency=max_concurrency,
            max_pages=max_pages,
        )
        print(f"\npages found: {len(page_data)}")
        write_json_report(page_data)
        print("wrote JSON report to report.json")


if __name__ == "__main__":
    asyncio.run(main_async())