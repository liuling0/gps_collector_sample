import threading
from dotenv import load_dotenv
import requests
from datetime import datetime
import time
import logging
import os
import csv
from typing import Dict, List, Optional
from config import Config

class RequestLogger:
    @staticmethod
    def log_request_details(logger: logging.Logger, response: requests.Response, *args, **kwargs):
        """Log detailed request information when in DEBUG mode"""
        if logger.isEnabledFor(logging.DEBUG):
            request = response.request
            details = [
                "\n=== HTTP REQUEST DETAILS ===",
                f"URL: {request.url}",
                f"Method: {request.method}",
                f"Headers: {dict(request.headers)}",
                f"Body: {request.body}",
                "\n=== HTTP RESPONSE DETAILS ===",
                f"Status: {response.status_code}",
                f"Headers: {dict(response.headers)}",
                f"Response Body: {response.text[:500]}...",  # Limit response body length
                "============================\n"
            ]
            logger.debug("\n".join(details))

class ApiClient:
    def __init__(self, config: Config, logger: logging.Logger):
        self.config = config
        self.logger = logger
        self.session = requests.Session()
        if not hasattr(ApiClient, '_hook_added'):
            self.session.hooks['response'].append(
                lambda r, *args, **kwargs: RequestLogger.log_request_details(self.logger, r)
            )
            ApiClient._hook_added = True

    def _refresh_token(self):
        """Refresh authentication token"""
        url = f"{self.config.base_url}token"
        params = {"acctId": self.config.account_id, "secret": self.config.secret_key}
        headers = {"x-api-key": self.config.api_key}

        try:
            response = self.session.get(url, params=params, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            self.config.token = data['token']
            self.config.token_expiry_time = datetime.fromtimestamp(data['expireTime'])
            self.logger.info("Successfully refreshed FleetUp token")
        except requests.RequestException as e:
            self.logger.error(f"Token refresh failed: {str(e)}")
            raise

    def _ensure_valid_token(self):
        """Validate and refresh token if needed"""
        if not self.config.token or datetime.now() > self.config.token_expiry_time:
            self.logger.info("Token expired or missing, initiating refresh")
            self._refresh_token()

    def get_locations(self) -> List[Dict]:
        """Fetch device locations from API"""
        self._ensure_valid_token()
        url = f"{self.config.base_url}gpsdata/device-last-location"
        headers = {
            "x-api-key": self.config.api_key,
            "token": self.config.token,
            "Content-Type": "application/json"
        }
        body = {"acctId": self.config.account_id}

        try:
            response = self.session.post(url, json=body, headers=headers)
            response.raise_for_status()
            return response.json().get('data', [])
        except requests.RequestException as e:
            self.logger.error(f"Failed to get locations: {str(e)}")
            raise

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
        current_date = datetime.now().strftime('%Y%m%d')
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
                        datetime.now().isoformat(),
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

class GPSDataCollector:
    def __init__(self, config: Config, api_client: ApiClient, csv_handler: CsvHandler, logger: logging.Logger):
        self.config = config
        self.api_client = api_client
        self.csv_handler = csv_handler
        self.logger = logger

    def collect_data(self):
        """Execute data collection cycle"""
        try:
            self.logger.info("Starting data collection cycle")
            locations = self.api_client.get_locations()
            self.csv_handler.save_records(locations)
            self.logger.debug(f"Collected {len(locations)} location(s). Sample data: {locations[:2]}...")  # Log count and sample data
        except Exception as e:
            self.logger.error(f"Data collection cycle failed: {str(e)}", exc_info=True)
            raise

    def run_periodically(self):
        """Run collection task on schedule."""
        self.logger.debug("Running periodically")
        self.logger.debug(f"Collection interval: {self.config.get_collection_interval()}")
        interval = self.config.get_collection_interval()  # Default to 300 seconds if not specified
        self.logger.info(f"Starting periodic collection with {interval} second interval.")
        next_run_time = time.time()
        while True:
            try:
                self.collect_data()
            except Exception as e:
                self.logger.critical(f"Critical failure in collection cycle: {str(e)}")
            
            next_run_time += interval
            sleep_time = max(0, next_run_time - time.time())
            time.sleep(sleep_time)

class ApplicationFactory:
    @staticmethod
    def create_app():
        """Dependency injection container"""
        load_dotenv()
        config = Config()
        logger = ApplicationFactory._configure_logger(config)
        csv_handler = CsvHandler(
            base_dir=os.path.join(os.path.dirname(__file__), '../data'),
            logger=logger
        )
        api_client = ApiClient(config=config, logger=logger)
        return GPSDataCollector(
            config=config,
            api_client=api_client,
            csv_handler=csv_handler,
            logger=logger
        )

    @staticmethod
    def _configure_logger(config: Config) -> logging.Logger:
        """Configure application-wide logging"""
        logger = logging.getLogger('gps_collector')
        log_lock = threading.Lock()  # Thread-safe lock for logger initialization
    
        # Get log level from config
        log_level = config.get_log_level()
        logger.setLevel(log_level)

        # Prevent duplicate handlers using a thread-safe lock
        with log_lock:
            if not logger.handlers:
                script_dir = os.path.dirname(os.path.abspath(__file__))
                
                # Get the current date to create a daily log file
                current_date = datetime.now().strftime('%Y%m%d')
                log_dir = os.path.abspath(os.path.join(script_dir, '../logs'))
                os.makedirs(log_dir, exist_ok=True)
                log_file = os.path.join(log_dir, f'qanalytics_integration_{current_date}.log')

                handler = logging.FileHandler(log_file, encoding='utf-8')
                formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
                handler.setFormatter(formatter)
                logger.addHandler(handler)

        return logger

if __name__ == "__main__":
    collector = ApplicationFactory.create_app()
    collector.run_periodically()