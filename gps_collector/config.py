import logging
import os

class Config:
    def __init__(self):
        # FleetUp API configuration
        self.account_id = os.getenv('FLEETUP_ACCOUNT_ID')
        self.secret_key = os.getenv('FLEETUP_SECRET_KEY')
        self.api_key = os.getenv('FLEETUP_API_KEY')
        self.base_url = os.getenv('FLEETUP_BASE_URL')

        self.collection_interval = os.getenv('COLLECTION_INTERVAL')

        # Token management
        self.token = None
        self.token_expiry_time = None

        # Logging configuration
        self.log_level = os.getenv('LOG_LEVEL', 'INFO')

    def get_log_level(self):
        """Return log level"""
        log_levels = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL
        }
        return log_levels.get(self.log_level, logging.INFO)  
    
    def get_collection_interval(self):
        """Return collection interval"""
        return int(self.collection_interval) if self.collection_interval else 300