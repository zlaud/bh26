import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.news_service import fetch_all_articles

async def main():
    days_back = int(sys.argv[1]) if len(sys.argv) > 1 else 7
    print(f"Fetching articles from last {days_back} days...")
    result = await fetch_all_articles(days_back=days_back)
    print(f"Done: {result['new']} new, {result['skipped']} skipped, {result['total']} total")

asyncio.run(main())