# LeetCode Analysis Website

AI-powered analysis tool for LeetCode solutions to help software engineering candidates prepare for technical interviews.

## Features

- **Time Complexity Analysis**: Understand the Big O complexity of your solutions
- **Strategic Hints**: Get progressive hints without revealing complete solutions
- **Solution Optimization**: Identify improvement opportunities in working solutions
- **Debugging Assistance**: Find and fix bugs in non-working solutions
- **Solution History**: Track your progress and compare multiple attempts

## Tech Stack

**Frontend:**
- React 18 with TypeScript
- Tailwind CSS
- Vite

**Backend:**
- Python FastAPI
- SQLite for history storage
- Free AI services (OpenAI/Hugging Face/Ollama)

## Setup

### Prerequisites

- Python 3.8+
- Node.js 18+
- npm or yarn

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd leetcode-analyzer
   ```

2. **Backend Setup**
   ```bash
   cd backend
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   ```

4. **Environment Configuration**
   
   Create a `.env` file in the `backend` directory:
   ```env
   # AI Service Configuration (choose one)
   AI_PROVIDER=openai  # Options: openai, huggingface, ollama
   
   # OpenAI (if using)
   OPENAI_API_KEY=your_api_key_here
   
   # Hugging Face (if using)
   HUGGINGFACE_API_KEY=your_api_key_here
   ```

## Development

### Run Both Servers

Use the convenience script:
```bash
./dev.sh
```

Or run them separately:

**Backend:**
```bash
cd backend
source venv/bin/activate
uvicorn main:app --reload --port 8000
```

**Frontend:**
```bash
cd frontend
npm run dev
```

The application will be available at:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Project Structure

```
leetcode-analyzer/
├── backend/
│   ├── main.py              # FastAPI application entry point
│   ├── requirements.txt     # Python dependencies
│   └── venv/               # Python virtual environment
├── frontend/
│   ├── src/
│   │   ├── App.tsx         # Main React component
│   │   ├── main.tsx        # React entry point
│   │   └── index.css       # Tailwind CSS imports
│   ├── package.json        # Node dependencies
│   └── vite.config.ts      # Vite configuration
├── .kiro/
│   └── specs/              # Feature specifications
└── dev.sh                  # Development convenience script
```

## API Endpoints

- `GET /` - API status
- `GET /health` - Health check
- `POST /api/analyze` - Analyze code (coming soon)
- `GET /api/problem/:slug` - Get problem details (coming soon)
- `GET /api/history` - Get analysis history (coming soon)

## Development Workflow

This project follows a spec-driven development approach. See `.kiro/specs/leetcode-analysis-website/` for:
- `requirements.md` - Feature requirements and acceptance criteria
- `design.md` - System architecture and design decisions
- `tasks.md` - Implementation task list

## Testing

```bash
# Frontend tests (coming soon)
cd frontend
npm test

# Backend tests (coming soon)
cd backend
pytest
```

## License

MIT
