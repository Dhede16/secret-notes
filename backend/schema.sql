-- SecretNotes Database Schema (Supabase/PostgreSQL)
-- Run this in Supabase SQL Editor or via psql

-- ============================================
-- Table: app_settings
-- Stores PIN hash and KDF salt for the single user
-- ============================================
create table app_settings (
  id uuid primary key default gen_random_uuid(),
  pin_hash text not null,
  kdf_salt text not null,
  idle_timeout_sec int not null default 180,
  created_at timestamptz default now()
);

-- ============================================
-- Table: notes
-- All note titles and bodies are stored as ciphertext
-- ============================================
create table notes (
  id uuid primary key default gen_random_uuid(),
  title_ciphertext text not null,
  title_iv text not null,
  body_ciphertext text not null,
  body_iv text not null,
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

-- ============================================
-- Row Level Security
-- Only the backend service key can access data
-- ============================================
alter table app_settings enable row level security;
alter table notes enable row level security;

-- No public policies — access only via service key
-- (Backend uses SUPABASE_SERVICE_KEY from .env)

-- ============================================
-- Indexes for performance
-- ============================================
create index idx_notes_updated_at on notes(updated_at desc);