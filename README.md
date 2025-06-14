# azure-cost-optimization
Cost optimization solution for billing records using Azure serverless architecture

Problem Statement
We store billing records in Azure Cosmos DB, and the size has grown significantly. We aim to optimize cost while maintaining availability of all records (new and old), without any changes to the existing API layer.

## Solution Overview
We use a hybrid active+archive pattern:
- Keep only recent 3 months of data in Cosmos DB.
- Archive older records in Azure Blob Storage.
- Intercept read requests to fallback to archive if record is not found in Cosmos DB.

## Technologies
- Azure Cosmos DB
- Azure Blob Storage
- Azure Functions (Timer & HTTP)
- Python SDKs (azure-cosmos, azure-storage-blob)


##  Deployment Steps
1. Deploy Cosmos DB and Blob Storage.
2. Set up Azure Functions using `archive_to_blob.py` and `fallback_reader.py`.
3. Schedule archival using a Timer Trigger.
4. Proxy reads through `fallback_reader.py`.

##  Cost Benefits
- Reduces Cosmos DB storage & RU charges.
- Cold archive in Blob is ~90% cheaper.

##  Performance
- All recent reads are fast (Cosmos DB).
- Archived reads are slower (~seconds), but still acceptable.

##  No API Changes
API contract remains the same — fallback handled internally.
