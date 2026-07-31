# AI Voice Appointment Booking Agent

A generalized, white-label demo product: an AI voice agent (VAPI) that books appointments, plus a real-time business dashboard.

## Monorepo Structure

```
├── client/              # React + TypeScript (Vite) + TailwindCSS
├── server/              # Node.js + Express + TypeScript + MongoDB
├── packages/types/      # Shared DTOs and interfaces
└── AI-Voice-Booking-Agent-TechSpec.md
```

## Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | React, TypeScript, Vite, TailwindCSS |
| Backend | Node.js, Express, TypeScript, Mongoose |
| Database | MongoDB |
| Voice AI | VAPI |
| Auth | JWT |
| Realtime | Socket.io |
| Export | csv-writer, pdfkit |

## Prerequisites

- Node.js 18+
- MongoDB (local or Atlas)

## Setup

1. Install dependencies from the repo root:

   ```bash
   npm install
   ```

2. Copy the server environment template and fill in values:

   ```bash
   cp server/.env.example server/.env
   ```

3. Start both apps in development:

   ```bash
   npm run dev
   ```

   - Client: http://localhost:5173
   - Server: http://localhost:5000

4. Seed demo data (Bella Salon):

   ```bash
   npm run seed
   ```

   Demo login: `demo@bellasalon.com` / `demo1234`

## VAPI Setup (auto-provisioned)

When `VAPI_API_KEY` and `VAPI_SERVER_URL` are set in `server/.env`, the app **creates and updates the VAPI assistant automatically** via the VAPI API — no manual dashboard copy-paste.

### 1. Add to `server/.env`

```env
VAPI_API_KEY=your-private-key-from-dashboard.vapi.ai
VAPI_WEBHOOK_SECRET=your-webhook-secret
VAPI_SERVER_URL=https://your-ngrok-url.ngrok-free.app
```

`VAPI_SERVER_URL` must be a **public HTTPS URL** (use ngrok while developing locally).

### 2. Start server + tunnel

```bash
npm run dev
ngrok http 5000
```

Copy the ngrok HTTPS URL into `VAPI_SERVER_URL`, then restart the server or re-run seed.

### 3. Provision the assistant

Either:

```bash
npm run seed
```

Or, while logged into the dashboard, call:

```http
POST /api/business/provision-vapi
Authorization: Bearer <token>
```

Saving business settings also re-syncs the assistant (prompt, tools, services).

### 4. Assign a phone number (one manual step)

In [VAPI Dashboard](https://dashboard.vapi.ai) → **Phone Numbers** → assign your number to the auto-created assistant (`Bella Salon Booking Agent`). The assistant ID is stored on the business record and printed by the seed script.

### What gets created automatically

- **4 standalone tools** in VAPI → **Tools** (global library), each pointing at your `/api/vapi/*` webhooks
- **Assistant** with those tools attached via `toolIds` (visible on the assistant **Tools** tab)
- System prompt, voice, transcriber, and `metadata.businessId`

## Scripts

| Command | Description |
|---------|-------------|
| `npm run dev` | Run client and server concurrently |
| `npm run dev:server` | Run API server only |
| `npm run dev:client` | Run Vite dev server only |
| `npm run build` | Build types, server, and client |
| `npm run seed` | Seed Bella Salon demo data |

## Troubleshooting

### Vite proxy error on `/api/*`

If you see `[vite] http proxy error` when logging in, the backend is not listening on port 5000. Check the server terminal for:

- `MongoDB connected` + `Server running on http://localhost:5000` — ready to use
- `querySrv ECONNREFUSED` — MongoDB Atlas DNS lookup failed

**Fixes for MongoDB connection issues:**

1. Confirm `server/.env` exists and `MONGO_URI` is set (not the root `.env`)
2. **Use a direct `mongodb://` URI** instead of `mongodb+srv://` if you see `querySrv ECONNREFUSED` — common on Windows with some DNS providers (e.g. Cloudflare) that block SRV lookups. Copy the standard connection string from Atlas → Connect → Drivers.
3. In MongoDB Atlas → Network Access, allow your IP (or `0.0.0.0/0` for dev)
4. Restart: `npm run dev` and wait for `MongoDB connected` before logging in

The server auto-falls back from `mongodb+srv://` to a direct `mongodb://` URI when SRV DNS fails.

### Demo login not working

Run `npm run seed` first, then use `demo@bellasalon.com` / `demo1234`.

See [AI-Voice-Booking-Agent-TechSpec.md](./AI-Voice-Booking-Agent-TechSpec.md) for the full technical specification.
