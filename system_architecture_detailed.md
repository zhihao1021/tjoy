```mermaid
graph TD
    subgraph "Client"
        Client
    end

    subgraph "Backend Application (FastAPI)"
        API_Gateway["api.py / Uvicorn"]

        subgraph "Routing & Auth"
            Routes
            Auth["Auth (Handles JWT)"]
        end

        subgraph "Business Logic"
            Services
            Snowflake["Snowflake ID Service"]
        end

        subgraph "Data Layer"
            Models["SQLAlchemy Models"]
            Schemas["Pydantic Schemas"]
        end

        WebSockets
    end

    subgraph "External Services"
        PostgreSQL
        RabbitMQ
    end

    subgraph "Data Analysis Pipeline"
        Analysis["Analysis Scripts (Topic Modeling, Sentiment Analysis)"]
    end


    Client -- "HTTP/S Request" --> API_Gateway
    Client -- "WebSocket Conn" --> WebSockets

    API_Gateway --> Routes
    Routes -- "Protected by" --> Auth
    Routes -- "Calls" --> Services
    Routes -- "Validates with" --> Schemas

    Services -- "Generates IDs with" --> Snowflake
    Services -- "Uses" --> Models
    Services -- "Publishes to" --> RabbitMQ

    Models -- "Maps to" --> PostgreSQL

    RabbitMQ -- "Triggers" --> Analysis
    Analysis -- "Reads from" --> PostgreSQL
```
