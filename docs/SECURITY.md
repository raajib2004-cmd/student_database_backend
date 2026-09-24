# Security Model

This document describes the security practices used in the Student Database Backend.

---

## 1. Secrets Management

All sensitive values live in a `.env` file that is **never committed to Git**.

### What lives in `.env`

| Variable | Purpose |
|---|---|
| `DATABASE_URL` | MariaDB connection string (contains DB username and password) |
| `GEMINI_API_KEY` | Google Gemini API key for LLM and embeddings |
| `APP_NAME` | Display name (non-sensitive) |
| `DEBUG` | Debug flag (non-sensitive) |

### How `.env` is protected

- `.env` is listed in `.gitignore` (verified with `git check-ignore .env`)
- `.env.example` (a safe template) is committed — it contains only placeholders
- The Git history has been scanned for the API key pattern — no matches found

### What to do if a secret leaks

1. **Rotate the key immediately** — generate a new one on the provider's dashboard
2. Delete the old key from the provider
3. Update `.env` locally with the new key
4. If the leak is in a Git commit, rewrite history (e.g., `git filter-repo`) and force-push

---

## 2. Database Security

- The database connection string is read from `DATABASE_URL` (env var) — never hardcoded
- SQLAlchemy uses parameterized queries (no SQL injection risk)
- The chatbot only reads; it cannot issue arbitrary SQL
- The database runs on `localhost` for development

---

## 3. Chatbot Safety

### The no-hallucination guarantee

The system prompt instructs Gemini:

> "NEVER invent or guess student names, IDs, CGPAs, departments, or any other data."

Every fact in a chatbot reply comes from a real tool call. If a tool returns no data, the chatbot says "no matching students found" — it does not fabricate.

### Sensitive field protection

The system prompt includes:

> "Do NOT return emails, phone numbers, or full addresses unless the user explicitly asks for them."

This prevents incidental leakage of PII in casual answers.

---

## 4. API Security

### Validation

All incoming requests pass through Pydantic schemas. Invalid requests return **422** before reaching any database or LLM code.

### Error handling

Errors are returned as JSON with a clear `detail` message. Stack traces are never exposed to clients.

---

## 5. Production TODOs

This is a **development prototype**. For production deployment, add:

- Authentication (OAuth2 / JWT)
- Authorization (role-based access)
- HTTPS via reverse proxy
- Rate limiting on `/chat`
- Secrets manager (AWS / GCP / Vault)
- Audit logging
- PII encryption at rest
- CORS policy

---

## 6. Verification Commands

```bash
# Confirm .env is not tracked
git check-ignore .env

# Confirm no secret files are tracked
git ls-files | grep -E "\.env$|\.venv|chroma_data"


Save with **Ctrl+S**.

---

## Step C: Run the verification commands

Run these **one at a time** and paste each output.

### C1
```powershell
git check-ignore .env