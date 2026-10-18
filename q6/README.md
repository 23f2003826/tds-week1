# Question 6: Multi-Layer Configuration Service

A production-ready **FastAPI** microservice that merges configuration settings across five hierarchical layers—from baseline hardcoded defaults up to dynamic query-parameter overrides—enforcing strict type coercion, alias mapping, secret masking, and permissive CORS.

---

## 🏗️ Architecture & Precedence Ladder

Configuration values are resolved in order from **lowest to highest precedence**:

```
[Layer 1: Defaults] (Hardcoded baseline)
       ↓
[Layer 2: YAML] (config.<env>.yaml)
       ↓
[Layer 3: .env File] (Environment file)
       ↓
[Layer 4: OS Env Vars] (APP_* prefixed variables)
       ↓
[Layer 5: CLI Overrides] (?set=key=value query parameters)  ⭐ HIGHEST PRECEDENCE
```

Any key defined at a higher layer overrides the same key from all lower layers.

---

## 📋 Assigned Layer Values

| Layer | Source | Assigned Values | Notes |
| :--- | :--- | :--- | :--- |
| **1. Defaults** | Hardcoded | `port: 8000`<br>`workers: 1`<br>`debug: false`<br>`log_level: info`<br>`api_key: default-secret-000` | Baseline fallback |
| **2. YAML** | `config.development.yaml` | `port: 8489`<br>`workers: 12`<br>`debug: true` | Overrides Layer 1 |
| **3. .env** | `.env` file | `APP_DEBUG=true`<br>`APP_API_KEY=key-a0wigr7om6` | Injected securely via Render Secret Files |
| **4. OS Env** | `os.environ` (`APP_*`) | `APP_PORT=8144`<br>`APP_WORKERS=11` | Strips `APP_` prefix, highest file precedence |
| **5. Overrides** | `?set=key=value` | Fresh dynamic overrides from the grader | Evaluated at request time |

---

## ⚙️ Special Rules & Specifications

1. **Type Coercion**:
   * `port`, `workers` $\to$ `int` (e.g. `"9000"` $\to$ `9000`)
   * `debug` $\to$ `bool` (`true`, `1`, `yes`, `on` case-insensitive $\to$ `True`; all others $\to$ `False`)
   * `log_level` and all extra keys $\to$ `str`

2. **Alias Resolution**:
   * `NUM_WORKERS` in `.env` (or via `set=NUM_WORKERS=...`) automatically resolves to the `workers` key.

3. **Secret Masking**:
   * `api_key` **must always appear as `"****"`** in the response. The real secret is never exposed, even if overridden via query parameters.

4. **CORS Support**:
   * Configured with `CORSMiddleware` (`allow_origins=["*"]`) so the browser-based assignment grader can send cross-origin requests directly.

---

## 📡 API Endpoint

### `GET /effective-config`

#### Query Parameters:
* `set`: *(Optional, repeatable)* One or more key-value overrides in the format `key=value`.

#### Example Requests:

**1. Baseline Request (No overrides):**
```bash
curl -X GET "https://<your-service>/effective-config"
```
**Response (200 OK):**
```json
{
  "port": 8144,
  "workers": 11,
  "debug": true,
  "log_level": "info",
  "api_key": "****"
}
```

**2. With Dynamic CLI Overrides:**
```bash
curl -X GET "https://<your-service>/effective-config?set=port=9000&set=debug=false"
```
**Response (200 OK):**
```json
{
  "port": 9000,
  "workers": 11,
  "debug": false,
  "log_level": "info",
  "api_key": "****"
}
```

**3. With Worker Alias Override:**
```bash
curl -X GET "https://<your-service>/effective-config?set=NUM_WORKERS=50"
```
**Response (200 OK):**
```json
{
  "port": 8144,
  "workers": 50,
  "debug": true,
  "log_level": "info",
  "api_key": "****"
}
```

---

## 🧪 Local Development & Testing

### Run Locally:
```bash
./run.sh
```
*Or manually:*
```bash
APP_PORT=8144 APP_WORKERS=11 uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Run Automated Unit Tests:
```bash
python test_service.py
```
Verifies layer precedence, type coercion, alias resolution, secret masking, and CORS preflight headers.

---

## 📂 File Structure

```text
q6/
├── README.md                  # This documentation
├── main.py                    # Core FastAPI service with layer merging logic
├── config.development.yaml    # Layer 2 YAML configuration
├── .env                       # Layer 3 .env file (kept out of Git for security)
├── requirements.txt           # Python dependencies
├── Procfile                   # Cloud process definition for PaaS deployment
├── Dockerfile                 # Optional container build definition
├── run.sh                     # Local startup script with assigned OS env vars
└── test_service.py            # Comprehensive test suite
```

