import os
import tempfile
import requests
import logging
from azure.storage.blob import BlobClient

# # You can store this securely with environment variables or settings
# AZURE_CONN_STR = (
#     "DefaultEndpointsProtocol=http;"
#     "AccountName=devstoreaccount1;"
#     "AccountKey=Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==;"
#     "BlobEndpoint=http://127.0.0.1:10000/devstoreaccount1;"
#     "QueueEndpoint=http://127.0.0.1:10001/devstoreaccount1;"
# )

connect_str = os.environ["AzureWebJobsStorage"]
# if connect_str == "UseDevelopmentStorage=true":
#     # Use full Azurite connection string manually when ran locally
#     connect_str = (
#         "DefaultEndpointsProtocol=http;"
#         "AccountName=devstoreaccount1;"
#         "AccountKey=Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==;"
#         "BlobEndpoint=http://127.0.0.1:10000/devstoreaccount1;"
#         "QueueEndpoint=http://127.0.0.1:10001/devstoreaccount1;"
#     )

def download_to_temp(source_path: str, suffix=".mp4") -> str:
    """
    Downloads a video or image to a temporary file from:
    - Local file
    - Public URL
    - Azure Blob Storage
    Returns the path to the temp file (or original file if local).
    """

    if source_path.startswith("http://") or source_path.startswith("https://"):
        logging.info(f"Downloading from public URL: {source_path}")
        response = requests.get(source_path)
        response.raise_for_status()
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
        tmp.write(response.content)
        tmp.close()
        return tmp.name

    elif source_path.startswith("blob://"):
        logging.info(f"Downloading from blob: {source_path}")
        try:
 
            parsed = source_path.replace("blob://", "", 1).split("/", 1)
            if len(parsed) != 2:
                raise ValueError(f"Malformed blob path: {source_path}")
            container, blob = parsed

            logging.info(f"Container: {container}")
            logging.info(f"Blob: {blob}")

            blob_client = BlobClient.from_connection_string(
                connect_str,
                container_name=container,
                blob_name=blob
            )
            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
            with open(tmp.name, "wb") as f:
                data = blob_client.download_blob()
                f.write(data.readall())
            return tmp.name
        except ValueError:
            logging.info(f"Download failed due to ValueError: {source_path}")

    elif os.path.exists(source_path):
        logging.info(f"Using local file: {source_path}")
        return source_path
    
    else:
        raise ValueError(f"Unrecognized source or file not found: {source_path}")

def generate_blob_uri(container: str, filename: str) -> str:
    """Generate a blob:// URI for internal use."""
    return f"blob://{container}/{filename}"