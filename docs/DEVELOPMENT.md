# Development Guide

This guide provides detailed information for developers working on the Privacy-Focused AI Document Summarizer.

## 🏗️ Project Structure

```
DocumentSummarizer/
├── backend/                    # Python FastAPI backend
│   ├── app/                   # Application code
│   │   ├── main.py           # FastAPI application entry point
│   │   ├── models.py         # Pydantic models
│   │   ├── config.py         # Configuration management
│   │   ├── middleware.py     # Custom middleware
│   │   └── services/         # Business logic services
│   │       ├── document_processor.py
│   │       ├── llm_service.py
│   │       ├── database_service.py
│   │       └── model_updater.py
│   ├── scripts/              # Utility scripts
│   │   └── init_db.py       # Database initialization
│   ├── tests/               # Backend tests
│   ├── requirements.txt     # Python dependencies
│   └── config.yaml         # Configuration file
├── frontend/               # Electron + React frontend
│   ├── src/               # React source code
│   │   ├── components/    # React components
│   │   ├── services/      # Frontend services
│   │   └── App.js        # Main React component
│   ├── public/           # Static assets
│   ├── package.json      # Node.js dependencies
│   └── electron.js       # Electron main process
├── models/               # LLM model storage
├── database/            # Database files and schemas
│   └── schema.sql       # SQLite database schema
├── packaging/           # Build and packaging scripts
│   └── build.py        # Cross-platform build script
├── docs/               # Documentation
├── tests/              # Integration tests
└── README.md          # Project overview
```

## 🚀 Development Setup

### Prerequisites

- **Python 3.9+**: For backend development
- **Node.js 16+**: For frontend development
- **Ollama**: For local LLM hosting
- **Git**: Version control
- **SQLCipher**: For database encryption (optional)

### Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   
   # Activate (Windows)
   venv\Scripts\activate
   
   # Activate (macOS/Linux)
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize database:**
   ```bash
   python scripts/init_db.py
   ```

5. **Start development server:**
   ```bash
   python app/main.py
   ```

The backend API will be available at `http://localhost:8050`

### Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Start development server:**
   ```bash
   npm run dev
   ```

The Electron app will start with hot reload enabled.

### Model Setup

1. **Install Ollama:**
   Follow instructions at [ollama.ai](https://ollama.ai/)

2. **Pull TinyLlama model:**
   ```bash
   ollama pull tinyllama
   ```

3. **Verify model is running:**
   ```bash
   curl http://localhost:11434/api/generate -d '{
     "model": "tinyllama",
     "prompt": "Test prompt"
   }'
   ```

## 🧪 Testing

### Backend Tests

```bash
cd backend
python -m pytest tests/ -v
```

### Frontend Tests

```bash
cd frontend
npm test
```

### Integration Tests

```bash
python tests/integration/test_e2e.py
```

### Manual Testing

1. **Document Processing:**
   - Test PDF upload and text extraction
   - Test DOCX upload and text extraction
   - Verify chunking for large documents

2. **Summarization:**
   - Test different templates (general, customer feedback, contract)
   - Test custom prompts
   - Verify summary quality and processing time

3. **Database Operations:**
   - Test summary storage and retrieval
   - Test history functionality
   - Verify encryption works

4. **UI/UX:**
   - Test drag-and-drop file upload
   - Test navigation between views
   - Test responsive design

## 🔧 Configuration

### Backend Configuration (`backend/config.yaml`)

Key configuration sections:

- **app**: Basic application settings
- **database**: SQLite database configuration
- **model**: LLM model settings
- **documents**: Document processing limits
- **templates**: Summary prompt templates
- **security**: CORS and authentication settings
- **performance**: Resource limits and timeouts

### Frontend Configuration (`frontend/package.json`)

Key sections:

- **build**: Electron builder configuration
- **scripts**: Development and build commands
- **dependencies**: React and Electron dependencies

### Environment Variables

Create `.env` file in backend directory:

```env
DB_ENCRYPTION_KEY=your_encryption_key_here
OLLAMA_HOST=http://localhost:11434
LOG_LEVEL=INFO
```

## 🏛️ Architecture

### Backend Architecture

- **FastAPI**: Modern Python web framework
- **Pydantic**: Data validation and serialization
- **SQLite + SQLCipher**: Encrypted local database
- **Ollama**: Local LLM hosting
- **PyPDF2/python-docx**: Document processing

### Frontend Architecture

- **Electron**: Cross-platform desktop app framework
- **React**: UI library with hooks
- **Styled Components**: CSS-in-JS styling
- **Chart.js**: Data visualization
- **React Router**: Client-side routing

### Key Design Patterns

1. **Service Layer**: Business logic separated into services
2. **Repository Pattern**: Database access abstraction
3. **Observer Pattern**: Event-driven updates
4. **Strategy Pattern**: Pluggable document processors

## 📦 Building and Packaging

### Development Build

```bash
cd packaging
python build.py --debug
```

### Production Build

```bash
cd packaging
python build.py --platform windows  # or darwin, linux
```

### Manual Packaging

```bash
# Frontend build
cd frontend
npm run build

# Backend packaging
cd backend
pyinstaller app.spec

# Electron packaging
cd frontend
npm run dist
```

## 🔍 Debugging

### Backend Debugging

1. **Enable debug logging:**
   ```yaml
   # config.yaml
   app:
     debug: true
   logging:
     level: "DEBUG"
   ```

2. **Use Python debugger:**
   ```python
   import pdb; pdb.set_trace()
   ```

3. **FastAPI debug mode:**
   ```bash
   uvicorn app.main:app --reload --log-level debug
   ```

### Frontend Debugging

1. **Electron DevTools:**
   - Enable in development mode automatically
   - Use `Ctrl+Shift+I` to open

2. **React Developer Tools:**
   - Install browser extension
   - Available in Electron DevTools

3. **Console logging:**
   ```javascript
   console.log('Debug info:', data);
   ```

### Common Issues

1. **Ollama not responding:**
   ```bash
   # Check if Ollama is running
   ollama list
   
   # Restart Ollama service
   ollama serve
   ```

2. **Database locked:**
   ```bash
   # Reset database
   python scripts/init_db.py --reset
   ```

3. **Build fails:**
   ```bash
   # Clean build artifacts
   python packaging/build.py --clean-only
   ```

## 🤝 Contributing

### Code Style

- **Python**: Follow PEP 8, use Black formatter
- **JavaScript**: Use Prettier, follow Airbnb style guide
- **Documentation**: Use clear, concise comments

### Commit Guidelines

Use conventional commits:

```
feat: add new document template
fix: resolve PDF parsing issue
docs: update installation guide
test: add unit tests for LLM service
```

### Pull Request Process

1. Fork the repository
2. Create feature branch: `git checkout -b feature/new-feature`
3. Make changes and add tests
4. Update documentation
5. Submit pull request with clear description

### Code Review Checklist

- [ ] Tests pass
- [ ] Documentation updated
- [ ] Performance considerations addressed
- [ ] Security implications reviewed
- [ ] Cross-platform compatibility verified

## 🔐 Security Considerations

### Data Privacy

- All processing occurs locally
- No external API calls (except model updates)
- Database encryption enabled by default
- Secure file handling

### Vulnerability Prevention

- Input validation on all endpoints
- SQL injection prevention with parameterized queries
- XSS prevention in frontend
- CSRF protection with proper CORS configuration

### Security Testing

```bash
# Backend security scan
bandit -r backend/app/

# Frontend dependency audit
cd frontend && npm audit

# Check for secrets in code
git-secrets --scan
```

## 📊 Performance Optimization

### Backend Optimization

- Use async/await for I/O operations
- Implement connection pooling for database
- Cache frequently accessed data
- Use background tasks for heavy operations

### Frontend Optimization

- Code splitting with React lazy loading
- Optimize bundle size with webpack analysis
- Use React.memo for expensive components
- Implement virtual scrolling for large lists

### Memory Management

- Clean up resources in service destructors
- Monitor memory usage during development
- Use memory profiling tools
- Implement garbage collection hints

## 📈 Monitoring and Logging

### Application Logging

```python
from loguru import logger

logger.info("Processing document: {filename}", filename=file.name)
logger.error("Failed to process: {error}", error=str(e))
```

### Performance Metrics

- Document processing time
- Memory usage
- Database query performance
- LLM response time

### Error Tracking

- Centralized error logging
- User-friendly error messages
- Error reporting to development team
- Crash report collection

## 🔄 Continuous Integration

### GitHub Actions (example)

```yaml
name: CI
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.9
      - name: Install dependencies
        run: pip install -r backend/requirements.txt
      - name: Run tests
        run: pytest backend/tests/
```

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [Electron Documentation](https://electronjs.org/docs)
- [Ollama Documentation](https://ollama.ai/docs)
- [SQLite Documentation](https://sqlite.org/docs.html)

## 🆘 Getting Help

- **Issues**: Use GitHub Issues for bug reports
- **Discussions**: Use GitHub Discussions for questions
- **Documentation**: Check docs/ directory
- **Examples**: See tests/ for usage examples 