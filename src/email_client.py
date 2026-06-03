import ssl
import html
import smtplib
from email.message import EmailMessage

PROVIDER_STYLES = {
    "AWS": {"color": "#FF9900", "bg": "#FFF2E6"},
    "Google Cloud": {"color": "#34A853", "bg": "#E6F4EA"},
    "Azure": {"color": "#0078D4", "bg": "#E6F2FC"},
    "Databricks": {"color": "#FF3621", "bg": "#FFEBEA"},
    "Snowflake": {"color": "#29B5E8", "bg": "#EBF8FD"},
    "OpenAI": {"color": "#10A37F", "bg": "#E7F6F2"},
    "Anthropic": {"color": "#E0573E", "bg": "#FCF3F1"}
}

def generate_trends_html(news_trends):
    if not news_trends:
        return ""
        
    trends_html = """
    <div style="margin-top: 32px; border-top: 2px dashed #e2e8f0; padding-top: 24px;">
        <h2 style="margin: 0 0 16px 0; font-size: 20px; color: #1e3a8a; font-family: 'Inter', sans-serif; font-weight: 700;">
            🔥 Global AI News & Trends of the Day
        </h2>
    """
    
    for item in news_trends:
        trend_cat = item.get("trend", "General AI")
        cat_styles = {
            "Regulatory": {"color": "#7c3aed", "bg": "#f5f3ff"},
            "AI Agents": {"color": "#ea580c", "bg": "#fff7ed"},
            "Research Breakthrough": {"color": "#0d9488", "bg": "#f0fdfa"},
            "Hardware & Chips": {"color": "#0284c7", "bg": "#f0f9ff"},
            "Investment & Startup": {"color": "#b45309", "bg": "#fef3c7"},
            "AI Security": {"color": "#dc2626", "bg": "#fef2f2"},
            "Enterprise Adoption": {"color": "#2563eb", "bg": "#eff6ff"},
            "General AI": {"color": "#4b5563", "bg": "#f3f4f6"}
        }
        style = cat_styles.get(trend_cat, cat_styles["General AI"])
        
        trends_html += f"""
        <div style="margin-bottom: 16px; padding: 16px; border-radius: 10px; background-color: #ffffff; border: 1px solid #e2e8f0; box-shadow: 0 2px 4px rgba(0,0,0,0.02);">
            <div style="margin-bottom: 6px;">
                <span style="display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 10px; font-weight: bold; text-transform: uppercase; color: {style['color']}; background-color: {style['bg']}; font-family: 'Inter', sans-serif; margin-right: 8px;">
                    {trend_cat}
                </span>
                <span style="font-size: 11px; color: #94a3b8; font-family: 'Inter', sans-serif;">{item.get('source', 'News')} &bull; {item.get('date', '')}</span>
            </div>
            <h4 style="margin: 0 0 6px 0; font-size: 15px; color: #1e293b; font-family: 'Inter', sans-serif; font-weight: 600;">
                <a href="{item['link']}" target="_blank" style="color: #2563eb; text-decoration: none;">{html.escape(item['title'])}</a>
            </h4>
            <p style="margin: 0; font-size: 13px; color: #64748b; line-height: 1.5; font-family: 'Inter', sans-serif;">
                {html.escape(item['description'])}
            </p>
        </div>
        """
        
    trends_html += "</div>"
    return trends_html

def generate_no_updates_email(news_trends, report_date):
    trends_html = generate_trends_html(news_trends)
    
    email_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Daily Cloud & AI Intelligence - All Quiet</title>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
    </head>
    <body style="margin: 0; padding: 0; background-color: #f7fafc; font-family: 'Inter', sans-serif;">
        <table width="100%" border="0" cellspacing="0" cellpadding="0" style="background-color: #f7fafc; padding: 40px 20px;">
            <tr>
                <td align="center">
                    <table width="600" border="0" cellspacing="0" cellpadding="0" style="background-color: #ffffff; border-radius: 16px; overflow: hidden; box-shadow: 0 10px 15px rgba(0,0,0,0.03);">
                        <!-- Header -->
                        <tr>
                            <td style="background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); padding: 40px 30px; text-align: center;">
                                <h1 style="margin: 0; font-size: 24px; color: #ffffff; font-weight: 700; letter-spacing: -0.5px;">Cloud & AI Release Intelligence</h1>
                                <p style="margin: 8px 0 0 0; font-size: 14px; color: #94a3b8;">Daily Digest &bull; {report_date}</p>
                            </td>
                        </tr>
                        <!-- Content -->
                        <tr>
                            <td style="padding: 40px 30px; background-color: #f8fafc;">
                                <div style="text-align: center; margin-bottom: 32px; padding: 24px; border-radius: 12px; background-color: #e2e8f0; border: 1px dashed #94a3b8;">
                                    <span style="font-size: 32px;">☕</span>
                                    <h3 style="margin: 12px 0 6px 0; font-size: 16px; color: #334155; font-family: 'Inter', sans-serif; font-weight: 600;">
                                        All Quiet on the Tech Front
                                    </h3>
                                    <p style="margin: 0; font-size: 14px; color: #64748b; font-family: 'Inter', sans-serif; line-height: 1.5;">
                                        No new official AI product or feature releases were detected from AWS, Google Cloud, Azure, Databricks, Snowflake, OpenAI, or Anthropic in the last 24 hours.
                                    </p>
                                </div>
                                
                                {trends_html}
                                
                                <div style="text-align: center; margin-top: 32px;">
                                    <a href="http://localhost:8000" target="_blank" style="display: inline-block; padding: 12px 24px; border-radius: 8px; background-color: #2563eb; color: #ffffff; font-weight: bold; text-decoration: none; font-size: 14px; font-family: 'Inter', sans-serif; box-shadow: 0 4px 6px rgba(37, 99, 235, 0.2);">
                                        Open Interactive Dashboard
                                    </a>
                                </div>
                            </td>
                        </tr>
                        <!-- Footer -->
                        <tr>
                            <td style="background-color: #f1f5f9; padding: 24px 30px; text-align: center; border-top: 1px solid #e2e8f0;">
                                <p style="margin: 0; font-size: 12px; color: #94a3b8;">
                                    Automated Daily Intelligence System &bull; Structured Project Release
                                </p>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """
    return email_body

def generate_html_email(new_updates, report_date, news_trends=[]):
    items_html = ""
    for item in new_updates:
        prov = item.get("provider", "Cloud & AI")
        style = PROVIDER_STYLES.get(prov, {"color": "#4A5568", "bg": "#EDF2F7"})
        
        items_html += f"""
        <div style="margin-bottom: 24px; padding: 20px; border-radius: 12px; background-color: #ffffff; border-left: 5px solid {style['color']}; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);">
            <div style="margin-bottom: 8px;">
                <span style="display: inline-block; padding: 4px 10px; border-radius: 6px; font-size: 11px; font-weight: bold; text-transform: uppercase; color: {style['color']}; background-color: {style['bg']};">
                    {prov}
                </span>
            </div>
            <h3 style="margin: 0 0 8px 0; font-size: 18px; color: #1a202c; font-family: 'Inter', sans-serif;">
                {html.escape(item['title'])}
            </h3>
            <p style="margin: 0 0 16px 0; font-size: 14px; color: #4a5568; line-height: 1.6; font-family: 'Inter', sans-serif;">
                {html.escape(item['description'])}
            </p>
            <a href="{item['link']}" target="_blank" style="display: inline-block; font-size: 14px; font-weight: bold; color: {style['color']}; text-decoration: none; font-family: 'Inter', sans-serif;">
                Read full announcement &rarr;
            </a>
        </div>
        """

    trends_section = generate_trends_html(news_trends)

    email_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Daily Cloud & AI Intelligence</title>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
    </head>
    <body style="margin: 0; padding: 0; background-color: #f7fafc; font-family: 'Inter', sans-serif;">
        <table width="100%" border="0" cellspacing="0" cellpadding="0" style="background-color: #f7fafc; padding: 40px 20px;">
            <tr>
                <td align="center">
                    <table width="600" border="0" cellspacing="0" cellpadding="0" style="background-color: #ffffff; border-radius: 16px; overflow: hidden; box-shadow: 0 10px 15px rgba(0,0,0,0.03);">
                        <!-- Header -->
                        <tr>
                            <td style="background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%); padding: 40px 30px; text-align: center;">
                                <h1 style="margin: 0; font-size: 24px; color: #ffffff; font-weight: 700; letter-spacing: -0.5px;">Cloud & AI Release Intelligence</h1>
                                <p style="margin: 8px 0 0 0; font-size: 14px; color: #bfdbfe;">AI-Focused Releases &bull; {report_date}</p>
                            </td>
                        </tr>
                        <!-- Content -->
                        <tr>
                            <td style="padding: 40px 30px; background-color: #f8fafc;">
                                <p style="margin: 0 0 24px 0; font-size: 15px; color: #334155; line-height: 1.5;">
                                    Hello, here are the latest AI-focused features, concepts, and tool releases detected across major cloud and AI platforms.
                                </p>
                                {items_html}
                                {trends_section}
                            </td>
                        </tr>
                        <!-- Footer -->
                        <tr>
                            <td style="background-color: #f1f5f9; padding: 24px 30px; text-align: center; border-top: 1px solid #e2e8f0;">
                                <p style="margin: 0; font-size: 12px; color: #94a3b8;">
                                    Automated Daily Intelligence System &bull; Structured Project Release
                                </p>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """
    return email_body

def send_email_via_google_script(url, subject, html_body):
    import json
    import urllib.request
    
    payload = {
        "subject": subject,
        "htmlBody": html_body
    }
    
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(
        url,
        data=data,
        headers={'Content-Type': 'application/json'}
    )
    
    try:
        # Apps Script Web Apps require following redirects automatically in urllib
        context = ssl.create_default_context()
        with urllib.request.urlopen(req, timeout=20, context=context) as response:
            res_content = response.read().decode('utf-8')
            try:
                res_json = json.loads(res_content)
                if res_json.get("status") == "success":
                    print("[+] Successfully sent email via Google Apps Script Web App!")
                    return True
                else:
                    print(f"[-] Google Apps Script returned an error: {res_json.get('message')}")
                    return False
            except Exception:
                # If Apps Script returns raw HTML or success string without JSON formatting
                if "success" in res_content.lower() or response.status == 200:
                    print("[+] Successfully dispatched email via Google Apps Script Web App!")
                    return True
                print(f"[-] Google Apps Script response parsed failure: {res_content[:200]}")
                return False
    except Exception as e:
        print(f"[-] Failed to send email via Google Apps Script: {e}")
        return False

def send_email(config, email_html, report_date):
    if not config.get("send_email_enabled"):
        print("Email notification is disabled in config.json")
        return False
        
    subject = f"Cloud & AI Release Intelligence - {report_date}"
    
    # 1. Try Google Apps Script Web App (Passwordless Option)
    script_url = config.get("google_script_url")
    if script_url and "YOUR_GOOGLE_APPS_SCRIPT" not in script_url and script_url.strip():
        print("[*] Detected Google Apps Script Web App URL. Routing email passwordlessly...")
        return send_email_via_google_script(script_url, subject, email_html)
        
    # 2. Fallback to standard SMTP
    smtp_server = config.get("smtp_server")
    smtp_port = config.get("smtp_port", 587)
    username = config.get("smtp_username")
    password = config.get("smtp_password")
    sender = config.get("sender_email")
    receiver = config.get("receiver_email")
    
    if not all([smtp_server, username, password, sender, receiver]) or "YOUR_EMAIL" in username:
        print("Warning: Neither Google Apps Script nor SMTP credentials are fully configured in config.json. Cannot send email.")
        return False
        
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = receiver
    msg.set_content("Please enable HTML viewing to see the latest Cloud & AI updates.")
    msg.add_alternative(email_html, subtype='html')
    
    context = ssl.create_default_context()
    try:
        if smtp_port == 465:
            # Implicit SSL/TLS
            with smtplib.SMTP_SSL(smtp_server, smtp_port, context=context) as server:
                server.login(username, password)
                server.send_message(msg)
        else:
            # Explicit STARTTLS
            with smtplib.SMTP(smtp_server, smtp_port, timeout=15) as server:
                server.starttls(context=context)
                server.login(username, password)
                server.send_message(msg)
        print(f"Successfully sent updates email to {receiver}!")
        return True
    except Exception as e:
        print(f"Failed to send email via SMTP: {e}")
        return False
