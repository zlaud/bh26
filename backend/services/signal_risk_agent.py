from db.crud import get_all_articles, store_signal, signal_exists
from agents.signal_risk_agent import run_signal_extraction, ArticleMessage
import time

async def extract_all_signals() -> dict:
    articles = get_all_articles()
    total = len(articles)
    new_signals = 0
    skipped = 0
    failed = 0

    print(f"\n Starting signal extraction for {total} articles...")

    for idx, article in enumerate(articles, 1):
        article_id = article["id"]
        title = article.get("title", "No title")[:50]
        
        if signal_exists(article_id):
            print(f"[{idx}/{total}] Skipping (already processed): {title}...")
            skipped += 1
            continue
        
        print(f"\n [{idx}/{total}] Processing: {title}...")
        print(f"   Article ID: {article_id}")
        
        msg = ArticleMessage(
            article_id=article_id,
            title=article["title"],
            snippet=article["snippet"],
            source=article["source"],
            published_at=article["published_at"],
            event_type_hint=article["event_type_hint"]
        )
        
        try:
            results = run_signal_extraction(msg)
            
            if results:
                valid_signals = [r for r in results if r.get("relevant", False)]
                
                if valid_signals:
                    # Store first signal with base article_id
                    first = valid_signals[0]
                    store_signal(article_id, first)
                    new_signals += 1
                    print(f" Signal extracted and stored!")
                    print(f"   Event: {first.get('event_type', 'N/A')}")
                    print(f"   Severity: {first.get('severity', 'N/A')}")
                    
                    # Store additional signals with compound IDs
                    if len(valid_signals) > 1:
                        for extra in valid_signals[1:]:
                            compound_id = f"{article_id}_{extra['event_type']}"
                            store_signal(compound_id, extra)
                            new_signals += 1
                            print(f"   + Additional signal: {extra.get('event_type', 'N/A')} (severity: {extra.get('severity', 'N/A')})")
                else:
                    failed += 1
                    print(f" Not relevant or extraction failed")
            else:
                failed += 1
                print(f" Not relevant or extraction failed")
        except Exception as e:
            failed += 1
            print(f" Error: {str(e)[:100]}")
        
        # Rate limiting
        if idx < total:
            print(f" Waiting 2s...")
            time.sleep(2)

    print(f"\n{'='*60}")
    print(f" Extraction complete!")
    print(f"   New signals: {new_signals}")
    print(f"   Skipped: {skipped}")
    print(f"   Failed: {failed}")
    print(f"{'='*60}\n")

    return {
        "new_signals": new_signals,
        "skipped": skipped,
        "failed": failed
    }