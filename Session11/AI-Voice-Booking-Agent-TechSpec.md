# Technical Specification: AI Voice Appointment Booking Agent (Generalized Demo)

## 1. Project Overview

**Goal:** Build a generalized, white-label-able demo product consisting of:

1. An AI voice calling agent (powered by VAPI) that handles inbound/outbound calls for appointment scheduling (salons, spas, clinics, dentists).
2. A business dashboard (MERN stack) that displays live appointments booked via the AI agent, with detailed views and CSV/PDF export.

**Purpose:** Record a polished demo video and use it as a cold-email asset to pitch "AI receptionist + automated scheduling" automation services to local service businesses.

**Positioning for outreach:** "Never miss a booking again — your AI receptionist answers every call, books appointments, and syncs everything to your dashboard in real time."

---

## 2. Tech Stack


| Layer            | Technology                                                                   |
| ---------------- | ---------------------------------------------------------------------------- |
| Frontend         | React.js + TypeScript (Vite), TailwindCSS                                    |
| Backend          | Node.js + Express.js + TypeScript                                            |
| Database         | MongoDB (Mongoose, typed schemas/models)                                     |
| Voice AI         | VAPI (Voice AI platform)                                                     |
| Auth             | JWT-based business login                                                     |
| Export           | `csv-writer` / `papaparse` (CSV), `pdfkit` or `puppeteer` (PDF)              |
| Realtime updates | Socket.io (for live dashboard updates)                                       |
| Hosting (demo)   | Frontend: Vercel; Backend: Render/Railway; DB: MongoDB Atlas                 |
| Calendar logic   | Custom slot-based availability engine (MongoDB collection)                   |
| Type sharing     | Shared `types/` package or folder for DTOs used by both frontend and backend |


---

## 3. System Architecture

```
[Caller] --(phone call)--> [VAPI Assistant]
                                |
                                | (function/tool calls via webhook)
                                v
                     [Node/Express Backend API]
                       - Availability check
                       - Slot booking
                       - Customer record creation
                       - Appointment CRUD
                                |
                                v
                         [MongoDB Atlas]
                                |
                    (Socket.io live push)
                                v
                  [React Business Dashboard]
                  - Live appointment feed
                  - Calendar view
                  - CSV/PDF export
                  - Business profile/settings (generalized config)
```

---

## 4. VAPI Voice Agent — Configuration

### 4.1 Assistant Setup

- Create one **generalized assistant template** in VAPI that can be configured per-business via dynamic variables (business name, services offered, working hours, booking rules) — passed at call-time via `assistant overrides` or `metadata`.
- Use VAPI's **Custom Functions / Tools** to connect to backend endpoints.

### 4.2 System Prompt (Template)

```
You are {{business_name}}'s virtual receptionist. Your job is to:
1. Greet the caller warmly.
2. Identify the service they want to book (from {{services_list}}).
3. Ask for preferred date/time.
4. Call check_availability tool to confirm open slots.
5. If unavailable, offer 2-3 alternative slots.
6. Collect customer name and phone number.
7. Call book_appointment tool to confirm booking.
8. Confirm appointment details back to caller and end politely.

Tone: Friendly, professional, concise. Keep responses under 2 sentences when possible.
```

### 4.3 VAPI Tools (Function Calling) → Backend Webhooks


| Tool Name            | Trigger                                           | Backend Endpoint                    | Purpose                          |
| -------------------- | ------------------------------------------------- | ----------------------------------- | -------------------------------- |
| `check_availability` | After service + date/time mentioned               | `POST /api/vapi/check-availability` | Returns available slots          |
| `book_appointment`   | After slot confirmed + customer details collected | `POST /api/vapi/book-appointment`   | Creates appointment record       |
| `cancel_appointment` | If caller wants to cancel                         | `POST /api/vapi/cancel-appointment` | Cancels existing booking         |
| `get_business_info`  | Optional, FAQ-type queries                        | `POST /api/vapi/business-info`      | Returns hours, services, pricing |


### 4.4 Webhook Payload Handling

Each VAPI tool-call webhook sends `call.id`, `assistant.metadata` (containing `businessId`), and function arguments. Backend uses `businessId` to scope all DB queries — this is what makes the agent "generalized."

---

## 5. Backend (Node/Express) — API Design

### 5.1 Folder Structure

```
/server
  tsconfig.json
  /src
    /config        -> db.ts, vapi.ts
    /models        -> Business.ts, Service.ts, Appointment.ts, Customer.ts
    /routes        -> vapiRoutes.ts, appointmentRoutes.ts, businessRoutes.ts, authRoutes.ts, exportRoutes.ts
    /controllers   -> vapiController.ts, appointmentController.ts, exportController.ts
    /middleware    -> auth.ts, errorHandler.ts
    /utils         -> slotEngine.ts, pdfGenerator.ts, csvGenerator.ts
    /sockets       -> socketHandler.ts
    /types         -> index.ts (shared interfaces, also published/copied to frontend)
    server.ts
```

> Use `interface`/`type` definitions for all models, request/response DTOs, and VAPI webhook payloads. Mongoose schemas should use `Document & I<Model>` typing (e.g., `interface IAppointment extends Document { ... }`).

### 5.2 Data Models (TypeScript Interfaces)

**Business**

```ts
interface IBusiness extends Document {
  name: string;
  email: string;
  passwordHash: string;
  phoneNumber: string;          // VAPI-assigned number
  services: IService[];
  workingHours: Record<DayOfWeek, { start: string; end: string }>;
  timezone: string;
  vapiAssistantId: string;
  createdAt: Date;
}

interface IService {
  name: string;
  durationMinutes: number;
  price: number;
}

type DayOfWeek = "mon" | "tue" | "wed" | "thu" | "fri" | "sat" | "sun";
```

**Appointment**

```ts
type AppointmentStatus = "booked" | "cancelled" | "completed" | "no-show";
type AppointmentSource = "ai-call" | "manual";

interface IAppointment extends Document {
  businessId: Types.ObjectId;
  customerName: string;
  customerPhone: string;
  service: string;
  date: string;          // ISO date (YYYY-MM-DD)
  startTime: string;      // HH:mm
  endTime: string;        // HH:mm
  status: AppointmentStatus;
  source: AppointmentSource;
  callId?: string;        // VAPI call reference
  notes?: string;
  createdAt: Date;
}
```

**Customer** (optional, for CRM-lite)

```ts
interface ICustomer extends Document {
  businessId: Types.ObjectId;
  name: string;
  phone: string;
  history: Types.ObjectId[];
  totalVisits: number;
}
```

### 5.3 Core Endpoints


| Method  | Endpoint                       | Auth                            | Description                                          |
| ------- | ------------------------------ | ------------------------------- | ---------------------------------------------------- |
| POST    | `/api/vapi/check-availability` | webhook (verify VAPI signature) | Returns open slots for given service/date            |
| POST    | `/api/vapi/book-appointment`   | webhook                         | Creates appointment, emits socket event              |
| POST    | `/api/vapi/cancel-appointment` | webhook                         | Cancels appointment                                  |
| GET     | `/api/appointments`            | JWT                             | Paginated list, filters: date range, status, service |
| GET     | `/api/appointments/:id`        | JWT                             | Single appointment detail                            |
| PATCH   | `/api/appointments/:id`        | JWT                             | Manual edit/reschedule                               |
| DELETE  | `/api/appointments/:id`        | JWT                             | Cancel/delete                                        |
| GET     | `/api/export/csv`              | JWT                             | Export filtered appointments as CSV                  |
| GET     | `/api/export/pdf`              | JWT                             | Export filtered appointments as PDF                  |
| POST    | `/api/auth/login`              | —                               | Business login                                       |
| GET/PUT | `/api/business/profile`        | JWT                             | Get/update business config (services, hours)         |


### 5.4 Slot Availability Engine (`slotEngine.ts`)

```ts
interface AvailabilityRequest {
  businessId: string;
  serviceName: string;
  date: string; // YYYY-MM-DD
}

interface AvailabilitySlot {
  startTime: string; // HH:mm
  endTime: string;
}

function getAvailableSlots(req: AvailabilityRequest): Promise<AvailabilitySlot[]>;
```

- Logic:
  1. Fetch business `workingHours` and service `durationMinutes`.
  2. Generate all possible slots for that day (e.g., 30-min increments).
  3. Subtract slots already occupied by existing appointments (with buffer if needed).
  4. Return list of available `startTime` slots.

---

## 6. Real-Time Dashboard Updates

- Use **Socket.io**: when `book-appointment` webhook creates a new record, emit `appointment:new` event to the room scoped by `businessId`.
- Dashboard subscribes on login → live list updates without refresh, plus a toast notification ("New booking via AI call: John Doe — Haircut, 3:00 PM").

---

## 7. Frontend (React + TypeScript) — Pages & Components

> All components use `.tsx`, typed props via `interface XProps`, and a shared `types/` folder (mirroring backend DTOs: `Appointment`, `Business`, `Service`, `AvailabilitySlot`, etc.) for consistency across the stack.

### 7.1 Pages


| Page                  | Route           | Description                                                                         |
| --------------------- | --------------- | ----------------------------------------------------------------------------------- |
| Login                 | `/login`        | Business auth                                                                       |
| Dashboard (Live Feed) | `/dashboard`    | Today's bookings, real-time updates, quick stats (total today, upcoming, cancelled) |
| Calendar View         | `/calendar`     | Weekly/monthly view of all appointments                                             |
| Appointments Table    | `/appointments` | Filterable/sortable table, detail drawer, export buttons                            |
| Business Settings     | `/settings`     | Configure services, working hours, assistant greeting/name (drives VAPI metadata)   |


### 7.2 Key Components

- `LiveFeedCard` — shows latest AI-booked appointments with "via AI Call" badge
- `AppointmentsTable` — pagination, status filters, search by customer
- `ExportButtons` — triggers `/api/export/csv` and `/api/export/pdf` downloads
- `CalendarGrid` — visual day/week calendar with color-coded statuses
- `StatsCards` — total bookings today, this week, cancellation rate
- `CallTranscriptModal` (optional, nice demo touch) — shows VAPI call transcript/recording link per appointment

### 7.3 CSV/PDF Export

- **CSV:** Use `papaparse` (frontend, on already-fetched data) or backend `csv-writer` for full dataset exports.
- **PDF:** Use `pdfkit` on backend to generate a formatted appointment report (business logo, date range, table of appointments) → return as downloadable blob.

---

## 8. Demo Flow (for Recording)

1. **Setup screen**: Show generalized config (e.g., "Bella Salon" — services: Haircut, Coloring, Manicure; hours 9 AM–6 PM).
2. **Live call simulation**: Call the VAPI number → AI greets as "Bella Salon" receptionist → caller books a haircut for tomorrow 2 PM.
3. **Dashboard reveal**: Switch to dashboard — new appointment appears live (Socket.io) with toast notification.
4. **Detail view**: Click appointment → shows customer name, phone, service, time, "Booked via AI Call" + optional transcript.
5. **Export demo**: Click "Export CSV" and "Export PDF" → show downloaded files with formatted data.
6. **Closing pitch overlay**: "This is what your business could have — 24/7 booking, zero missed calls, fully automated."

---

## 9. Generalization Strategy (Multi-Tenant Ready)

- All VAPI assistants share one prompt template; per-business variables (`business_name`, `services_list`, `working_hours`) injected via VAPI's assistant `overrides`/`metadata` at call start.
- `businessId` is the tenant key across DB, dashboard auth, and socket rooms.
- Onboarding a new prospect for a live pilot = create `Business` record + configure services/hours + assign/point a VAPI number to the shared assistant with that business's metadata. No code changes needed.

---

## 10. MVP Build Order (Suggested for Cursor)

1. Initialize both `/server` and `/client` as TypeScript projects (`tsconfig.json`, `ts-node`/`tsx` for dev, strict mode enabled). Create shared `types/` folder/package for cross-stack DTOs.
2. Backend: MongoDB models + Express boilerplate + auth.
3. Slot availability engine + appointment CRUD endpoints.
4. VAPI webhook endpoints (check-availability, book-appointment) + signature verification.
5. VAPI assistant config (prompt + tools) — test via VAPI dashboard test calls.
6. React dashboard: login, live feed (Socket.io), appointments table.
7. CSV/PDF export endpoints + frontend buttons.
8. Settings page for business config.
9. Seed demo data ("Bella Salon") for recording.
10. Polish UI (frontend-design pass) for demo-quality visuals.
11. Record demo video for cold email campaign.

---

## 11. Environment Variables (.env)

```
MONGO_URI=
JWT_SECRET=
VAPI_API_KEY=
VAPI_WEBHOOK_SECRET=
PORT=5000
CLIENT_URL=
```

---

## 12. Future Add-ons (Post-Demo, for Upsell)

- SMS/email confirmation + reminders (Twilio/SendGrid)
- Google Calendar two-way sync
- No-show prediction / follow-up automation
- Multi-language voice support
- Analytics: call volume, conversion rate, peak hours

