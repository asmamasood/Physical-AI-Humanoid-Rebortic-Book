# Quick Start Guide 🚀

## Start All Services

Follow these steps to run the complete system:

### 1. Start Backend (Port 8000)
```bash
# Terminal 1
cd D:\digital-book\backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**Wait for**: "Application startup complete"

### 2. Start Auth Service (Port 3001)
```bash
# Terminal 2
cd D:\digital-book\auth-service
node index.js
```

**Wait for**: "Auth service running on http://localhost:3001"

### 3. Start Frontend (Port 3000)
```bash
# Terminal 3
cd D:\digital-book\physical-ai-robotics-book
npm start
```

**Wait for**: Browser opens automatically at http://localhost:3000

---

## Test Everything Works

### Test 1: Backend Health
```bash
curl http://localhost:8000/health
```
**Expected**: `{"status":"ok","version":"1.0.0"}`

### Test 2: Auth Service
```bash
curl http://localhost:3001/api/auth/session
```
**Expected**: Session data (may be empty if not logged in)

### Test 3: Chat
Open browser at http://localhost:3000
1. Click chat widget (bottom right corner)
2. Type: "What is robotics?"
3. **Expected**: Full answer with friendly greeting

---

## Quick Test Commands

### Test Chat (No Auth Required)
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"query":"hello","top_k":3}'
```

### Test Summary Generation
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"query":"summarize module 1","top_k":10}'
```

### Test Quiz Generation
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"query":"create a quiz for chapter 2","chapter_id":"chapter-2","top_k":10}'
```

---

## Stop All Services

```bash
# Press Ctrl+C in each terminal window
# Or close all terminal windows
```

---

## Troubleshooting

### Port Already in Use

**Backend (8000)**:
```bash
# Windows
netstat -ano | findstr :8000
taskkill //F //PID <PID>
```

**Auth (3001)**:
```bash
netstat -ano | findstr :3001
taskkill //F //PID <PID>
```

**Frontend (3000)**:
```bash
netstat -ano | findstr :3000
taskkill //F //PID <PID>
```

### Clear Caches

**Frontend**:
```bash
cd D:\digital-book\physical-ai-robotics-book
npm run clear
npm start
```

### Reset Everything

```bash
# Stop all services (Ctrl+C)
# Kill any remaining processes
taskkill //F //IM python.exe
taskkill //F //IM node.exe

# Start fresh
# Follow "Start All Services" steps above
```

---

## Quick Reference

| Service | Port | URL | Status Check |
|---------|------|-----|--------------|
| Backend | 8000 | http://localhost:8000 | `/health` |
| Auth | 3001 | http://localhost:3001 | `/api/auth/session` |
| Frontend | 3000 | http://localhost:3000 | Open in browser |

---

## What's Working

✅ Sign-in / Sign-up
✅ Chat with RAG (retrieval-augmented generation)
✅ Intent detection (QA, Summary, Quiz, Selected Text)
✅ Context-aware greetings with emojis
✅ Citations to source material
✅ User profiles & gamification
✅ Chat history
✅ Custom AI agents
✅ Urdu translation

---

**Ready to use!** Open http://localhost:3000 and start chatting! 🎉
