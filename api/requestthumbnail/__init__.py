import logging
import azure.functions as func
import json
from azure.storage.queue import QueueClient
import os

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("HTTP request received for thumbnail generation.")
    try:
        message = req.get_json()
        queue = QueueClient.from_connection_string(
            os.environ["AzureWebJobsStorage"], "queue-generate-thumbnail"
        )
        queue.send_message(json.dumps(message))
        return func.HttpResponse("Thumbnail request queued.", status_code=200)
    except Exception as e:
        logging.error(f"Failed to queue thumbnail request: {e}")
        return func.HttpResponse("Failed to queue thumbnail request", status_code=500)
