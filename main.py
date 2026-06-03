import os
import sys
import urllib.request
import urllib.error
import ssl
from datetime import datetime, timezone

# Add src to the path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(BASE_DIR, "src"))

from state import StateManager
from parser import parse_rss_feed, is_ai_related, parse_news_feed
from email_client import generate_html_email, send_email, generate_no_updates_email
import json

REPORTS_DIR = os.path.join(BASE_DIR, "reports")
SEEN_FILE = os.path.join(BASE_DIR, "seen_updates.json")
CONFIG_FILE = os.path.join(BASE_DIR, "config.json")
SEARCH_FILE = os.path.join(BASE_DIR, "search_updates.json")
HISTORY_FILE = os.path.join(BASE_DIR, "updates_history.json")
DASHBOARD_DATA_JS = os.path.join(BASE_DIR, "dashboard_data.js")
STOCKS_UNIVERSE_JSON = os.path.join(BASE_DIR, "stocks_universe.json")

os.makedirs(REPORTS_DIR, exist_ok=True)

# ── Live Valuation Fetcher (Yahoo Finance, zero dependencies) ──────────────────
STOCK_TICKERS = [
    "NVDA", "GOOGL", "MSFT", "AMZN", "SNOW",  # Direct AI
    "TSM", "AVGO", "ASML", "VRT", "ANET"       # Infrastructure
]

def fetch_valuations(tickers=None):
    """Pull live valuation data from Yahoo Finance for the stock radar universe.
    Returns a dict keyed by ticker, e.g. {"NVDA": {"forwardPE": 42.3, ...}}.
    Uses crumb-based authentication (zero external dependencies)."""
    import http.cookiejar

    if tickers is None:
        # Load from stocks_universe.json if available
        universe = []
        if os.path.exists(STOCKS_UNIVERSE_JSON):
            try:
                with open(STOCKS_UNIVERSE_JSON, 'r', encoding='utf-8') as f:
                    universe = json.load(f)
            except Exception as e:
                print(f"Warning: Could not load stocks universe: {e}")
        
        if universe:
            tickers = [s["ticker"] for s in universe if s.get("ticker") and "IPO" not in s["ticker"].upper()]
        else:
            tickers = STOCK_TICKERS
    symbols = ",".join(tickers)

    # Build an opener with cookie persistence and SSL context
    ctx = ssl._create_unverified_context()
    https_handler = urllib.request.HTTPSHandler(context=ctx)
    cj = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(https_handler, urllib.request.HTTPCookieProcessor(cj))
    opener.addheaders = [
        ("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
    ]

    valuations = {}
    try:
        # Step 1: Get cookies from Yahoo
        try:
            opener.open("https://fc.yahoo.com", timeout=10)
        except Exception:
            pass  # Expected to fail, but sets required cookies

        # Step 2: Get crumb
        crumb = opener.open(
            "https://query2.finance.yahoo.com/v1/test/getcrumb", timeout=10
        ).read().decode("utf-8")

        # Step 3: Fetch quote data with crumb
        url = (
            f"https://query2.finance.yahoo.com/v7/finance/quote"
            f"?symbols={symbols}&crumb={crumb}"
        )
        resp = opener.open(url, timeout=15)
        data = json.loads(resp.read().decode("utf-8"))

        for quote in data.get("quoteResponse", {}).get("result", []):
            ticker = quote.get("symbol", "")
            price = quote.get("regularMarketPrice", 0)
            hi52 = quote.get("fiftyTwoWeekHigh", 0)
            lo52 = quote.get("fiftyTwoWeekLow", 0)
            fwd_pe = quote.get("forwardPE")
            trail_pe = quote.get("trailingPE")
            mkt_cap = quote.get("marketCap", 0)
            ps_ratio = quote.get("priceToSalesTrailing12Months")
            day_chg = quote.get("regularMarketChangePercent", 0)

            # 52-week range position (0 = at 52w low, 1 = at 52w high)
            range_pos = 0.5
            if hi52 and lo52 and hi52 != lo52:
                range_pos = round((price - lo52) / (hi52 - lo52), 3)

            valuations[ticker] = {
                "name": quote.get("shortName", ticker),
                "price": round(price, 2) if price else None,
                "forwardPE": round(fwd_pe, 2) if fwd_pe else None,
                "trailingPE": round(trail_pe, 2) if trail_pe else None,
                "marketCap": mkt_cap,
                "psRatio": round(ps_ratio, 2) if ps_ratio else None,
                "dayChange": round(day_chg, 2) if day_chg else 0,
                "rangePosition": range_pos,
                "fetchedAt": datetime.now().strftime("%Y-%m-%d %I:%M %p")
            }
        print(f"Fetched live valuations for {len(valuations)} tickers.")
    except Exception as e:
        print(f"Warning: Could not fetch Yahoo Finance valuations: {e}")
    return valuations

def discover_new_stocks(new_updates, news_trends, api_key, current_universe):
    """
    Analyzes new release updates and news trends via the Gemini API to discover potential new public stocks.
    Verifies discovered stock tickers against Yahoo Finance.
    Appends successfully validated stocks to the stocks_universe list and saves to stocks_universe.json.
    """
    if not api_key:
        print("Gemini API key not configured. Skipping stock discovery.")
        return current_universe

    if not new_updates and not news_trends:
        print("No new updates or news trends to analyze for stock discovery.")
        return current_universe

    # Prepare context
    context = "NEW RELEASES:\n"
    for item in new_updates:
        context += f"- Title: {item.get('title')}\n  Description: {item.get('description')}\n"
    
    context += "\nNEWS TRENDS:\n"
    for item in news_trends:
        context += f"- Title: {item.get('title')}\n  Description: {item.get('description')}\n"

    # Prepare current tickers list so the AI doesn't duplicate them
    existing_tickers = [s["ticker"].upper() for s in current_universe if s.get("ticker")]
    existing_names = [s["name"].lower() for s in current_universe if s.get("name")]

    prompt = f"""You are an Expert Financial Advisor and AI Market Analyst.
Your goal is to analyze the following daily cloud provider releases and tech news trends to identify any public companies (not currently in our stock radar) that are playing a critical, high-growth role in AI (e.g. AI systems, custom accelerators, AI networking, high-density data center power/cooling, enterprise AI software, data lake platforms).

Here are the today's releases and tech news trends:
{context}

Here are the companies/stocks already in our universe (do NOT recommend or include any of these):
Tickers: {', '.join(existing_tickers)}
Names: {', '.join(existing_names)}

For any newly mentioned or highly relevant public company that is NOT in the current list:
1. Verify the company is publicly traded on a major US exchange and identify its correct stock ticker.
2. Determine if it is a "direct" player (builds models/platforms/compute) or "infra" player (networking, cooling, fabs, chip design tools, data center hardware).
3. Assign a suggested Moat Score (0.0 to 10.0) and Tailwind Score (0.0 to 10.0).
4. Summarize its strategic AI moat (baseReason) and write a short expert advisor investment thesis (expertStrategy).

Output a raw JSON list of these discovered companies. Each company object in the list must have exactly these keys:
- "name": (string, e.g. "Dell Technologies Inc.")
- "ticker": (string, e.g. "DELL")
- "category": (string, either "direct" or "infra")
- "subCategory": (string, e.g. "AI Server Infrastructure")
- "moatScore": (float, e.g. 7.5)
- "tailwindScore": (float, e.g. 8.5)
- "baseReason": (string, e.g. "Leading scale in enterprise AI rack-scale server integrations.")
- "expertStrategy": (string, e.g. "Benefiting from high enterprise demand for plug-and-play Llama-3 compute clusters.")

Output ONLY the JSON list. Do not wrap in ```json ... ``` code blocks, do not write "Here is the list", do not include any other text. If no new public companies match, output an empty list: []."""

    # Call Gemini API
    model_name = "gemini-2.5-flash"
    discovered = []
    
    for attempt in range(2):
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
        payload = {
            "contents": [{
                "parts": [{
                    "text": prompt
                }]
            }]
        }
        
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode('utf-8'),
            headers={'Content-Type': 'application/json'},
            method='POST'
        )
        
        ctx = ssl._create_unverified_context()
        try:
            with urllib.request.urlopen(req, timeout=25, context=ctx) as response:
                res_content = response.read().decode('utf-8')
                res_json = json.loads(res_content)
                reply_text = res_json['candidates'][0]['content']['parts'][0]['text'].strip()
                
                # Clean up any potential markdown formatting if the model ignored instructions
                if reply_text.startswith("```"):
                    reply_text = reply_text.strip("`").replace("json\n", "", 1).strip()
                
                discovered = json.loads(reply_text)
                break
        except urllib.error.HTTPError as he:
            status_code = he.code
            try:
                error_msg = json.loads(he.read().decode('utf-8')).get('error', {}).get('message', '')
            except Exception:
                error_msg = str(he)
                
            if model_name == "gemini-2.5-flash" and (status_code == 503 or "capacity" in error_msg.lower() or "overloaded" in error_msg.lower()):
                print(f"Warning: {model_name} overloaded, falling back to gemini-1.5-flash for discovery...")
                model_name = "gemini-1.5-flash"
                continue
            print(f"Warning: Gemini stock discovery failed: {error_msg}")
            return current_universe
        except Exception as e:
            if model_name == "gemini-2.5-flash":
                print(f"Warning: {model_name} failed ({e}), falling back to gemini-1.5-flash for discovery...")
                model_name = "gemini-1.5-flash"
                continue
            print(f"Warning: Gemini stock discovery failed: {e}")
            return current_universe

    if not discovered or not isinstance(discovered, list):
        print("No new stocks discovered by AI or output format invalid.")
        return current_universe

    print(f"AI suggested {len(discovered)} potential new stocks. Validating tickers...")
    
    # Validation phase using Yahoo Finance crumb opener
    import http.cookiejar
    cj = http.cookiejar.CookieJar()
    https_handler = urllib.request.HTTPSHandler(context=ctx)
    opener = urllib.request.build_opener(https_handler, urllib.request.HTTPCookieProcessor(cj))
    opener.addheaders = [("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")]
    
    valid_new_stocks = []
    try:
        # Get session cookies & crumb
        try:
            opener.open("https://fc.yahoo.com", timeout=10)
        except Exception:
            pass
        
        crumb = opener.open("https://query2.finance.yahoo.com/v1/test/getcrumb", timeout=10).read().decode("utf-8")
        
        for stock in discovered:
            ticker = stock.get("ticker", "").strip().upper()
            if not ticker or ticker in existing_tickers:
                continue
            
            # Query Yahoo quote endpoint for this specific ticker to validate it
            val_url = f"https://query2.finance.yahoo.com/v7/finance/quote?symbols={ticker}&crumb={crumb}"
            try:
                val_resp = opener.open(val_url, timeout=10)
                val_data = json.loads(val_resp.read().decode("utf-8"))
                results = val_data.get("quoteResponse", {}).get("result", [])
                if results:
                    # Valid ticker!
                    quote = results[0]
                    stock["ticker"] = ticker
                    # Override name with standard short name from Yahoo if available
                    stock["name"] = quote.get("shortName", stock.get("name"))
                    valid_new_stocks.append(stock)
                    print(f"   [+] Verified ticker '{ticker}' ({stock['name']}) - price ${quote.get('regularMarketPrice')}")
                else:
                    print(f"   [-] Discarded ticker '{ticker}': Not found in Yahoo Finance")
            except Exception as ve:
                print(f"   [-] Discarded ticker '{ticker}': Validation call failed ({ve})")
    except Exception as e:
        print(f"Warning: Could not perform validation due to Yahoo Finance error: {e}")
        return current_universe

    if valid_new_stocks:
        print(f"Adding {len(valid_new_stocks)} new validated stocks to stocks_universe.json!")
        updated_universe = current_universe + valid_new_stocks
        try:
            with open(STOCKS_UNIVERSE_JSON, 'w', encoding='utf-8') as f:
                json.dump(updated_universe, f, indent=2, ensure_ascii=False)
            return updated_universe
        except Exception as e:
            print(f"Error saving updated stocks universe: {e}")
    else:
        print("No new validated stocks were added today.")
    
    return current_universe

def load_json(filepath, default):
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading {filepath}: {e}")
    return default

def generate_markdown_report(new_updates, report_date):
    md = f"# Release Radar - {report_date}\n\n"
    md += "Here are the latest AI-focused feature, concept, and tool updates from major cloud and AI providers.\n\n"
    
    # Group by provider
    grouped = {}
    for item in new_updates:
        prov = item.get("provider", "Other")
        if prov not in grouped:
            grouped[prov] = []
        grouped[prov].append(item)
        
    for provider, items in grouped.items():
        md += f"## {provider} Updates\n\n"
        for item in items:
            md += f"### [{item['title']}]({item['link']})\n"
            md += f"{item['description']}\n\n"
            md += "---\n\n"
            
    return md

def compute_daily_sentiment(new_updates, news_trends):
    companies = {
        "Anthropic": {"base": 88, "keywords": ["anthropic", "claude"]},
        "OpenAI": {"base": 82, "keywords": ["openai", "chatgpt", "gpt", "sora", "codex", "agentkit"]},
        "NVIDIA": {"base": 91, "keywords": ["nvidia", "blackwell", "b200", "gpu", "superchip"]},
        "Google Cloud": {"base": 80, "keywords": ["google", "gcp", "alloydb", "vertex", "gemini"]},
        "Microsoft": {"base": 78, "keywords": ["microsoft", "azure", "copilot", "sentinel"]},
        "Databricks": {"base": 84, "keywords": ["databricks", "lakehouse", "lakebase"]},
        "Snowflake": {"base": 81, "keywords": ["snowflake", "cortex"]},
        "Meta": {"base": 79, "keywords": ["meta", "llama"]},
        "Groq": {"base": 85, "keywords": ["groq", "lpu"]},
        "Apple": {"base": 76, "keywords": ["apple", "intelligence"]}
    }
    
    pos_words = ["launch", "upgrade", "breakthrough", "success", "partnership", "funding", "accelerate", "improve", "ga", "leader", "powerful"]
    neg_words = ["vulnerability", "hack", "lawsuit", "sued", "jailbreak", "leak", "cut", "layoff", "psychosis", "limit", "safety"]
    
    results = []
    
    for name, data in companies.items():
        mentions = 0
        score = data["base"]
        headline = ""
        
        combined_items = new_updates + news_trends
        
        pos_hits = 0
        neg_hits = 0
        
        for item in combined_items:
            title = item.get("title", "")
            desc = item.get("description", "")
            text = f"{title} {desc}".lower()
            
            if any(k in text for k in data["keywords"]) or (item.get("provider") == name):
                mentions += 1
                if not headline:
                    headline = title[:60] + "..." if len(title) > 60 else title
                
                for p in pos_words:
                    if p in text:
                        pos_hits += 1
                for n in neg_words:
                    if n in text:
                        neg_hits += 1
                        
        score += (pos_hits * 3) - (neg_hits * 6)
        score = max(45, min(98, score))
        
        chg_val = (score + len(name)) % 5 - 2
        if chg_val > 0:
            change = f"▲ +{chg_val}"
        elif chg_val < 0:
            change = f"▼ {chg_val}"
        else:
            change = "▬ Stable"
            
        if mentions == 0:
            headline = "Consistent solid market indexing"
            change = "▬ Stable"
            
        status = "Bullish" if score >= 85 else ("Mixed" if score >= 70 else "Bearish")
        
        results.append({
            "company": name,
            "score": score,
            "status": status,
            "change": change,
            "reason": headline,
            "mentions": mentions
        })
        
    results = sorted(results, key=lambda x: x["score"], reverse=True)
    return results[:10]


def main():
    config = load_json(CONFIG_FILE, {})
    
    # Overwrite/supplement with environment variables for cloud execution
    env_mappings = {
        "send_email_enabled": "SEND_EMAIL_ENABLED",
        "google_script_url": "GOOGLE_SCRIPT_URL",
        "receiver_email": "RECEIVER_EMAIL",
        "smtp_server": "SMTP_SERVER",
        "smtp_port": "SMTP_PORT",
        "smtp_username": "SMTP_USERNAME",
        "smtp_password": "SMTP_PASSWORD",
        "sender_email": "SENDER_EMAIL",
        "gemini_api_key": "GEMINI_API_KEY"
    }
    for config_key, env_key in env_mappings.items():
        env_val = os.environ.get(env_key)
        if env_val is not None:
            if config_key == "send_email_enabled":
                config[config_key] = env_val.lower() in ("true", "1", "yes")
            elif config_key == "smtp_port":
                try:
                    config[config_key] = int(env_val)
                except ValueError:
                    pass
            else:
                config[config_key] = env_val
                
    if "send_email_enabled" not in config:
        config["send_email_enabled"] = True
        
    state_manager = StateManager(SEEN_FILE)
    
    # Load history database
    history = load_json(HISTORY_FILE, [])
    
    rss_feeds = {
        "AWS": "https://aws.amazon.com/blogs/aws/feed/",
        "AWS What's New": "https://aws.amazon.com/about-aws/whats-new/recent/feed/",
        "Google Cloud": "https://cloud.google.com/feeds/gcp-release-notes.xml",
        "Azure": "https://www.microsoft.com/releasecommunications/api/v2/azure/rss",
        "Databricks": "https://databricks.com/feed",
        "OpenAI": "https://openai.com/blog/rss.xml",
        "Anthropic": "https://rsshub.bestblogs.dev/anthropic/news",
        "Google Antigravity": "https://github.com/google-antigravity/antigravity-sdk-python/releases.atom"
    }
    
    new_updates = []
    
    print("Fetching and parsing RSS feeds...")
    for provider, url in rss_feeds.items():
        feed_provider = "AWS" if "AWS" in provider else provider
        raw_updates = parse_rss_feed(feed_provider, url, state_manager)
        new_updates.extend(raw_updates)
        
    # Integrate Snowflake and Anthropic search results
    search_updates = load_json(SEARCH_FILE, [])
    if search_updates:
        print(f"Merging {len(search_updates)} search updates from agent...")
        for item in search_updates:
            link = item.get("link")
            if link and state_manager.is_new(link):
                if is_ai_related(item.get("title", ""), item.get("description", ""), item.get("provider", "")):
                    new_updates.append(item)
        # Clear the search file after reading
        if os.path.exists(SEARCH_FILE):
            try:
                os.remove(SEARCH_FILE)
            except Exception as e:
                print(f"Error removing search file: {e}")
                
    # Update historical database with newly discovered updates
    for item in new_updates:
        # Check duplicate in history list to prevent double entry
        if not any(h.get("link") == item["link"] for h in history):
            history.append({
                "title": item["title"],
                "link": item["link"],
                "description": item["description"],
                "provider": item["provider"],
                "timestamp": item.get("timestamp", datetime.now(timezone.utc).isoformat())
            })
            
    # Save the updated history database
    try:
        with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(history, f, indent=2, ensure_ascii=False)
        print(f"Successfully updated release database ({len(history)} total records)")
    except Exception as e:
        print(f"Error saving history file: {e}")
        
    # Fetch AI News & Trends
    print("Fetching AI News & Trends...")
    news_trends = parse_news_feed("https://techcrunch.com/category/artificial-intelligence/feed/")
    
    # Compute Daily AI Sentiment Index
    print("Computing Daily AI Sentiment Index...")
    sentiments = compute_daily_sentiment(new_updates, news_trends)
    
    # Fetch live stock valuations from Yahoo Finance
    print("Fetching live stock valuations from Yahoo Finance...")
    universe = load_json(STOCKS_UNIVERSE_JSON, [])
    
    # Discover new stocks using AI
    api_key = config.get("gemini_api_key") or os.environ.get("GEMINI_API_KEY")
    if api_key:
        print("Running autonomous AI Market Analysis & Stock Discovery...")
        universe = discover_new_stocks(new_updates, news_trends, api_key, universe)
        
    fetch_tickers = [s["ticker"] for s in universe if s.get("ticker") and "IPO" not in s["ticker"].upper()] if universe else None
    valuations = fetch_valuations(tickers=fetch_tickers)
    
    # Save dashboard data JS to bypass CORS restrictions when opening locally
    dashboard_data = {
        "last_updated": datetime.now().strftime("%Y-%m-%d %I:%M %p"),
        "updates": sorted(history, key=lambda x: x.get("timestamp", ""), reverse=True),
        "trends": news_trends,
        "sentiments": sentiments,
        "valuations": valuations,
        "stocks_universe": universe
    }
    
    try:
        with open(DASHBOARD_DATA_JS, 'w', encoding='utf-8') as f:
            f.write(f"const DASHBOARD_DATA = {json.dumps(dashboard_data, indent=2, ensure_ascii=False)};")
        print("Generated dashboard_data.js successfully!")
    except Exception as e:
        print(f"Error writing dashboard data JS: {e}")
        
    report_date = datetime.now().strftime("%Y-%m-%d")
    
    if not new_updates:
        print("NEW_UPDATES_FOUND=False")
        print("No new updates found today. Shooting 'All Quiet' email with AI news trends...")
        email_html = generate_no_updates_email(news_trends, report_date)
        send_email(config, email_html, report_date)
        return
        
    print(f"NEW_UPDATES_FOUND=True")
    print(f"Found {len(new_updates)} new updates!")
    
    md_content = generate_markdown_report(new_updates, report_date)
    report_filename = f"report_{report_date.replace('-', '_')}.md"
    report_path = os.path.join(REPORTS_DIR, report_filename)
    
    try:
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(md_content)
        print(f"Saved markdown report to {report_path}")
    except Exception as e:
        print(f"Error saving markdown report: {e}")
        
    email_html = generate_html_email(new_updates, report_date, news_trends)
    send_email(config, email_html, report_date)
    
    # Save the links to seen file
    for item in new_updates:
        state_manager.add(item["link"])
    state_manager.save()

if __name__ == "__main__":
    main()
