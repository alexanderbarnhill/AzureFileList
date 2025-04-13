import os
import json
import azure.functions as func
from azure.storage.blob import BlobServiceClient
import urllib.parse

# Create a Function App with HTTP trigger and function-level authorization
app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)


def get_files(container, folder, connection_string_input_env_var):
    """
    Retrieve a list of image files (JPEG/JPG) from a specified folder in an Azure Blob Storage container.

    Args:
        container (str): Name of the Azure Blob Storage container.
        folder (str): Folder path to list blobs from.
        connection_string_input_env_var (str): Name of the environment variable containing the connection string.

    Returns:
        list: A list of dictionaries, where each dictionary contains:
            - name (str): Name of the blob (file).
            - container (str): Name of the container where the file resides.
    """
    # Retrieve the connection string from environment variables
    connection_string = os.getenv(connection_string_input_env_var)
    if not connection_string:
        raise ValueError(f"{connection_string_input_env_var} is not set")

    # Create a BlobServiceClient to connect to the blob storage account
    service_client = BlobServiceClient.from_connection_string(connection_string)
    container_client = service_client.get_container_client(container)

    # Initialize a list to store matching file details
    child_items = []

    # List all blobs with a prefix matching the specified folder
    if folder is None or len(folder) == 0 or folder == "ROOT":
        print(f"Looking in root directory: {container}")
        folder = None
    items = container_client.list_blobs(name_starts_with=folder)
    # Loop through all items and filter for JPEG/JPG files
    for item in items:
        if item.name.lower().endswith(("jpg", "jpeg")) and not os.path.basename(item.name.lower()).startswith("."):
            # Add file information to the list
            child_items.append({
                "name": urllib.parse.quote(item.name),
                "container": container
            })

    return child_items


@app.route(route="get_files", methods=["GET"])
def get_files_function(req: func.HttpRequest) -> func.HttpResponse:
    """
    HTTP-triggered function to retrieve a list of image files from Azure Blob Storage.

    Query Parameters:
        - container (str): Name of the container where the files are stored.
        - folder (str): Path to the folder containing the images.
        - con_env_in (str): Name of the environment variable containing the input connection string.

    Returns:
        HttpResponse: JSON response containing a list of matching files or an error message.
    """
    try:
        print("Params:", req.params)

        # Get query parameters from the HTTP request
        container = req.params.get("container")
        folder = req.params.get("folder")
        connection_string_input_env_var = req.params.get("con_env_in")

        # Validate that all required query parameters are provided
        if not container or not folder or not connection_string_input_env_var:
            return func.HttpResponse(
                json.dumps({"error": "Missing required query parameters. Expected: container, folder, con_env_in."}),
                status_code=400,
                mimetype="application/json"
            )

        # Fetch matching file paths from the specified container and folder
        files = get_files(container, folder, connection_string_input_env_var)

        # Return a success response with the list of files
        return func.HttpResponse(
            json.dumps({"childItems": files}),
            status_code=200,
            mimetype="application/json"
        )

    except Exception as e:
        # Return an error response if an exception occurs
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            status_code=500,
            mimetype="application/json"
        )
