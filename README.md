# 📡 Release Radar — Cloud & AI Intelligence

An elegant, automated daily intelligence system that tracks, aggregates, and reports new features, models, and tools across major Cloud & AI providers (AWS, Google Cloud, Azure, Databricks, Snowflake, Anthropic, and OpenAI).

---

## 🚀 How to Host on GitHub Pages (Free & Serverless)

You can launch your own self-hosted tracker in under a minute:

### 1. Simple Interactive Tracker (Zero Complex Setup)
If you only want to view the aggregated releases and interact with the AI assistant:
1. **Fork** this repository.
2. Go to **Settings** > **Pages** and set the deployment source to build from the `main` branch.
3. Open your live dashboard link: `https://<your-username>.github.io/<your-repository-name>/` (or just `https://<your-username>.github.io/` if hosted as your primary user page).
4. Enter your name and optional receiver email on the onboarding screen.
5. **AI Assistant Chat**: Click the Settings **Gear Icon (⚙️)** in the chat widget header and paste a free **Gemini API Key** from [Google AI Studio](https://aistudio.google.com/). You can now chat with the AI assistant to summarize, explain, or answer questions about any release!

*No GitHub Personal Access Tokens or cloud workflow settings are required for this mode.*

### 2. Live Cloud Scraper & Auto-Sync
If you want your dashboard to run daily cloud scraping runs to fetch new releases:
1. **Configure Repository Secrets**: In your fork under **Settings** > **Secrets and variables** > **Actions**, add:
   - `GEMINI_API_KEY`: *(Required)* Your Google Gemini API Key.
   - `GOOGLE_SCRIPT_URL`: *(Optional)* Your deployed Google Apps Script URL to receive daily email summaries.
   - `RECEIVER_EMAIL`: *(Optional)* Recipient email address.
2. **Setup "Sync Now" UI Button (Optional)**: Click the **Gear icon (⚙️)** in the dashboard chat header to configure your repository name (e.g. `your-username/your-repository-name`) and a **GitHub Personal Access Token (PAT)** with `actions:write` scope. This lets you trigger scraping runs in the cloud directly from the hosted webpage.

---

## ⚙️ How the Settings & Secrets Flow Together

The front-end dashboard includes an in-browser settings panel (accessible via the **Gear Icon ⚙️** in the chat header) that links everything together securely:

### 🔑 Local Browser Settings (Stored in `localStorage`)
These options are processed 100% in the visitor's local browser and are never uploaded, committed, or shared:
- **Gemini API Key**: Used to chat directly with the AI assistant about any tech release. The browser sends HTTPS requests straight to Google's official Gemini endpoint.
- **GitHub PAT (`actions:write` scope)**: Used by the **"Sync Now"** button to authenticate direct requests to the GitHub API and trigger a scraper run in the cloud.
- **Recipient Email & Name**: Saved in browser local storage to personalize greetings and pre-configure the sync inputs.

### 🔒 Repository Secrets (for Daily Cloud Scrapes)
The daily background cron job runs on GitHub's secure runners and uses variables defined in your repository settings under **Actions Secrets**:
- `GEMINI_API_KEY`: Used by the python aggregator running in the cloud to categorize and rank announcements.
- `GOOGLE_SCRIPT_URL`: Used by the runner to dispatch daily summary emails securely via Google Web Apps.
- `RECEIVER_EMAIL`: The target inbox address for daily summary emails.

---

## 💻 Local Setup & Development

If you'd like to run it on your local machine:
1. Clone your repository.
2. Launch the local web server:
   ```bash
   python serve.py
   ```
3. Open `http://localhost:8000` in your web browser.
4. Run the scraper manually:
   ```bash
   python main.py
   ```

*Note: Create a local `config.json` based on the template to configure local SMTP credentials or Apps Script triggers.*
