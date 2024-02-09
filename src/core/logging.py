import logging
from datetime import datetime


def configure_logging():
    log_filename = datetime.now().strftime("app_log_%Y-%m-%d_%H-%M-%S.log")

    logging.basicConfig(
        filename=log_filename,
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    print(f"Logging to file {log_filename}")
