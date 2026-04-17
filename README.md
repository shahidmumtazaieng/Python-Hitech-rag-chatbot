# Hitech RAG Chatbot

A production-ready RAG (Retrieval-Augmented Generation) chatbot for Hitech Steel Industries with lead capture, conversation memory, and embeddable widget support.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLIENT SITES                              │
│  ┌──────────────┐  ┌──────────────┐                             │
│  │  WordPress   │  │    Odoo      │                             │
│  │  +widget.js  │  │  +widget.js  │                             │
│  └──────┬───────┘  └──────┬───────┘                             │
└─────────┼─────────────────┼─────────────────────────────────────┘
          │                 │
          └─────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                    NEXT.JS FRONTEND (Vercel)                     │
│  - Standalone Chat Page (/chat)                                  │
│  - Widget.js Generator (/api/widget.js)                          │
└─────────────────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────────┐
│                   FASTAPI BACKEND (Vercel)                       │
│  - POST /api/lead              → Store lead, create session      │
│  - POST /api/chat/sync         → RAG chat with memory            │
│  - POST /api/talk-to-human     → Escalate to human               │
│  - POST /api/ingest            → Knowledgebase ingestion         │
└─────────────────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────────┐
│                      DATA STORES                                 │
│  ┌─────────────────────┐  ┌─────────────────────┐               │
│  │   MongoDB Atlas     │  │     Pinecone        │               │
│  │  - hitech.leads     │  │  - hitech-kb-index  │               │
│  │  - hitech.conversations│  (BGE-M3 embeddings)│               │
│  └─────────────────────┘  └─────────────────────┘               │
└─────────────────────────────────────────────────────────────────┘
```

## Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **LangGraph** - RAG pipeline with document grading and query transformation
- **Google Gemini 2.5 Flash** - LLM for response generation
- **BGE-M3** - Multilingual embeddings (1024 dims)
- **Pinecone** - Vector store for knowledgebase
- **MongoDB Atlas** - Lead and conversation storage
- **BeautifulSoup** - Web scraping for knowledgebase

### Frontend
- **Next.js 15** - React framework with App Router
- **TypeScript** - Type safety
- **Tailwind CSS** - Utility-first styling
- **shadcn/ui** - UI component library
- **React Hook Form** - Form handling
- **Zod** - Schema validation

## Project Structure

```
hitech-rag-chatbot/
├── backend/                 # FastAPI Backend
│   ├── app/
│   │   ├── config.py       # Configuration settings
│   │   ├── main.py         # FastAPI entry point
│   │   ├── models/         # Pydantic models
│   │   ├── services/       # Business logic
│   │   │   ├── mongodb_service.py
│   │   │   ├── embedding_service.py
│   │   │   ├── pinecone_service.py
│   │   │   ├── scraper_service.py
│   │   │   └── rag_service.py
│   │   ├── graph/          # LangGraph RAG pipeline
│   │   │   └── rag_graph.py
│   │   └── routers/        # API endpoints
│   ├── requirements.txt
│   └── vercel.json         # Vercel deployment config
│
├── frontend/               # Next.js Frontend
│   ├── app/
│   │   ├── page.tsx        # Landing page
│   │   ├── chat/page.tsx   # Standalone chat
│   │   └── api/widget.js/  # Widget generator
│   ├── components/
│   │   ├── chat/           # Chat components
│   │   └── ui/             # UI components
│   ├── lib/
│   │   ├── api.ts          # API client
│   │   └── utils.ts
│   └── next.config.ts
│
└── README.md
```

## Environment Variables

### Backend (.env)
```bash
# MongoDB Atlas
MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/hitech

# Pinecone
PINECONE_API_KEY=pc_your_key

# Google Gemini
GEMINI_API_KEY=AIzaSyYourKey

# CORS
CORS_ORIGINS="*"
```

### Frontend (.env.local)
```bash
NEXT_PUBLIC_API_URL=https://your-backend.vercel.app
NEXT_PUBLIC_WIDGET_API_URL=https://your-frontend.vercel.app
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/lead` | POST | Submit lead form, create session |
| `/api/chat/sync` | POST | Send message, get RAG response |
| `/api/talk-to-human` | POST | Request human escalation |
| `/api/ingest` | POST | Trigger knowledgebase ingestion |
| `/api/health` | GET | Health check |
| `/api/widget.js` | GET | Get embeddable widget script |

## Widget Integration

### WordPress
Add to your theme's footer or use a plugin like "Insert Headers and Footers":

```html
<script src="https://your-frontend.vercel.app/api/widget.js?apiUrl=https://your-backend.vercel.app"></script>
```

### Odoo
Add to your website template:

```xml
<script src="https://your-frontend.vercel.app/api/widget.js?apiUrl=https://your-backend.vercel.app"/>
```

### Custom Website
```html
<!DOCTYPE html>
<html>
<head>
    <title>My Site</title>
</head>
<body>
    <!-- Your content -->
    
    <script src="https://your-frontend.vercel.app/api/widget.js?apiUrl=https://your-backend.vercel.app"></script>
</body>
</html>
```

## Deployment

### Backend (Vercel)
```bash
cd backend
vercel --prod
```

### Frontend (Vercel)
```bash
cd frontend
vercel --prod
```

## Knowledgebase Ingestion

To populate the vector store with your website content:

```bash
# Using the API endpoint
curl -X POST https://your-backend.vercel.app/api/ingest \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.hitech.sa", "max_pages": 50}'
```

## Features

- **Lead Capture Form** - Collects name, email, phone, company, inquiry type
- **Session Persistence** - 24-hour session storage in localStorage
- **Conversation Memory** - Last 10 messages included in context
- **RAG Pipeline** - Multi-query retrieval with document grading
- **Human Escalation** - "Talk to Human" button with ticket creation
- **Embeddable Widget** - Works on any website via script tag
- **Mobile Responsive** - Works on all device sizes
- **Saudi Phone Validation** - Validates Saudi mobile numbers

## License

MIT License - Hitech Steel Industries
