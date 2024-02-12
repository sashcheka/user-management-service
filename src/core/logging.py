import logging
import os
from datetime import datetime


class IgnoreWatchfilesFilter(logging.Filter):
    def filter(self, record):
        return not ("watchfiles.main" in record.name)


def configure_logging():
    log_folder = "logs"

    if not os.path.exists(log_folder):
        os.makedirs(log_folder)

    log_filename = datetime.now().strftime(f"{log_folder}/log_%Y-%m-%d_%H-%M.log")

    logging.basicConfig(
        filename=log_filename,
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M",
    )

    logging.getLogger("watchfiles.main").addFilter(IgnoreWatchfilesFilter())
    logging.getLogger().addFilter(IgnoreWatchfilesFilter())

    print(f"Logging to file {log_filename}")
