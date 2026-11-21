# Deployment Guide: Deep Research AI Agent

This guide provides instructions to run and deploy the **Deep Research AI Agent** to free cloud hosting platforms (Render, Hugging Face Spaces, Railway, or Docker).

---

## 🚀 Option 1: Deploy on Render (Recommended & Free)

[Render](https://render.com/) offers a free tier for hosting Python web services with automatic GitHub CI/CD.

### Step 1: Push your Code to GitHub
1. Ensure your latest changes are pushed to your GitHub repository:
   ```bash
   git add .
   git commit -m "Update Deep Research AI Agent for production deployment"
   git push origin main
   ```

### Step 2: Create a Web Service on Render
1. Go to [Render Dashboard](https://dashboard.render.com/) and sign in with GitHub.
2. Click **New +** and select **Web Service**.
3. Choose your repository: `internship-springboard-project`.
4. Configure the service settings:
   - **Name**: `deep-research-ai-agent`
   - **Region**: Select closest to you (e.g., Singapore or Oregon)
   - **Branch**: `main`
   - **Runtime**: `Python 3`
   - **Build Command**:
     ```bash
     pip install -r requirements.txt
     ```
   - **Start Command**:
     ```bash
     gunicorn app:app --workers 2 --timeout 120 --bind 0.0.0.0:$PORT
     ```
   - **Instance Type**: `Free`

### Step 3: Add Environment Variables
Scroll to the **Environment Variables** section and add:
- `GEMINI_API_KEY`: Your Google Gemini API key (Get a free key at [Google AI Studio](https://aistudio.google.com/app/apikey))
- `PYTHON_VERSION`: `3.11.9`

### Step 4: Click Deploy!
1. Click **Create Web Service**.
2. Render will build and deploy your app. Within 2-3 minutes, your live URL will be ready (e.g., `https://deep-research-ai-agent.onrender.com`).
3. You can share this URL in your internship project submission!

---

## 🐳 Option 2: Deploy on Hugging Face Spaces (Free)

1. Go to [Hugging Face Spaces](https://huggingface.co/spaces).
2. Click **Create new Space**.
3. Choose **Docker** as Space SDK (Blank template).
4. Clone the space repo or connect GitHub.
5. In Space **Settings** -> **Variables and secrets**, add:
   - Secret Name: `GEMINI_API_KEY`
   - Secret Value: *your Gemini API key*
6. Push this repository. Hugging Face will automatically build the `Dockerfile` and launch the app with a public URL!

---

## 💻 Option 3: Local Execution

### Prerequisites
- Python 3.10+ installed
- pip package manager

### Steps:
1. Clone the repository and navigate into the folder:
   ```bash
   git clone https://github.com/AdarshPandey1203/internship-springboard-project.git
   cd "infosys intern project"
   ```

2. (Optional) Create and activate a virtual environment:
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set your API Key:
   Create a `.env` file or copy `.env.example`:
   ```bash
   cp .env.example .env
   ```
   Add your key:
   ```env
   GEMINI_API_KEY="YOUR_KEY_HERE"
   ```

5. Run the application:
   ```bash
   python app.py
   ```
   Or run Milestone 3 directly:
   ```bash
   python Milestone_3/app.py
   ```

6. Open your web browser:
   ```
   http://127.0.0.1:5001
   ```

---

## 📦 Option 4: Run with Docker

1. Build the Docker container image:
   ```bash
   docker build -t deep-research-agent .
   ```

2. Run the container:
   ```bash
   docker run -p 5001:5001 -e GEMINI_API_KEY="your_api_key_here" deep-research-agent
   ```

3. Open `http://localhost:5001` in your browser.

---

## 🔑 Getting a Free Gemini API Key
1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey).
2. Click **Create API Key**.
3. Copy the key and either:
   - Paste it in `.env`
   - Or paste it directly in the application's **Settings (⚙️)** menu in your browser!
