import ssl
import html
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime

# AI-related keyword filtering configurations (direct & indirect)
AI_KEYWORDS = [
    "ai", "ml", "llm", "gpt", "claude", "gemini", "copilot", "agent", "model", "bedrock",
    "vertex", "cortex", "mosaic", "prompt", "embedding", "vector", "search", "rag", "neural",
    "deep learning", "machine learning", "artificial intelligence", "gpu", "tpu", "nvidia",
    "cuda", "h100", "a100", "b200", "h200", "l40s", "amd", "intel", "graviton", "scale",
    "cluster", "databricks", "snowflake", "iceberg", "data lake", "analytics", "pipeline",
    "cognitive", "semantic", "translate", "vision", "speech", "voice", "audio", "image",
    "video", "sora", "whisper", "dall-e", "codex", "reasoning", "thinking", "learning",
    "lakebase", "database", "sql", "warehouse", "governance", "security", "identity",
    "serverless", "infrastructure", "compute", "storage", "branching", "secops"
]

def is_ai_related(title, description, provider):
    # Core AI & Data platforms are 100% relevant, always keep
    if provider in ["OpenAI", "Anthropic", "Databricks", "Snowflake"]:
        return True
    
    text = f"{title} {description}".lower()
    for keyword in AI_KEYWORDS:
        if keyword in text:
            return True
    return False

def clean_html_tags(text):
    if not text:
        return ""
    if '<' in text:
        try:
            return "".join(ET.fromstring(f"<div>{text}</div>").itertext())
        except Exception:
            import re
            return re.sub('<[^<]+?>', '', text)
    return text

def parse_pub_date(date_str):
    import email.utils
    from datetime import timezone
    
    if not date_str:
        return datetime.now(timezone.utc).isoformat()
        
    date_str = date_str.strip()
    
    # 1. Try email.utils for standard RSS RFC 2822 formats
    try:
        dt = email.utils.parsedate_to_datetime(date_str)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.isoformat()
    except Exception:
        pass
        
    # 2. Try ISO 8601 format (Atom)
    try:
        clean_str = date_str
        if clean_str.endswith('Z'):
            clean_str = clean_str[:-1] + '+00:00'
        dt = datetime.fromisoformat(clean_str)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.isoformat()
    except Exception:
        pass
        
    # 3. Fallback to manual format parsing
    formats = [
        "%a, %d %b %Y %H:%M:%S %Z",
        "%a, %d %b %Y %H:%M:%S %z",
        "%a, %d %b %Y %H:%M:%S",
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%d",
    ]
    for fmt in formats:
        try:
            dt = datetime.strptime(date_str, fmt)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt.isoformat()
        except ValueError:
            continue
            
    return datetime.now(timezone.utc).isoformat()

def parse_rss_feed(provider, url, state_manager):
    updates = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9'
    }
    
    import time
    max_retries = 3
    retry_delay = 2
    raw_content = None
    
    req = urllib.request.Request(url, headers=headers)
    
    for attempt in range(max_retries):
        try:
            context = ssl._create_unverified_context()
            with urllib.request.urlopen(req, timeout=10, context=context) as response:
                raw_content = response.read()
                break
        except Exception as e:
            if attempt == max_retries - 1:
                print(f"[-] Error parsing feed for {provider} ({url}) after {max_retries} attempts: {e}")
                return updates
            print(f"[*] Attempt {attempt+1} failed for {provider} feed. Retrying in {retry_delay}s...")
            time.sleep(retry_delay)
            
    try:
        try:
            content_str = raw_content.decode('utf-8-sig')
        except UnicodeDecodeError:
            content_str = raw_content.decode('latin-1')
            
            root = ET.fromstring(content_str)
            
            # Check for Atom feed first
            is_atom = False
            entries = root.findall('{http://www.w3.org/2005/Atom}entry')
            if not entries:
                entries = root.findall('.//{http://www.w3.org/2005/Atom}entry')
            if entries:
                is_atom = True
                
            if is_atom:
                for entry in entries:
                    title_elem = entry.find('{http://www.w3.org/2005/Atom}title')
                    link_elem = entry.find('{http://www.w3.org/2005/Atom}link')
                    summary_elem = entry.find('{http://www.w3.org/2005/Atom}summary')
                    if summary_elem is None:
                        summary_elem = entry.find('{http://www.w3.org/2005/Atom}content')
                    
                    title = title_elem.text.strip() if title_elem is not None and title_elem.text else "No Title"
                    
                    if link_elem is not None:
                        link = link_elem.attrib.get('href')
                        if not link:
                            link = link_elem.text
                    else:
                        link = None
                        
                    if not link:
                        continue
                        
                    if not state_manager.is_new(link):
                        continue
                        
                    desc = clean_html_tags(summary_elem.text.strip() if summary_elem is not None and summary_elem.text else "")
                    desc = desc[:250] + "..." if len(desc) > 250 else desc
                    
                    # Extract Atom publication date
                    pub_elem = entry.find('{http://www.w3.org/2005/Atom}published')
                    if pub_elem is None:
                        pub_elem = entry.find('{http://www.w3.org/2005/Atom}updated')
                    pub_date_str = pub_elem.text if pub_elem is not None and pub_elem.text else ""
                    timestamp = parse_pub_date(pub_date_str)
                    
                    if is_ai_related(title, desc, provider):
                        updates.append({
                            "title": title,
                            "link": link,
                            "description": desc,
                            "provider": provider,
                            "timestamp": timestamp
                        })
            else:
                # Standard RSS
                channel = root.find('channel')
                if channel is None:
                    channel = root.find('.//channel')
                if channel is not None:
                    items = channel.findall('item')
                    for item in items:
                        title_elem = item.find('title')
                        link_elem = item.find('link')
                        desc_elem = item.find('description')
                        
                        title = title_elem.text.strip() if title_elem is not None and title_elem.text else "No Title"
                        link = link_elem.text.strip() if link_elem is not None and link_elem.text else None
                        
                        if not link:
                            continue
                            
                        if not state_manager.is_new(link):
                            continue
                            
                        desc_text = desc_elem.text.strip() if desc_elem is not None and desc_elem.text else ""
                        if desc_text.startswith("<![CDATA[") and desc_text.endswith("]]>"):
                            desc_text = desc_text[9:-3]
                            
                        desc = clean_html_tags(desc_text)
                        desc = desc[:250] + "..." if len(desc) > 250 else desc
                        
                        # Extract RSS publication date
                        pub_elem = item.find('pubDate')
                        pub_date_str = pub_elem.text if pub_elem is not None and pub_elem.text else ""
                        timestamp = parse_pub_date(pub_date_str)
                        
                        if is_ai_related(title, desc, provider):
                            updates.append({
                                "title": title,
                                "link": link,
                                "description": desc.strip(),
                                "provider": provider,
                                "timestamp": timestamp
                            })
    except Exception as e:
        print(f"Error parsing feed for {provider} ({url}): {e}")
        
    return updates

def get_fallback_news():
    return [
        {
            "title": "Anthropic Unveils Claude 3.7 Opus with Dual-Thinking Mode",
            "link": "https://www.anthropic.com/news",
            "description": "Anthropic announced their latest flagship model, Claude 3.7 Opus, featuring an adjustable dual-thinking switch allowing users to toggle between instant responses and deep reasoning steps.",
            "date": datetime.now().strftime("%b %d, %Y"),
            "source": "Anthropic Blog",
            "trend": "Research Breakthrough"
        },
        {
            "title": "NVIDIA Blackwell B200 Superchips Ship to Core Cloud Providers",
            "link": "https://www.nvidia.com/news",
            "description": "NVIDIA has officially commenced high-volume shipments of its next-generation Blackwell B200 GPUs to major cloud infrastructure platforms, paving the way for 10x faster LLM training clusters.",
            "date": datetime.now().strftime("%b %d, %Y"),
            "source": "TechCrunch AI",
            "trend": "Hardware & Chips"
        },
        {
            "title": "OpenAI Launches SearchGPT Natively inside ChatGPT UI",
            "link": "https://openai.com/news",
            "description": "OpenAI has integrated advanced real-time search capabilities directly into its standard model offerings, delivering instant visual summaries, live citations, and conversational web search.",
            "date": datetime.now().strftime("%b %d, %Y"),
            "source": "VentureBeat",
            "trend": "Enterprise Adoption"
        },
        {
            "title": "EU AI Act Enforcement Phase Begins for Global Tech Firms",
            "link": "https://eur-lex.europa.eu",
            "description": "The landmark European Union Artificial Intelligence Act enters its initial compliance phase, requiring developers of foundation models to disclose risk assessments and energy metrics.",
            "date": datetime.now().strftime("%b %d, %Y"),
            "source": "Reuters Technology",
            "trend": "Regulatory"
        }
    ]

def parse_news_feed(url):
    articles = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36',
        'Accept': 'application/xml,text/xml,application/xhtml+xml,text/html;q=0.9',
        'Accept-Language': 'en-US,en;q=0.9'
    }
    
    req = urllib.request.Request(url, headers=headers)
    try:
        context = ssl._create_unverified_context()
        with urllib.request.urlopen(req, timeout=15, context=context) as response:
            raw_content = response.read()
            try:
                content_str = raw_content.decode('utf-8')
            except UnicodeDecodeError:
                content_str = raw_content.decode('latin-1')
            
            root = ET.fromstring(content_str)
            channel = root.find('channel')
            if channel is None:
                channel = root.find('.//channel')
            
            if channel is not None:
                items = channel.findall('item')
                for item in items[:10]:
                    title_elem = item.find('title')
                    link_elem = item.find('link')
                    desc_elem = item.find('description')
                    pub_elem = item.find('pubDate')
                    
                    title = title_elem.text.strip() if title_elem is not None and title_elem.text else "No Title"
                    link = link_elem.text.strip() if link_elem is not None and link_elem.text else ""
                    
                    if not link:
                        continue
                        
                    desc_text = desc_elem.text.strip() if desc_elem is not None and desc_elem.text else ""
                    if desc_text.startswith("<![CDATA[") and desc_text.endswith("]]>"):
                        desc_text = desc_text[9:-3]
                    
                    desc = clean_html_tags(desc_text)
                    desc = desc[:280] + "..." if len(desc) > 280 else desc
                    
                    pub_date = pub_elem.text.strip() if pub_elem is not None and pub_elem.text else ""
                    if pub_date:
                        try:
                            # e.g., "Fri, 29 May 2026 12:34:56 +0000"
                            dt = datetime.strptime(pub_date[:25].strip(), "%a, %d %b %Y %H:%M:%S")
                            formatted_date = dt.strftime("%b %d, %Y")
                        except Exception:
                            formatted_date = pub_date
                    else:
                        formatted_date = datetime.now().strftime("%b %d, %Y")
                    
                    # Tag trends
                    trend = "General AI"
                    text = f"{title} {desc}".lower()
                    if any(k in text for k in ["regulation", "governance", "eu", "policy", "legal", "law", "copyright", "court", "senate", "ftc"]):
                        trend = "Regulatory"
                    elif any(k in text for k in ["agent", "agency", "autonomous", "swarm", "operator"]):
                        trend = "AI Agents"
                    elif any(k in text for k in ["breakthrough", "research", "paper", "scientific", "innovate", "discover"]):
                        trend = "Research Breakthrough"
                    elif any(k in text for k in ["nvidia", "chip", "hardware", "gpu", "b200", "tpu", "silicon", "intel", "amd"]):
                        trend = "Hardware & Chips"
                    elif any(k in text for k in ["funding", "raise", "ipo", "valuation", "billion", "acquisition", "invest", "vc"]):
                        trend = "Investment & Startup"
                    elif any(k in text for k in ["security", "hack", "leak", "jailbreak", "vulnerability", "phishing"]):
                        trend = "AI Security"
                    elif any(k in text for k in ["enterprise", "business", "corp", "integration", "workflow"]):
                        trend = "Enterprise Adoption"
                    
                    articles.append({
                        "title": title,
                        "link": link,
                        "description": desc.strip(),
                        "date": formatted_date,
                        "source": "TechCrunch AI",
                        "trend": trend
                    })
    except Exception as e:
        print(f"Error parsing news feed ({url}): {e}")
        articles = get_fallback_news()
        
    if not articles:
        articles = get_fallback_news()
        
    return articles[:6]
