# Project File Classification & Directory Organization

**Project Title**: AI Prompt Injection and Jailbreak Detection Firewall  
**Base Paper**: *JailbreakTracer: Explainable Detection of Jailbreaking Prompts in LLMs Using Synthetic Data Generation* (IEEE Access, Vol. 13, 2025)  

---

## 1. High-Level Classification Schema

The codebase is organized into **5 functional domains**:

```
PI_fireWall/
├── 👥 TEAM INTERIM MODULES      --> Individual deliverables for interim reviews
│   ├── Anjith_Rule_Engine/     --> Layer 1: Normalizer, 6 Regex Categories, Hit/Miss Logs
│   ├── Anusree_ML_Classifier/  --> Layer 2: Baseline TF-IDF+LogReg, Benchmark Training, Report
│   ├── Asna_Backend/           --> Gateway: FastAPI Service, /check-prompt, SQLite Telemetry
│   └── Aswathy_Frontend/       --> UI/UX: Interactive Dashboard, Audit Table, Slides, Concept
│
├── ⚙️ CORE PRODUCTION SYSTEM    --> Full-stack enterprise firewall application
│   ├── backend/                --> FastAPI modular production backend & ML pipeline
│   └── frontend/               --> React 18 + Vite + Tailwind CSS management dashboard
│
├── 📊 DATASETS & BENCHMARKS     --> IEEE Access JailbreakTracer corpus & test splits
│   └── backend/data/           --> 1,000 benchmark samples, 650 curated prompts, attack/benign CSVs
│
├── 📚 RESEARCH & DOCUMENTATION  --> Project reports, base paper data, architecture, presentation
│   └── docs/                   --> Academic specs, slide deck, thesis report, threat taxonomy
│
└── 🔧 CONFIGURATION & DEVOPS    --> Environment configs, docker orchestration, automation
    └── (Root files)            --> docker-compose.yml, Makefile, .env.example, README.md
```

---

## 2. Detailed File Classification by Domain

### Domain 1: Team Member Interim Deliverables

| Folder | Owner | Core Files | Purpose |
| :--- | :--- | :--- | :--- |
| **`Anjith_Rule_Engine/`** | Anjith | `normalizer.py`<br>`rules.py`<br>`test_rules.py`<br>`results_log.md`<br>`pseudocode_presentation.md` | **Layer 1 Rule Engine**: Normalizes unicode/homoglyphs, evaluates the 6 regex categories, benchmarks hit/miss counts, and provides presentation pseudocode. |
| **`Anusree_ML_Classifier/`** | Anusree | `train_baseline.py`<br>`baseline_classifier.joblib`<br>`classifier_report.md`<br>`pseudocode_presentation.md` | **Layer 2 ML Classifier**: Verifies 50:50 class balance, trains baseline TF-IDF + Logistic Regression model (89% accuracy), and documents next-phase transformer upgrade. |
| **`Asna_Backend/`** | Asna | `main.py`<br>`database.py`<br>`firewall_logs.db`<br>`api_spec.md`<br>`requirements.txt`<br>`pseudocode_presentation.md` | **Backend Gateway Service**: Provides `POST /check-prompt` contract, wires Layer 1 rules, logs requests to SQLite, and defines the API spec. |
| **`Aswathy_Frontend/`** | Aswathy | `index.html`<br>`style.css`<br>`app.js`<br>`demo_slides/slides.html`<br>`evaluation_concept.md`<br>`pseudocode_presentation.md` | **Frontend Client UI**: Interactive sandbox dashboard with preset prompts, live allow/block display, audit table, 3 demo slides, and evaluation concept. |

---

### Domain 2: Core Production System

#### A. Backend Service (`backend/`)
- **`app/main.py`**: Production FastAPI application entry point with CORS, middleware, and route mounting.
- **`app/config.py`**: Centralized environment variable settings (pydantic-settings).
- **`app/database.py`**: SQLAlchemy session factory and SQLite/PostgreSQL connection engine.
- **`app/api/`**: Modular API endpoints:
  - `firewall.py`: Main `/api/firewall/analyze` inspection route.
  - `rules.py`: Dynamic CRUD for custom firewall rules.
  - `logs.py`: Querying and filtering audit detection events.
  - `metrics.py`: Latency, attack distribution, and detection throughput telemetry.
  - `llm.py`: Upstream LLM proxy gateway router.
- **`app/rule_engine/`**: Production Layer 1 implementation (`matcher.py`, `normalizer.py`, `obfuscation.py`, `scorer.py`).
- **`app/ml/`**: Production Layer 2 training, feature union extraction, and inference (`train.py`, `predict.py`, `explain.py`).
- **`app/services/`**: Core business services (Rule engine, ML classifier, LLM gateway, Continuous learning).
- **`app/models/`**: Database models (`detection_event.py`, `rule.py`, `dataset_record.py`).
- **`app/tests/`**: Automated pytest test suite (31 unit and integration tests).

#### B. Frontend Application (`frontend/`)
- **`src/App.tsx`**: Single-Page Application routing and navigation shell.
- **`src/pages/`**:
  - `AnalyzePromptPage.tsx`: Live prompt testing and inspection interface.
  - `ChatbotPage.tsx`: End-to-end LLM chat protected by firewall.
  - `DashboardPage.tsx`: Real-time traffic, latency, and attack category overview.
  - `EvaluationPage.tsx`: Model benchmark metrics, ROC curves, and confusion matrix.
  - `LogsPage.tsx`: Searchable audit log viewer with inspector drawer.
  - `RulesPage.tsx`: Interactive rule management table.
- **`src/components/`**: Reusable UI widgets (DecisionBadge, ConfidenceBar, ExplanationPanel, LatencyChart).

---

### Domain 3: Datasets & Evaluation Benchmarks (`backend/data/`)

| File / Subfolder | Size / Count | Description |
| :--- | :--- | :--- |
| `jailbreaktracer_benchmark.csv` | 1,000 samples | Curated balanced test split directly from the IEEE Access 2025 paper (500 Benign, 500 Jailbreak). |
| `prompts.csv` | 650 samples | Master curated prompt firewall dataset spanning 10 threat categories. |
| `attack_prompts.csv` | 550 samples | Dedicated adversarial injection and jailbreak attack subset. |
| `benign_prompts.csv` | 100 samples | Verified non-adversarial user queries for false-positive validation. |
| `evaluation_prompts.csv` | 130 samples | Held-out validation split for regression testing. |
| `jailbreaktracer/` | Raw corpus | Raw synthetic prompts, regular prompts, and merged benchmark zips from authors. |

---

### Domain 4: Research, Documentation & Presentation (`docs/`)

| File | Content Summary |
| :--- | :--- |
| `base_paper_data.md` | Deep dive into the IEEE Access 2025 *JailbreakTracer* paper (equations, dataset distribution, author info, baseline metrics). |
| `architecture.md` | Detailed 2-layer defense architecture, mathematical risk score formula, and threat taxonomy. |
| `project-report.md` | Academic project thesis report (Abstract, Literature Review, Methodology, Results, Conclusion). |
| `presentation_slides.md` | 12-slide comprehensive presentation outline with speaker notes for project defense. |
| `presentation_slides.pptx` | Pre-formatted PowerPoint presentation deck. |
| `api.md` & `database.md` | Technical specifications for backend endpoints and database schemas. |

---

### Domain 5: Configuration & DevOps (Root)

| File | Purpose |
| :--- | :--- |
| `docker-compose.yml` | Multi-container setup orchestrating backend and frontend services. |
| `Makefile` | CLI shortcuts for running tests, formatting, and starting services. |
| `.env.example` | Template for environment variables (ports, API keys, database URLs). |
| `README.md` | Master project documentation, quickstart guide, and architectural overview. |

---

## 3. Recommended Workflow by Role

- **For Anjith (Rule Engine)**:
  `cd Anjith_Rule_Engine && python test_rules.py`
- **For Anusree (ML Classifier)**:
  `cd Anusree_ML_Classifier && python train_baseline.py`
- **For Asna (Backend Gateway)**:
  `cd Asna_Backend && uvicorn main:app --reload --port 8000`
- **For Aswathy (Frontend Client)**:
  Open `Aswathy_Frontend/index.html` in browser or view `Aswathy_Frontend/demo_slides/slides.html`.
