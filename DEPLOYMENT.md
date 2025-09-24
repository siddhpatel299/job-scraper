# 🚀 Deployment Guide

## Option 1: Railway (Recommended)

### 1. Prepare for Deployment

```bash
# Make sure all dependencies are listed
pip freeze > requirements.txt

# Create a .gitignore if you don't have one
echo "venv/
__pycache__/
.env
*.pyc
.DS_Store
node_modules/
.next/" > .gitignore
```

### 2. Deploy to Railway

1. Go to [railway.app](https://railway.app)
2. Sign up with GitHub
3. Click "New Project" → "Deploy from GitHub repo"
4. Select your Job Scraper repository
5. Railway will automatically detect Python and build your app

### 3. Set Environment Variables

In Railway dashboard:
- `FLASK_ENV` = `production`
- `PORT` = `8000` (Railway will set this automatically)
- Add any API keys you use (like `SERP_API_KEY`)

### 4. Custom Start Command (if needed)

In Railway settings, set start command to:
```
python web_app.py
```

## Option 2: Split Architecture

### Frontend (Vercel)
```bash
cd next-app
npx vercel
```

### Backend (Render/Railway)
Deploy just the Python backend separately and update API endpoints in Next.js.

## Option 3: Docker (Advanced)

Create `Dockerfile`:
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["python", "web_app.py"]
```

## Environment Variables Needed

- `FLASK_ENV=production`
- `PORT` (set by hosting platform)
- `SERP_API_KEY` (if using Google Dorks)
- Any other API keys your scrapers need

## Testing Deployment

1. Your app will be available at the URL provided by Railway
2. Test the job search functionality
3. Monitor logs for any errors

## Troubleshooting

- Check Railway logs for Python errors
- Ensure all dependencies are in `requirements.txt`
- Verify environment variables are set correctly
