# Database Schema & Entity Relationships

The AI Prompt Firewall utilizes **SQLAlchemy ORM** supporting SQLite for local zero-dependency execution and PostgreSQL for multi-container production deployments.

---

## 1. Entity-Relationship Diagram

```mermaid
erDiagram
    USERS {
        int id PK
        string username UK
        string password_hash
        string role
        boolean is_active
        datetime created_at
        datetime updated_at
    }

    DETECTION_RULES {
        int id PK
        string rule_code UK
        string name
        text description
        string category
        string pattern_type
        text pattern
        string severity
        float weight
        boolean enabled
        boolean case_sensitive
        string created_by
        datetime created_at
        datetime updated_at
    }

    PROMPT_RECORDS {
        int id PK
        string request_id UK
        string conversation_id
        string user_id
        string original_prompt_hash
        text redacted_prompt
        int prompt_length
        string decision
        string attack_category
        float confidence
        float risk_score
        string detected_by
        float processing_time_ms
        string llm_provider
        string llm_model
        boolean llm_called
        text llm_response
        datetime created_at
    }

    DETECTION_EVENTS {
        int id PK
        string request_id FK
        string rule_id
        string detection_layer
        string category
        string severity
        float confidence
        text reason
        string matched_text_hash
        string matched_text_redacted
        datetime created_at
    }

    DATASET_RECORDS {
        int id PK
        string name UK
        string filename
        int row_count
        text class_distribution
        string validation_status
        datetime created_at
    }

    MODEL_METADATA {
        int id PK
        string model_name
        string model_type
        string version UK
        float accuracy
        float precision
        float recall
        float f1_score
        datetime trained_at
        string artifact_path
        boolean active
    }

    PROMPT_RECORDS ||--o{ DETECTION_EVENTS : "links via request_id"
```

---

## 2. Table Specifications

### `users`
Stores administrator accounts authorized to manage detection rules, review datasets, and configure threshold parameters.
- **Indexes**: `username` (Unique)

### `detection_rules`
Defines Layer 1 deterministic pattern signatures.
- **Indexes**: `rule_code` (Unique), `category`, `enabled`

### `prompt_records`
Core immutable audit ledger logging every evaluated prompt transaction, calculated risk score, detection attribution, and upstream response metadata.
- **Indexes**: `request_id` (Unique), `decision`, `attack_category`, `detected_by`, `created_at`

### `detection_events`
Detailed breakdown of specific rule triggers or ML classification evidence associated with a given `request_id`.

### `model_metadata`
Versioned metadata registry recording accuracy, precision, recall, and F1-score across trained classification iterations.
