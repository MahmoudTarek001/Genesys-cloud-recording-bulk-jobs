# Genesys Cloud – Bulk Recording Jobs Automation (Python)

This project automates **Genesys Cloud Recording Bulk Jobs** using the **PureCloudPlatformClientV2 Python SDK**.

It performs bulk actions on recordings based on a conversation time interval:

- **EXPORT** – Export recordings to an external integration
- **ARCHIVE** – Archive recordings
- **DELETE** – Delete recordings (subject to retention/legal policies)

Authentication is done via **OAuth Client Credentials**. Credentials are loaded from a local file named:
**`.env.genesys.credentials`**.

---

## Project Structure

```
.
├── src/
│   └── main.py
├── .env.genesys.credentials
├── .env.example
└── README.md
```

> ⚠️ **Security note:** `.env.genesys.credentials` contains sensitive credentials. Do not share it publicly.

---

## Prerequisites

### 1) Genesys Cloud OAuth Client (Client Credentials)
Create an OAuth client in Genesys Cloud with:
- **Grant type:** Client Credentials
- Required permissions to manage recording jobs and access recordings  
  (EXPORT also requires access to the target export integration)

If you see `401` or `403`, verify the OAuth roles/permissions and export integration access.

### 2) Python
- Python **3.8+** recommended

---

## Install Dependencies

```bash
pip install PureCloudPlatformClientV2 python-dotenv pandas openpyxl xlsxwriter
```

---

## Credentials Configuration

### 1) Create your credentials file: `.env.genesys.credentials`

Use `.env.example` as a template and create a file called:

**`.env.genesys.credentials`** (in the project root)

Example:

```ini
GENESYS_CLOUD_CLIENT_ID=your_client_id
GENESYS_CLOUD_CLIENT_SECRET=your_client_secret
GENESYS_CLOUD_REGION=me_central_1
```

> ✅ In `src/main.py`, ensure you load this file explicitly:
>
> ```python
> from dotenv import load_dotenv
> load_dotenv(".env.genesys.credentials")
> ```

### 2) `.env.example` (Reference Only)

```ini
GENESYS_CLOUD_CLIENT_ID=your_client_id_here
GENESYS_CLOUD_CLIENT_SECRET=your_client_secret_here
GENESYS_CLOUD_REGION=me_central_1
```

---

## Genesys Cloud Region Mapping

Use one of the following region keys in `GENESYS_CLOUD_REGION`:

- `us_east_1` = `https://api.mypurecloud.com`
- `eu_west_1` = `https://api.mypurecloud.ie`
- `ap_southeast_2` = `https://api.mypurecloud.com.au`
- `ap_northeast_1` = `https://api.mypurecloud.jp`
- `eu_central_1` = `https://api.mypurecloud.de`
- `us_west_2` = `https://api.usw2.pure.cloud`
- `ca_central_1` = `https://api.cac1.pure.cloud`
- `ap_northeast_2` = `https://api.apne2.pure.cloud`
- `eu_west_2` = `https://api.euw2.pure.cloud`
- `ap_south_1` = `https://api.aps1.pure.cloud`
- `us_east_2` = `https://api.use2.us-gov-pure.cloud`
- `sa_east_1` = `https://api.sae1.pure.cloud`
- `me_central_1` = `https://api.mec1.pure.cloud`
- `ap_northeast_3` = `https://api.apne3.pure.cloud`
- `eu_central_2` = `https://api.euc2.pure.cloud`
- `mx_central_1` = `https://api.mxc1.pure.cloud`
- `ap_southeast_1` = `https://api.apse1.pure.cloud`

> These are the API hosts used by `PureCloudPlatformClientV2.PureCloudRegionHosts`.

---

## Run the Script

From the project root:

```bash
python src/main.py
```

---

## What the Script Does

1. Loads credentials from `.env.genesys.credentials`
2. Resolves Genesys API host using `GENESYS_CLOUD_REGION`
3. Authenticates using OAuth Client Credentials
4. Creates a **Recording Bulk Job** (`POST /api/v2/recording/jobs`)
5. Polls the job state until it is no longer `PENDING`
6. Executes the job when it reaches `READY` (`PUT /api/v2/recording/jobs/{jobId}`)
7. Optionally cancels the job during `PROCESSING` (`DELETE /api/v2/recording/jobs/{jobId}`)
8. Lists bulk jobs for visibility (`GET /api/v2/recording/jobs`)

---

## Configuration (Inside `src/main.py`)

### Action Type
```python
query.action = "EXPORT"  # EXPORT | ARCHIVE | DELETE
```

### Action Date
```python
query.action_date = "2029-01-01T00:00:00.000Z"
```

### Conversation Interval
```python
"interval": "2019-01-01T00:00:00.000Z/2019-07-10T00:00:00.000Z"
```

### Export Integration ID (EXPORT only)
```python
query.integration_id = "YOUR_EXPORT_INTEGRATION_ID"
```

> For ARCHIVE or DELETE actions, remove/comment out `integration_id`.

---

## Job States

Common job states:
- `PENDING`
- `READY`
- `PROCESSING`
- `FULFILLED`
- `FAILED`
- `CANCELLED`

> If you want the job to fully complete, remove the cancellation section from the script.

---

## Compliance & Safety Notes

- Call recordings and transcripts often contain **PII**
- Ensure operations follow PDPL/GDPR and internal retention policies
- Use **DELETE** with extreme caution

---

## Author

**Mahmoud Tarek Abdelghafar Elaasar**  
Genesys Specialist / CX Engineer  
Genesys Cloud Automation (Python / APIs)
