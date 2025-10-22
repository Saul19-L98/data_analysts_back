Here are **clear, production-minded user stories (with acceptance criteria and API contracts)** to guide your agent in building the backend that:

1. accepts a file **and** a free-text message,
2. parses the spreadsheet into a pandas `DataFrame`,
3. extracts **schema + dtypes + summary stats** (`describe()` + `info()`), and
4. sends that compact context to an **AWS Bedrock Agent** using a **valid `InvokeAgent` request**.

I’ve grounded key details with sources for **Bedrock `InvokeAgent`** (request fields, streaming, sessions), **FastAPI file uploads**, and **pandas `describe()` / `info()` capture**. ([AWS Documentation][1])

---

# 📓 Epic: Upload → Analyze with pandas → Send to Bedrock Agent

Great update. Here’s a clean, **markdown** add-on to your instruction set that (1) introduces a `.env` for AWS creds/region and (2) makes **`AGENT_ID`** and **`ALIAS_ID`** **request-supplied** (never hardcoded).

---

# 🔒 Environment & Credentials + Request-Scoped Agent IDs

## 1) `.env` for AWS configuration

Create a `.env` at the repo root (and **git-ignore it**) to hold **only** runtime configuration your backend needs to call Bedrock:

```
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=XXXXXXXXXXXXXXXXXXXX
AWS_SECRET_ACCESS_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
# (optional)
AWS_SESSION_TOKEN=IQoJb3JpZ2luX2VjE...
```

* The AWS SDKs (including **boto3**) will pick these up automatically via the **default credential provider chain**; environment variables are the first lookup, so no extra code is required. ([AWS Documentation][1])
* **Never commit `.env`** (add it to `.gitignore`)—it contains secrets that vary per environment. Prefer short-lived credentials (STS) over long-lived keys. ([Stack Overflow][2])
* If you later deploy to AWS, prefer **IAM roles** on the compute platform over static keys; env vars are fine for local dev but roles are the best practice in production. (AWS docs describe the same provider chain behavior across SDKs.) ([AWS Documentation][3])

> FastAPI note: to receive **file + form fields** you’ll use `UploadFile` + `Form` and install `python-multipart`. ([FastAPI][4])

---

## 2) Request supplies Bedrock `AGENT_ID` and `ALIAS_ID`

Do **not** bake Agent IDs into config. The frontend includes them in the request so the backend can call Bedrock **dynamically**.

### Request shape (multipart)

```
POST /api/v1/ingest
Content-Type: multipart/form-data

- file: (csv/xlsx)   REQUIRED
- message: string    OPTIONAL
- agent_id: string   REQUIRED
- alias_id: string   REQUIRED
```

### Validation rules

* Reject if `agent_id` or `alias_id` is missing (`422`).
* Enforce file type/size limits (CSV/XLSX only; e.g., ≤25 MB). ([FastAPI][4])

### Bedrock call

Use **Agents Runtime** `InvokeAgent` with **`agentId`**, **`agentAliasId`**, **`sessionId`**, and **`inputText`** (your composed prompt that includes the pandas profile + the user message). Reuse the same `sessionId` to keep conversation state. ([AWS Documentation][5])

---

## Story A — Load AWS config from `.env`

**As** a backend service
**I want** to read `AWS_REGION`, `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` (and optional `AWS_SESSION_TOKEN`) from environment
**So that** boto3 can authenticate without hardcoded secrets.

**Acceptance**

* Variables exist in `.env` and are loaded at process start (e.g., via `pydantic-settings` or `python-dotenv` in dev).
* No code passes credentials to the frontend or logs them.
* AWS SDK picks them up (default provider chain) and calls succeed. ([AWS Documentation][1])

---

## Story B — Frontend provides `agent_id` and `alias_id`

**As** an API consumer
**I want** to specify which Bedrock Agent + Alias to use per request
**So that** the backend can route analysis to the correct agent version.

**Acceptance**

* `agent_id` and `alias_id` are required multipart fields.
* Backend forwards them to `InvokeAgent` unchanged and uses a generated `sessionId`.
* If Bedrock returns errors (e.g., `ValidationException`, `ThrottlingException`), backend maps them to the appropriate HTTP status with actionable messages. ([AWS Documentation][5])

---

## Story 1 — Upload a spreadsheet and context message

**As** an API consumer
**I want** to `POST` a spreadsheet file **and** a text message
**So that** the backend can parse data and use my context when calling the LLM.

### Acceptance Criteria

* **Endpoint**: `POST /api/v1/ingest` (multipart/form-data).
* **Parts**:

  * `file`: required, accepts `text/csv`, `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet` (xlsx).
  * `message`: optional string; defaults to `""` if not provided.
* **Size limits**: reject payloads > configured max (e.g., 25 MB).
* **Responses**:

  * `201 Created` with JSON: `{ "session_id": "...", "columns": [...], "dtypes": {...}, "summary": { ... }, "sent_to_agent": true }`
  * `415` for unsupported media type.
  * `422` for missing `file`.
* **Notes**:

  * Use FastAPI `UploadFile` for efficient streaming & metadata. ([FastAPI][2])

### API Contract (request)

```
POST /api/v1/ingest
Content-Type: multipart/form-data; boundary=...

--boundary
Content-Disposition: form-data; name="file"; filename="data.xlsx"
Content-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet

(binary)
--boundary
Content-Disposition: form-data; name="message"

"This dataset contains store-level daily sales for Q3..."
--boundary--
```

### API Contract (response – success)

```json
{
  "session_id": "sess_2025_10_21T15_45_00Z_abc123",
  "columns": ["date", "store_id", "sales", "category"],
  "dtypes": {"date":"datetime64[ns]","store_id":"int64","sales":"float64","category":"object"},
  "summary": {
    "describe_numeric": { "...": "..." },
    "describe_non_numeric": { "...": "..." },
    "info_text": "class DataFrame...\nColumns (4 entries)..."
  },
  "sent_to_agent": true
}
```

---

## Story 2 — Parse spreadsheet into pandas DataFrame

**As** a backend engineer
**I want** robust parsing for CSV/XLSX
**So that** the `DataFrame` is created consistently and safely.

### Acceptance Criteria

* Detect format by extension or MIME; use:

  * `pd.read_csv(...)` for CSV, and
  * `pd.read_excel(...)` for XLSX. ([Pandas][3])
* Support `sheet_name` parameter defaulting to the first sheet for XLSX.
* Trim BOM, normalize headers (`strip()`, collapse spaces), and preserve original header names in a separate map if mutated.
* On parse error: return `400` with a concise cause.

---

## Story 3 — Extract schema, dtypes, and statistical summary

**As** a data analyst
**I want** the backend to derive **column names**, **data types**, and **summary stats**
**So that** the LLM receives a compact but informative dataset profile.

### Acceptance Criteria

* **Columns**: `df.columns.tolist()`
* **Dtypes**: `{col: str(dtype) for col, dtype in df.dtypes.items()}`
* **Summary**:

  * Numeric summary via `df.describe(include=[np.number]).to_dict()` (or `.to_json()`).
  * Non-numeric summary via `df.describe(include=['object']).to_dict()` (when present). ([Pandas][4])
  * **Info text** captured via `io.StringIO()` + `df.info(buf=buffer)`; return `buffer.getvalue()` in response. ([Pandas][5])
* Handle empty frames or all-non-numeric gracefully (return empty blocks instead of failing).

---

## Story 4 — Compose Bedrock Agent request (valid `InvokeAgent`)

**As** the integration layer
**I want** to send the user’s **message** + computed **schema summary** to the Bedrock Agent
**So that** the agent can reason with both user intent and data profile.

### Acceptance Criteria

* **Invoke API**: call **Agents for Amazon Bedrock Runtime** `InvokeAgent`.

  * Required **URI params**: `agentId`, `agentAliasId`, `sessionId`.
  * Body may include: `inputText`, `enableTrace`, `sessionState`, etc. ([AWS Documentation][1])
* **Sessioning**: reuse the same `sessionId` for conversational continuity. ([AWS Documentation][1])
* **Prompt shape** (example):

  ```
  inputText = (
    "User message:\n{message}\n\n"
    "Data columns:\n{columns}\n\n"
    "Dtypes:\n{dtypes}\n\n"
    "df.describe():\n{describe_numeric}\n\n"
    "Non-numeric describe:\n{describe_non_numeric}\n\n"
    "df.info():\n{info_text}\n"
    "Task: Analyze potential insights, anomalies, and quality issues. "
    "Ask clarifying questions if context seems insufficient."
  )
  ```
* **Python (boto3) shape** (non-streaming or streaming supported). Use the **bedrock-agent-runtime** client and pass the documented fields. ([Boto3][6])

**Sample (pseudocode, aligned to docs):**

```python
from boto3.session import Session

br = Session().client("bedrock-agent-runtime", region_name="us-east-1")

resp = br.invoke_agent(
    agentId=AGENT_ID,
    agentAliasId=AGENT_ALIAS_ID,
    sessionId=session_id,          # reuse for continuity
    inputText=prompt_text,          # ignored if you use returnControl in sessionState
    enableTrace=False               # toggle if you want trace
)
# If streaming is enabled, iterate event stream per docs; otherwise parse 'chunk' text. 
```

(Fields and behaviors per AWS API reference & examples.) ([AWS Documentation][1])

---

## Story 5 — Return both the local summary and the Agent’s first reply

**As** an API consumer
**I want** the API to respond with the computed summary **and** the agent’s initial message
**So that** I can confirm what was sent and see the LLM reaction.

### Acceptance Criteria

* Response includes:

  * `"summary"` (same object as Story 3),
  * `"agent_reply"` (first textual chunk from Bedrock; if streaming, aggregate until final token),
  * `"session_id"`, `"agent_id"`, `"agent_alias_id"`.
* On Bedrock errors (`ValidationException`, `ThrottlingException`, etc.), surface mapped HTTP errors with actionable messages. ([AWS Documentation][1])

---

## Story 6 — Security & limits

**As** a security engineer
**I want** safe file handling and predictable resource usage
**So that** the system is resilient and compliant.

### Acceptance Criteria

* Accept only CSV/XLSX content types; block other types with `415`.
* Enforce file size limit (e.g., via ASGI server and application-level checks).
* Use FastAPI `UploadFile` (spooled to disk for large files) to avoid loading entire file in memory. ([FastAPI][2])
* Sanitize filenames; do **not** write to permanent storage by default.
* Add timeout/circuit-breaker for Bedrock requests; retry on transient 5xx per SDK guidance.
* Log request IDs and `sessionId`, never log raw data.

---

## Story 7 — Observability & DX

**As** a developer
**I want** good logs and minimal friction
**So that** I can debug quickly and iterate.

### Acceptance Criteria

* Log: start/end of parse, column count, row count (not sample values).
* If parsing fails, include pandas parser error message in a safe way.
* Feature flags for: streaming vs. non-streaming Bedrock responses. ([AWS Documentation][7])

---

# 🔌 Endpoint Sketch (MVC-friendly controller–service split)

**Controller (`/controllers/v1/ingest.py`)**

* Validate multipart (`file`, `message`).
* Call `IngestService.handle_upload(file, message, session_id)`.

**Service (`/services/ingest_service.py`)**

* Detect file type → `pd.read_csv` / `pd.read_excel`. ([Pandas][3])
* Build `columns`, `dtypes`.
* `describe()` summaries (numeric & object). ([Pandas][4])
* Capture `df.info()` via `io.StringIO` buffer. ([Pandas][5])
* Compose `inputText` prompt and call `bedrock-agent-runtime.invoke_agent(...)`. ([AWS Documentation][1])
* Return combined payload.

**Repository**

* Not required unless you persist uploads/summaries.

---

# 🧪 Acceptance Tests (Given/When/Then)

### AT-1: CSV Happy Path

**Given** a valid CSV (≤10 MB) and message `"Analyze Q3 sales"`
**When** `POST /api/v1/ingest` with both parts
**Then** `201` and JSON contains:

* `columns` (length ≥ 1)
* `dtypes` (keys match `columns`)
* `summary.describe_numeric` or `summary.describe_non_numeric` present
* `summary.info_text` contains `"class 'pandas.core.frame.DataFrame'"`
* `agent_reply` is a non-empty string

### AT-2: XLSX Happy Path (first sheet)

**Given** a valid `.xlsx` file and no message
**When** `POST /api/v1/ingest`
**Then** backend uses `read_excel` default sheet, returns `201` with same guarantees. ([Pandas][8])

### AT-3: Unsupported Type

**Given** a `.pdf` upload
**When** `POST /api/v1/ingest`
**Then** `415` with `{"detail":"Unsupported media type: application/pdf"}`

### AT-4: Bedrock Error Surface

**Given** a valid file but Bedrock returns `ThrottlingException`
**When** the controller receives the exception
**Then** return `429` with a concise message and include retry hint. (See documented errors.) ([AWS Documentation][1])

### AT-5: Large File Rejection

**Given** a 200 MB file
**When** `POST /api/v1/ingest`
**Then** `413` Payload Too Large

---

# 🧱 API/SDK Notes your agent should follow

* **FastAPI file uploads**: prefer `UploadFile` for large files; it uses a spooled file object and async interface. ([FastAPI][2])
* **pandas**:

  * `describe()` provides numeric stats; object stats differ (count, unique, top, freq). ([Pandas][4])
  * Capture `info()` to a string using `buf=io.StringIO()` and `getvalue()`. ([Pandas][5])
* **Bedrock Agent invocation**:

  * Use **`InvokeAgent`** (Agents Runtime) with `agentId`, `agentAliasId`, `sessionId`, `inputText`.
  * If you include **`sessionState.returnControlInvocationResults`**, `inputText` is ignored (be aware).
  * Streaming is available to lower first-byte latency; otherwise parse the single `chunk`. ([AWS Documentation][1])
  * Python SDK client name: `bedrock-agent-runtime`; method: `invoke_agent`. ([Boto3][6])

---

# 🔐 Minimal Prompt Template (what the service sends to the Agent)

> **System context (you control in Agent configuration)**:
> “You are a data assistant. When given a dataset profile and a short user message, produce insights, data quality checks, and questions to clarify the task.”

> **`inputText` (sent by the backend)**:

```
User message:
{message}

Dataset profile:
- Columns: {columns}
- Dtypes: {dtypes}

Numeric describe():
{describe_numeric}

Non-numeric describe():
{describe_non_numeric}

df.info():
{info_text}

Task:
1) Summarize relevant insights.
2) Identify potential data quality issues.
3) Ask at most 3 precise follow-up questions to clarify goals.
```

(Delivered via `InvokeAgent` with the required URI parameters and a consistent `sessionId`.) ([AWS Documentation][1])

---

## 🔎 Sources

* **Agents for Amazon Bedrock – `InvokeAgent` API** (URI params, request body, streaming, errors). ([AWS Documentation][1])
* **Invoke an Agent (user guide – streaming & usage)**. ([AWS Documentation][7])
* **Boto3 client for Bedrock Agents Runtime (`invoke_agent`)**. ([Boto3][6])
* **FastAPI file uploads (`UploadFile`)**. ([FastAPI][2])
* **pandas `describe()`** and **`info(buf=io.StringIO())` capture**. ([Pandas][4])
* **pandas I/O readers**: `read_csv`, `read_excel`. ([Pandas][3])

---

[1]: https://docs.aws.amazon.com/bedrock/latest/APIReference/API_agent-runtime_InvokeAgent.html "InvokeAgent - Amazon Bedrock"
[2]: https://fastapi.tiangolo.com/tutorial/request-files/?utm_source=chatgpt.com "Request Files"
[3]: https://pandas.pydata.org/docs/reference/api/pandas.read_csv.html?utm_source=chatgpt.com "pandas.read_csv — pandas 2.3.3 documentation - PyData |"
[4]: https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.describe.html?utm_source=chatgpt.com "pandas.DataFrame.describe — pandas 2.3.3 documentation"
[5]: https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.info.html?utm_source=chatgpt.com "pandas.DataFrame.info — pandas 2.3.3 documentation"
[6]: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/bedrock-agent-runtime/client/invoke_agent.html?utm_source=chatgpt.com "invoke_agent - Boto3 1.40.55 documentation - AWS"
[7]: https://docs.aws.amazon.com/bedrock/latest/userguide/agents-invoke-agent.html?utm_source=chatgpt.com "Invoke an agent from your application - Amazon Bedrock"
[8]: https://pandas.pydata.org/docs/reference/api/pandas.read_excel.html?utm_source=chatgpt.com "pandas.read_excel — pandas 2.3.3 documentation - PyData |"
