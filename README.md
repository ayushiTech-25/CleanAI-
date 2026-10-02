# CleanAI – Intelligent Data Quality & ML Readiness Platform

CleanAI is a premium, production-ready SaaS interface built with **Streamlit** and configured with custom **glassmorphic styling** (inspired by Vercel, Linear, and Stripe). It offers automated data profiling indicators, ML readiness grading, tabular clean pipelines, and a ChatGPT-style conversational assistant.

## Features

- 🏠 **Home Landing Page**: Custom hero banner, core metric values, and feature grids.
- 📊 **Dashboard**: Drag-and-drop file uploader, sample churn dataset loader, Health Score, and ML Readiness indicators.
- 🧹 **Data Cleaning**: Quality repair configs (KNN/Mean imputation, outlier boundary clipping, text case standardizations), and a live "Before vs Cleaned" interactive diff preview.
- 🤖 **AI Assistant**: A ChatGPT-style chat log container featuring quick suggested query chips and context-awareness of the active dataset.
- 📈 **Analytics**: Interactive Plotly distribution histograms, outlier box plots, Pearson correlation matrices, and completeness bars.
- 📄 **Reports**: Structured audit checklists, quality recommendations, and export actions for HTML/PDF downloads.
- ⚙ **Settings**: Form inputs for OpenAI/Anthropic/Gemini credentials, warning sliders, and custom database credentials.

---

## Folder Layout

```text
cleanai/
├── .streamlit/
│   └── config.toml          # Streamlit theme colors (indigo accent + zinc-950 black)
├── assets/
│   └── css/
│       └── style.css        # Glassmorphic panels, glowing lines, custom fonts, animations
├── components/
│   ├── ui.py                # Reusable UI cards, status badges, hero banner, and footers
│   └── assistant_ui.py      # Conversation layout builders and suggestion chips
├── utils/
│   └── styling.py           # CSS stylesheet loader and fonts injector helper
├── views/
│   ├── home.py              # SaaS landing page view
│   ├── dashboard.py         # Main data control panel view
│   ├── cleaning.py          # Data repair config view
│   ├── assistant.py         # AI chatbot co-pilot view
│   ├── analytics.py         # Plotly express visualization view
│   ├── reports.py           # Compliance audit sheet and download view
│   └── settings.py          # Config dashboard (API keys, warning levels)
├── app.py                   # Central routing layout manager (uses st.navigation)
├── .env.example             # API keys and environment templates
├── .gitignore               # Standard python/Streamlit gitignore rules
├── requirements.txt         # Core dependencies definitions
└── README.md                # Documentation guide
```

---

## Local Setup

### 1. Clone & Set Directory
Make sure your active workspace or terminal is inside the project directory:
```bash
cd /Users/ayushi/.gemini/antigravity/scratch/cleanai
```

### 2. Environment Setup (Optional)
Create a Python virtual environment and activate it:
```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies
Install packages listed in `requirements.txt`:
```bash
pip install -r requirements.txt
```

### 4. Run the Platform
Start the Streamlit development server locally:
```bash
streamlit run app.py
```

The application will launch on your local host (usually `http://localhost:8501`).
