# Deployment & Operations Guide

The AI Prompt Firewall is containerized with Docker and Docker Compose, supporting local development, air-gapped workstations, and cloud environments.

---

## 1. Local Development (No Docker Required)

### Step 1: Install Backend Requirements
```bash
cd backend
pip install -r requirements.txt
```

### Step 2: Seed Database & Train Classifier
```bash
python -m app.seed.seed_database
```
*Initializes SQLite database, registers default administrator (`admin` / `admin123`), seeds Layer 1 rules, and compiles initial ML artifacts.*

### Step 3: Start FastAPI Backend
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Step 4: Start Frontend Vite Dev Server
In a new terminal:
```bash
cd frontend
npm install
npm run dev
```
Open **http://localhost:5173** in your web browser.

---

## 2. Multi-Container Docker Deployment

To launch the full stack (PostgreSQL, FastAPI Backend, and Nginx Frontend):

```bash
# Build and start all services in detached mode
docker compose up --build -d

# View real-time container logs
docker compose logs -f backend
docker compose logs -f frontend

# Stop containers
docker compose down
```

---

## 3. Connecting Local Ollama Models

To use local open-source models with zero API cost:

1. Install Ollama from [ollama.com](https://ollama.com).
2. Pull a target model:
   ```bash
   ollama run llama3.2
   ```
3. Set in `.env`:
   ```ini
   LLM_PROVIDER=ollama
   OLLAMA_BASE_URL=http://localhost:11434
   OLLAMA_MODEL=llama3.2
   ```
4. Safe allowed prompts will now be forwarded directly to your local Ollama instance.
