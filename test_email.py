import os
import sys

# Configure directories
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(BASE_DIR, "src"))

from email_client import generate_html_email, send_email, generate_no_updates_email
import json

CONFIG_FILE = os.path.join(BASE_DIR, "config.json")

def main():
    print("==================================================")
    print("   Cloud & AI Release Intelligence - SMTP Tester  ")
    print("==================================================\n")
    
    if not os.path.exists(CONFIG_FILE):
        print(f"Error: Configuration file {CONFIG_FILE} not found!")
        return
        
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        config = json.load(f)
        
    # Check which method is configured
    script_url = config.get("google_script_url", "")
    has_script = script_url and "YOUR_GOOGLE_APPS_SCRIPT" not in script_url and script_url.strip()
    
    has_smtp = (config.get("smtp_username") != "YOUR_EMAIL@gmail.com" and 
                config.get("smtp_password") != "YOUR_APP_PASSWORD" and 
                config.get("smtp_username", "").strip())
                
    if not has_script and not has_smtp:
        print("[-] CONFIGURATION REQUIRED:")
        print("Please edit the 'config.json' file with either a Google Apps Script Web App URL")
        print("or your standard SMTP credentials.\n")
        print("Option A (Recommended & Passwordless):")
        print(" - google_script_url: Paste your Google Apps Script Web App URL\n")
        print("Option B (Standard SMTP):")
        print(" - smtp_server   : e.g., smtp.gmail.com")
        print(" - smtp_username : Your email address")
        print(" - smtp_password : Your App Password")
        print(" - receiver_email: Your recipient email address (akanuj21@gmail.com)\n")
        print("==================================================")
        return
        
    # Force enable for testing
    config["send_email_enabled"] = True
    
    # Mock AI updates
    sample_updates = [
        {
            "title": "Claude Managed Agents: Secure Tunnels and Self-Hosted Sandboxes",
            "link": "https://www.anthropic.com/news/managed-agents",
            "description": "Anthropic announced MCP Tunnels in research preview, allowing developers to route secure agent commands to private databases without public API exposure.",
            "provider": "Anthropic"
        },
        {
            "title": "Google Cloud AlloyDB remote MCP Server Integrations",
            "link": "https://docs.cloud.google.com/release-notes#AlloyDB_MCP",
            "description": "Google Cloud generally released AlloyDB remote MCP tools, letting LLM agents natively query database schemas and execute secure SQL transactions.",
            "provider": "Google Cloud"
        }
    ]
    
    # Mock AI news trends
    sample_trends = [
        {
            "title": "Anthropic Unveils Claude 3.7 Opus with Dual-Thinking Mode",
            "link": "https://www.anthropic.com/news",
            "description": "Anthropic announced their latest flagship model, Claude 3.7 Opus, featuring an adjustable dual-thinking switch allowing users to toggle between instant responses and deep reasoning steps.",
            "date": "May 29, 2026",
            "source": "Anthropic Blog",
            "trend": "Research Breakthrough"
        },
        {
            "title": "NVIDIA Blackwell B200 Superchips Ship to Core Cloud Providers",
            "link": "https://www.nvidia.com/news",
            "description": "NVIDIA has officially commenced high-volume shipments of its next-generation Blackwell B200 GPUs to major cloud infrastructure platforms, paving the way for 10x faster LLM training clusters.",
            "date": "May 28, 2026",
            "source": "TechCrunch AI",
            "trend": "Hardware & Chips"
        }
    ]
    
    print("[1/2] Generating and sending Standard Release Digest (Updates + News)...")
    email_html_1 = generate_html_email(sample_updates, "TEST DIGEST", sample_trends)
    success_1 = send_email(config, email_html_1, "TEST RUN (WITH RELEASES)")
    
    if success_1:
        print("[+] SUCCESS! Test email 1 sent successfully.")
    else:
        print("[-] FAILED: Could not send test email 1.")
        
    print("\n[2/2] Generating and sending 'All Quiet' Digest (Zero Releases, News Only)...")
    email_html_2 = generate_no_updates_email(sample_trends, "TEST DIGEST")
    success_2 = send_email(config, email_html_2, "TEST RUN (ALL QUIET)")
    
    if success_2:
        print("[+] SUCCESS! Test email 2 sent successfully. Please check your inbox.")
    else:
        print("[-] FAILED: Could not send test email 2.")
        
    print("\n==================================================")

if __name__ == "__main__":
    main()
