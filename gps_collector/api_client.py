import requests
import datetime
import logging
from .logger import configure_logger
from typing import List, Dict

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
    def __init__(self, config, logger: logging.Logger):
        self.config = config
        self.logger = logger
        self.session = requests.Session()
        self.session.hooks['response'].append(lambda r, *args, **kwargs: RequestLogger.log_request_details(self.logger, r))

    def _refresh_token(self):
        """Refresh authentication token."""
        url = f"{self.config.base_url}token"
        params = {"acctId": self.config.account_id, "secret": self.config.secret_key}
        headers = {"x-api-key": self.config.api_key}

        try:
            response = self.session.get(url, params=params, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            self.config.token = data['token']
            self.config.token_expiry_time = datetime.datetime.fromtimestamp(data['expireTime'])
            self.logger.info("Successfully refreshed FleetUp token")
        except requests.RequestException as e:
            self.logger.error(f"Token refresh failed: {str(e)}")
            raise

    def _ensure_valid_token(self):
        """Validate and refresh token if needed."""
        if not self.config.token or datetime.datetime.now() > self.config.token_expiry_time:
            self.logger.info("Token expired or missing, initiating refresh.")
            self._refresh_token()

    def get_locations(self) -> List[Dict]:
        """Fetch device locations from API."""
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
