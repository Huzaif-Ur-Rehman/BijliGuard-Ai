# BijliGuard AI (روشن پاکستان)

An early-stage civic electricity-bill audit harness. It is organized into four
layers: bill extraction, deterministic tariff checks, dispute drafting, and a
Streamlit interface.

> **Important:** This scaffold is not legal advice and does not yet contain a
verified, current NEPRA tariff schedule. Do not use sample data or audit output
to make a payment or legal decision. Add and cite the applicable official
notifications before relying on any tariff calculations.

## Setup

Requires Python 3.10 or later. These commands use the Python 3.15 installation
provided for this project.

```powershell
Set-Location 'D:\Hacktoberfest Islamabad 2026\bijliguard-ai'
& 'C:\Users\hp\AppData\Local\Programs\Python\Python315\python.exe' -m venv venv
Set-ExecutionPolicy -ExecutionPolicy Unrestricted -Scope Process
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Replace the placeholder `GEMINI_API_KEY` in `.env` with your Google AI Studio
API key; do not commit or share the key. `DEFAULT_VISION_MODEL` defaults to
`gemini-2.5-flash`. Run `python test_env.py` from the activated environment to
check venv activation and local configuration without printing the key.

## Run

```powershell
streamlit run src/app.py
```

The NEPRA desk includes Graphify views for project-module dependencies and a
modeled grid topology. These visualizations are interactive; the topology is
illustrative, not a live operational grid feed. The app also provides synthetic
offline sample data. Extraction requires a configured API key. Tariff evaluation
must be checked against current official notifications before legal or payment
decisions.
