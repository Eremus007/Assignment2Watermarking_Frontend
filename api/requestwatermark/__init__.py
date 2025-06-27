import logging
import azure.functions as func
import json
from azure.storage.queue import QueueClient
import os

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("HTTP request received to queue watermark job.")
    try:
        message = req.get_json()
        # Split into chunk jobs (as you've implemented)
        # Send to `queue-watermark-chunk` and then to `queue-merge`
        # ...
        return func.HttpResponse("Watermark render job queued.", status_code=200)
    except Exception as e:
        logging.error(f"Error queuing watermark job: {e}")
        return func.HttpResponse(f"Failed: {e}", status_code=500)
