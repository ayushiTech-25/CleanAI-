# CleanAI – Deployment & Cloud Hosting Blueprint

This document details configurations to deploy CleanAI in local or production container environments.

---

## 1. Streamlit Community Cloud (Recommended)

Streamlit Community Cloud is the fastest hosting option. It reads files directly from your GitHub repository.

### Setup Steps:
1. Push your clean code to a public GitHub repository.
2. Visit [share.streamlit.io](https://share.streamlit.io/) and log in with your GitHub account.
3. Click **New app**, select your repository, branch (`main`), and set the main file path to:
   `app.py`
4. Click **Advanced settings...** to configure environment credentials.
5. In the **Secrets** text box, paste your API keys:
   ```toml
   GEMINI_API_KEY = "your-google-gemini-key-here"
   CLEANAI_ENV = "production"
   ```
6. Click **Deploy!** Your application will be live at a custom sub-domain link in minutes.

---

## 2. Docker & Containerized Runs (Local or VPS)

To deploy containerized instances locally or on virtual private servers (like AWS EC2 or DigitalOcean Droplets):

### Local Single Run:
1. Build the container image:
   ```bash
   docker build -t cleanai:latest .
   ```
2. Start the container, passing your Gemini key:
   ```bash
   docker run -d -p 8501:8501 -e GEMINI_API_KEY="your_api_key_here" --name cleanai-app cleanai:latest
   ```
3. Visit the dashboard at `http://localhost:8501`.

### Docker Compose Run:
Or run using docker-compose to orchestrate port mappings and folder mounts:
1. Expose your API key in your shell:
   ```bash
   export GEMINI_API_KEY="your_api_key_here"
   ```
2. Launch compose services:
   ```bash
   docker-compose up -d --build
   ```
3. Check container logs:
   ```bash
   docker-compose logs -f
   ```

---

## 3. Render (Cloud Web Services hosting)

Render is a robust cloud alternative to host custom Docker container configurations.

### Setup Steps:
1. Log in to the [Render Dashboard](https://dashboard.render.com/).
2. Click **New +** and select **Web Service**.
3. Link your GitHub repository.
4. Set the following settings:
   - **Runtime**: `Docker`
   - **Instance Type**: Select the Free tier.
5. Click **Advanced** to add environment variables:
   - Key: `GEMINI_API_KEY` | Value: `[your-api-key]`
   - Key: `CLEANAI_ENV` | Value: `production`
   - Key: `PORT` | Value: `8501`
6. Click **Create Web Service**. Render will read your `Dockerfile` automatically, expose port 8501 to a secure public URL, and execute the health check.
