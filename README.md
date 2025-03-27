# GPS Data Collector

A Python service designed to collect GPS data from the FleetUp API every 5 minutes, enabling businesses to monitor vehicle locations, optimize fleet operations, and maintain accurate records by storing the data in a CSV file for further analysis.

## Setup Instructions

1. **Clone the repository**
    ```bash
    git clone https://github.com/liuling0/gps_collector_sample.git
    cd gps_collector_sample
    ```

2. **Install dependencies**
    ```bash
    pip install -r requirements.txt
    ```

3. **Configure environment variables**  
    Environment variables are used to store configuration settings securely. You can learn more about them [here](https://www.twilio.com/blog/2017/01/how-to-set-environment-variables.html).  
    Create a `.env` file in the project root with your FleetUp credentials:
    ```env
    FLEETUP_ACCOUNT_ID=your_account_id
    FLEETUP_SECRET_KEY=your_secret_key
    FLEETUP_API_KEY=your_api_key
    FLEETUP_BASE_URL=https://api.fleetup.net/
    COLLECTION_INTERVAL=300  # Data collection interval in seconds
    LOG_LEVEL=INFO  # Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    ```

4. **Create required directories**
    ```bash
    mkdir -p data logs
    ```

## Running the Service

### Option 1: Run directly
```bash
python -m gps_collector/main.py
```

### Option 2: Run as a systemd service (Linux)
1. Create a service file `/etc/systemd/system/gps-collector.service`:
    ```ini
    [Unit]
    Description=GPS Data Collector
    After=network.target

    [Service]
    User=yourusername
    WorkingDirectory=/path/to/gps_collector_sample
    EnvironmentFile=/path/to/gps_collector_sample/.env
    ExecStart=/usr/bin/python3 -m gps_collector/main.py
    Restart=always

    [Install]
    WantedBy=multi-user.target
    ```

2. Enable and start the service:
    ```bash
    sudo systemctl daemon-reload
    sudo systemctl enable gps-collector
    sudo systemctl start gps-collector
    ```
