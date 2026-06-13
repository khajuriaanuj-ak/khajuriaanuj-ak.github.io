# 📡 Release Radar — Cloud & AI Intelligence

An elegant, automated daily intelligence system that tracks, aggregates, and reports new features, models, and tools across major Cloud & AI providers (AWS, Google Cloud, Azure, Databricks, Snowflake, Anthropic, and OpenAI).

---

## 🚀 How to Host on GitHub Pages (Free & Serverless)

You can launch your own self-hosted tracker in under a minute:

### 1. View-Only Dashboard (No Config Required)
1. **Fork** this repository.
2. Go to **Settings** > **Pages** and set the deployment source to build from the `main` branch.
3. Your live dashboard is now hosted at:
   `https://<your-username>.github.io/daily-updater/`

### 2. Enable Daily Scraping & Email Summaries
To automate daily runs or enable manual triggers from the website:
1. **Create Secrets**: In your fork under **Settings** > **Secrets and variables** > **Actions**, add:
   - `GEMINI_API_KEY`: *(Required)* Obtain a free API key from [Google AI Studio](https://aistudio.google.com/).
   - `GOOGLE_SCRIPT_URL`: *(Optional)* Deployed Google Apps Script URL to receive email summaries.
   - `RECEIVER_EMAIL`: *(Optional)* Recipient email address.
2. **Setup manual trigger (Optional)**: Click the **Gear icon (⚙️)** in the dashboard chat header to configure your repository name and a **GitHub Personal Access Token (PAT)** with `actions:write` scope. This allows you to trigger the scraper in the cloud with one click.

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
