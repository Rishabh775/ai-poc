flowchart LR

    U[Users<br/>Ops / PM / Support]

    subgraph FE[Frontend Layer]
        FE1[React App]
        FE2[UI Components]
        FE3[API Service]
    end

    subgraph BE[Backend Layer]
        BE1[FastAPI App]
        BE2[REST Endpoints]
        BE3[In Memory Cache]
    end

    subgraph AI[AI Processing Layer]
        AI1[Ticket Processing Pipeline]
        AI2[Symptom Classifier]
        AI3[Category Classifier]
        AI4[Dynamic Category Builder]
        AI5[Text Normalization]
        AI6[Embedding Generation]
        AI7[Hybrid Feature Builder]
        AI8[DBSCAN or HDBSCAN]
        AI9[Confidence and Metrics]
    end

    subgraph DATA[Data Layer]
        D1[poc_tickets.json]
        D2[ground_truth.py]
        D3[config.py]
        D4[Fallback Demo Tickets]
    end

    U --> FE1
    FE1 --> FE2
    FE1 --> FE3
    FE3 --> BE1
    BE1 --> BE2
    BE1 --> BE3

    D1 --> BE1
    D2 --> AI9
    D3 --> BE1
    D4 --> BE1

    BE1 --> AI1
    AI1 --> AI2
    AI2 --> AI3
    AI3 --> AI4
    AI4 --> AI5
    AI5 --> AI6
    AI6 --> AI7
    AI7 --> AI8
    AI8 --> AI9
    AI9 --> BE3

    BE3 --> BE2
    BE2 --> FE3
    FE3 --> FE1

    classDef frontend fill:#dcfce7,stroke:#16a34a,stroke-width:2px,color:#14532d;
    classDef backend fill:#fef3c7,stroke:#d97706,stroke-width:2px,color:#78350f;
    classDef ai fill:#ede9fe,stroke:#7c3aed,stroke-width:2px,color:#4c1d95;
    classDef data fill:#fee2e2,stroke:#dc2626,stroke-width:2px,color:#7f1d1d;
    classDef user fill:#e0f2fe,stroke:#0284c7,stroke-width:2px,color:#0c4a6e;

    class U user;
    class FE1,FE2,FE3 frontend;
    class BE1,BE2,BE3 backend;
    class AI1,AI2,AI3,AI4,AI5,AI6,AI7,AI8,AI9 ai;
    class D1,D2,D3,D4 data;