# AI Prompt Injection & Jailbreak Firewall - Use Case Diagram (Minimal)

---

## 1. Minimal Use Case Diagram (Mermaid)

```mermaid
flowchart LR
    User["👤 User / Client"]
    Admin["🛡️ Security Admin"]
    LLM["🤖 Upstream LLM"]

    subgraph Firewall ["AI Prompt Firewall"]
        UC1(["Submit Prompt / Chat"])
        UC2(["Inspect & Detect Attacks"])
        UC3(["Block Malicious Prompt"])
        UC4(["Forward Safe Prompt"])
        UC5(["Manage Detection Rules"])
        UC6(["View Logs & Dashboard"])
    end

    User --> UC1
    UC1 -.->|«include»| UC2
    UC2 -.->|«extend»| UC3
    UC2 -.->|«extend»| UC4
    UC4 --> LLM

    Admin --> UC5
    Admin --> UC6
```

---

## 2. Minimal PlantUML Code (For Slides & Report)

```plantuml
@startuml
left to right direction
skinparam packageStyle rectangle
skinparam shadowing false

actor "User / Client" as User
actor "Security Admin" as Admin
actor "Upstream LLM" as LLM <<External System>>

rectangle "AI Prompt Firewall" {
    usecase "Submit Prompt / Chat" as UC1
    usecase "Inspect & Detect Attacks" as UC2
    usecase "Block Malicious Prompt" as UC3
    usecase "Forward Safe Prompt" as UC4
    usecase "Manage Detection Rules" as UC5
    usecase "View Logs & Dashboard" as UC6
}

User --> UC1
UC1 .> UC2 : <<include>>
UC2 .> UC3 : <<extend>> (If Attack)
UC2 .> UC4 : <<extend>> (If Safe)
UC4 --> LLM

Admin --> UC5
Admin --> UC6
@enduml
```

---

## 3. Core Summary

| Actor | Action / Use Case | Purpose |
|---|---|---|
| **User / Client** | **Submit Prompt / Chat** | Sends prompt or chat message to the application. |
| **Firewall (System)** | **Inspect & Detect Attacks** | Evaluates prompt through Rule Engine (L1) and ML Classifier (L2). |
| **Firewall (System)** | **Block Malicious Prompt** | Blocks threat and stops prompt from reaching upstream LLM. |
| **Firewall (System)** | **Forward Safe Prompt** | Forwards benign prompt to Upstream LLM and returns completion. |
| **Security Admin** | **Manage Detection Rules** | Creates, modifies, and toggles regex detection rules. |
| **Security Admin** | **View Logs & Dashboard** | Monitors real-time attack metrics, latency, and audit logs. |
