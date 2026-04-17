# Configuration Management

<cite>
**Referenced Files in This Document**
- [config.py](file://backend/app/config.py)
- [main.py](file://backend/app/main.py)
- [mongodb_service.py](file://backend/app/services/mongodb_service.py)
- [pinecone_service.py](file://backend/app/services/pinecone_service.py)
- [embedding_service.py](file://backend/app/services/embedding_service.py)
- [api.ts](file://frontend/lib/api.ts)
- [next.config.ts](file://frontend/next.config.ts)
- [package.json](file://frontend/package.json)
- [vercel.json](file://backend/vercel.json)
</cite>

## Table of Contents
1. [Introduction](#introduction)
2. [Project Structure](#project-structure)
3. [Core Components](#core-components)
4. [Architecture Overview](#architecture-overview)
5. [Detailed Component Analysis](#detailed-component-analysis)
6. [Dependency Analysis](#dependency-analysis)
7. [Performance Considerations](#performance-considerations)
8. [Troubleshooting Guide](#troubleshooting-guide)
9. [Conclusion](#conclusion)
10. [Appendices](#appendices)

## Introduction
This document explains the configuration management strategy across the full-stack application. It covers:
- Environment variable configuration for MongoDB Atlas, Pinecone, Google Gemini, and CORS
- Centralized configuration via Pydantic settings and FastAPI application lifecycle integration
- Frontend configuration using environment variables, build-time constants, and runtime configuration
- Deployment-specific configurations for Vercel and environment-specific overrides
- Security considerations for sensitive data, validation, defaults, and error handling for missing configurations
- Practical examples, templates, and troubleshooting steps

## Project Structure
The configuration system spans the backend Python application and the frontend Next.js app:
- Backend: centralized settings in a single module, consumed by services and FastAPI app lifecycle
- Frontend: environment-driven API base URL and build-time configuration

```mermaid
graph TB
subgraph "Backend"
CFG["config.py<br/>Settings class"]
APP["main.py<br/>FastAPI app + lifespan"]
MDB["mongodb_service.py"]
PC["pinecone_service.py"]
EMB["embedding_service.py"]
end
subgraph "Frontend"
NXCFG["next.config.ts<br/>NEXT_PUBLIC_API_URL"]
API["lib/api.ts<br/>Axios client"]
PKG["package.json<br/>scripts"]
end
subgraph "Deployment"
VERCEL["vercel.json<br/>route + env"]
end
CFG --> APP
CFG --> MDB
CFG --> PC
CFG --> EMB
NXCFG --> API
PKG --> API
VERCEL --> APP
```

**Diagram sources**
- [config.py:1-65](file://backend/app/config.py#L1-L65)
- [main.py:1-90](file://backend/app/main.py#L1-L90)
- [mongodb_service.py:1-202](file://backend/app/services/mongodb_service.py#L1-L202)
- [pinecone_service.py:1-186](file://backend/app/services/pinecone_service.py#L1-L186)
- [embedding_service.py:1-158](file://backend/app/services/embedding_service.py#L1-L158)
- [next.config.ts:1-15](file://frontend/next.config.ts#L1-L15)
- [api.ts:1-93](file://frontend/lib/api.ts#L1-L93)
- [package.json:1-37](file://frontend/package.json#L1-L37)
- [vercel.json:1-22](file://backend/vercel.json#L1-L22)

**Section sources**
- [config.py:1-65](file://backend/app/config.py#L1-L65)
- [main.py:1-90](file://backend/app/main.py#L1-L90)
- [next.config.ts:1-15](file://frontend/next.config.ts#L1-L15)
- [api.ts:1-93](file://frontend/lib/api.ts#L1-L93)
- [vercel.json:1-22](file://backend/vercel.json#L1-L22)

## Core Components
- Centralized settings: a typed Settings class with defaults and environment file binding
- FastAPI integration: settings consumed during app creation and startup/shutdown
- Service integration: services access settings for external services and runtime behavior
- Frontend configuration: API base URL from environment, with build-time defaults

Key configuration categories:
- Application identity and URLs
- MongoDB connection and database name
- Pinecone API key, environment, index, and dimension
- Google Gemini API key, model, temperature, and max tokens
- RAG behavior (top-k, threshold, chunking)
- Session and scraping parameters
- CORS origins parsing

**Section sources**
- [config.py:7-64](file://backend/app/config.py#L7-L64)
- [main.py:39-85](file://backend/app/main.py#L39-L85)

## Architecture Overview
The configuration architecture ensures a single source of truth for environment-dependent values, with explicit defaults and runtime validation via Pydantic. The FastAPI app lifecycle initializes services using these settings, while the frontend reads its own environment-derived configuration.

```mermaid
sequenceDiagram
participant Dev as "Developer"
participant Env as "Environment Variables"
participant Cfg as "Settings (config.py)"
participant App as "FastAPI App (main.py)"
participant SvcMDB as "MongoDB Service"
participant SvcPC as "Pinecone Service"
participant SvcEmb as "Embedding Service"
Dev->>Env : Set variables (.env)
Env-->>Cfg : Values loaded by BaseSettings
Cfg-->>App : get_settings()
App->>SvcMDB : connect() using MONGODB_URI/DB
App->>SvcPC : initialize() using PINECONE_* values
App->>SvcEmb : access singleton (loads model)
App-->>Dev : Health check and endpoints
```

**Diagram sources**
- [config.py:7-64](file://backend/app/config.py#L7-L64)
- [main.py:14-37](file://backend/app/main.py#L14-L37)
- [mongodb_service.py:21-28](file://backend/app/services/mongodb_service.py#L21-L28)
- [pinecone_service.py:27-55](file://backend/app/services/pinecone_service.py#L27-L55)
- [embedding_service.py:26-48](file://backend/app/services/embedding_service.py#L26-L48)

## Detailed Component Analysis

### Backend Configuration System (config.py)
- Defines strongly-typed settings with defaults for all subsystems
- Loads from an environment file and supports case-sensitive keys
- Provides a cached settings accessor for performance
- Exposes a computed property to parse CORS origins from a comma-delimited string

```mermaid
classDiagram
class Settings {
+string APP_NAME
+bool DEBUG
+string BACKEND_URL
+string MONGODB_URI
+string MONGODB_DB_NAME
+string PINECONE_API_KEY
+string PINECONE_ENVIRONMENT
+string PINECONE_INDEX_NAME
+int PINECONE_DIMENSION
+string GEMINI_API_KEY
+string GEMINI_MODEL
+float GEMINI_TEMPERATURE
+int GEMINI_MAX_TOKENS
+int RAG_TOP_K
+float RAG_SIMILARITY_THRESHOLD
+int CHUNK_SIZE
+int CHUNK_OVERLAP
+int SESSION_TTL_HOURS
+int MAX_CONVERSATION_HISTORY
+string SCRAPE_BASE_URL
+int SCRAPE_MAX_PAGES
+float SCRAPE_DELAY
+string CORS_ORIGINS
+cors_origins_list() list
}
class get_settings {
+get_settings() Settings
}
Settings <.. get_settings : "returns cached instance"
```

**Diagram sources**
- [config.py:7-64](file://backend/app/config.py#L7-L64)

**Section sources**
- [config.py:7-64](file://backend/app/config.py#L7-L64)

### FastAPI Application Lifecycle Integration (main.py)
- Creates the FastAPI app with title, description, version, and lifespan
- Adds CORS middleware using parsed origins from settings
- Initializes services during startup and disconnects on shutdown
- Exposes health and root endpoints

```mermaid
sequenceDiagram
participant Lifespan as "lifespan()"
participant Settings as "get_settings()"
participant MDB as "mongodb_service"
participant PC as "pinecone_service"
participant EMB as "embedding_service"
Lifespan->>Settings : Load configuration
Lifespan->>MDB : connect()
Lifespan->>PC : initialize()
Lifespan->>EMB : access singleton
Lifespan-->>Lifespan : yield control to app
Lifespan->>MDB : disconnect()
```

**Diagram sources**
- [main.py:14-37](file://backend/app/main.py#L14-L37)
- [mongodb_service.py:21-28](file://backend/app/services/mongodb_service.py#L21-L28)
- [pinecone_service.py:27-55](file://backend/app/services/pinecone_service.py#L27-L55)
- [embedding_service.py:26-48](file://backend/app/services/embedding_service.py#L26-L48)

**Section sources**
- [main.py:14-37](file://backend/app/main.py#L14-L37)
- [main.py:39-85](file://backend/app/main.py#L39-L85)

### MongoDB Service Configuration (mongodb_service.py)
- Consumes MONGODB_URI and MONGODB_DB_NAME from settings
- Establishes connections and creates indexes at startup
- Manages collections for leads and conversations

```mermaid
flowchart TD
Start(["Connect"]) --> ReadCfg["Read MONGODB_URI/DB from Settings"]
ReadCfg --> InitClient["Initialize AsyncIOMotorClient"]
InitClient --> SelectDB["Select Database"]
SelectDB --> CreateIdx["Create Indexes"]
CreateIdx --> Ready(["Connected"])
```

**Diagram sources**
- [mongodb_service.py:21-47](file://backend/app/services/mongodb_service.py#L21-L47)
- [config.py:15-17](file://backend/app/config.py#L15-L17)

**Section sources**
- [mongodb_service.py:21-47](file://backend/app/services/mongodb_service.py#L21-L47)
- [config.py:15-17](file://backend/app/config.py#L15-L17)

### Pinecone Service Configuration (pinecone_service.py)
- Consumes PINECONE_API_KEY, PINECONE_ENVIRONMENT, PINECONE_INDEX_NAME, PINECONE_DIMENSION from settings
- Ensures index existence and connects to it
- Performs similarity search and upsert operations

```mermaid
flowchart TD
Start(["Initialize"]) --> ReadCfg["Read PINECONE_* from Settings"]
ReadCfg --> EnsureKey{"API Key Present?"}
EnsureKey --> |No| Error["Raise Configuration Error"]
EnsureKey --> |Yes| Connect["Create/Connect to Index"]
Connect --> Ready(["Initialized"])
```

**Diagram sources**
- [pinecone_service.py:27-55](file://backend/app/services/pinecone_service.py#L27-L55)
- [config.py:19-23](file://backend/app/config.py#L19-L23)

**Section sources**
- [pinecone_service.py:27-55](file://backend/app/services/pinecone_service.py#L27-L55)
- [config.py:19-23](file://backend/app/config.py#L19-L23)

### Embedding Service Configuration (embedding_service.py)
- Uses settings indirectly via the global settings accessor
- Loads the BGE-M3 model once and raises on failure

```mermaid
flowchart TD
Start(["Access Embedding Service"]) --> LoadModel{"Model Loaded?"}
LoadModel --> |No| TryLoad["Load BGE-M3 (CPU)"]
TryLoad --> ModelOK{"Load Success?"}
ModelOK --> |No| RaiseErr["Raise Runtime Error"]
ModelOK --> |Yes| Ready(["Ready"])
LoadModel --> |Yes| Ready
```

**Diagram sources**
- [embedding_service.py:26-48](file://backend/app/services/embedding_service.py#L26-L48)
- [config.py:25-29](file://backend/app/config.py#L25-L29)

**Section sources**
- [embedding_service.py:26-48](file://backend/app/services/embedding_service.py#L26-L48)
- [config.py:25-29](file://backend/app/config.py#L25-L29)

### Frontend Configuration (Next.js)
- API base URL is taken from NEXT_PUBLIC_API_URL with a build-time default
- Axios client constructed with the base URL
- Scripts and build pipeline defined in package.json

```mermaid
flowchart TD
Start(["Build/Run Frontend"]) --> ReadEnv["Read NEXT_PUBLIC_API_URL"]
ReadEnv --> HasVal{"Value Set?"}
HasVal --> |Yes| UseEnv["Use Environment Value"]
HasVal --> |No| UseDefault["Use Build-Time Default"]
UseEnv --> CreateAxios["Create Axios Client"]
UseDefault --> CreateAxios
CreateAxios --> Runtime["Runtime Requests to Backend"]
```

**Diagram sources**
- [next.config.ts:9-11](file://frontend/next.config.ts#L9-L11)
- [api.ts:4](file://frontend/lib/api.ts#L4)
- [package.json:5-10](file://frontend/package.json#L5-L10)

**Section sources**
- [next.config.ts:9-11](file://frontend/next.config.ts#L9-L11)
- [api.ts:4](file://frontend/lib/api.ts#L4)
- [package.json:5-10](file://frontend/package.json#L5-L10)

### Deployment Configuration (Vercel)
- Routes all requests to the FastAPI entrypoint
- Sets PYTHONPATH for import resolution
- Environment variables are managed externally (not embedded in this file)

```mermaid
flowchart TD
Request["Incoming HTTP Request"] --> Route["Route to app/main.py"]
Route --> Serve["Serve FastAPI App"]
```

**Diagram sources**
- [vercel.json:12-16](file://backend/vercel.json#L12-L16)
- [vercel.json:18-20](file://backend/vercel.json#L18-L20)

**Section sources**
- [vercel.json:1-22](file://backend/vercel.json#L1-L22)

## Dependency Analysis
- Centralized settings dependency: all services depend on settings via a cached accessor
- FastAPI depends on settings for CORS and app metadata
- Frontend depends on environment variables for API base URL
- Vercel routes traffic to the backend entrypoint

```mermaid
graph TB
Settings["Settings (config.py)"]
App["FastAPI App (main.py)"]
MDB["MongoDB Service"]
PC["Pinecone Service"]
EMB["Embedding Service"]
FE["Frontend API Client"]
Vercel["Vercel Config"]
Settings --> App
Settings --> MDB
Settings --> PC
Settings --> EMB
FE --> App
Vercel --> App
```

**Diagram sources**
- [config.py:61-64](file://backend/app/config.py#L61-L64)
- [main.py:39-57](file://backend/app/main.py#L39-L57)
- [mongodb_service.py:8](file://backend/app/services/mongodb_service.py#L8)
- [pinecone_service.py:6](file://backend/app/services/pinecone_service.py#L6)
- [embedding_service.py:7](file://backend/app/services/embedding_service.py#L7)
- [api.ts:4](file://frontend/lib/api.ts#L4)
- [vercel.json:12-16](file://backend/vercel.json#L12-L16)

**Section sources**
- [config.py:61-64](file://backend/app/config.py#L61-L64)
- [main.py:39-57](file://backend/app/main.py#L39-L57)
- [mongodb_service.py:8](file://backend/app/services/mongodb_service.py#L8)
- [pinecone_service.py:6](file://backend/app/services/pinecone_service.py#L6)
- [embedding_service.py:7](file://backend/app/services/embedding_service.py#L7)
- [api.ts:4](file://frontend/lib/api.ts#L4)
- [vercel.json:12-16](file://backend/vercel.json#L12-L16)

## Performance Considerations
- Settings caching: a single cached instance prevents repeated environment parsing
- Singleton services: embedding and Pinecone services avoid redundant initialization
- Minimal overhead: environment variables are read once at startup/lazy initialization

Recommendations:
- Keep environment files out of version control
- Use separate environment files per deployment stage
- Avoid frequent restarts by changing environment variables at deployment boundaries

**Section sources**
- [config.py:61-64](file://backend/app/config.py#L61-L64)
- [pinecone_service.py:13-19](file://backend/app/services/pinecone_service.py#L13-L19)
- [embedding_service.py:13-20](file://backend/app/services/embedding_service.py#L13-L20)

## Troubleshooting Guide
Common issues and resolutions:
- Missing Pinecone API key
  - Symptom: initialization fails or raises configuration/runtime error
  - Resolution: set the Pinecone API key in environment variables
  - Reference: [pinecone_service.py:33](file://backend/app/services/pinecone_service.py#L33)

- Incorrect MongoDB URI or database name
  - Symptom: connection errors at startup
  - Resolution: verify connection string and database name
  - Reference: [mongodb_service.py:23](file://backend/app/services/mongodb_service.py#L23)

- CORS policy blocking frontend
  - Symptom: cross-origin errors in browser console
  - Resolution: adjust CORS_ORIGINS to include frontend origin(s)
  - Reference: [config.py:46-58](file://backend/app/config.py#L46-L58), [main.py:50-57](file://backend/app/main.py#L50-L57)

- Frontend cannot reach backend
  - Symptom: network errors from Axios client
  - Resolution: set NEXT_PUBLIC_API_URL to the deployed backend URL
  - Reference: [next.config.ts:10](file://frontend/next.config.ts#L10), [api.ts:4](file://frontend/lib/api.ts#L4)

- Vercel routing issues
  - Symptom: 404s or cold-start slowness
  - Resolution: ensure route matches the FastAPI entrypoint and PYTHONPATH is set
  - Reference: [vercel.json:12-16](file://backend/vercel.json#L12-L16), [vercel.json:19](file://backend/vercel.json#L19)

Security checklist:
- Never commit secrets to repositories
- Use environment-specific files and platform secret managers
- Restrict CORS origins to trusted domains only
- Validate environment variables at startup and fail fast on missing values

**Section sources**
- [pinecone_service.py:33](file://backend/app/services/pinecone_service.py#L33)
- [mongodb_service.py:23](file://backend/app/services/mongodb_service.py#L23)
- [config.py:46-58](file://backend/app/config.py#L46-L58)
- [main.py:50-57](file://backend/app/main.py#L50-L57)
- [next.config.ts:10](file://frontend/next.config.ts#L10)
- [api.ts:4](file://frontend/lib/api.ts#L4)
- [vercel.json:12-16](file://backend/vercel.json#L12-L16)
- [vercel.json:19](file://backend/vercel.json#L19)

## Conclusion
The configuration system centralizes environment-dependent values in a single, typed settings class with sensible defaults. FastAPI integrates these settings during startup to initialize services and apply CORS policies. The frontend consumes its own environment-derived configuration for API base URL. Vercel deployment routes traffic to the backend entrypoint with appropriate environment setup. Following the security and troubleshooting guidance ensures reliable operation across environments.

## Appendices

### Environment Variable Reference
- Application
  - APP_NAME: application name
  - DEBUG: debug mode flag
  - BACKEND_URL: backend base URL
- MongoDB
  - MONGODB_URI: MongoDB connection string
  - MONGODB_DB_NAME: database name
- Pinecone
  - PINECONE_API_KEY: Pinecone API key
  - PINECONE_ENVIRONMENT: Pinecone environment
  - PINECONE_INDEX_NAME: index name
  - PINECONE_DIMENSION: vector dimension
- Google Gemini
  - GEMINI_API_KEY: Gemini API key
  - GEMINI_MODEL: model identifier
  - GEMINI_TEMPERATURE: generation temperature
  - GEMINI_MAX_TOKENS: max tokens
- RAG
  - RAG_TOP_K: number of retrieved chunks
  - RAG_SIMILARITY_THRESHOLD: similarity threshold
  - CHUNK_SIZE: chunk size for ingestion
  - CHUNK_OVERLAP: overlap between chunks
- Session
  - SESSION_TTL_HOURS: session TTL
  - MAX_CONVERSATION_HISTORY: max stored messages
- Scraping
  - SCRAPE_BASE_URL: base URL to scrape
  - SCRAPE_MAX_PAGES: max pages to crawl
  - SCRAPE_DELAY: delay between requests
- CORS
  - CORS_ORIGINS: comma-separated origins or "*" for any

**Section sources**
- [config.py:10-48](file://backend/app/config.py#L10-L48)

### Environment Setup Procedures
- Backend
  - Create a local environment file and populate the variables listed above
  - Ensure the environment file path aligns with the configured loader
- Frontend
  - Set NEXT_PUBLIC_API_URL to the backend URL
  - Build and preview using the provided scripts
- Vercel
  - Configure environment variables in the platform’s dashboard
  - Confirm route and PYTHONPATH settings

**Section sources**
- [config.py:49-51](file://backend/app/config.py#L49-L51)
- [next.config.ts:9-11](file://frontend/next.config.ts#L9-L11)
- [package.json:5-10](file://frontend/package.json#L5-L10)
- [vercel.json:12-20](file://backend/vercel.json#L12-L20)

### Configuration Templates
- Backend .env template
  - APP_NAME=your-app-name
  - DEBUG=false
  - BACKEND_URL=https://your-backend.vercel.app
  - MONGODB_URI=mongodb+srv://user:pass@cluster/db
  - MONGODB_DB_NAME=hitech
  - PINECONE_API_KEY=sk-...key
  - PINECONE_ENVIRONMENT=gcp-starter
  - PINECONE_INDEX_NAME=hitech-kb-index
  - PINECONE_DIMENSION=1024
  - GEMINI_API_KEY=AIza...key
  - GEMINI_MODEL=gemini-2.5-flash-preview-05-20
  - GEMINI_TEMPERATURE=0.3
  - GEMINI_MAX_TOKENS=2048
  - RAG_TOP_K=5
  - RAG_SIMILARITY_THRESHOLD=0.7
  - CHUNK_SIZE=500
  - CHUNK_OVERLAP=50
  - SESSION_TTL_HOURS=24
  - MAX_CONVERSATION_HISTORY=10
  - SCRAPE_BASE_URL=https://www.hitech.sa
  - SCRAPE_MAX_PAGES=100
  - SCRAPE_DELAY=1.0
  - CORS_ORIGINS=http://localhost:3000,https://your-frontend.vercel.app
- Frontend .env.local template
  - NEXT_PUBLIC_API_URL=https://your-backend.vercel.app

Note: Replace placeholder values with your actual configuration.

**Section sources**
- [config.py:10-48](file://backend/app/config.py#L10-L48)
- [next.config.ts:9-11](file://frontend/next.config.ts#L9-L11)