# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an AI-powered BI Dashboard Assistant that converts wireframe sketches into structured dashboard layouts and implementation instructions. The application uses FastAPI for the backend API and Streamlit for the frontend interface, with GPT-4 and GPT-4 Vision for intelligent analysis.

## Common Development Commands

### Running the Application

**Quick Start (both services)**:
```bash
cd agent-bi-assistant
python run.py
```

**Run Services Separately**:
```bash
# Backend API (Terminal 1) - with extended timeouts for AI processing
cd agent-bi-assistant
uvicorn main:app --reload --timeout-keep-alive 900

# Frontend UI (Terminal 2)
cd agent-bi-assistant
streamlit run streamlit_layout_ui.py
```

### Installation
```bash
cd agent-bi-assistant
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
```

### Environment Setup
Create `.env` file with:
```
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxx
API_KEY=supersecrettoken123
```

## High-Level Architecture

### Application Flow
1. **Data Model Definition** → User uploads JSON schema or SQL DDL
2. **Data Preparation** → AI generates platform-specific data prep instructions
3. **Dashboard Development** → Wireframe (text/image) → AI generates layout instructions
4. **Sprint Planning** → Converts instructions into agile sprint stories

### Core Components

**Backend (FastAPI)**:
- `main.py`: API endpoints orchestration
- `/api/v1/analyze-image`: GPT-4 Vision analysis
- `/api/v1/generate-layout`: Main layout generation endpoint
- `/api/v1/generate-model`: SQL DDL to JSON conversion
- `/api/v1/generate-sprint`: Sprint backlog generation
- Authentication via Bearer token in Authorization header

**Frontend (Streamlit)**:
- `streamlit_layout_ui.py`: Multi-page dashboard interface
- Progressive workflow with 4 main sections
- Session state management for workflow persistence
- Custom blue (#0C62FB) branded theme

**AI Integration**:
- OpenAI GPT-4 for text analysis and instruction generation
- GPT-4 Vision for wireframe image analysis
- Fallback OpenCV shape detection when vision unavailable
- Smart chunking for large SQL schemas

### Key Dependencies
- **FastAPI + Uvicorn**: High-performance API framework
- **Streamlit**: Interactive web UI
- **OpenAI SDK**: GPT-4 and Vision API integration
- **OpenCV + Pillow**: Image processing
- **Pydantic**: Data validation and serialization

### Important Notes
- Project has duplicate code in root and `agent-bi-assistant/` subdirectory
- No automated tests currently exist
- API requires valid Bearer token authentication
- All AI features require valid OpenAI API key in environment
- Both services support hot reload during development
- Any new updates that you would suggest on top of the feature that you build make sure to review with me why that aspect is a good feature to have