# 🛡️ ScamShield

**AI-Based Scam Detection & Public Reporting Platform**

ScamShield is a cloud-native web application that detects and classifies potential online scams using Natural Language Processing (NLP) and rule-based risk analysis. Users can scan suspicious links or messages, report scams, and view scam trends from a personalized dashboard.

---

## 📌 Problem Statement

With the rapid increase in digital payments, social media usage, and online platforms, cyber fraud cases — phishing, fake job offers, investment scams, UPI fraud — are rising significantly. Many users fail to recognize scam patterns until financial damage has already occurred.

ScamShield provides an accessible tool that helps users **identify scams early** and **report suspicious activity**.

---

## 🚀 Features

| Feature | Description |
|---------|-------------|
| 🔍 **URL & Message Scanner** | Analyze suspicious links and text messages using AI classification |
| 📊 **Risk Score Engine** | Generates *Low / Medium / High* risk levels with probability scores |
| 🧠 **Explainable Results** | Shows why a message was flagged (keyword triggers, pattern match) |
| 🗂️ **Public Scam Reporting** | Report scam phone numbers, links, or messages |
| 📈 **Analytics Dashboard** | View scan history, reported scams, and risk distribution |
| 🔐 **JWT Authentication** | Secure login/registration with bcrypt password hashing |
| ⚡ **Rate Limiting** | API protection via slowapi |
| ☁️ **Docker Deployment** | Containerized with Docker Compose (PostgreSQL + FastAPI) |

---

## 🏗️ System Architecture

```
Frontend (HTML/CSS/JS)
        ↓  (REST API + JWT)
Backend API (FastAPI)
        ↓
ML Risk Engine (Scikit-learn)
        ↓
PostgreSQL Database
        ↓
Docker / AWS Infrastructure
```

---

## 📁 Project Structure

```
ScamShield/
├── assets/                          # Frontend (HTML, CSS, JS)
│   ├── index.html                   # Landing page
│   ├── scan.html                    # Scan suspicious messages/URLs
│   ├── report.html                  # Report a scam
│   ├── dashboard.html               # User dashboard
│   ├── login.html / register.html   # Authentication pages
│   ├── css/                         # Stylesheets
│   └── js/
│       ├── auth.js                  # Login/register API calls
│       ├── scan.js                  # Scan API integration
│       └── dashboard.js             # Dashboard API integration
│
├── backend/
│   ├── app/
│   │   ├── main.py                  # FastAPI entry point
│   │   ├── config.py                # Environment-based settings
│   │   ├── database.py              # SQLAlchemy engine & session
│   │   ├── models.py                # ORM models (User, ScanResult, ScamReport)
│   │   ├── schemas.py               # Pydantic request/response schemas
│   │   ├── auth.py                  # JWT + bcrypt utilities
│   │   ├── dependencies.py          # Auth dependency (Bearer token)
│   │   ├── routers/
│   │   │   ├── auth_router.py       # /api/register, /api/login, /api/logout
│   │   │   ├── scan_router.py       # /api/predict, /api/history
│   │   │   ├── report_router.py     # /api/report (POST + GET)
│   │   │   └── dashboard_router.py  # /api/dashboard/stats
│   │   └── ml/
│   │       ├── predictor.py         # ML model loader + rule-based fallback
│   │       ├── train.py             # Model training script
│   │       ├── build_dataset.py     # Dataset downloader & merger
│   │       └── data/
│   │           └── sample_scams.csv # Training dataset (75K+ samples)
│   ├── Dockerfile
│   └── .env / .env.example
│
├── requirements.txt                 # Python dependencies
├── docker-compose.yml               # PostgreSQL + Backend containers
└── readme.md
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | HTML5, CSS3 (Tailwind), JavaScript |
| **Backend** | Python 3.11, FastAPI, Uvicorn |
| **Database** | PostgreSQL 16, SQLAlchemy ORM |
| **Authentication** | JWT (python-jose), bcrypt (passlib) |
| **ML Pipeline** | Scikit-learn, TF-IDF Vectorizer, Logistic Regression |
| **DevOps** | Docker, Docker Compose, GitHub Actions |
| **Cloud** | AWS EC2, RDS, S3 (production) |

---

## 🔌 API Endpoints

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `POST` | `/api/register` | Create a new account | ✗ |
| `POST` | `/api/login` | Authenticate & get JWT | ✗ |
| `POST` | `/api/logout` | End session | ✓ |
| `POST` | `/api/predict` | Scan text/URL for scam risk | ✓ |
| `GET`  | `/api/history` | User's scan history | ✓ |
| `POST` | `/api/report` | Submit a scam report | ✓ |
| `GET`  | `/api/report` | User's report history | ✓ |
| `GET`  | `/api/dashboard/stats` | Aggregated user stats | ✓ |
| `GET`  | `/` | Health check | ✗ |

---

## 🧪 Machine Learning Pipeline

### Training Data
- **2000000+ samples** from multiple public sources:
  - UCI SMS Spam Collection (5,574 SMS)
  - Kaggle SMS Spam Collection (5,542 SMS)
  - Combined Smishing Dataset (84,000+ SMS)
  - 240+ hand-crafted Indian scam patterns (UPI fraud, KYC scams, lottery, job scams, investment fraud)

### Model Architecture
1. **Text Preprocessing:** Tokenization, stopword removal, lowercasing
2. **Feature Engineering:** TF-IDF Vectorizer (5,000 features, bigrams, sublinear TF)
3. **Classifier:** Logistic Regression (balanced class weights, 1000 iterations)
4. **Fallback:** Rule-based keyword scoring when no trained model is available

### Performance Metrics

| Metric | Score |
|--------|-------|
| **Accuracy** | 93% |
| **Weighted Precision** | 0.94 |
| **Weighted Recall** | 0.93 |
| **Weighted F1** | 0.93 |

---

## ▶️ Getting Started

### Prerequisites

- Python 3.11+
- **PostgreSQL 16** (required — the app will not work without it)
- Docker & Docker Compose *(recommended)* **or** a local PostgreSQL installation
- Node.js *(optional, for frontend tooling)*

---

### Option 1: Docker Compose (Recommended)

> PostgreSQL is included automatically via `docker-compose.yml` — no manual DB setup needed.

```bash
git clone https://github.com/your-username/ScamShield.git
cd ScamShield
docker-compose up --build
```

| Service | URL |
|---------|-----|
| Backend API | http://localhost:8000 |
| Swagger Docs | http://localhost:8000/docs |
| Frontend | Open `assets/index.html` with Live Server (port 5500) |

---

### Option 2: Manual Setup

#### Step 1 — Install PostgreSQL

Download and install **PostgreSQL 16** for your OS:

| OS | Install Command / Link |
|----|----------------------|
| **Windows** | [postgresql.org/download/windows](https://www.postgresql.org/download/windows/) |
| **macOS** | `brew install postgresql@16 && brew services start postgresql@16` |
| **Linux (Debian/Ubuntu)** | `sudo apt install postgresql postgresql-contrib` |

#### Step 2 — Create the Database & User

Open a PostgreSQL shell (`psql`) and run:

```sql
CREATE USER scamshield WITH PASSWORD 'password';
CREATE DATABASE scamshield_db OWNER scamshield;
GRANT ALL PRIVILEGES ON DATABASE scamshield_db TO scamshield;
```

**Platform-specific ways to open psql:**

| OS | Command |
|----|---------|
| **Windows** | Open **SQL Shell (psql)** from the Start Menu, or use pgAdmin |
| **macOS** | `psql postgres` |
| **Linux** | `sudo -u postgres psql` |

Verify the connection:

```bash
psql -U scamshield -d scamshield_db -h localhost
# You should see a "scamshield_db=>" prompt. Type \q to exit.
```

#### Step 3 — Clone & Create Virtual Environment

```bash
git clone https://github.com/your-username/ScamShield.git
cd ScamShield

python -m venv venv

# Windows (PowerShell)
.\venv\Scripts\Activate.ps1

# macOS / Linux
# source venv/bin/activate
```

> **Windows note:** If you get an execution policy error, run:
> `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned`

#### Step 4 — Install Python Dependencies

```bash
pip install -r requirements.txt
```

#### Step 5 — Configure Environment Variables

```bash
cp backend/.env.example backend/.env
```

Edit `backend/.env` with your database credentials. The default `DATABASE_URL` is:

```
DATABASE_URL=postgresql://scamshield:password@localhost:5432/scamshield_db
```

Update the username/password if you used different values in Step 2.

#### Step 6 — (Optional) Build Dataset & Train ML Model

> **Note:** The pre-trained model is already included in the repository! You only need to perform this step if you wish to retrain the model from scratch.

To train the model yourself, you must first download the complete training dataset (as it is not committed to GitHub due to file size limits):
1. Download `sample_scams.csv` from: `https://drive.google.com/drive/folders/1uxq6dLnNglKgGQt1R2Pua3UK7LTGJI6R?usp=sharing`
2. Place the downloaded file inside the `backend/app/ml/data/` directory.

Then, you can run the training scripts:

```bash
cd backend
python -m app.ml.build_dataset   # (Optional) Download & merge secondary datasets
python -m app.ml.train           # Train & evaluate model
```

#### Step 7 — Start the Backend Server

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

#### Step 8 — Open the Frontend

Open the `assets/` folder with **VS Code Live Server** (port 5500) or any static file server.

---

## 🔒 Security

- **JWT Authentication** with configurable expiration
- **bcrypt** password hashing (passlib)
- **Rate limiting** via slowapi
- **Input validation** with Pydantic schemas
- **CORS** middleware with configurable origins
- **SQL injection prevention** via SQLAlchemy ORM
- **Environment-based secrets** (never hardcoded)

---

## 👥 Team Roles

| Role | Responsibility |
|------|---------------|
| ☁️ Cloud & DevOps | Infrastructure, deployment, CI/CD, monitoring |
| ⚙️ Backend Developer | API development, database design, ML integration |
| 🎨 Frontend Developer | UI/UX, dashboard, user interaction |

---

## 📌 Future Enhancements

- 🌐 Browser extension for real-time URL scanning
- 📱 SMS classification via mobile app
- 📊 Admin analytics dashboard
- 🚨 Real-time scam alert notification system
- 📲 Native mobile application (React Native)
- 🤖 LLM-based explanation generation

---

### ⚠️ Disclaimer

*ScamShield provides risk analysis based on trained models and known scam patterns. It does not guarantee 100% accuracy and should not replace official cybercrime reporting mechanisms.*