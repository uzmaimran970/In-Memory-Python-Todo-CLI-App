# Quickstart: AI-Powered Todo Chatbot

**Feature**: 004-ai-chatbot-integration
**Time to Complete**: ~30 minutes setup

---

## Prerequisites

- [ ] Backend running on Railway (or localhost:8000)
- [ ] Frontend running on Vercel (or localhost:3000)
- [ ] Cohere API key obtained
- [ ] Existing user account for testing

---

## Step 1: Backend Setup

### 1.1 Add Environment Variable

**Railway Dashboard**:
```
COHERE_API_KEY=sW7XFBBpDLE77rTergTCa2nL5oizsC458LA47cF8
```

**Local Development** (backend/.env):
```bash
# Add to existing .env
COHERE_API_KEY=sW7XFBBpDLE77rTergTCa2nL5oizsC458LA47cF8
```

### 1.2 Install Cohere SDK

```bash
cd backend
pip install cohere
# Or add to requirements.txt:
# cohere>=5.0.0
```

### 1.3 Create Database Tables

```bash
# If using Alembic
alembic revision --autogenerate -m "Add chat tables"
alembic upgrade head

# Or run migration script
python -c "from app.database import engine; from app.models import *; SQLModel.metadata.create_all(engine)"
```

### 1.4 Verify Backend

```bash
# Start server
uvicorn app.main:app --reload

# Test endpoint exists
curl http://localhost:8000/api/chat \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "hello"}'
```

---

## Step 2: Frontend Setup

### 2.1 Add Chat Components

Required files:
- `frontend/src/components/chat/ChatbotIcon.tsx`
- `frontend/src/components/chat/ChatModal.tsx`
- `frontend/src/components/chat/ChatMessages.tsx`
- `frontend/src/components/chat/ChatInput.tsx`

### 2.2 Add to Layout

```tsx
// frontend/src/app/layout.tsx or dashboard layout
import { ChatbotIcon } from '@/components/chat/ChatbotIcon';

export default function Layout({ children }) {
  return (
    <div>
      {children}
      <ChatbotIcon />
    </div>
  );
}
```

### 2.3 Verify Frontend

```bash
cd frontend
npm run dev

# Open http://localhost:3000
# Floating chat icon should appear bottom-right
```

---

## Step 3: Test Chat Flow

### 3.1 Login and Open Chat

1. Login with existing account
2. Click floating chat icon (bottom-right)
3. Chat modal should open

### 3.2 Test Basic Commands

| Command | Expected Response |
|---------|-------------------|
| "hello" | Warm greeting in detected language |
| "add task buy milk" | Confirmation: "Task 'buy milk' add ho gaya!" |
| "show my tasks" | List of user's tasks |
| "complete task 1" | Confirmation: "Task complete ho gaya!" |

### 3.3 Test Roman Urdu

| Command | Expected Response |
|---------|-------------------|
| "mujhe grocery leni hai" | Roman Urdu confirmation |
| "mere kitne tasks hain?" | Count in Roman Urdu |
| "task 2 delete karo" | Confirmation request in Roman Urdu |

---

## Step 4: Deploy

### 4.1 Backend (Railway)

```bash
# Commit changes
git add .
git commit -m "Add AI chatbot feature"
git push origin 004-ai-chatbot-integration

# Railway auto-deploys from main
# Or manually trigger deploy in dashboard
```

### 4.2 Frontend (Vercel)

```bash
# Push triggers auto-deploy
git push origin 004-ai-chatbot-integration

# Verify deployment
# Check Vercel dashboard for build status
```

### 4.3 Production Test

```bash
# Test production endpoint
curl https://in-memory-python-todo-cli-app-production.up.railway.app/api/chat \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "hello"}'
```

---

## Troubleshooting

### "Cohere API Error"

- Verify COHERE_API_KEY is set in Railway
- Check API key is valid at https://dashboard.cohere.ai
- Check rate limits not exceeded

### "Chat Not Responding"

- Check browser console for errors
- Verify JWT token is valid (not expired)
- Check network tab for API response

### "Tasks Not Showing"

- Verify user has existing tasks
- Check user_id matches between auth and database
- Test list_tasks skill directly

### "Modal Not Opening"

- Check ChatbotIcon is rendered in layout
- Verify Tailwind classes are compiled
- Check z-index conflicts with other elements

---

## Quick Verification Checklist

- [ ] Cohere API key added to Railway
- [ ] Database tables created (conversations, messages)
- [ ] Chat endpoint responds (POST /api/chat)
- [ ] Floating icon visible on all pages
- [ ] Modal opens on icon click
- [ ] Messages sent and received
- [ ] Task operations work via chat
- [ ] Roman Urdu responses work

---

**Setup Complete!** Your AI chatbot should now be functional.

For detailed implementation, see `plan.md`.
