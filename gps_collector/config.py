import os

class Config:
    def __init__(self):
        # FleetUp API configuration
        self.account_id = os.getenv('FLEETUP_ACCOUNT_ID')
        self.secret_key = os.getenv('FLEETUP_SECRET_KEY')
        self.api_key = os.getenv('FLEETUP_API_KEY')
        self.base_url = os.getenv('FLEETUP_BASE_URL')
        
        # Token management
        self.token = None
        self.token_expiry_time = None