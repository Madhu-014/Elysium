# Elysium (Green AI Middleware)

Elysium is an API middleware that optimizes prompts before they reach LLM providers. It focuses on reducing token volume while keeping intent quality acceptable, and reports sustainability metrics per request.

## Mission framing: problem, approach, long-term impact

- What we are trying to solve:
  - AI applications send too many redundant tokens, which increases latency, model cost, and inference energy use.
- How we are solving it:
  - Elysium sits between clients and model providers, then applies tokenizer checks, deduplication, relevance filtering, and prompt compression before model inference.
- Long-run impact:
  - Per-request token savings compound into large annual reductions in GPU utilization, infrastructure spend, and estimated carbon emissions.

## 1) High-level explanation

### Value proposition

- Reduce LLM costs and latency by trimming unnecessary prompt content.
- Provide transparent estimates of energy and CO2 savings from token reduction.
- Offer a single optimization endpoint that can sit in front of OpenAI, Anthropic, local models, or custom inference stacks.

### Why this can reduce emissions

1. Fewer tokens means fewer forward-pass operations in transformer inference.
2. Lower operations reduce GPU time/energy consumed.
3. Lower energy consumption multiplied by grid intensity yields lower carbon emissions.

This is an estimate model, not direct metering. Treat the metrics as directional and disclose assumptions.

## 2) Architecture

### Text diagram (production flow)

```text
Client App (Web/Mobile/Backend)
  -> Elysium API (FastAPI)
      -> Auth + Rate Limits
      -> Optimization Pipeline
          1. Tokenizer
          2. Deduplicator
          3. Relevance Filter
          4. Compressor (rule-based, optional LLM-based)
      -> Sustainability Estimator
      -> Usage Metrics Store
  -> Upstream LLM Provider (OpenAI/Anthropic/Ollama)
  -> Response to Client
```

### Full stack plan

```text
Frontend: Next.js (Vercel)
Backend: FastAPI (Render or Railway free tier)
Metrics: Postgres (Supabase free tier) or SQLite (starter)
Queue (optional): Upstash Redis or Render background worker
Model fallback: Ollama on Mac M2 for local optimization/compression
```

### Request data flow

1. Client calls `POST /optimize` with prompt + mode.
2. API verifies `X-API-Key` only when auth enforcement is enabled.
3. Pipeline transforms prompt by stage.
4. API computes token delta + sustainability estimates.
5. Result is returned and usage totals are updated.
6. Client can query `GET /usage` for aggregate impact.

### Scalability considerations

- Stateless API instances for horizontal scaling.
- Move usage stats to Postgres for multi-instance consistency.
- Add Redis caching for repeated prompts and embedding lookups.
- Add async queue for expensive LLM-based compression.
- Add provider adapters and retry/circuit-breaker policy.

## 3) Step-by-step implementation

### Step A - Backend (already scaffolded)

Project path:

- `backend/app/main.py`
- `backend/app/api/routes.py`
- `backend/app/services/*.py`

Implemented endpoints:

- `GET /health`
- `POST /optimize`
- `GET /usage`

Implemented modules:

- `tokenizer.py`
- `deduplicator.py`
- `relevance.py`
- `compressor.py`
- `carbon.py`
- `usage_store.py`

### Step B - Run locally on Mac M2

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000
```

Test:

```bash
curl -X GET http://127.0.0.1:8000/health

curl -X POST http://127.0.0.1:8000/optimize \
  -H "Content-Type: application/json" \
  -d '{"prompt":"Please please summarize this text. Please summarize this text clearly.","mode":"eco"}'

curl -X GET http://127.0.0.1:8000/usage
```

Auth mode:

- Local/default: `REQUIRE_API_KEY=false` so no key is required.
- Production: set `REQUIRE_API_KEY=true` and configure `ELYSIUM_API_KEYS`.

### Step C - Frontend (Next.js on Vercel)

Use this minimal component structure:

```text
frontend/
  app/
    page.tsx
  components/
    PromptForm.tsx
    ResultsPanel.tsx
```

UI fields:

- Prompt textarea
- Mode select (`eco`, `balanced`, `high_quality`)
- Optimize button
- Result cards for tokens saved, energy saved, CO2 saved

Run frontend locally:

```bash
cd frontend
npm install
npm run dev
```

Frontend env for live playground:

```bash
NEXT_PUBLIC_ELYSIUM_API_BASE_URL=http://127.0.0.1:8000
# Optional in local mode. Required only if REQUIRE_API_KEY=true in backend.
NEXT_PUBLIC_ELYSIUM_API_KEY=dev-key-123
```

### Step D - Persisted metrics (next production step)

- Replace in-memory usage store with Postgres table:
  - request_id
  - api_key_hash
  - tokens_before
  - tokens_after
  - energy_saved_kwh
  - co2_saved_g
  - created_at

## 4) Practical formulas and assumptions

Current estimation model in backend:

- Energy saved:
  - `energy_saved_kwh = (tokens_saved / 1000) * KWH_PER_1K_TOKENS`
- CO2 saved:
  - `co2_saved_g = energy_saved_kwh * GRID_CO2_G_PER_KWH`

Default assumptions in `.env.example`:

- `KWH_PER_1K_TOKENS = 0.0005`
- `GRID_CO2_G_PER_KWH = 400`

Notes for credibility:

- Publish assumptions in API docs/dashboard.
- Show uncertainty ranges (low/medium/high scenarios).
- Never claim exact measured emissions without telemetry from inference hardware/provider.
- Keep language as "estimated" savings.

## 5) API design

### Authentication

- Optional header: `X-API-Key`
- If `REQUIRE_API_KEY=true`, missing/invalid key returns `401`.

### IP rate limiting

- Rate limiting is enforced per client IP when `RATE_LIMIT_ENABLED=true`.
- Default: `RATE_LIMIT_REQUESTS_PER_MINUTE=120`.
- Exceeding limit returns `429 Too Many Requests`.

### Integration contract (what users send and receive)

Client sends to Elysium:

```http
POST /optimize
Content-Type: application/json

{
  "prompt": "Your original prompt",
  "mode": "eco"
}
```

Elysium returns:

```json
{
  "optimized_prompt": "optimized text",
  "tokens_before": 120,
  "tokens_after": 80,
  "token_reduction_pct": 33.33,
  "sustainability": {
    "energy_saved_kwh": 0.00002,
    "co2_saved_g": 0.008
  }
}
```

Then client forwards `optimized_prompt` to its target LLM provider.

### Endpoints

- `GET /health`
- `POST /optimize`
- `GET /usage`

### Request schema (`/optimize`)

```json
{
  "prompt": "string",
  "mode": "eco | balanced | high_quality",
  "max_output_tokens": 1024
}
```

### Response schema (`/optimize`)

```json
{
  "optimized_prompt": "string",
  "tokens_before": 120,
  "tokens_after": 72,
  "token_reduction_pct": 40.0,
  "sustainability": {
    "energy_saved_kwh": 0.000024,
    "co2_saved_g": 0.0096
  }
}
```

## 6) Performance and optimization

### Reduce latency

- Keep stage-1 optimization rule-based and in-process.
- Avoid calling external models for every request.
- Cache deterministic outputs by hash of `(prompt, mode)`.

### Embeddings strategy

- Compute embeddings only for long prompts or retrieval-rich cases.
- Reuse embeddings with content hash keys.
- Batch embedding calls when possible.

### Trade-offs

- More aggressive compression improves savings but risks quality loss.
- Balanced mode should preserve constraints/instructions.
- High-quality mode should favor semantic fidelity over token cuts.

## 7) Product features roadmap

### Dashboard

- Total requests
- Total tokens saved
- Total energy saved (kWh)
- Total CO2 reduced (g)
- Savings by mode and by API key/project

### Developer experience

- API keys and quotas
- SDKs (TypeScript/Python)
- Webhooks for monthly impact reports

### Advanced features

- Query-aware summarization
- Token budget optimizer by target model context window
- Multi-model routing (best quality-per-kWh profile)
- "Stripe for LLMs" middleware with billing + governance + sustainability controls

## 8) Deployment (free stack)

### First-time deployment plan (Vercel + Render, free)

This path is no-cost on starter/free tiers and is beginner-friendly.

### A. Prerequisites

1. Push this repository to GitHub.
2. Ensure local checks pass before first deploy:
  - Backend tests: `cd backend && .venv/bin/python -m pytest -q`
  - Frontend build: `cd frontend && npm run build`

### B. Deploy backend on Render (free)

1. In Render, choose `New +` -> `Web Service`.
2. Connect your GitHub repo.
3. Configure service:
  - Root Directory: `backend`
  - Runtime: `Python`
  - Build Command: `pip install -r requirements.txt`
  - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Add environment variables:
  - `CORS_ALLOWED_ORIGINS` = `https://YOUR-VERCEL-DOMAIN.vercel.app`
  - `CORS_ALLOW_CREDENTIALS` = `false`
  - `REQUIRE_API_KEY` = `false` (current no-key mode)
  - `RATE_LIMIT_ENABLED` = `true`
  - `RATE_LIMIT_REQUESTS_PER_MINUTE` = `120`
  - `KWH_PER_1K_TOKENS` = `0.0005`
  - `GRID_CO2_G_PER_KWH` = `400`
  - `ENABLE_LLM_COMPRESSION` = `false`
5. Deploy and copy backend URL (for example: `https://elysium-api.onrender.com`).
6. Verify backend:
  - `GET /health` returns `{"status":"ok"...}`.

### C. Deploy frontend on Vercel (free)

1. In Vercel, `Add New Project` and import this repository.
2. Configure:
  - Framework: `Next.js`
  - Root Directory: `frontend`
3. Add environment variables:
  - `NEXT_PUBLIC_ELYSIUM_API_BASE_URL` = your Render URL
  - `NEXT_PUBLIC_ELYSIUM_API_KEY` = leave empty in current no-key mode
4. Deploy.
5. After Vercel gives your domain, set Render `CORS_ALLOWED_ORIGINS` to that exact domain and redeploy backend.

### D. Post-deploy verification checklist

1. Open Vercel app URL.
2. In Playground, test `eco`, `balanced`, and `high_quality`.
3. Confirm optimized output and token/sustainability metrics update.
4. Check browser console has no CORS errors.
5. Confirm backend `GET /usage` works.

### E. Optional hardening (after launch)

1. Enable API keys in production:
  - `REQUIRE_API_KEY=true`
  - Set `ELYSIUM_API_KEYS` on Render
  - Set matching `NEXT_PUBLIC_ELYSIUM_API_KEY` on Vercel
2. Adjust `RATE_LIMIT_REQUESTS_PER_MINUTE` to match expected traffic.
3. Add a free cron ping to reduce cold-start delay on free tier.

## 9) Best practices

- Keep optimization pipeline modular and test each stage independently.
- Add golden test prompts to detect quality regressions.
- Track both token savings and downstream answer quality metrics.
- Version assumptions and formulas in config.
- Add per-project quotas and abuse protection.

## 10) Common mistakes to avoid

- Over-compressing and deleting critical instructions.
- Reporting sustainability as exact measurements.
- Storing usage in memory only in production.
- No tracing/monitoring for optimization side effects.
- Ignoring mode-specific quality expectations.
