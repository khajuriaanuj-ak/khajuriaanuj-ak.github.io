import http.server
import socketserver
import webbrowser
import os
import sys
from threading import Timer

PORT = 8000
DIRECTORY = os.path.dirname(os.path.abspath(__file__))

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)
        
    def end_headers(self):
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        super().end_headers()
        
    def do_POST(self):
        if self.path == '/api/sync':
            try:
                import subprocess
                import json
                import re
                
                # Run main.py as a subprocess
                process = subprocess.run([sys.executable, os.path.join(DIRECTORY, 'main.py')], capture_output=True, text=True, encoding='utf-8')
                
                if process.returncode == 0:
                    output = process.stdout
                    new_releases = 0
                    match = re.search(r'Found (\d+) new updates', output)
                    if match:
                        new_releases = int(match.group(1))
                    
                    response_body = {
                        "success": True,
                        "new_releases": new_releases,
                        "log": output
                    }
                    self.send_response(200)
                else:
                    response_body = {
                        "success": False,
                        "error": process.stderr or process.stdout or "Scraper exited with non-zero status"
                    }
                    self.send_response(500)
                    
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(response_body).encode('utf-8'))
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"success": False, "error": str(e)}).encode('utf-8'))
        elif self.path == '/api/valuations':
            try:
                import json
                # Import valuation fetcher from main.py
                sys.path.insert(0, DIRECTORY)
                from main import fetch_valuations
                
                # Load tickers dynamically from stocks_universe.json
                universe_path = os.path.join(DIRECTORY, "stocks_universe.json")
                tickers = None
                if os.path.exists(universe_path):
                    try:
                        with open(universe_path, 'r', encoding='utf-8') as f:
                            universe = json.load(f)
                            tickers = [s["ticker"] for s in universe if s.get("ticker") and "IPO" not in s["ticker"].upper()]
                    except Exception as ue:
                        print(f"Warning: serve.py could not load stocks universe: {ue}")
                
                valuations = fetch_valuations(tickers=tickers)
                response_body = {"success": True, "valuations": valuations}
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps(response_body).encode('utf-8'))
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"success": False, "error": str(e)}).encode('utf-8'))
        elif self.path == '/api/chat':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            try:
                import json
                request_data = json.loads(post_data.decode('utf-8'))
                query = request_data.get('query', '')
                
                # Load configuration and API key
                config_path = os.path.join(DIRECTORY, "config.json")
                config = {}
                if os.path.exists(config_path):
                    with open(config_path, 'r', encoding='utf-8') as f:
                        config = json.load(f)
                        
                api_key = config.get("gemini_api_key") or os.environ.get("GEMINI_API_KEY")
                
                if not api_key or "YOUR_GEMINI_API_KEY" in api_key or not api_key.strip():
                    # Return instructions to add key
                    response_body = {
                        "reply": "I would love to help you understand this feature in deep technical detail! To activate my advanced reasoning capabilities, please open your <code>config.json</code> file and add a free <strong>Gemini API Key</strong>:<br><br><pre style='background:rgba(0,0,0,0.3); padding:10px; border-radius:6px; font-family:monospace; font-size:11px;'>{\n  \"gemini_api_key\": \"AIzaSyYourKeyHere\",\n  ...\n}</pre><br>You can get a free API Key instantly from <a href='https://aistudio.google.com/' target='_blank' style='color:#60a5fa; font-weight:600; text-decoration:underline;'>Google AI Studio</a>! In the meantime, I can still assist with basic local queries."
                    }
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps(response_body).encode('utf-8'))
                    return
                
                # Fetch relevant releases context
                history_path = os.path.join(DIRECTORY, "updates_history.json")
                history_data = []
                if os.path.exists(history_path):
                    with open(history_path, 'r', encoding='utf-8') as f:
                        history_data = json.load(f)
                
                # Search related items using keywords
                keywords = [w for w in query.lower().split() if len(w) > 2]
                related_releases = []
                for item in history_data:
                    text = f"{item.get('title', '')} {item.get('description', '')}".lower()
                    if any(k in text for k in keywords) or query.lower() in item.get('provider', '').lower():
                        related_releases.append(item)
                        if len(related_releases) >= 8:
                            break
                            
                # If no matching items by keyword, grab the latest 5
                if not related_releases:
                    related_releases = history_data[:5]
                    
                context_str = ""
                for idx, item in enumerate(related_releases):
                    context_str += f"[{idx+1}] Provider: {item.get('provider')}\nTitle: {item.get('title')}\nLink: {item.get('link')}\nDescription: {item.get('description')}\n\n"
                
                # Call Gemini API
                import urllib.request
                import ssl
                
                # Call Gemini API with automatic fallback from 2.5-flash to 1.5-flash
                import urllib.request
                import ssl
                import re
                
                reply_text = None
                model_name = "gemini-2.5-flash"
                
                for attempt in range(2):
                    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
                    prompt = f"""You are the Antigravity AI Release Intelligence Assistant. Your goal is to help the user understand new cloud features, tech releases, and product announcements in depth.

Here is the context of relevant releases we tracked:
{context_str}

User Question: {query}

Provide a comprehensive, clear, and technically rich explanation. Summarize what the feature accomplishes, why it is important (the 'so what'), and how they can get started. Use clean bullet points and concise paragraphs. If a link is provided in the context, refer to it so they can read more. Convert any code snippets to pre/code tags."""

                    payload = {
                        "contents": [{
                            "parts": [{
                                "text": prompt
                            }]
                        }]
                    }
                    
                    headers = {'Content-Type': 'application/json'}
                    req = urllib.request.Request(
                        url,
                        data=json.dumps(payload).encode('utf-8'),
                        headers=headers,
                        method='POST'
                    )
                    
                    context = ssl._create_unverified_context()
                    try:
                        with urllib.request.urlopen(req, timeout=20, context=context) as response:
                            res_content = response.read().decode('utf-8')
                            res_json = json.loads(res_content)
                            reply_text = res_json['candidates'][0]['content']['parts'][0]['text']
                            break
                    except urllib.error.HTTPError as he:
                        status_code = he.code
                        try:
                            error_data = json.loads(he.read().decode('utf-8'))
                            error_msg = error_data.get('error', {}).get('message', '')
                        except Exception:
                            error_msg = str(he)
                            
                        # If 2.5-flash fails with 503 or demand issues, fall back to 1.5-flash
                        if model_name == "gemini-2.5-flash" and (status_code == 503 or any(k in error_msg.lower() for k in ["demand", "overloaded", "capacity", "temporary"])):
                            print("[*] Backend: gemini-2.5-flash experiencing high demand, falling back to gemini-1.5-flash...")
                            model_name = "gemini-1.5-flash"
                            continue
                        raise Exception(error_msg or f"HTTP Error {status_code}")
                    except Exception as e:
                        if model_name == "gemini-2.5-flash":
                            print(f"[*] Backend: gemini-2.5-flash call failed ({e}), falling back to gemini-1.5-flash...")
                            model_name = "gemini-1.5-flash"
                            continue
                        raise e
                        
                if not reply_text:
                    raise Exception("Failed to get response from Gemini API models.")
                
                # Convert simple markdown formatting to HTML tags
                reply_html = reply_text.replace('\n', '<br>')
                reply_html = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', reply_html)
                reply_html = re.sub(r'\*(.*?)\*', r'<em>\1</em>', reply_html)
                reply_html = re.sub(r'```(.*?)```', r'<pre style="background:rgba(0,0,0,0.25); padding:8px; border-radius:6px; font-family:monospace; font-size:11px; margin:8px 0; overflow-x:auto;">\1</pre>', reply_html)
                
                response_body = {"reply": reply_html}
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(response_body).encode('utf-8'))
                    
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"reply": f"Error calling AI Assistant: {e}"}).encode('utf-8'))
        else:
            self.send_error(404, "File not found")

def main():
    os.chdir(DIRECTORY)
    
    if not os.path.exists("index.html"):
        print("Error: index.html not found in current directory!")
        sys.exit(1)
        
    print("==================================================")
    print("   Cloud & AI Release Intelligence - Web Server   ")
    print("==================================================\n")
    print(f"[*] Starting local server at http://localhost:{PORT}...")
    print(f"[*] Root directory: {DIRECTORY}")
    print("[*] Close this command prompt (Ctrl+C) to stop.\n")
    
    socketserver.TCPServer.allow_reuse_address = True
    
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        # Launch browser silently after server has bound to the port
        Timer(1.5, lambda: webbrowser.open(f"http://localhost:{PORT}")).start()
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n[-] Server stopped. Goodbye!")

if __name__ == "__main__":
    main()
