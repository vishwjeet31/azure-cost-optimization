import os
import json
from datetime import datetime, timedelta
from azure.cosmos import CosmosClient
from azure.storage.blob import BlobServiceClient

# Environment variables (configure in Azure Function App)
COSMOS_URL = os.environ['COSMOS_URL']
COSMOS_KEY = os.environ['COSMOS_KEY']
DB_NAME = "billing"
CONTAINER_NAME = "records"

BLOB_CONN_STR = os.environ['BLOB_CONN_STR']
BLOB_CONTAINER = "billing-archive"

# Initialize Cosmos and Blob clients
cosmos_client = CosmosClient(COSMOS_URL, COSMOS_KEY)
db = cosmos_client.get_database_client(DB_NAME)
container = db.get_container_client(CONTAINER_NAME)

blob_service = BlobServiceClient.from_connection_string(BLOB_CONN_STR)
blob_container = blob_service.get_container_client(BLOB_CONTAINER)

def main(mytimer) -> None:
    cutoff_date = datetime.utcnow() - timedelta(days=90)
    query = f"SELECT * FROM c WHERE c.timestamp < '{cutoff_date.isoformat()}'"

    for item in container.query_items(query, enable_cross_partition_query=True):
        blob_path = f"{item['id']}.json"
        blob_container.upload_blob(blob_path, json.dumps(item), overwrite=True)
        container.delete_item(item=item['id'], partition_key=item['partitionKey'])

    print("Archival completed for items older than 90 days.")
