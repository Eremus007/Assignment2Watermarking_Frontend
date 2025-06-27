import logging
import azure.functions as func
from workers import merge_and_upload  # your merging logic module

def main(msg: func.QueueMessage):
    logging.info("Merging video chunks...")
    return merge_and_upload.handle(msg)
