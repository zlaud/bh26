import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.signal_risk_agent import extract_all_signals

async def main():
    print("Extracting signals from cached articles...")
    result = await extract_all_signals()
    print(f"Done: {result['new_signals']} new, {result['skipped']} skipped, {result['failed']} failed")

asyncio.run(main())