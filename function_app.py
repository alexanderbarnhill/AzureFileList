import os
import json
import azure.functions as func
from azure.storage.blob import BlobServiceClient

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)


def get_files(container, folder, connection_string_input_env_var):
    # Retrieve the connection string from environment variables
    connection_string = os.getenv(connection_string_input_env_var)

    if not connection_string:
        raise ValueError(f"{connection_string_input_env_var} is not set")

    # Create a BlobServiceClient using the connection string
    service_client = BlobServiceClient.from_connection_string(connection_string)
    container_client = service_client.get_container_client(container)

    child_items = []
    items = container_client.list_blobs(name_starts_with=folder)

    for item in items:
        if item.name.lower().endswith(("jpg", "jpeg")):
            child_items.append({
                "name": item.name,
                "container": container
            })

    return child_items

@app.route(route="get_files", methods=["GET"])
def get_files_function(req: func.HttpRequest) -> func.HttpResponse:
    try:
        print("Params:", req.params)
        # Get query parameters
        container = req.params.get("container")
        folder = req.params.get("folder")
        connection_string_input_env_var = req.params.get("con_env_in")

        # Validate query parameters
        if not container or not folder or not connection_string_input_env_var:
            return func.HttpResponse(
                json.dumps({"error": "Missing required query parameters. Expected: container, folder, conv_env_in."}),
                status_code=400,
                mimetype="application/json"
            )

        # Fetch file paths
        files = get_files(container, folder, connection_string_input_env_var)

        return func.HttpResponse(
            json.dumps({"childItems": files}),
            status_code=200,
            mimetype="application/json"
        )

    except Exception as e:
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            status_code=500,
            mimetype="application/json"
        )
