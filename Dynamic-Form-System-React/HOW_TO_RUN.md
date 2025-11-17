HOW TO RUN

🚀 Quick Start (5 minutes)
Step 1: Setup
bash
cd Dynamic-Form-System-React

# Create environment file
cp .env.example .env

# npm install
cd frontend
npm install
cd ..

# Build Docker images
docker-compose build --no-cache
Step 2: Run
bash
docker-compose up -d
Step 3: Access
text
Frontend:  http://localhost/
API Docs:  http://localhost:8000/docs
API:       http://localhost:8000/api/
Health:    http://localhost:8000/health
🛑 Stop Services
bash
docker-compose down
📊 View Logs
bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f frontend
docker-compose logs -f api
docker-compose logs -f postgres
docker-compose logs -f redis
🔍 Test API
Submit form:
bash
curl -X POST http://localhost:8000/api/submissions/submit \
  -H "Content-Type: application/json" \
  -d '{
  "data": {
    "age": 30,
    "email": "test@example.com",
    "gender": "male",
    "name": "John Doe"
  }
}'
Get all submissions:
bash
curl http://localhost:8000/api/submissions/
Health check:
bash
curl http://localhost:8000/health
🐛 Troubleshooting
Frontend not loading
bash
docker-compose logs frontend
docker-compose restart frontend
API connection error
bash
docker-compose logs api
# Check if API is running
curl http://localhost:8000/health
Database connection failed
bash
docker-compose logs postgres
docker-compose restart postgres
docker-compose up -d api
Cache issues
bash
docker-compose logs redis
docker-compose restart redis
📝 Environment Variables
Located in .env:

text
DATABASE_URL=postgresql://user:password@postgres:5432/formdb
REDIS_URL=redis://redis:6379
DEBUG=False
ENV=production
REACT_APP_API_URL=http://localhost:8000
🎯 Request Flow
text
1. User opens browser
   ↓
2. http://localhost/ (NGINX)
   ↓
3. Serves React Frontend
   ↓
4. User fills & submits form
   ↓
5. Frontend validates (client-side)
   ↓
6. POST to http://localhost/api/submissions/submit
   ↓
7. NGINX routes to FastAPI (port 8000)
   ↓
8. FastAPI validates + checks email duplicate
   ↓
9. Saves to PostgreSQL
   ↓
10. Returns response
    ↓
11. Success message shown
✨ Key Features
✅ Dynamic form with email validation

✅ Duplicate detection

✅ Redis caching (1-hour TTL)

✅ Pagination

✅ Multi-stage Docker build

✅ Health checks

✅ NGINX reverse proxy

📦 Docker Services
bash
# View running containers
docker ps

# Enter container shell
docker exec -it form_api bash
docker exec -it form_postgres bash

# View resource usage
docker stats
🔄 Development Workflow
bash
# Make code changes
# ... edit files ...

# Rebuild services
docker-compose build

# Restart affected services
docker-compose up -d
💾 Database Access
bash
# Connect to PostgreSQL
docker exec -it form_postgres psql -U user -d formdb

# Inside psql:
\dt                    # List tables
SELECT * FROM form_submission;
\q                     # Exit
🎓 Next Steps
Open http://localhost/ in browser

Fill and submit the form

Check submissions list

Review API docs at http://localhost:8000/docs

Monitor logs: docker-compose logs -f

❓ Need Help?
Check logs for errors:

bash
docker-compose logs [service-name]
Or restart all services:

bash
docker-compose down
docker-compose up -d