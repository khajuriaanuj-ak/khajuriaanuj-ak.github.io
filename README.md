# Cloud & AI Release Intelligence Aggregator

An elegant, automated daily intelligence system designed to discover, track, and report new features, concepts, and tool releases across major cloud and AI platforms:
* **AWS**
* **Google Cloud**
* **Azure / Microsoft**
* **Databricks**
* **Snowflake**
* **Anthropic**
* **OpenAI**

## Project Structure

- `main.py`: Main orchestrator connecting all modular files.
- `config.json`: Configurations for dispatching daily emails (supports both Google Apps Script and SMTP).
- `seen_updates.json`: State file tracking already reported URLs to prevent duplicates.
- `search_updates.json`: Agent-injected search updates for Snowflake and Anthropic.
- `reports/`: Stores premium historical markdown reports generated daily.
- `src/`: Module source code folder containing `state.py`, `parser.py`, and `email_client.py`.

## Setup Email Notifications

To enable daily email updates, change `"send_email_enabled": false` to `"send_email_enabled": true` in `config.json`, then select one of the two methods below:

### Option A: Passwordless Setup (Google Apps Script Web App) - RECOMMENDED
This method is fully secure and uses Google's native authorization so you **do not need to input any SMTP passwords** into the local configuration file.

1. Go to [script.google.com](https://script.google.com) and click **New Project**.
2. Replace all code in `Code.gs` with the following:
   ```javascript
   function doPost(e) {
     try {
       var data = JSON.parse(e.postData.contents);
       var subject = data.subject || "Cloud & AI Release Intelligence";
       var htmlBody = data.htmlBody;
       
       MailApp.sendEmail({
         to: "YOUR_RECEIVER_EMAIL@gmail.com",
         subject: subject,
         htmlBody: htmlBody
       });
       
       return ContentService.createTextOutput(JSON.stringify({status: "success"}))
         .setMimeType(ContentService.MimeType.JSON);
     } catch (error) {
       return ContentService.createTextOutput(JSON.stringify({status: "error", message: error.toString()}))
         .setMimeType(ContentService.MimeType.JSON);
     }
   }
   ```
3. Click the Save icon, then click **Deploy** > **New deployment**.
4. Click the gear icon next to "Select type" and choose **Web app**.
5. Configure the deployment:
   * **Description**: `AI Aggregator Webhook`
   * **Execute as**: `Me (your-email@gmail.com)`
   * **Who has access**: **`Anyone`** *(This is required to allow your local python script to submit POST requests securely).*
6. Click **Deploy**, authorize the secure permissions dialog once, and copy the **Web app URL**.
7. Paste this URL into the `"google_script_url"` field in `config.json`.

### Option B: Standard Setup (SMTP)
Configure your SMTP credentials in `config.json`:
1. Enter your SMTP details:
   - For **Gmail**:
     - `smtp_server`: `smtp.gmail.com`
     - `smtp_port`: `587`
     - `smtp_username`: Your full Gmail address.
     - `smtp_password`: A Google App Password (generate one under Google Account > Security > 2-Step Verification > App Passwords).
2. Set `receiver_email` to your recipient email address.

## Execution Flow

1. The automated background cron job runs daily.
2. The agent fetches target web search updates for **Anthropic** and **Snowflake** and saves them in `search_updates.json`.
3. The agent triggers `main.py`.
4. `main.py` parses new releases, merges search results, and filters duplicates based on AI keywords.
5. If new updates are found:
   - A gorgeous historical report is created in `reports/`.
   - A premium HTML email is dispatched to your inbox (via Apps Script or SMTP).
   - The agent prints a detailed notification.
6. If no new updates are found, it exits silently without bothering you.

## Self-Hosting & GitHub Pages

You can easily host your own copy of this intelligence tracker on GitHub Pages by forking this repository.

### 1. View-Only Dashboard (No Setup Required)
If you just want to host and view the aggregated release histories statically:
1. **Fork** this repository to your own GitHub account.
2. Go to **Settings** > **Pages**.
3. Under **Build and deployment**, set the **Source** to "Deploy from a branch", select `main` as the branch, `/ (root)` as the folder, and click **Save**.
4. Your static dashboard will be live at:
   `https://<your-github-username>.github.io/daily-updater/`
   
*No Personal Access Tokens or API keys are required to simply view the dashboard.*

### 2. Enabling Automated Cloud Sync & Customizations
If you want your fork to run the scraper automatically every day or allow manual syncs from the web UI:
1. **Configure Repository Secrets**:
   Go to your fork's **Settings** > **Secrets and variables** > **Actions** and create the following secrets:
   - `GEMINI_API_KEY`: *(Required)* Your Google Gemini API Key (obtain a free key from [Google AI Studio](https://aistudio.google.com/)).
   - `GOOGLE_SCRIPT_URL`: *(Optional)* Your deployed Google Apps Script Web App URL for routing summary emails.
   - `RECEIVER_EMAIL`: *(Optional)* The email address where daily digests will be sent.
2. **Web UI Manual Sync (Optional)**:
   If you want to use the **"Sync Now"** button on your hosted GitHub Pages site to trigger a live run:
   - Open your hosted dashboard and click the settings **Gear Icon (⚙️)** in the chat widget header.
   - Under **GitHub Actions Sync Settings**, enter your repository path (`owner/repository`, e.g., `your-username/daily-updater`).
   - Paste a **GitHub Personal Access Token (PAT)** with `actions:write` scope.
   - *Security Note: Your PAT is stored securely in your browser's local storage (`localStorage`) and is only used to send direct, authenticated requests to GitHub's REST API. It is never transmitted to any third party.*

