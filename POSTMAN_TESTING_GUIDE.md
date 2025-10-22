# 📮 Testing Data Analyst Backend with Postman

Complete guide for testing the FastAPI backend using Postman.

---

## 🚀 Prerequisites

1. **Server Running**: Make sure the backend is running on `http://localhost:8000`
   ```bash
   uv run uvicorn app.main:app --reload
   ```

2. **Sample Data**: Use the provided `sample_data.csv` or create your own CSV/XLSX file

3. **AWS Bedrock Credentials**: You need:
   - `AGENT_ID` - Your AWS Bedrock Agent ID (e.g., `ABCDEFGHIJ`)
   - `AGENT_ALIAS_ID` - Your AWS Bedrock Alias ID (e.g., `TSTALIASID`)

---

## 📋 Quick Start Guide

### Step 1: Create a New Request

1. Open **Postman**
2. Click **"New"** → **"HTTP Request"**
3. Name it: `Ingest Data - Data Analyst`
4. Save to a collection (optional but recommended)

### Step 2: Configure Request Method & URL

- **Method**: `POST`
- **URL**: `http://localhost:8000/api/v1/ingest`

### Step 3: Configure Request Body

1. Click the **"Body"** tab (below the URL bar)
2. Select **"form-data"** radio button (⚠️ NOT "raw" or "x-www-form-urlencoded")
3. Add the following fields:

| KEY | TYPE | VALUE | REQUIRED |
|-----|------|-------|----------|
| `file` | **File** | [Select your CSV/XLSX file] | ✅ Yes |
| `message` | Text | `"Analyze Q3 sales trends and identify anomalies"` | ⚪ Optional |
| `agent_id` | Text | `YOUR_BEDROCK_AGENT_ID` | ✅ Yes |
| `agent_alias_id` | Text | `YOUR_BEDROCK_ALIAS_ID` | ✅ Yes |

#### How to Add the File Field:

1. In the KEY column, type: `file`
2. In the TYPE dropdown (next to the value), select **"File"** (not "Text")
3. Click **"Select Files"** button that appears
4. Navigate to and select `sample_data.csv` or your own CSV/XLSX file

#### How to Add Text Fields:

1. Click "Add new field" or press Enter on the last row
2. Type the KEY name (e.g., `message`)
3. Make sure TYPE is set to **"Text"**
4. Enter the VALUE

### Step 4: Send the Request

1. Click the blue **"Send"** button
2. Check the response in the lower panel

---

## ✅ Expected Success Response

**Status Code**: `200 OK`

**Response Body** (JSON):

```json
{
  "message": "Archivo analizado con éxito",
  "session_id": "sess_2025_10_21T20_45_30Z_a1b2c3",
  "columns": [
    "date",
    "store_id",
    "sales",
    "category",
    "units_sold"
  ],
  "dtypes": {
    "date": "object",
    "store_id": "int64",
    "sales": "float64",
    "category": "object",
    "units_sold": "int64"
  },
  "summary": {
    "describe_numeric": {
      "store_id": {
        "count": 15.0,
        "mean": 102.0,
        "std": 0.816,
        "min": 101.0,
        "25%": 101.0,
        "50%": 102.0,
        "75%": 103.0,
        "max": 103.0
      },
      "sales": {
        "count": 15.0,
        "mean": 1758.18,
        "std": 850.45,
        "min": 450.0,
        "25%": 1200.0,
        "50%": 1750.0,
        "75%": 2300.0,
        "max": 3200.0
      },
      "units_sold": {
        "count": 15.0,
        "mean": 33.8,
        "std": 18.92,
        "min": 8.0,
        "25%": 22.0,
        "50%": 35.0,
        "75%": 45.0,
        "max": 58.0
      }
    },
    "describe_non_numeric": {
      "date": {
        "count": 15,
        "unique": 5,
        "top": "2024-01-01",
        "freq": 3
      },
      "category": {
        "count": 15,
        "unique": 3,
        "top": "Food",
        "freq": 5
      }
    },
    "info_text": "<class 'pandas.core.frame.DataFrame'>\\nRangeIndex: 15 entries, 0 to 14..."
  },
  "agent_reply": {
    "version": "1.0",
    "context": {
      "dataset_name": null,
      "row_count": 15,
      "column_count": 5,
      "columns": [
        {
          "name": "date",
          "dtype": "object",
          "role": "datetime"
        },
        {
          "name": "store_id",
          "dtype": "int64",
          "role": "categorical"
        },
        {
          "name": "sales",
          "dtype": "float64",
          "role": "numeric"
        }
      ],
      "quality_notes": [
        "Date column is stored as object type - requires conversion to datetime"
      ]
    },
    "insights": [
      {
        "title": "Preliminary Sales Overview",
        "summary": "Average daily sales are 1758.33 with 31.8 units sold per transaction",
        "method_hint": "Descriptive statistics from sample data",
        "evidence_columns": ["sales", "units_sold"]
      }
    ],
    "suggested_charts": [
      {
        "title": "Q3 2024 Sales Trend",
        "chart_type": "line",
        "parameters": {
          "x_axis": "date",
          "y_axis": "sales",
          "aggregations": [{"column": "sales", "func": "sum"}]
        },
        "insight": "Will show sales fluctuations during Q3 to identify trends/anomalies",
        "priority": "high"
      }
    ],
    "next_actions": [
      {
        "type": "REQUEST_CHART_DATA",
        "action_group": "AnalyticsAPI",
        "operation": "get-chart-data"
      }
    ],
    "errors": []
  },
  "sent_to_agent": true
}
```

---

## 🧪 Test Scenarios

### Test 1: Health Check

**Purpose**: Verify the server is running

**Request**:
- Method: `GET`
- URL: `http://localhost:8000/health`
- Body: None

**Expected Response** (200 OK):
```json
{
  "status": "healthy",
  "service": "Data Analyst Backend"
}
```

---

### Test 2: Successful Upload

**Purpose**: Test complete workflow with valid data

**Request**:
- Method: `POST`
- URL: `http://localhost:8000/api/v1/ingest`
- Body (form-data):
  ```
  file: sample_data.csv (File)
  message: "Analyze Q3 sales trends" (Text)
  agent_id: "YOUR_AGENT_ID" (Text)
  agent_alias_id: "YOUR_ALIAS_ID" (Text)
  ```

**Expected Response**: `200 OK` with success message (see above)

---

### Test 3: Missing File (Validation Error)

**Purpose**: Test validation for missing file

**Request**:
- Method: `POST`
- URL: `http://localhost:8000/api/v1/ingest`
- Body (form-data):
  ```
  message: "Test" (Text)
  agent_id: "ABCDEFGHIJ" (Text)
  agent_alias_id: "TSTALIASID" (Text)
  ```
  ⚠️ **No file field**

**Expected Response** (422 Unprocessable Entity):
```json
{
  "detail": [
    {
      "type": "missing",
      "loc": ["body", "file"],
      "msg": "Field required",
      "input": null
    }
  ]
}
```

---

### Test 4: Missing agent_id (Validation Error)

**Purpose**: Test validation for missing agent_id

**Request**:
- Method: `POST`
- URL: `http://localhost:8000/api/v1/ingest`
- Body (form-data):
  ```
  file: sample_data.csv (File)
  message: "Test" (Text)
  agent_alias_id: "TSTALIASID" (Text)
  ```
  ⚠️ **No agent_id field**

**Expected Response** (422 Unprocessable Entity):
```json
{
  "detail": [
    {
      "type": "missing",
      "loc": ["body", "agent_id"],
      "msg": "Field required",
      "input": null
    }
  ]
}
```

---

### Test 5: Empty agent_id (Validation Error)

**Purpose**: Test validation for empty agent_id

**Request**:
- Method: `POST`
- URL: `http://localhost:8000/api/v1/ingest`
- Body (form-data):
  ```
  file: sample_data.csv (File)
  message: "Test" (Text)
  agent_id: "   " (Text - empty or whitespace)
  agent_alias_id: "TSTALIASID" (Text)
  ```

**Expected Response** (422 Unprocessable Entity):
```json
{
  "detail": "agent_id is required and cannot be empty",
  "error_type": "ValidationError"
}
```

---

### Test 6: Unsupported File Type (Media Type Error)

**Purpose**: Test validation for unsupported file types

**Request**:
- Method: `POST`
- URL: `http://localhost:8000/api/v1/ingest`
- Body (form-data):
  ```
  file: document.pdf (File - PDF file)
  message: "Test" (Text)
  agent_id: "ABCDEFGHIJ" (Text)
  agent_alias_id: "TSTALIASID" (Text)
  ```

**Expected Response** (415 Unsupported Media Type):
```json
{
  "detail": "Unsupported media type: application/pdf",
  "error_type": "UnsupportedFileTypeError"
}
```

**Supported File Types**:
- ✅ CSV: `text/csv`, `application/csv`
- ✅ Excel: `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`, `application/vnd.ms-excel`

---

### Test 7: File Too Large (Payload Size Error)

**Purpose**: Test file size validation (max 25MB by default)

**Request**:
- Method: `POST`
- URL: `http://localhost:8000/api/v1/ingest`
- Body (form-data):
  ```
  file: large_file.csv (File > 25MB)
  message: "Test" (Text)
  agent_id: "ABCDEFGHIJ" (Text)
  agent_alias_id: "TSTALIASID" (Text)
  ```

**Expected Response** (413 Payload Too Large):
```json
{
  "detail": "File size (30MB) exceeds maximum allowed (25MB)",
  "error_type": "FileSizeExceededError"
}
```

---

### Test 8: Invalid Bedrock Credentials (Gateway Error)

**Purpose**: Test AWS Bedrock error handling

**Request**:
- Method: `POST`
- URL: `http://localhost:8000/api/v1/ingest`
- Body (form-data):
  ```
  file: sample_data.csv (File)
  message: "Test" (Text)
  agent_id: "INVALID_AGENT_ID" (Text)
  agent_alias_id: "INVALID_ALIAS" (Text)
  ```

**Expected Response** (502 Bad Gateway):
```json
{
  "detail": "Bedrock invocation failed: ValidationException - Invalid agent ID",
  "error_type": "BedrockInvocationError"
}
```

---

## 📦 Import Postman Collection

Save this JSON as `DataAnalystBackend.postman_collection.json` and import into Postman:

```json
{
  "info": {
    "name": "Data Analyst Backend API",
    "description": "FastAPI backend for data analysis with AWS Bedrock",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "Health Check",
      "request": {
        "method": "GET",
        "header": [],
        "url": {
          "raw": "http://localhost:8000/health",
          "protocol": "http",
          "host": ["localhost"],
          "port": "8000",
          "path": ["health"]
        }
      },
      "response": []
    },
    {
      "name": "Ingest Data - Success",
      "request": {
        "method": "POST",
        "header": [],
        "body": {
          "mode": "formdata",
          "formdata": [
            {
              "key": "file",
              "type": "file",
              "src": "sample_data.csv",
              "description": "CSV or XLSX file to analyze"
            },
            {
              "key": "message",
              "value": "Analyze Q3 sales trends and identify anomalies",
              "type": "text",
              "description": "Optional context message"
            },
            {
              "key": "agent_id",
              "value": "{{agent_id}}",
              "type": "text",
              "description": "AWS Bedrock Agent ID"
            },
            {
              "key": "agent_alias_id",
              "value": "{{agent_alias_id}}",
              "type": "text",
              "description": "AWS Bedrock Agent Alias ID"
            }
          ]
        },
        "url": {
          "raw": "http://localhost:8000/api/v1/ingest",
          "protocol": "http",
          "host": ["localhost"],
          "port": "8000",
          "path": ["api", "v1", "ingest"]
        }
      },
      "response": []
    },
    {
      "name": "Ingest Data - Missing File",
      "request": {
        "method": "POST",
        "header": [],
        "body": {
          "mode": "formdata",
          "formdata": [
            {
              "key": "message",
              "value": "Test",
              "type": "text"
            },
            {
              "key": "agent_id",
              "value": "{{agent_id}}",
              "type": "text"
            },
            {
              "key": "agent_alias_id",
              "value": "{{agent_alias_id}}",
              "type": "text"
            }
          ]
        },
        "url": {
          "raw": "http://localhost:8000/api/v1/ingest",
          "protocol": "http",
          "host": ["localhost"],
          "port": "8000",
          "path": ["api", "v1", "ingest"]
        }
      },
      "response": []
    },
    {
      "name": "Ingest Data - Missing agent_id",
      "request": {
        "method": "POST",
        "header": [],
        "body": {
          "mode": "formdata",
          "formdata": [
            {
              "key": "file",
              "type": "file",
              "src": "sample_data.csv"
            },
            {
              "key": "message",
              "value": "Test",
              "type": "text"
            },
            {
              "key": "agent_alias_id",
              "value": "{{agent_alias_id}}",
              "type": "text"
            }
          ]
        },
        "url": {
          "raw": "http://localhost:8000/api/v1/ingest",
          "protocol": "http",
          "host": ["localhost"],
          "port": "8000",
          "path": ["api", "v1", "ingest"]
        }
      },
      "response": []
    },
    {
      "name": "Ingest Data - Empty agent_id",
      "request": {
        "method": "POST",
        "header": [],
        "body": {
          "mode": "formdata",
          "formdata": [
            {
              "key": "file",
              "type": "file",
              "src": "sample_data.csv"
            },
            {
              "key": "message",
              "value": "Test",
              "type": "text"
            },
            {
              "key": "agent_id",
              "value": "   ",
              "type": "text"
            },
            {
              "key": "agent_alias_id",
              "value": "{{agent_alias_id}}",
              "type": "text"
            }
          ]
        },
        "url": {
          "raw": "http://localhost:8000/api/v1/ingest",
          "protocol": "http",
          "host": ["localhost"],
          "port": "8000",
          "path": ["api", "v1", "ingest"]
        }
      },
      "response": []
    }
  ],
  "variable": [
    {
      "key": "agent_id",
      "value": "YOUR_BEDROCK_AGENT_ID",
      "type": "string"
    },
    {
      "key": "agent_alias_id",
      "value": "YOUR_BEDROCK_ALIAS_ID",
      "type": "string"
    }
  ]
}
```

**To Import**:
1. Open Postman
2. Click **"Import"** button (top left)
3. Drag and drop the JSON file or click "Upload Files"
4. The collection will appear in your Collections sidebar
5. Update the collection variables:
   - Right-click the collection → **"Edit"**
   - Go to **"Variables"** tab
   - Update `agent_id` and `agent_alias_id` with your actual values

---

## 🎯 Using Environment Variables (Recommended)

### Create an Environment

1. Click **"Environments"** icon (left sidebar)
2. Click **"+"** to create new environment
3. Name it: `Data Analyst - Local`
4. Add variables:

| VARIABLE | INITIAL VALUE | CURRENT VALUE |
|----------|---------------|---------------|
| `base_url` | `http://localhost:8000` | `http://localhost:8000` |
| `agent_id` | `YOUR_AGENT_ID` | `YOUR_AGENT_ID` |
| `agent_alias_id` | `YOUR_ALIAS_ID` | `YOUR_ALIAS_ID` |

5. Click **"Save"**
6. Select the environment from the dropdown (top right)

### Use Variables in Requests

In your request URL and body, use variables like this:

**URL**: `{{base_url}}/api/v1/ingest`

**Body fields**:
- `agent_id`: `{{agent_id}}`
- `agent_alias_id`: `{{agent_alias_id}}`

---

## 🔧 Troubleshooting

### Problem: "Could not send request"

**Causes**:
- Server is not running
- Wrong URL or port

**Solution**:
```bash
# Start the server
uv run uvicorn app.main:app --reload

# Check it's running
curl http://localhost:8000/health
```

---

### Problem: "422 Unprocessable Entity"

**Causes**:
- Missing required fields
- Empty or whitespace-only values

**Solution**:
- Verify all required fields are present: `file`, `agent_id`, `agent_alias_id`
- Make sure `agent_id` and `agent_alias_id` are not empty or just whitespace

---

### Problem: "415 Unsupported Media Type"

**Causes**:
- Uploading wrong file type (PDF, Word, etc.)
- File has wrong extension

**Solution**:
- Only upload CSV or XLSX files
- Check the file extension matches the content

---

### Problem: "Body type is showing as 'raw' instead of 'form-data'"

**Solution**:
1. Click **"Body"** tab
2. Select **"form-data"** radio button (not "raw", "x-www-form-urlencoded", etc.)

---

### Problem: "File field shows 'Text' type"

**Solution**:
1. Click the dropdown next to the value field
2. Select **"File"** from the dropdown
3. The "Select Files" button should appear

---

### Problem: "502 Bad Gateway - Bedrock error"

**Causes**:
- Invalid AWS credentials in `.env`
- Invalid `agent_id` or `agent_alias_id`
- AWS Bedrock service unavailable
- Network/firewall blocking AWS API calls

**Solution**:
- Verify AWS credentials in `.env` file
- Check `agent_id` and `agent_alias_id` are correct
- Test AWS connection: `aws sts get-caller-identity`
- Check AWS service status

---

## 📊 Response Status Codes Reference

| Status Code | Meaning | Cause |
|-------------|---------|-------|
| `200 OK` | Success (file analyzed) | File processed and agent responded successfully |
| `400 Bad Request` | File parsing error | Invalid CSV/XLSX format |
| `413 Payload Too Large` | File too big | File exceeds 25MB limit |
| `415 Unsupported Media Type` | Wrong file type | Must be CSV or XLSX |
| `422 Unprocessable Entity` | Validation error | Missing or invalid fields |
| `429 Too Many Requests` | Rate limited | Bedrock throttling |
| `500 Internal Server Error` | Server error | Unexpected error |
| `502 Bad Gateway` | Bedrock error | AWS Bedrock API error |

---

## 🚀 Advanced Testing

### Test with Scripts (Tests Tab)

Add this JavaScript to the **Tests** tab to automatically validate responses:

```javascript
// Test for successful upload
pm.test("Status code is 200", function () {
    pm.response.to.have.status(200);
});

pm.test("Response has success message", function () {
    var jsonData = pm.response.json();
    pm.expect(jsonData).to.have.property('message');
    pm.expect(jsonData.message).to.equal('Archivo analizado con éxito');
});

pm.test("Response has session_id", function () {
    var jsonData = pm.response.json();
    pm.expect(jsonData).to.have.property('session_id');
});

pm.test("Response has columns array", function () {
    var jsonData = pm.response.json();
    pm.expect(jsonData.columns).to.be.an('array');
    pm.expect(jsonData.columns.length).to.be.above(0);
});

pm.test("Response has agent_reply as object", function () {
    var jsonData = pm.response.json();
    pm.expect(jsonData).to.have.property('agent_reply');
    pm.expect(jsonData.agent_reply).to.be.an('object');
});

pm.test("Response time is less than 30 seconds", function () {
    pm.expect(pm.response.responseTime).to.be.below(30000);
});
```

---

## 📚 Additional Resources

- **API Documentation**: http://localhost:8000/docs (Swagger UI)
- **Alternative Docs**: http://localhost:8000/redoc (ReDoc)
- **Health Check**: http://localhost:8000/health
- **Sample Data**: `sample_data.csv` in the project root

---

## ✅ Quick Checklist

Before testing, make sure:

- [ ] Server is running (`uv run uvicorn app.main:app --reload`)
- [ ] `.env` file has valid AWS credentials
- [ ] You have your Bedrock `agent_id` and `agent_alias_id`
- [ ] Sample CSV/XLSX file is ready
- [ ] Postman is installed and updated
- [ ] Request method is set to POST
- [ ] Body type is set to **form-data** (not raw)
- [ ] File field type is set to **File** (not Text)

---

Happy Testing! 🎉

For issues or questions, check the main README or consult the API documentation at `/docs`.
