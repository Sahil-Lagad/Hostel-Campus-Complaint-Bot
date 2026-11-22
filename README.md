# Hostel & Campus Complaint Bot (Roll No. 17)

A Streamlit application for students to submit hostel/campus complaints. The LLM classifies the complaint category, urgency, and short summary. Python generates a unique complaint ID and stores records in CSV.

## Features
- Complaint submission form
- LLM classification using Groq (optional API key)
- Rule-based fallback classification if the API is unavailable
- Complaint tracking by ID
- Admin dashboard with filters and status updates
- CSV export

## Tech stack
Python, Streamlit, Groq API, Pandas, CSV, python-dotenv.

## Setup (Windows PowerShell)
1. Install Python 3.10+.
2. Open this project folder in terminal.
3. Create a virtual environment:
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```
4. Install packages:
   ```powershell
   pip install -r requirements.txt
   ```
5. Copy `.env.example` to `.env`.
   ```powershell
   Copy-Item .env.example .env
   ```
6. Open `.env`, add your Groq API key and set a private admin password. Never commit `.env`.
7. Run:
   ```powershell
   streamlit run app.py
   ```

## How to use
- Submit tab: fill student name, location/room, and complaint description.
- The app classifies the complaint and displays its generated ID.
- Track tab: enter the complaint ID to see status and summary.
- Admin dashboard: enter the password set in `ADMIN_PASSWORD`, filter records, update status, and export CSV.

## Example test complaints
1. "The ceiling fan in room B-204 is not working." → Electrical or Maintenance; Medium.
2. "Water is leaking continuously near the washroom." → Water; High.
3. "There is smoke and a burning smell near the electrical panel." → Electrical; Critical.
4. "The mess food was cold today." → Mess/Food; Low or Medium.
5. "Wi-Fi is unavailable in the hostel wing." → Internet/Network; Medium.

These are sample expectations, not guaranteed LLM outputs. Record your actual results during testing.

## Data and privacy
Complaint data is stored locally in `data/complaints.csv`. Do not enter unnecessary sensitive information. The basic admin password check is suitable only for a classroom demonstration, not production security. Use a real authentication system and secure database before deployment.

## Project structure
```
hostel_campus_complaint_bot/
├── app.py
├── complaint_service.py
├── storage.py
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
├── data/
└── tests/
```

## Limitations
- Classification can be wrong; staff should review urgency.
- CSV is suitable for a small demo but not concurrent production use.
- Admin password is a basic demo gate.
- Groq API requires internet access and may have rate limits.
