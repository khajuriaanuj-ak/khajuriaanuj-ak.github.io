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
         to: "akanuj21@gmail.com",
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
2. Set `receiver_email` to `akanuj21@gmail.com`.

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
