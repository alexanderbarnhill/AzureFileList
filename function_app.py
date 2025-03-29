import os
import json
import azure.functions as func
from azure.storage.blob import BlobServiceClient

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

def get_files(storage_account, container, folder):
    # Retrieve the connection string from environment variables
    connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")

    if not connection_string:
        raise ValueError("AZURE_STORAGE_CONNECTION_STRING is not set")

    # Create a BlobServiceClient using the connection string
    service_client = BlobServiceClient.from_connection_string(connection_string)
    container_client = service_client.get_container_client(container)

    child_items = []
    items = container_client.list_blobs(name_starts_with=folder)

    for item in items:
        if item.name.lower().endswith(("jpg", "jpeg")):
            child_items.append({"path": f"https://{storage_account}.blob.core.windows.net/{container}/{item.name}"})

    return func.HttpResponse(str(child_items), mimetype="application/json")

@app.route(route="get_files", methods=["GET"])
def get_files_function(req: func.HttpRequest) -> func.HttpResponse:
    try:
        # Get query parameters
        storage_account = req.params.get("storage_account")
        container = req.params.get("container")
        folder = req.params.get("folder")

        # Validate query parameters
        if not storage_account or not container or not folder:
            return func.HttpResponse(
                json.dumps({"error": "Missing required query parameters. Expected: storage_account, container, folder."}),
                status_code=400,
                mimetype="application/json"
            )

        # Fetch file paths
        files = get_files(storage_account, container, folder)

        return func.HttpResponse(
            json.dumps({"files": files}),
            status_code=200,
            mimetype="application/json"
        )

    except Exception as e:
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            status_code=500,
            mimetype="application/json"
        )
