from dotenv import load_dotenv
from gps_collector.factory import ApplicationFactory

load_dotenv()

if __name__ == "__main__":
    collector = ApplicationFactory.create_app()
    collector.run_periodically()
