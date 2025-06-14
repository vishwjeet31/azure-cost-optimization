import os
import json
from azure.cosmos import CosmosClient, exceptions
from azure.storage.blob import BlobServiceClient
from azure.functions import HttpRequest, HttpResponse

# Environment variables (set these in Azure Function App settings)
COSMOS_URL = os.environ['COSMOS_URL']
COSMOS_KEY = os.environ['COSMOS_KEY']
DB_NAME = "billing"
CONTAINER_NAME = "records"

BLOB_CONN_STR = os.environ['BLOB_CONN_STR']
BLOB_CONTAINER = "billing-archive"

# Cosmos and Blob setup
cosmos_client = CosmosClient(COSMOS_URL, COSMOS_KEY)
db = cosmos_client.get_database_client(DB_NAME)
container = db.get_container_client(CONTAINER_NAME)

blob_service = BlobServiceClient.from_connection_string(BLOB_CONN_STR)
blob_container = blob_service.get_container_client(BLOB_CONTAINER)

def main(req: HttpRequest) -> HttpResponse:
    record_id = req.params.get("id")
    partition_key = req.params.get("partitionKey")

    if not record_id or not partition_key:
        return HttpResponse("Missing 'id' or 'partitionKey' in query params", status_code=400)

    try:
        # First try Cosmos DB
        item = container.read_item(item=record_id, partition_key=partition_key)
        return HttpResponse(json.dumps(item), mimetype="application/json")

    except exceptions.CosmosResourceNotFoundError:
        # If not found, try Blob Storage
        blob_path = f"{record_id}.json"
        try:
            blob_client = blob_container.get_blob_client(blob_path)
            stream = blob_client.download_blob().readall()
            return HttpResponse(stream, mimetype="application/json")
        except Exception as e:
            return HttpResponse(f"Record not found in Cosmos DB or Blob Storage. Error: {str(e)}", status_code=404)

    except Exception as e:
        return HttpResponse(f"Unexpected error: {str(e)}", status_code=500)
