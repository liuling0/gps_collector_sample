import os
from .config import Config
from .logger import configure_logger
from .api_client import ApiClient
from .csv_handler import CsvHandler
from .data_collector import GPSDataCollector

class ApplicationFactory:
    @staticmethod
    def create_app():
        """Dependency injection container."""
        config = Config()
        logger = configure_logger(config=config)
        
        base_dir = os.path.join(os.path.dirname(__file__), '../data')
        
        # Create CsvHandler with dynamic daily file generation
        csv_handler = CsvHandler(base_dir=base_dir, logger=logger)
        
        api_client = ApiClient(config=config, logger=logger)
        return GPSDataCollector(
            config=config,
            api_client=api_client,
            csv_handler=csv_handler,
            logger=logger
        )
