# 🚀 Dynamic Form System - Quick Guide

## 📊 What It Does
- ✅ Create forms from JSON schemas
- ✅ Dynamic field validation (text, email, number, date, dropdown)
- ✅ Store submissions in PostgreSQL
- ✅ Detect duplicates + analytics
- ✅ Cache with Redis
- ✅ Docker + Nginx + FastAPI

---

## 🏗️ Architecture Flow

```
Browser/Postman (Port 80)
        ↓
    NGINX (Reverse Proxy)
        ↓
  FastAPI (Port 8000)
    ├─ /api/forms (CRUD)
    ├─ /api/submissions (CRUD)
    └─ / (UI)
        ↓
  Validators (Pydantic)
        ↓
  Cache: Redis (1hr TTL)
        ↓
  DB: PostgreSQL
```

---

## 🚀 How to Run

### Development (Direct)
```bash
python main.py
# Opens: http://localhost:8000
```

### Production (Docker)
```bash
docker-compose up -d
# Starts: Nginx + FastAPI + PostgreSQL + Redis
# Access: http://localhost (Port 80)
```

---

## 🧪 Test with Postman/curl

### 1️⃣ Create Form
```bash
curl -X POST http://localhost/api/forms/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Contact Form",
    "description": "Test contact",
    "schema_definition": {
      "name": {"type": "string", "required": true, "minLength": 3},
      "email": {"type": "email", "required": true},
      "age": {"type": "number", "required": true, "min": 18, "max": 100},
      "gender": {"type": "dropdown", "options": ["male", "female", "other"], "required": true}
    }
  }'
```
**Response:** `{"id": 1, "name": "Contact Form", ...}`

---

### 2️⃣ Get All Forms
```bash
curl http://localhost/api/forms/
```
**Response:** Lists all forms with user_details stored

---

### 3️⃣ Submit Data (Valid)
```bash
curl -X POST http://localhost/api/submissions/?form_id=1 \
  -H "Content-Type: application/json" \
  -d '{
    "data": {
      "name": "John Doe",
      "email": "john@example.com",
      "age": 25,
      "gender": "male"
    }
  }'
```
**Response:** `{"success": true, "submission_id": 5, ...}`

---

### 4️⃣ Submit Data (Invalid - Rejected)
```bash
curl -X POST http://localhost/api/submissions/?form_id=1 \
  -H "Content-Type: application/json" \
  -d '{
    "data": {
      "name": "ab",
      "email": "invalid-email",
      "age": 200,
      "gender": "unknown"
    }
  }'
```
**Response:** `422 Unprocessable Entity`
```json
{
  "detail": [
    "name: minimum length 3",
    "email: invalid format",
    "age: must be < 100",
    "gender: invalid option"
  ]
}
```

---

### 5️⃣ Get Submissions
```bash
curl http://localhost/api/submissions/?form_id=1&limit=10&skip=0
```
**Response:** Paginated submissions + analytics

---

### 6️⃣ Get Form by ID
```bash
curl http://localhost/api/forms/1
```
**Response:** Full form with user_details

---

### 7️⃣ Update Form
```bash
curl -X PUT http://localhost/api/forms/1 \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Updated Form",
    "description": "New description"
  }'
```

---

### 8️⃣ Delete Form
```bash
curl -X DELETE http://localhost/api/forms/1
```

---

## 🐳 Docker Services Architecture

```
┌─────────────────────────────────────┐
│        NGINX (Port 80)              │ ← User hits here
│  ├─ Reverse proxy                   │
│  └─ → Forward to FastAPI:8000       │
└────────────┬────────────────────────┘
             │
┌────────────▼────────────────────────┐
│     FastAPI (Port 8000)             │ ← Business logic
│  ├─ /api/forms                      │
│  ├─ /api/submissions                │
│  ├─ Validators (Pydantic)           │
│  └─ Middleware (error, log, cache)  │
└────────────┬────────────────────────┘
             │
    ┌────────┴────────┐
    │                 │
┌───▼──────┐    ┌────▼──────┐
│ PostgreSQL│    │   Redis   │
│ (DB)     │    │ (Cache)   │
│ Port 5432│    │ Port 6379 │
└──────────┘    └───────────┘


## 📈 Performance

| Action | Time (DB) | Time (Cache) |
|--------|-----------|--------------|
| GET /forms/ | ~100ms | ~5ms ⚡ |
| POST /submissions/ | ~80ms | (always fresh) |
| GET /submissions/ | ~150ms | ~10ms ⚡ |

**Cache TTL:** 1 hour | Invalidates on POST/PUT/DELETE

---

## 🔒 Environment Variables

Set in `docker-compose.yml`:

```yaml
DATABASE_URL: postgresql://user:password@postgres:5432/formdb
REDIS_URL: redis://redis:6379
ENV: production
DEBUG: False
```

---

## ✅ Tech Stack

- **Backend:** FastAPI (Python)
- **Validation:** Pydantic
- **Database:** PostgreSQL 15
- **Cache:** Redis 7
- **Proxy:** Nginx
- **Container:** Docker + docker-compose
- **Server:** Gunicorn (production)

---


---

## 📞 API Endpoints Summary

| Method | Endpoint | Purpose |
|--------|----------|---------|
| **GET** | `/api/forms/` | List all forms |
| **POST** | `/api/forms/` | Create form |
| **GET** | `/api/forms/{id}` | Get form detail |
| **PUT** | `/api/forms/{id}` | Update form |
| **DELETE** | `/api/forms/{id}` | Delete form |
| **POST** | `/api/submissions/` | Submit data |
| **GET** | `/api/submissions/` | List submissions |

---
