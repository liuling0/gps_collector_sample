import time
import logging
from typing import List, Dict
from .api_client import ApiClient
from .csv_handler import CsvHandler

class GPSDataCollector:
    def __init__(self, config, api_client: ApiClient, csv_handler: CsvHandler, logger: logging.Logger):
        self.config = config
        self.api_client = api_client
        self.csv_handler = csv_handler
        self.logger = logger

    def collect_data(self):
        """Execute data collection cycle."""
        try:
            self.logger.info("Starting data collection cycle.")
            locations = self.api_client.get_locations()
            self.csv_handler.save_records(locations)
            self.logger.debug(f"Collected data samples: {locations[:2]}...")  # Log sample data
        except Exception as e:
            self.logger.error(f"Data collection cycle failed: {str(e)}", exc_info=True)
            raise

    def run_periodically(self):
        """Run collection task on schedule."""
        print("Running periodically")
        print(self.config.get_collection_interval())
        interval = self.config.get_collection_interval()  # Default to 300 seconds if not specified
        self.logger.info(f"Starting periodic collection with {interval} second interval.")
        while True:
            start_time = time.time()
            try:
                self.collect_data()
            except Exception as e:
                self.logger.critical(f"Critical failure in collection cycle: {str(e)}")
            
            elapsed = time.time() - start_time
            sleep_time = max(0, interval - elapsed)
            time.sleep(sleep_time)
