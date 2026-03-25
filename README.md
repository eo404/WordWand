
# 🪄 WordWand

### *An Adaptive Phonics & Reading Platform for Children Ages 5–10*

![Django](https://img.shields.io/badge/Django-6.0.1-green)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Neon-blue)
![Groq AI](https://img.shields.io/badge/Groq-AI-red)
![Railway](https://img.shields.io/badge/Hosted-Railway-purple)
![Python](https://img.shields.io/badge/Python-3.12-yellow)

🔗 **Live App:** https://wordwand-production.up.railway.app  
📦 **Repository:** https://github.com/eo404/WordWand  

---

## 01 · Overview

## What is WordWand?

WordWand is a full-stack educational web application that helps children learn to read through interactive games, AI-powered assistance, and adaptive difficulty.

The platform tracks each learner's progress and dynamically adjusts content to their skill level.

**Built with:**
- Django 6
- Neon PostgreSQL (cloud)
- Railway (hosting)
- Groq Llama 3.3 (AI chatbot)

---

### 🌐 Project Info

| Category | Details |
|--------|--------|
| Live URL | wordwand-production.up.railway.app |
| Repository | github.com/eo404/WordWand |
| Database | Neon PostgreSQL (Singapore) |
| AI Model | Groq · llama-3.3-70b |

---

##  02 · Games

## 7 Interactive Learning Games

Each game targets a specific reading skill and adapts difficulty (levels 1–4).

| Game | Description | Skill |
|------|------------|------|
| 🔊 Sound Match | Match phoneme to letter/word | Phoneme Awareness |
| 🔤 Word Builder | Arrange letters to form words | Spelling & Blending |
| 👁️ Sight Word Tap | Identify memorized words | Sight Recognition |
| 🔡 Letter Fix | Distinguish confusing letters | Letter Discrimination |
| ✂️ Syllable Breaker | Split words into syllables | Segmentation |
| 👂 Listen & Type | Hear and type words | Phonemic Spelling |
| 📖 Story Builder | Interactive reading stories | Fluency |

---

##  03 · Tech Stack

## Technology Stack

- 🐍 **Django 6.0.1** — Backend framework & ORM  
- 🐘 **PostgreSQL (Neon)** — Cloud database  
- 🤖 **Groq API** — Wanda AI chatbot (Llama 3.3)  
- 🚂 **Railway** — Hosting platform  
- ⚡ **WhiteNoise** — Static file serving  
- 🔊 **Web Speech API** — Text-to-speech  
- 🔐 **Django Auth** — Authentication  
- 🌐 **Gunicorn** — Production server  

---

##  04 · Structure

## Project Structure

```

WordWand/
├── wordwand/               # Django project root
│   ├── wordwand/           # Core settings & URLs
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   ├── games/              # All 7 games
│   ├── chatbot/            # Wanda AI chatbot
│   ├── users/              # Authentication
│   ├── dashboard/          # Progress tracking
│   ├── learning/           # Learning modules
│   ├── tts_engine/         # Text-to-speech
│   ├── templates/          # HTML templates
│   ├── static/             # CSS, JS, images
│   ├── manage.py
│   ├── requirements.txt
│   ├── Procfile
│   └── runtime.txt
└── .env                    # Environment variables (DO NOT COMMIT)

````

---

##  05 · Local Setup

## Local Development

### Prerequisites

- Python 3.12+
- Git
- Groq API Key → https://console.groq.com
- PostgreSQL (local or Neon)

---

### Installation Steps

```bash
# 1. Clone repo
git clone https://github.com/eo404/WordWand.git
cd WordWand/wordwand

# 2. Create virtual environment
python -m venv .venv

# Activate
source .venv/bin/activate     # Mac/Linux
.venv\Scripts\activate        # Windows

# 3. Install dependencies
pip install -r requirements.txt
````

---

### Environment File

Create `WordWand/.env`

```env
DJANGO_SECRET_KEY=your-secret-key
DEBUG=True
GROQ_API_KEY=gsk_xxxxxxxxxxxxx
DATABASE_URL=postgresql://user:pass@host/dbname
```

---

### Run Project

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

➡ [http://127.0.0.1:8000](http://127.0.0.1:8000)

---

##  06 · Configuration

## Environment Variables

| Variable             | Required    | Description           |
| -------------------- | ----------- | --------------------- |
| DJANGO_SECRET_KEY    | Yes         | Django secret key     |
| DEBUG                | Optional    | Dev mode toggle       |
| ALLOWED_HOSTS        | Prod        | Allowed domains       |
| CSRF_TRUSTED_ORIGINS | Prod        | Trusted origins       |
| DATABASE_URL         | Recommended | PostgreSQL connection |
| DB_* vars            | Optional    | Alternative DB config |
| GROQ_API_KEY         | Yes         | AI chatbot key        |
| TESSERACT_CMD        | Optional    | OCR path              |

---

##  07 · Deployment

## Deploying to Railway

1. Push code to GitHub
2. Create Railway project
3. Set **Root Directory → `wordwand`**
4. Add environment variables
5. Auto-deploy on push

---

### Procfile

```bash
web: python manage.py migrate --noinput \
  && python manage.py collectstatic --noinput \
  && gunicorn wordwand.wsgi --bind 0.0.0.0:$PORT
```

---

### Database Priority Logic

```python
# Priority:
# 1 → DATABASE_URL
# 2 → DB_* variables
# 3 → SQLite fallback

if DATABASE_URL:
    ...
elif DB_HOST:
    ...
else:
    ...
```

---

##  08 · API

## Game API Endpoints

| Method | Endpoint                    | Description       |
| ------ | --------------------------- | ----------------- |
| POST   | /games/sound-match/submit/  | Submit phoneme    |
| POST   | /games/word-builder/submit/ | Submit word       |
| POST   | /games/sight-word/submit/   | Submit sight word |
| POST   | /games/confusion/submit/    | Submit letter     |
| POST   | /games/syllable/submit/     | Submit syllables  |
| POST   | /games/listen-type/submit/  | Submit typed word |
| POST   | /games/story/submit/        | Submit story      |
| POST   | /chatbot/message/           | Wanda AI          |

---

##  09 · Contributing

## Contributing

1. Fork repository
2. Create branch

   ```bash
   git checkout -b feature/my-feature
   ```
3. Commit changes
4. Push branch
5. Open Pull Request

---

##  10 · License

## License

This project is licensed under the **MIT License**.

---

## 🪄 WordWand

**Making Learning Fun, One Word at a Time**

🔗 GitHub: [https://github.com/eo404/WordWand](https://github.com/eo404/WordWand)
🚀 Live: [https://wordwand-production.up.railway.app](https://wordwand-production.up.railway.app)


