# Privacy-Focused AI Document Summarizer

A desktop application for small and mid-sized businesses (SMBs) to summarize documents locally using AI, ensuring 100% data privacy.

## 🎯 Overview

This application provides secure, local document summarization using a locally hosted Large Language Model (LLM). All data processing occurs on your device - no cloud dependency, no data exposure.

### Key Features

- **100% Local Processing**: Documents never leave your device
- **Multiple Document Formats**: Support for PDF and DOCX files
- **Smart Templates**: Pre-built prompts for common business use cases
- **Large Document Support**: Handles 100+ page documents efficiently
- **Encrypted Storage**: Local SQLite database with encryption
- **Model Updates**: Easy LLM model updates without reinstalling

### Target Users

- Small and mid-sized businesses (1-50 employees)
- Consulting firms, agencies, and creative industries
- Freelancers and solo entrepreneurs
- Anyone handling sensitive documents requiring privacy

## 🚀 Quick Start

### Prerequisites

- Windows 10/11 or macOS 11+ (Big Sur or later)
- 16GB RAM minimum
- 10GB available disk space
- Intel i5 processor or equivalent

### Installation

1. Download the installer for your platform:
   - Windows: `DocumentSummarizer-Setup.exe`
   - macOS: `DocumentSummarizer.dmg`

2. Run the installer and follow the setup wizard

3. Launch the application and complete the initial configuration

## 🏗️ Development Setup

### Prerequisites

- Python 3.9+
- Node.js 16+
- Ollama with models installed
- Git

### Current Development Status (Updated: 2025-06-28)

**✅ Working Components:**
- Backend API with real LLM integration (Ollama + llama3:8b)
- Document processing (PDF/DOCX extraction)
- Database with encryption
- Electron desktop app
- Real AI summarization (confirmed working - processed documents in ~7 seconds)

**🚨 Current Issues:**
- CORS configuration issue: Frontend (port 3002) cannot connect to backend (port 8050)
- Backend processes documents successfully but responses blocked by CORS
- Need to restart backend with updated CORS configuration

### Port Configuration

- **Backend API**: `http://127.0.0.1:8050`
- **Frontend (Electron)**: Auto-assigned (typically `http://localhost:3000-3002`)
- **Ollama LLM**: `http://localhost:11434`

### Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment (if not exists)
python -m venv venv

# Activate virtual environment
# Windows:
.\venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Initialize database (if not done)
python scripts/init_db.py

# Start the FastAPI server
python -m uvicorn app.main:app --host 127.0.0.1 --port 8050 --reload
```

### Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies (if not done)
npm install

# Start Electron development app
npm start
```

### Model Setup

```bash
# Install and start Ollama
# Follow instructions at: https://ollama.ai/

# Available models (from current setup):
ollama list
# - llama3:8b (4.7 GB) - Currently configured
# - phi:latest (1.6 GB) - Faster alternative
# - mistral:latest (4.1 GB)
# - llama2:latest (3.8 GB)

# Model is configured in backend/config.yaml
```

### Quick Start Commands

```bash
# Terminal 1: Start Backend
cd backend
.\venv\Scripts\activate
python -m uvicorn app.main:app --host 127.0.0.1 --port 8050 --reload

# Terminal 2: Start Frontend
cd frontend
npm start
```

## 📁 Project Structure

```
DocumentSummarizer/
├── backend/                    # Python FastAPI backend
│   ├── app/                   # Application code
│   ├── scripts/               # Utility scripts
│   ├── tests/                 # Backend tests
│   ├── requirements.txt       # Python dependencies
│   └── config.yaml           # Configuration
├── frontend/                  # Electron + React frontend
│   ├── src/                  # Source code
│   ├── public/               # Static assets
│   ├── package.json          # Node dependencies
│   └── electron.js           # Electron main process
├── models/                   # LLM model storage
├── database/                 # Database files and schemas
├── packaging/                # Build and packaging scripts
├── docs/                     # Documentation
├── tests/                    # Integration tests
└── README.md                 # This file
```

## 🔧 Configuration

The application uses a configuration file (`backend/config.yaml`) for:

- Model settings
- Database configuration
- API endpoints
- Security settings

## 🧪 Testing

### Manual Testing

```bash
# Test backend API directly
curl http://localhost:8050/health

# Test document processing
# Upload test_document.txt via the frontend interface

# Check backend logs for LLM processing
# Look for "Summarization completed in X.XXs" messages
```

### Automated Testing

```bash
# Run backend tests (when available)
cd backend
python -m pytest tests/

# Run frontend tests (when available)
cd frontend
npm test

# Test API connection
python test_api_connection.py
```

## 🔧 Troubleshooting

### Common Issues

**CORS Errors (Current Issue)**
```
Access to fetch at 'http://localhost:8050' from origin 'http://localhost:3002' 
has been blocked by CORS policy
```
- **Issue**: Frontend port not in backend's CORS allowed origins
- **Fix**: Update `backend/config.yaml` security.cors_origins to include actual frontend port
- **Current Config**: Includes ports 3000, 3001, 3002, 3050
- **Solution**: Restart backend after config changes

**Backend Not Starting**
```
No module named uvicorn
```
- **Issue**: Virtual environment not activated or dependencies not installed
- **Fix**: `cd backend && .\venv\Scripts\activate && pip install -r requirements.txt`

**Frontend Build Errors**
```
npm error code ENOENT
```
- **Issue**: Running npm from wrong directory
- **Fix**: Ensure you're in the `frontend/` directory before running `npm start`

**Ollama Connection Issues**
```
Connection refused to localhost:11434
```
- **Issue**: Ollama service not running
- **Fix**: Start Ollama service: `ollama serve`

### Debug Information

**Current Working Configuration:**
- Backend: Python FastAPI on port 8050 with real LLM integration
- Frontend: Electron app (React) on auto-assigned port
- LLM: Ollama + llama3:8b model (4.7 GB)
- Database: Encrypted SQLite with generated key
- Processing: Confirmed working (PDF processing in ~7 seconds)

**Log Locations:**
- Backend logs: Console output when running uvicorn
- Frontend logs: Electron DevTools console
- Database: `database/summaries.db` (encrypted)

**Test Files:**
- `test_document.txt`: Business meeting minutes for testing
- `test_api_connection.py`: Backend API connectivity test

### Resuming Development

**To continue from current state:**

1. **Check Current Status:**
   ```bash
   # Check if backend is running
   netstat -ano | findstr :8050
   
   # Check if frontend is running
   # Look for Electron window or check process list
   ```

2. **Start Development Environment:**
   ```bash
   # Terminal 1: Backend (with virtual environment)
   cd backend
   .\venv\Scripts\activate
   python -m uvicorn app.main:app --host 127.0.0.1 --port 8050 --reload
   
   # Terminal 2: Frontend
   cd frontend
   npm start
   ```

3. **Verify Setup:**
   ```bash
   # Test backend health
   curl http://localhost:8050/health
   
   # Check Ollama models
   ollama list
   
   # Check frontend loads (Electron window should open)
   ```

4. **Test LLM Processing:**
   - Upload `test_document.txt` through the frontend
   - Check backend console for processing logs
   - Verify summary generation and storage

## 📦 Building

### Development Build

```bash
# Build frontend
cd frontend
npm run build

# Package application
cd ../packaging
python build.py
```

### Production Build

```bash
# Create installer
cd packaging
python create_installer.py
```

## 🔐 Security & Privacy

- **Local Processing**: All document analysis happens on your device
- **Encrypted Storage**: SQLite database encrypted with user-defined key
- **No Cloud Dependency**: No external API calls except for model updates
- **Data Retention**: Configurable history retention (default: 50 summaries)

## 📊 Performance

- **Target**: Summarize 10-page PDF in <30 seconds on 16GB RAM laptop
- **Context Window**: 4K tokens with sliding window for larger documents
- **Memory Usage**: ~4GB RAM with 4-bit quantized TinyLlama
- **Document Size**: Supports up to 100+ page documents

## 🛠️ Architecture

- **Frontend**: Electron with React (cross-platform UI)
- **Backend**: Python FastAPI (local API server)
- **LLM**: TinyLlama (4-bit quantized, via Ollama)
- **Database**: SQLite with encryption
- **Packaging**: PyInstaller + NSIS/create-dmg

## 📈 Development Progress & Next Steps

### Current State (2025-06-28)

**✅ Completed:**
- [x] Backend API with FastAPI
- [x] Real LLM integration (Ollama + llama3:8b)
- [x] Document processing (PDF/DOCX extraction)
- [x] Three summary templates (general, customer feedback, contract analysis)
- [x] Encrypted SQLite database
- [x] Electron desktop application
- [x] React frontend with drag-and-drop
- [x] Real AI summarization (confirmed: 7-second processing)
- [x] Core architecture complete

**🔧 In Progress:**
- [ ] Fix CORS configuration issue (backend-frontend communication)
- [ ] Frontend error handling and loading states
- [ ] Summary display and export functionality

**📋 Immediate Next Steps:**
1. **Fix CORS Issue**: Restart backend with updated CORS configuration
2. **Test End-to-End**: Verify frontend can receive and display summaries
3. **Add Error Handling**: Improve frontend error messages and loading states
4. **Polish UI**: Enhance user experience and interface design

### MVP Roadmap

**Phase 1 (Current)**
- [x] Core summarization pipeline
- [x] Local document processing
- [x] Encrypted storage
- [ ] CORS resolution (90% complete)

**Phase 2 (Next)**
- [ ] Export functionality (PDF, DOCX, TXT)
- [ ] Summary history management
- [ ] Settings and preferences
- [ ] Model switching interface

**Phase 3 (Future)**
- [ ] Batch document processing
- [ ] Custom template builder
- [ ] Performance optimization
- [ ] Cross-platform packaging

### Technical Debt
- [ ] Add comprehensive test coverage
- [ ] Improve error handling throughout
- [ ] Add logging configuration
- [ ] Performance optimization for large documents
- [ ] Security audit and hardening

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Support

- Documentation: [docs/](docs/)
- Issues: [GitHub Issues](https://github.com/your-username/DocumentSummarizer/issues)
- Email: support@documentsummarizer.com

## 🎯 Business Model

- **One-Time Purchase**: $99 for desktop app
- **Subscription**: $10/month for premium templates and updates
- **Custom Consulting**: $500-$1,000 for custom template development

---

**Built with privacy in mind. Your documents stay on your device.** 