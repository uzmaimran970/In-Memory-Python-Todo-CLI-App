# Deploy Backend to Railway - ONE STEP

## You must run this ONE command first (opens browser):
```bash
railway login
```
This will open your browser to authenticate with GitHub. Click "Authorize" and come back.

## After you login, run this:
```bash
cd /mnt/c/Users/pc/Desktop/todo_hackathon2/backend && railway init && railway up
```

## That's it! Railway will give you the deployment URL.

---

## Alternative: Use Railway Web UI (No CLI needed)

1. Go to: https://railway.app/new
2. Click "Deploy from GitHub repo"
3. Select: `uzmaimran970/In-Memory-Python-Todo-CLI-App`
4. Click the deployed service → Settings → Root Directory: `backend`
5. Go to Variables tab, add:
   - DATABASE_URL = `postgresql://neondb_owner:npg_fjZJF8XEs5dv@ep-patient-king-a1eko8at-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require`
   - BETTER_AUTH_SECRET = `9eb4ea939ffbae7e084c9432d41fe55921f786164ba326c7a2070cf75fca58c6`
6. Settings → Generate Domain
7. Done! Your URL will be shown.

This takes 2 minutes.
