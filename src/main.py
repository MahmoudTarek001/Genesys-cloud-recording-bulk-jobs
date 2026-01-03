import os
import sys
import time

from dotenv import load_dotenv
import PureCloudPlatformClientV2
from PureCloudPlatformClientV2.rest import ApiException


print('-------------------------------------------------------------')
print('- Execute Bulk Action on recordings -')
print('-------------------------------------------------------------')

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env.genesys.credentials"))

# Credentials
CLIENT_ID = os.getenv("GENESYS_CLOUD_CLIENT_ID")
CLIENT_SECRET = os.getenv("GENESYS_CLOUD_CLIENT_SECRET")
ORG_REGION = os.getenv("GENESYS_CLOUD_REGION")  # e.g. me_central_1

if not CLIENT_ID or not CLIENT_SECRET or not ORG_REGION:
    print("[ERROR] Missing required credentials. Please verify '.env.genesys.credentials' contains:")
    print("  - GENESYS_CLOUD_CLIENT_ID")
    print("  - GENESYS_CLOUD_CLIENT_SECRET")
    print("  - GENESYS_CLOUD_REGION")
    sys.exit(1)

# Set environment / API host based on region
try:
    region = PureCloudPlatformClientV2.PureCloudRegionHosts[ORG_REGION]
except KeyError:
    print(f"[ERROR] Invalid GENESYS_CLOUD_REGION: '{ORG_REGION}'")
    print("Fix: set GENESYS_CLOUD_REGION to a valid key (see README Region Mapping).")
    sys.exit(1)

PureCloudPlatformClientV2.configuration.host = region.get_api_host()

# OAuth when using Client Credentials
api_client = (
    PureCloudPlatformClientV2.api_client.ApiClient()
    .get_client_credentials_token(CLIENT_ID, CLIENT_SECRET)
)

# Get the API
recording_api = PureCloudPlatformClientV2.RecordingApi(api_client)

# Build the create job query
# For export action, set query.action = "EXPORT"
# For delete action, set query.action = "DELETE"
# For archive action, set query.action = "ARCHIVE"
query = PureCloudPlatformClientV2.RecordingJobsQuery()
query.action = "EXPORT"
query.action_date = "2029-01-01T00:00:00.000Z"

# Comment out integration id if using DELETE or ARCHIVE
# For EXPORT, integration_id is usually required (depends on your org export integration)
query.integration_id = ""

query.conversation_query = {
    "interval": "2019-01-01T00:00:00.000Z/2019-07-10T00:00:00.000Z",
    "order": "asc",
    "orderBy": "conversationStart"
}

print("Recording Job Query:")
print(query)

# Call create_recording_job API
try:
    create_job_response = recording_api.post_recording_jobs(query)
    job_id = create_job_response.id
    print(f"Successfully created recording bulk job: {create_job_response}")
    print(f"Job ID: {job_id}")
except ApiException as e:
    print(f"Exception when calling RecordingApi->post_recording_jobs: {e}")
    sys.exit(1)

# Poll job state
while True:
    try:
        get_recording_job_response = recording_api.get_recording_job(job_id)
        job_state = get_recording_job_response.state
        if job_state != "PENDING":
            break
        print("Job state PENDING...")
        time.sleep(2)
    except ApiException as e:
        print(f"Exception when calling RecordingApi->get_recording_job: {e}")
        sys.exit(1)

# Execute job if READY
if job_state == "READY":
    try:
        execute_job_response = recording_api.put_recording_job(job_id, {"state": "PROCESSING"})
        job_state = execute_job_response.state
        print(f"Successfully executed recording bulk job: {execute_job_response}")
    except ApiException as e:
        print(f"Exception when calling RecordingApi->put_recording_job: {e}")
        sys.exit(1)
else:
    print(f"Expected Job State is: READY, however actual Job State is: {job_state}")

# Cancel job (optional)
# Can be canceled also in READY and PENDING states
if job_state == "PROCESSING":
    try:
        cancel_job_response = recording_api.delete_recording_job(job_id)
        print(f"Successfully cancelled recording bulk job: {cancel_job_response}")
    except ApiException as e:
        print(f"Exception when calling RecordingApi->delete_recording_job: {e}")
        sys.exit(1)

# List jobs (adjust filters as needed)
try:
    get_recording_jobs_response = recording_api.get_recording_jobs(
        page_size=25,
        page_number=1,
        sort_by="userId",        # or "dateCreated"
        state="CANCELLED",       # FULFILLED, PENDING, READY, PROCESSING, CANCELLED, FAILED
        show_only_my_jobs=True,
        job_type="EXPORT",       # or "DELETE" / "ARCHIVE"
    )
    print(f"Successfully fetched recording bulk jobs: {get_recording_jobs_response}")
except ApiException as e:
    print(f"Exception when calling RecordingApi->get_recording_jobs: {e}")
    sys.exit(1)
