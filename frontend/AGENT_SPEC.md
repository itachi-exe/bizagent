# BizAgent — Frontend Design

> **Status:** Design only. No implementation.
> **Part of:** BizAgent system (see also biz-backend.md, biz-ai-agent.md)

---

## AGENT BUILD PROMPT

```
You are building the FRONTEND ONLY for BizAgent.

Your scope is strictly:
  - /frontend directory (Vite + React + TypeScript project)
  - Landing page (/)
  - Owner dashboard (/dashboard) — including Knowledge Gaps panel
  - Bot settings page (/settings/bot)
  - Upload database page (/settings/upload)
  - All styles, components, and assets for these four pages

Your contract with the backend:
  - Dashboard stats:         GET  /api/dashboard/summary
  - Live activity stream:    GET  /api/dashboard/activity  (SSE)
  - Orders list:             GET  /api/dashboard/orders
  - Conversations list:      GET  /api/dashboard/conversations
  - Business brain:          GET  /api/dashboard/brain
  - Escalations:             GET  /api/dashboard/escalations
  - Knowledge gaps:          GET  /api/dashboard/knowledge-gaps
  - Resolve gap:             PATCH /api/dashboard/knowledge-gaps/{id}
  - Bot settings read:       GET  /api/settings/bot
  - Bot settings write:      PATCH /api/settings/bot
  - Upload database:         POST /api/upload/database  (multipart)
  - Confirm upload:          POST /api/upload/confirm

Assume the backend is already running at http://localhost:8000.
Do NOT build any backend code, any API routes, any database logic, or any Baileys/WhatsApp code.
Do NOT create server files, Python files, or SQL files.

Read this entire file before writing a single line of code.
Follow the layouts exactly as drawn. Follow the visual language exactly as specified.
Use the background image at /assets/bizagent-bg.jpg for the landing page hero.

PERFORMANCE: Every page must feel instant. No loading spinners longer than 200ms.
Skeleton screens while data loads. SSE feed must render new events in under 100ms.
No blocking renders. Lazy load anything below the fold.

TIME CONSTRAINT: You have 1 hour. Prioritize working over perfect.
Get all four pages rendering with real data first. Polish second.
If something is taking too long, ship a simpler version and move on.

When you are done with all four pages and they are visually complete and connected,
stop. Do not add extra pages, extra features, or extra routes.
```

---

## Tech Stack

| Layer | Choice | Reason |
|---|---|---|
| Framework | **Vite + React 18 + TypeScript** | Fast build, no SSR overhead needed, full control |
| Styling | **Tailwind CSS v3** | Utility-first, dark theme trivial, no imposed design |
| Routing | **React Router v6** | Lightweight, three routes only |
| Data fetching | **SWR** | Simple, handles polling and revalidation cleanly |
| SSE (live feed) | **Native browser `EventSource`** | No library needed, built into browsers |
| Animations | **Framer Motion** | Subtle feed entry animations only |
| Icons | **Lucide React** | Clean, consistent, tree-shakeable |
| No UI component library | | TitanGate look requires full custom control |

**Dev setup:**
```bash
npm create vite@latest frontend -- --template react-ts
cd frontend
npm install tailwindcss postcss autoprefixer react-router-dom swr framer-motion lucide-react
npx tailwindcss init -p
```

**Tailwind config (dark base):**
```js
// tailwind.config.js
module.exports = {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        bg:        '#0a0a0a',
        surface:   '#141414',
        border:    'rgba(255,255,255,0.06)',
        green:     '#25D366',
        red:       '#ff4444',
        blue:      '#4d9fff',
        primary:   '#f5f5f5',
        secondary: '#888888',
      },
      fontFamily: {
        sans: ['Inter', 'DM Sans', 'system-ui', 'sans-serif'],
      },
    },
  },
}
```

**Directory structure:**
```
frontend/
├── public/
│   └── assets/
│       └── bizagent-bg.jpg
├── src/
│   ├── main.tsx
│   ├── App.tsx                  Routes
│   ├── pages/
│   │   ├── Landing.tsx
│   │   ├── Dashboard.tsx
│   │   ├── BotSettings.tsx
│   │   └── UploadDatabase.tsx
│   ├── components/
│   │   ├── Navbar.tsx
│   │   ├── StatTile.tsx
│   │   ├── ActivityFeed.tsx       SSE consumer
│   │   ├── BrainPanel.tsx
│   │   ├── KnowledgeGapsPanel.tsx SSE-aware gaps list
│   │   ├── UploadZone.tsx         Drag-and-drop + review table
│   │   ├── WhatsAppPreview.tsx    Client-side mock only
│   │   └── ToneSelector.tsx
│   ├── hooks/
│   │   useActivityStream.ts     EventSource hook
│   └── api/
│       └── client.ts            fetch wrappers for all endpoints
```

---

## Design References

**Website Inspiration:** https://titangatequity.com

**Background Image:** `bizagent-bg.jpg` (cherry blossom street scene — used as hero/page background)

---

## What Gets Built

Three surfaces:

1. **Marketing / Landing Page** — public-facing, explains what BizAgent is, leads to a "Request Access" CTA.
2. **Owner Dashboard** — private, real-time view of agent activity, plus Knowledge Gaps panel.
3. **Bot Settings Page** — private, where the owner customizes their agent's name, personality, greeting, and tone.
4. **Upload Database Page** — private, drag-and-drop file upload with review and confirm step.

No customer-facing UI. The customer interface is WhatsApp.

---

## 1. Landing Page

### Purpose
Communicate what BizAgent is in under 10 seconds. One screen, one CTA. Judges land here during the demo.

### Layout

```
┌──────────────────────────────────────────────────────────┐
│  BIZAGENT                              [Request Access]   │
├──────────────────────────────────────────────────────────┤
│                                                          │
│         [Background: bizagent-bg.jpg]                    │
│                                                          │
│                                                          │
│         Your business already runs on WhatsApp.          │
│         Now your AI can run there too.                   │
│                                                          │
│         [Request Access]                                 │
│                                                          │
│                                                          │
├──────────────────────────────────────────────────────────┤
│  Not a chatbot. An AI employee.                          │
│                                                          │
│  Quotes prices    Creates orders    Escalates to humans  │
│  from real stock  in real DB        when it should       │
├──────────────────────────────────────────────────────────┤
│  [Dashboard preview screenshot / mockup]                 │
├──────────────────────────────────────────────────────────┤
│  © 2026 BizAgent                                         │
└──────────────────────────────────────────────────────────┘
```

### Visual Language (from TitanGate inspo)

- **Background:** `bizagent-bg.jpg` — full-bleed, fixed or parallax. Dark overlay at 40–55% opacity so text reads clean.
- **Color palette:**
  - Background: near-black `#0a0a0a` or pulled from the image dark tones
  - Primary accent: WhatsApp green `#25D366` — used sparingly (CTA button, active indicators only)
  - Text: `#f5f5f5` (primary), `#888` (secondary/labels)
  - Borders: `rgba(255,255,255,0.08)` — subtle, not heavy
- **Typography:**
  - Headline: large, round sans-serif (Inter, DM Sans, or Geist). Weight 300–400. Generous letter-spacing.
  - Labels: small-caps, tracked out, `0.15em` letter-spacing. Like TitanGate's section labels.
  - Body: 16–18px, comfortable line-height (1.6).
- **Buttons:** outline style by default. Filled only for primary CTA. No rounded pill shapes — slightly rounded rectangle (`border-radius: 4px`).
- **Spacing:** breathe. TitanGate's biggest move is whitespace. Don't fill every inch.
- **No gradients.** No glassmorphism. No blur effects. Clean edges.

### Copy

**Headline:** "Your business already runs on WhatsApp. Now your AI can run there too."

**Sub:** "BizAgent is an AI employee that knows your products, enforces your policies, and creates real orders — directly in WhatsApp."

**CTA:** "Request Access"

**Three pillars (below fold):**
- "Quotes real prices" — pulls from your live inventory, never guesses
- "Creates actual orders" — writes to your database, not just says so
- "Knows its limits" — escalates to a human when it should

---

## 2. Owner Dashboard

### Purpose
Live view of what the agent is doing. Read-only for MVP. Business owner watches the AI work in real time.

### Layout

```
┌──────────────────────────────────────────────────────────────────┐
│  BIZAGENT          Macaney Sustainable Solutions           🟢 Live│
├────────────┬─────────────┬───────────────┬───────────────────────┤
│ Convos     │ Orders      │ Escalations   │ Leads                 │
│ Today: 12  │ Today: 4    │ Open: 2       │ Today: 8              │
├────────────┴─────────────┴───────────────┴───────────────────────┤
│ Live Activity                                                     │
│ ─────────────────────────────────────────────────────────────    │
│ 14:32  🟢 Order #1024 created · 10x Beehive · NGN 350,000        │
│ 14:28  🔴 Escalation · Kunle requested 30% discount              │
│ 14:15  🔵 Quote Q-0043 sent · 5x Protective Suit · NGN 90,000    │
│ 14:02  ⚪ New conversation · Amaka Obi                            │
│ 13:55  🟢 Order #1023 created · 2x Smoker · NGN 17,000           │
├──────────────────────────────────────────────────────────────────┤
│ Business Brain                                                    │
│ ─────────────────────────────────────────────────────────────    │
│ Products (4)                    Services (2)                     │
│ ✅ Langstroth Beehive  ₦35,000  ✅ Beginner Training  ₦25,000   │
│ ✅ Protective Suit     ₦18,000  ✅ Advanced Course    ₦45,000   │
│ ✅ Bee Smoker          ₦8,500                                    │
│ ✅ Bee Feed (5kg)      ₦4,500                                    │
│                                                                  │
│ Policies ✅   Permissions ✅   Discount ceiling: 10%             │
└──────────────────────────────────────────────────────────────────┘
```

### Dashboard Visual Language

Darker than the landing page. This is a working tool, not a marketing surface.

- **Background:** `#0d0d0d`
- **Cards/panels:** `#141414` with `1px border rgba(255,255,255,0.06)`
- **Accent green** `#25D366` for positive events (order created, active status)
- **Accent red** `#ff4444` for escalations and flags
- **Accent blue** `#4d9fff` for neutral events (quotes, conversations)
- **Live indicator:** pulsing green dot next to "Live" label when SSE is connected
- **Activity feed:** monospaced timestamp, then event type dot, then description. No cards per event — a clean log.
- **Stat tiles:** four across the top. Large number, small label below. Border separates them from the feed.

### Stat Tiles

| Tile | Value | Label |
|---|---|---|
| Conversations | count | Today |
| Orders | count + NGN total | Today |
| Escalations | count | Open (unresolved) |
| Leads | count | Today (new customers) |

### Activity Feed

Each row:
```
[HH:MM]  [dot color]  [event summary one line]
```

Event dot colors:
- 🟢 Green: `order_created`, `quote_created`
- 🔴 Red: `escalation_created`
- 🔵 Blue: `conversation_started`, `message_received`
- ⚪ White: system events

Feed streams live via SSE. New events prepend to the top. Max 50 rows shown; older rows drop off.

### Business Brain Panel

Bottom section. Static snapshot, polled every 30s.

- Products listed as: `[name] · ₦[price]`
- Services same format
- Policy status: green checkmark if loaded, red X if missing
- Permissions: discount ceiling shown as a number

### SSE Event Format (consumed by dashboard)

```json
{
  "type": "order_created",
  "timestamp": "2026-09-08T14:32:00Z",
  "summary": "Order #1024 created — 10x Langstroth Beehive — NGN 350,000",
  "data": {
    "order_number": 1024,
    "customer_name": "Kunle Adeyemi",
    "total_ngn": 350000
  }
}
```

Event types: `order_created`, `quote_created`, `escalation_created`, `message_received`, `conversation_started`

---

## 3. Tech Stack (Frontend)

**Option A (recommended for hackathon speed):** Server-rendered Jinja2 templates + HTMX for live updates. FastAPI serves everything. No separate frontend build step. SSE handled natively by browser `EventSource`. Bot settings form submits via HTMX `hx-patch`.

**Option B (if team has React comfort):** React SPA. Vite build. SSE via `EventSource` in a `useEffect`. `fetch` for settings save.

For a 4-hour build: Option A. Ship faster, same result.

---

## 4. Pages Summary

| Page | Route | Auth | Notes |
|---|---|---|---|
| Landing | `/` | Public | Marketing, CTA |
| Dashboard | `/dashboard` | None (hackathon) | Owner live view + knowledge gaps |
| Bot Settings | `/settings/bot` | None (hackathon) | Agent customization |
| Upload Database | `/settings/upload` | None (hackathon) | File upload + review + confirm |

No login screen for MVP. Dashboard and settings URLs are shared verbally with judges.

---

## 5. Bot Settings Page

### Purpose

The owner configures their agent's identity here. Changes take effect immediately on the next customer message — no restart needed.

### Layout

```
┌──────────────────────────────────────────────────────────────────┐
│  BIZAGENT          Macaney Sustainable Solutions                  │
│  [Dashboard]  [Bot Settings]                                     │
├──────────────────────────────────────────────────────────────────┤
│  Bot Identity                                                     │
│  ─────────────────────────────────────────────────────────────   │
│                                                                  │
│  Bot Name                                                        │
│  ┌──────────────────────────────────────────────┐               │
│  │  Zara                                        │  max 40 chars │
│  └──────────────────────────────────────────────┘               │
│  This is the name your bot uses when greeting customers.         │
│                                                                  │
│  Personality                                                     │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Warm and knowledgeable about beekeeping. You speak to   │   │
│  │  customers like a helpful friend who happens to know     │   │
│  │  everything about bees. You use light emojis             │   │
│  │  occasionally. You always greet customers by name.       │   │
│  └──────────────────────────────────────────────────────────┘   │
│  Describe your bot's character. max 500 chars.                   │
│                                                                  │
│  Greeting Message                                                │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Hi there! 🐝 I'm Zara from Macaney. How can I help      │   │
│  │  you today?                                              │   │
│  └──────────────────────────────────────────────────────────┘   │
│  Sent automatically when a new customer messages you.            │
│  Leave empty to skip the greeting. max 300 chars.               │
│                                                                  │
│  Tone                                                            │
│  ● Friendly   ○ Professional   ○ Casual   ○ Formal              │
│                                                                  │
├──────────────────────────────────────────────────────────────────┤
│  Preview                                                         │
│  ─────────────────────────────────────────────────────────────   │
│                                                                  │
│  ┌────────────────────────────────────────────────────────┐     │
│  │  Zara · Macaney Sustainable Solutions                   │     │
│  │  ─────────────────────────────────────────────────     │     │
│  │                                                         │     │
│  │  Hi there! 🐝 I'm Zara from Macaney. How can I         │     │
│  │  help you today?                          [10:00 ✓✓]   │     │
│  │                                                         │     │
│  │  Hi I need 10 beehives how much  [10:01]               │     │
│  │                                                         │     │
│  │  We have 42 beehives available at NGN 35,000           │     │
│  │  each. 10 units = NGN 350,000 before delivery.         │     │
│  │  Would you like me to prepare an order? [10:01 ✓✓]     │     │
│  └────────────────────────────────────────────────────────┘     │
│                                                                  │
│                                  [Save Changes]                  │
└──────────────────────────────────────────────────────────────────┘
```

### Behavior

- **Live preview panel** on the right (or below on narrow screens). Shows a mock WhatsApp conversation using the current name, greeting, and tone. Updates as the owner types — no save needed to see the preview.
- **Save Changes** button calls `PATCH /api/settings/bot`. On success: brief "Saved" confirmation inline, no page reload.
- **Validation inline:** character count shown under each field. Goes red when approaching limit.
- **Tone selector:** four radio pills. Selecting one immediately updates the preview tone description in the preview panel.
- **Empty greeting:** if the owner clears the greeting field and saves, no greeting is sent to new customers.

### Preview Panel Logic

The preview is purely cosmetic — generated client-side from the current form values. It shows:
1. The greeting message (if set) as the first bubble, sent by the bot
2. A hardcoded "Hi I need 10 beehives how much" as a customer message
3. A hardcoded bot reply that uses the current `agent_name` in the wording

No API call for the preview. It is a visual mock, not a live agent call.

### API Integration

```
On page load:
  GET /api/settings/bot
  → Populate form fields with current values

On save:
  PATCH /api/settings/bot
  → Body: { agent_name, agent_personality, agent_greeting, agent_language_style }
  → Success: show "Saved ✓" for 2 seconds, stay on page
  → Error: show inline error, do not clear form
```

---

## 6. Tech Stack (Frontend)

Desktop-first. The demo runs on a laptop. Mobile responsiveness is post-MVP.

Minimum supported width: 1024px.

---

## 9. Security

### 9.1 No Sensitive Data in the Frontend
- The frontend never handles API keys, database credentials, or Baileys session files.
- The only secrets-adjacent value it touches is the OpenAI key — which it never sees. All LLM calls happen server-side.
- Do not store any business data in `localStorage` or `sessionStorage`. All state lives in React memory and is fetched fresh on page load.

### 9.2 API Communication
- All API calls go to `http://localhost:8000` (or a configured base URL). Never hardcode IPs or credentials in frontend source.
- CORS is handled by the backend. The frontend does not need to do anything special — just call the endpoints.
- If an API call returns a non-2xx response, show a generic error message to the user. Do not display the raw error body — it may contain server internals.

### 9.3 File Upload Safety
- The upload zone must validate file type client-side before sending: `.csv`, `.xlsx`, `.pdf`, `.docx` only.
- Show a clear error if an unsupported file type is dropped: "Only CSV, XLSX, PDF, and DOCX files are supported."
- Cap displayed file size to 10MB client-side with an inline error before uploading. Do not let the user wait for a server rejection on an obviously oversized file.
- Never preview file contents in the browser (no `FileReader` rendering of PDF/DOCX). Just show filename and size.

### 9.4 SSE Stream Safety
- The SSE `EventSource` connects to `/api/dashboard/activity`. Data arriving over this stream is JSON from the backend — treat it as trusted.
- Parse every SSE event with a try-catch. If the JSON is malformed, log it to the console and skip rendering. Do not crash the feed.
- If the SSE connection drops, `EventSource` reconnects automatically. No custom reconnect logic needed.

### 9.5 Content Display
- All text rendered from the API (customer names, message content, product names, knowledge gap questions) must be rendered as text, not as HTML. Use React's default text rendering — never `dangerouslySetInnerHTML`.
- This prevents any stored XSS from API-sourced content.

### 9.6 Bot Settings Form
- The personality and greeting fields accept free text from the owner. Render the preview exactly as typed — do not interpret it as HTML.
- Character limits enforced client-side (`maxLength` attributes) and validated server-side (backend rejects over-length values with 422). Both are needed.


---

## 7. Upload Database Page

### Purpose

Owner uploads a CSV, XLSX, PDF, or DOCX file. The system extracts products, services, and policies. Owner reviews the extracted data, edits if needed, then confirms to save it to the Business Brain.

### Route

`/settings/upload`

### Layout

```
┌──────────────────────────────────────────────────────────────────┐
│  BIZAGENT          Macaney Sustainable Solutions                  │
│  [Dashboard]  [Bot Settings]  [Upload Database]                  │
├──────────────────────────────────────────────────────────────────┤
│  Upload Business Data                                            │
│  ─────────────────────────────────────────────────────────────   │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                                                          │   │
│  │         Drag and drop your file here                     │   │
│  │         or click to browse                               │   │
│  │                                                          │   │
│  │         Supported: CSV, XLSX, PDF, DOCX                  │   │
│  │                                                          │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
│  [AFTER UPLOAD — REVIEW STEP]                                    │
│                                                                  │
│  ✅ macaney_products.csv uploaded                                │
│                                                                  │
│  Products found (4)                                              │
│  ──────────────────────────────────────────────────────────      │
│  Name                    Price (NGN)    Stock    [remove]        │
│  Langstroth Beehive      35,000         42       [×]            │
│  Protective Suit         18,000         28       [×]            │
│  Bee Smoker              8,500          60       [×]            │
│  Bee Feed (5kg)          4,500          120      [×]            │
│                                          [+ Add row]            │
│                                                                  │
│  Policies found                                                  │
│  ──────────────────────────────────────────────────────────      │
│  Delivery:  Delivery within Abuja: NGN 2,000 flat...            │
│             [edit inline]                                        │
│  Returns:   Unused items returnable within 7 days...            │
│             [edit inline]                                        │
│                                                                  │
│                     [Discard]     [Confirm and Save]            │
└──────────────────────────────────────────────────────────────────┘
```

### Behavior

- **Drag-and-drop zone:** Accepts file via drag or click. Shows filename and size on selection.
- **Upload on drop/select:** Immediately calls `POST /api/upload/database`. Shows a spinner while extracting.
- **Review step:** After extraction, the drag zone is replaced by the review table. No page navigation.
- **Editable cells:** Product name, price, stock are all editable inline in the table.
- **Add row:** Adds a blank row the owner can fill in manually (for items the extractor missed).
- **Remove row:** Removes a product from the extracted list before confirming.
- **Confirm and Save:** Calls `POST /api/upload/confirm` with the (possibly edited) extracted data. On success: shows "Saved — N products added to your Business Brain" and clears the form.
- **Discard:** Clears the review step, returns to the upload zone. No DB changes.
- **Error handling:** If extraction fails (bad file format, parse error): show an inline error message. Do not crash.

### API Integration

```
File selected/dropped:
  POST /api/upload/database  (multipart/form-data, field: "file")
  → Show spinner
  → On success: render review table from response.extracted
  → On error: show "Could not extract data from this file. Try a different format."

Confirm clicked:
  POST /api/upload/confirm
  → Body: { upload_id, products: [...edited...], services: [...], policies: {...} }
  → On success: show success banner, clear form
  → On error: show inline error, keep review table
```

---

## 8. Knowledge Gaps Panel (Dashboard Addition)

### Purpose

Added to the existing dashboard page as a third panel below the activity feed. Shows questions the agent couldn't answer. Owner can resolve each one with a note.

### Layout Addition (appended to dashboard below Brain panel)

```
├──────────────────────────────────────────────────────────────────┤
│  Knowledge Gaps                                      2 open      │
│  ─────────────────────────────────────────────────────────────   │
│  🟡 "Do you have beehive stands?"    product_not_found  14:05   │
│     [Mark resolved: ________________________]  [Save]           │
│                                                                  │
│  🟡 "What's your warranty policy?"  policy_missing     13:22    │
│     [Mark resolved: ________________________]  [Save]           │
└──────────────────────────────────────────────────────────────────┘
```

### Behavior

- **Yellow dot** for open gaps. Disappears when resolved.
- **Inline resolve:** Click on a gap row to expand an input. Owner types the resolution ("Added beehive stands to product list") and clicks Save.
- **Save** calls `PATCH /api/dashboard/knowledge-gaps/{id}` with `{ resolved: true, resolution: "..." }`.
- **On save:** Row fades out and disappears from the list.
- **Empty state:** "No open gaps — your agent can answer everything customers are asking."
- **SSE integration:** `knowledge_gap` events from the live feed prepend new gaps to this panel in real time. No page refresh needed.

### API Integration

```
On page load:
  GET /api/dashboard/knowledge-gaps
  → Populate gaps list

On SSE event type "knowledge_gap":
  → Prepend new gap to the list (animated entry)

On save click:
  PATCH /api/dashboard/knowledge-gaps/{id}
  → Body: { resolved: true, resolution: "..." }
  → On success: animate row out
```


## 10. Negotiation and Fulfillment UI (Dashboard Additions)

### 10.1 Pending Fulfillment Panel

Added to dashboard below the Knowledge Gaps panel. Shows orders waiting for owner delivery confirmation.

```
├──────────────────────────────────────────────────────────────────┤
│  Pending Fulfillment                             3 awaiting      │
│  ─────────────────────────────────────────────────────────────   │
│  ORD-KA-1031  Kunle · 1x Toothpaste · NGN 1,100     14:22      │
│  [/deliver ORD-KA-1031 ________________________]  [Copy]        │
│                                                                  │
│  ORD-AB-1032  Amaka · 2x Smoker · NGN 17,000         14:05      │
│  [/deliver ORD-AB-1032 ________________________]  [Copy]        │
└──────────────────────────────────────────────────────────────────┘
```

Each row shows the order ref, customer name, items, total, and time.
A pre-filled command template with a Copy button — owner pastes it into WhatsApp and adds delivery info.
When `order_confirmed` SSE event arrives for an order ref, that row fades out.

### 10.2 Business Type Selector (Settings)

Added to `/settings/bot` below the tone selector:

```
Business Type
● Retail   ○ Wholesale   ○ School   ○ Hospital   ○ Clinic
○ Events   ○ Restaurant  ○ Services ○ Real Estate ○ Logistics
```

Selecting a type shows the relevant extended brain fields below it (term dates for school, menu for restaurant, etc.). These fields call `PATCH /api/settings/brain-extended` on save.

### 10.3 New API Endpoints (Frontend Contract)

```
GET  /api/dashboard/orders/pending-fulfillment
     → Orders awaiting owner delivery confirmation

PATCH /api/settings/brain-extended
     → Body: type-specific brain fields
     → e.g. for school: { term_dates, admission_requirements, fee_structure }

GET  /api/settings/brain-extended
     → Returns current extended brain fields for the business type
```

### 10.4 Pages Table Update

| Page | Route | Notes |
|---|---|---|
| Landing | `/` | Marketing, CTA |
| Dashboard | `/dashboard` | Activity + gaps + pending fulfillment panels |
| Bot Settings | `/settings/bot` | Identity + tone + business type + extended brain |
| Upload Database | `/settings/upload` | File upload + review + confirm |
