# Security Policy

## API Key Management

- **Storage**: All API keys (Cohere, Qdrant, Gemini, Admin Secret) are stored in the `.env` file on the server.
- **Exposure**: Keys are **NEVER** exposed to the client-side (browser). The frontend communicates only with our backend API.
- **Rotation**: If a key is compromised:
  1. Revoke the key in the respective provider's dashboard.
  2. Generate a new key.
  3. Update the `.env` file.
  4. Restart the backend service.

## Backend Security

- **Proxying**: The FastAPI backend acts as a secure proxy. The frontend never talks directly to vector databases or LLM providers.
- **Rate Limiting**: IP-based rate limiting is enabled by default (60 requests/minute) to prevent abuse.
- **Admin Endpoints**: The `/api/ingest` endpoint is protected by a Bearer token (`ADMIN_SECRET`). This secret must be included in the `Authorization` header.

## Frontend Security

- **Inputs**: All user inputs are treated as untrusted and passed to the backend for processing.
- **XSS**: Docusaurus and React provide built-in protection against Cross-Site Scripting (XSS).

## Database Security

- **Qdrant**: Connection is secured via API key and HTTPS.
- **Neon (Optional)**: Connection uses SSL mode (`sslmode=require`).

## Reporting Vulnerabilities

If you discover a security vulnerability, please report it to the repository maintainers immediately.
