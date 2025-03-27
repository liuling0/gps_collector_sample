import threading
import requests
import datetime
import logging
import time
import os
import csv
from .config import Config

class GPSDataCollector:
    def __init__(self):
        self.config = Config()
        self.setup_logging()
        self.csv_file = os.path.join(os.path.dirname(__file__), '../data/gps_data.csv')
        self.ensure_csv_header()
        
    def setup_logging(self):
        """Configure logging system"""
        script_dir = os.path.dirname(os.path.abspath(__file__))
        log_file = os.path.join(script_dir, '../logs/qanalytics_integration.log')
        
        handler = logging.FileHandler(log_file, encoding='utf-8')
        formatter = logging.Formatter('%(asctime)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        handler.setFormatter(formatter)
        
        self.logger = logging.getLogger('gps_collector')
        self.logger.setLevel(logging.DEBUG)
        self.logger.addHandler(handler)

    def ensure_csv_header(self):
        """Ensure CSV file exists with proper headers"""
        if not os.path.exists(self.csv_file):
            with open(self.csv_file, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([
                    'timestamp', 'device_id', 'latitude', 'longitude',
                    'speed', 'direction', 'rpm', 'fuel_wear', 'idling'
                ])

    def get_fleetup_token(self):
        """Get authentication token from FleetUp API"""
        url = f"{self.config.base_url}token"
        params = {"acctId": self.config.account_id, "secret": self.config.secret_key}
        headers = {"x-api-key": self.config.api_key}
        
        try:
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            self.config.token = data['token']
            self.config.token_expiry_time = datetime.datetime.fromtimestamp(data['expireTime'])
            self.logger.info("Successfully obtained FleetUp token")
        except Exception as e:
            self.logger.error(f"Error getting FleetUp token: {str(e)}")
            raise

    def get_token_if_needed(self):
        """Check and renew token if expired"""
        if not self.config.token or datetime.datetime.now() > self.config.token_expiry_time:
            self.get_fleetup_token()
        return self.config.token

    def get_all_last_locations(self):
        """Fetch all device locations from FleetUp API"""
        token = self.get_token_if_needed()
        url = f"{self.config.base_url}gpsdata/device-last-location"
        headers = {
            "x-api-key": self.config.api_key,
            "token": token,
            "Content-Type": "application/json"
        }
        body = {"acctId": self.config.account_id}
        
        response = requests.post(url, json=body, headers=headers)
        return response.json().get('data', [])

    def save_to_csv(self, locations):
        """Save GPS data to CSV file"""
        with open(self.csv_file, mode='a', newline='') as file:
            writer = csv.writer(file)
            for location in locations:
                writer.writerow([
                    datetime.datetime.now().isoformat(),
                    location.get('devId', 'N/A'),
                    location.get('lat'),
                    location.get('lng'),
                    location.get('speed'),
                    location.get('direction'),
                    location.get('rpm'),
                    location.get('fuelWear'),
                    location.get('idling')
                ])

    def collect_data(self):
        """Main data collection method"""
        try:
            locations = self.get_all_last_locations()
            self.save_to_csv(locations)
            for location in locations:
                self.logger.info(f"Collected data: {location}")
        except Exception as e:
            self.logger.error(f"Data collection failed: {str(e)}")

    def run_periodically(self, interval=300):
        """Run collection task periodically"""
        while True:
            self.collect_data()
            time.sleep(interval)

if __name__ == "__main__":
    collector = GPSDataCollector()
    collector.run_periodically()