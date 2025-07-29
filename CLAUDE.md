# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an operations management system (sremanage) with a Vue.js frontend and Flask backend, designed for IT operations tasks including server management, batch commands, terminal access, and various operational tools.

## Architecture

### Frontend (Vue.js)
- **Framework**: Vue 3 with Vite build tool
- **UI**: Tailwind CSS with custom components  
- **State Management**: Uses Vue 3 Composition API
- **Routing**: Vue Router with authentication guards
- **Terminal**: xterm.js for web-based terminal functionality

### Backend (Flask)
- **Framework**: Flask with SQLAlchemy ORM
- **Database**: MySQL with PyMySQL connector
- **Authentication**: JWT tokens with session management
- **WebSocket**: flask-sock for terminal connections
- **SSH**: paramiko for remote server connections

## Development Commands

### Frontend Development
```bash
cd frontend
npm install
npm run dev        # Start development server on port 5173
npm run build      # Build for production
npm run preview    # Preview production build
```

### Backend Development
```bash
cd backend
pip3 install -r requirements.txt
python run.py      # Alternative entry point（优先使用）
# or
python main.py     # Start Flask server on port 5000
```

### Database Setup
```bash
cd backend
python scripts/init_db.py    # Initialize database
mysql -u root -p < sql/1.user.sql       # Load user tables
mysql -u root -p < sql/2.hosts.sql      # Load hosts tables  
mysql -u root -p < sql/3.settings.sql   # Load settings tables
```

## Key Architecture Patterns

### Frontend Structure
- **components/**: Reusable UI components (Button, Card, Input)
- **views/**: Page-level components organized by feature
  - `assets/`: Host and site management
  - `ops/`: Operations tools (CDN, Jenkins, batch commands)
  - `tools/`: Utility tools (password gen, file diff, JSON parser)
  - `terminal/`: Web terminal interface
- **router/**: Route definitions with authentication guards
- **utils/**: API client and helper functions

### Backend Structure
- **app/routes/**: Feature-based route blueprints
- **app/models/**: SQLAlchemy database models
- **app/services/**: Business logic layer
- **app/utils/**: Utility functions (auth, database, logging)
- **app/api/**: API endpoint definitions

### Authentication Flow
- JWT tokens stored in localStorage with expiration tracking
- Route guards check token validity before navigation
- Backend validates tokens on protected endpoints
- Session management with Flask-Session for WebSocket connections

### WebSocket Terminal
- Uses flask-sock for WebSocket connections
- paramiko handles SSH connections to remote servers
- xterm.js provides terminal UI in browser
- Real-time command execution and output streaming

## Configuration

### Environment Setup
- Backend config in `backend/config/mysql.cnf`
- Frontend proxy configured in `vite.config.js` 
- CORS configured for localhost:5173 ↔ localhost:5000
- Database connection pooling and retry logic implemented

### Default Credentials
- Username: admin
- Password: 9itNKA6nVs0ZkGw321Tu

## Development Notes

### Database Patterns
- SQLAlchemy models use explicit table names
- Connection pooling with automatic reconnection
- Separate database utility for connection management

### Frontend Patterns  
- Vue 3 Composition API throughout
- Route-based code splitting with dynamic imports
- Tailwind CSS for styling with custom components
- API calls centralized in utils/api.js

### Backend Patterns
- Blueprint-based route organization
- Decorator-based authentication (@token_required)
- Centralized error handling and logging
- WebSocket and HTTP route separation

## Testing

Run backend tests:
```bash
cd backend
python -m pytest tests/
```

Test specific functionality:
```bash
python tests/test_ssh_connection.py  # Test SSH connectivity
python tests/test_db_query.py        # Test database operations
```