import os
import sys
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

os.makedirs(REPORTS_DIR, exist_ok=True)

def load_json(filepath, default):
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading {filepath}: {e}")
    return default

def generate_markdown_report(new_updates, report_date):
    md = f"# Cloud & AI Releases Report - {report_date}\n\n"
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
        "Anthropic": "https://rsshub.bestblogs.dev/anthropic/news"
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
    
    # Save dashboard data JS to bypass CORS restrictions when opening locally
    dashboard_data = {
        "last_updated": datetime.now().strftime("%Y-%m-%d %I:%M %p"),
        "updates": sorted(history, key=lambda x: x.get("timestamp", ""), reverse=True),
        "trends": news_trends,
        "sentiments": sentiments
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
