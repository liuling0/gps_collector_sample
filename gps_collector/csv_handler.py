import os
import csv
import datetime
import logging
from typing import List, Dict

class CsvHandler:
    def __init__(self, base_dir: str, logger: logging.Logger):
        self.base_dir = base_dir
        self.logger = logger
        self._ensure_directory()
        self.file_path = self._get_file_path()

    def _ensure_directory(self):
        """Ensure the directory for CSV files exists."""
        if not os.path.exists(self.base_dir):
            os.makedirs(self.base_dir)

    def _get_file_path(self) -> str:
        """Generate CSV file path with the current date."""
        current_date = datetime.datetime.now().strftime('%Y%m%d')
        return os.path.join(self.base_dir, f'gps_data_{current_date}.csv')

    def _ensure_header(self):
        """Create file with headers if not exists."""
        if not os.path.exists(self.file_path):
            try:
                with open(self.file_path, mode='w', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    writer.writerow([
                        'timestamp', 'device_id', 'latitude', 'longitude',
                        'speed', 'direction', 'rpm', 'fuel_wear', 'idling'
                    ])
                self.logger.info(f"Created new CSV file at {self.file_path}")
            except IOError as e:
                self.logger.error(f"Failed to create CSV file: {str(e)}")
                raise

    def save_records(self, records: List[Dict]):
        """Save multiple records to CSV."""
        # Ensure the header exists before saving records
        self._ensure_header()
        try:
            with open(self.file_path, mode='a', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                for record in records:
                    writer.writerow([
                        datetime.datetime.now().isoformat(),
                        record.get('devId', 'N/A'),
                        record.get('lat'),
                        record.get('lng'),
                        record.get('speed'),
                        record.get('direction'),
                        record.get('rpm'),
                        record.get('fuelWear'),
                        record.get('idling')
                    ])
            self.logger.info(f"Successfully saved {len(records)} records.")
        except IOError as e:
            self.logger.error(f"CSV write failed: {str(e)}")
            raise
