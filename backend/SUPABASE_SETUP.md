# Supabase Setup Guide

## Prerequisites

- Supabase account (or Supabase CLI)
- Node.js 18+ and Python 3.11+

## Option 1: Supabase CLI (Recommended)

```bash
# Install Supabase CLI
npm install -g supabase

# Initialize Supabase project
cd backend
supabase init

# Start local Supabase
supabase start

# Note the connection details and service key from the output
```

## Option 2: Remote Supabase

1. Go to [supabase.com](https://supabase.com) and create a new project
2. Get your Project URL and `anon`/`service_role` keys from Settings > API

## Database Setup

After Supabase is running, execute the schema:

```bash
# Using Supabase CLI
supabase db reset

# Or run schema.sql in Supabase SQL Editor
# Copy the contents of backend/schema.sql and paste into the editor
```

## Environment Configuration

1. Copy `.env.example` to `.env`:
   ```bash
   cd backend
   copy .env.example .env
   ```

2. Update `.env` with your Supabase credentials:
   ```
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_SERVICE_KEY=your-service-role-key
   ENV=development
   DEBUG=true
   ```

## Running the Application

### Backend
```bash
cd backend
pip install -r requirements.txt
python -m app
# Server runs at http://localhost:8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
# Frontend runs at http://localhost:5173
```

## Testing

```bash
cd backend
python -m pytest tests/ -v
```

## Database Schema

The `schema.sql` file creates two tables:
- `app_settings` — Stores PIN hash and KDF salt (single user)
- `notes` — Stores encrypted notes (ciphertext + IV per field)

Both tables have Row Level Security enabled. Access is only via the backend service key.

## Security Notes

- Never commit `.env` to version control
- Never expose the `SUPABASE_SERVICE_KEY` in the frontend
- The service key is used server-side only via `app/db.py`
- Row Level Security ensures data is only accessible through the backend