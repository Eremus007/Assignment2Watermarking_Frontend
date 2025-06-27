import logging
import azure.functions as func
from workers import watermark  # your watermark.py logic

def main(msg: func.QueueMessage):
    logging.info("Processing a watermark chunk...")
    return watermark.handle(msg)
