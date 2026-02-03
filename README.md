# LeetCode Analyzer

AI-powered analysis tool for LeetCode solutions to help software engineering candidates prepare for technical interviews.

## Features

### Core Analysis Features
- **Two-Stage Complexity Analysis**: Fast Big O notation analysis with on-demand detailed explanations
- **Strategic Hints**: Progressive hints that guide without revealing complete solutions
- **Solution Optimization**: Identify improvement opportunities with specific suggestions
- **Debugging Assistance**: Find and fix bugs with detailed issue analysis
- **Problem Inference**: Analyze code without providing a problem URL - AI infers the problem

### User Experience
- **Dark/Light Mode**: Fully themed interface with persistent preference
- **Monaco Code Editor**: Professional code editing with syntax highlighting
- **Keyboard Shortcuts**: Efficient navigation and analysis triggering
- **Resizable Panels**: Customizable layout for optimal workflow
- **Smart Caching**: Frontend and backend caching for faster responses
- **Completeness Checking**: Automatic validation that solutions are complete before analysis

## Tech Stack

**Frontend:**
- React 19 with TypeScript
- Tailwind CSS 4
- Monaco Editor
- Vite
- Vitest for testing

**Backend:**
- Python 3.11 with FastAPI
- SQLite for history storage
- SQLAlchemy ORM
- Anthropic Claude Sonnet 4.5 / OpenAI GPT-5 Mini
- APScheduler for background jobs
- Pytest for testing

## Setup

### Prerequisites

- Python 3.11+
- Node.js 18+
- npm
- Claude API key or OpenAI API key

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
   # AI Service Configuration
   AI_PROVIDER=claude  # Options: claude, openai
   FALLBACK_PROVIDER=openai
   
   # Claude Configuration (recommended)
   CLAUDE_API_KEY=your_claude_api_key_here
   CLAUDE_MODEL=claude-sonnet-4-5-20250929
   
   # OpenAI Configuration (alternative)
   OPENAI_API_KEY=your_openai_api_key_here
   OPENAI_MODEL=gpt-5-mini-2025-08-07
   
   # Database Configuration
   DATABASE_URL=sqlite:///./leetcode_analysis.db
   
   # History Retention (days)
   HISTORY_RETENTION_DAYS=7
   
   # Rate Limiting
   RATE_LIMIT_PER_MINUTE=10
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
│   ├── main.py                    # FastAPI application
│   ├── config.py                  # Configuration management
│   ├── requirements.txt           # Python dependencies
│   ├── services/
│   │   ├── ai/
│   │   │   ├── ai_service.py      # AI service interface
│   │   │   ├── claude_service.py  # Claude implementation
│   │   │   ├── openai_service.py  # OpenAI implementation
│   │   │   └── prompts.py         # AI prompts
│   │   ├── cache_service.py       # Caching layer
│   │   ├── leetcode_parser.py     # LeetCode API integration
│   │   └── validation_service.py  # Input validation
│   └── tests/                     # Backend tests
├── frontend/
│   ├── src/
│   │   ├── App.tsx                # Main application
│   │   ├── components/            # React components
│   │   ├── contexts/              # React contexts (theme)
│   │   ├── hooks/                 # Custom hooks
│   │   ├── types/                 # TypeScript types
│   │   ├── utils/                 # Utilities (cache)
│   │   └── config/                # Configuration
│   ├── package.json               # Node dependencies
│   └── vite.config.ts             # Vite configuration
├── .kiro/
│   └── specs/                     # Feature specifications
├── render.yaml                    # Render.com deployment config
└── dev.sh                         # Development convenience script
```

## API Endpoints

### Analysis
- `POST /api/analyze` - Analyze code (complexity, hints, optimization, debugging)
- `POST /api/analyze-complexity-quick` - Fast Big O analysis
- `POST /api/explain-complexity` - Detailed complexity explanation
- `POST /api/check-completeness` - Check if solution is complete

### Problem Details
- `GET /api/problem/{slug}` - Get LeetCode problem details
- `POST /api/validate-url` - Validate LeetCode problem URL

### History (Planned)
- `GET /api/history` - Get analysis history with pagination
- `GET /api/history/{problem_slug}` - Get history for specific problem
- `DELETE /api/history/{entry_id}` - Delete history entry

### Cache Management
- `GET /api/cache/stats` - Get cache statistics
- `DELETE /api/cache/clear` - Clear cache (problem/analysis/all)

### System
- `GET /` - API status
- `GET /health` - Health check
- `POST /api/validate` - Validate inputs

## Keyboard Shortcuts

- `Ctrl+Enter` - Run analysis
- `Ctrl+Shift+C` - Select complexity analysis
- `Ctrl+Shift+H` - Select hints analysis
- `Ctrl+Shift+O` - Select optimization analysis
- `Ctrl+Shift+D` - Select debugging analysis
- `Ctrl+R` - Scroll to results
- `Alt+1` - Focus problem input
- `Alt+2` - Focus code editor
- `?` - Show keyboard shortcuts help
- `Escape` - Close dialogs

## Testing

**Frontend:**
```bash
cd frontend
npm test              # Run tests in watch mode
npm run test:run      # Run tests once
npm run test:ui       # Run tests with UI
```

**Backend:**
```bash
cd backend
source venv/bin/activate
pytest                # Run all tests
pytest -v             # Verbose output
pytest tests/test_specific.py  # Run specific test file
```

## Deployment

The application is configured for deployment on Render.com:

1. Backend deploys as a Python web service
2. Frontend deploys to Vercel (or similar)
3. Environment variables configured in Render dashboard
4. SQLite database persisted on Render disk
5. Automatic cleanup job runs daily at 2 AM

See `render.yaml` for deployment configuration.

## Development Workflow

This project follows a spec-driven development approach using Kiro specs:

1. **Requirements** - Define features and acceptance criteria
2. **Design** - Plan architecture and implementation
3. **Tasks** - Break down into actionable items
4. **Implementation** - Build features incrementally
5. **Testing** - Validate with comprehensive tests

See `.kiro/specs/` for feature specifications.

## Recent Updates

- ✅ Two-stage complexity analysis for faster responses
- ✅ Dark/light mode theme toggle with persistence
- ✅ Keyboard shortcuts for efficient navigation
- ✅ Problem inference (no URL required)
- ✅ Completeness checking before analysis
- ✅ Smart caching (frontend + backend)
- ✅ Comprehensive error handling
- ✅ Monaco code editor integration
- ✅ Resizable panel layout

## License

MIT
