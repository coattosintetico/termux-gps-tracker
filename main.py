import atexit
import logging
import os
import subprocess
import threading
import time
from datetime import datetime
from enum import Enum
from typing import Annotated

import geojson
import typer

# Flag to control the execution of the script
running = True


class Provider(str, Enum):
    gps = "g"
    network = "n"
    passive = "p"


PROVIDER_MAP = {"g": "gps", "n": "network", "p": "passive"}


def setup_logging(geojson_file):
    # Create logs directory if it doesn't exist
    logs_dir = "logs"
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)

    # Create log filename based on geojson filename
    base_name = os.path.splitext(os.path.basename(geojson_file))[0]
    log_file = os.path.join(logs_dir, f"{base_name}.log")

    # Create logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)  # Set root logger to DEBUG

    # Create formatters
    formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s", datefmt="%H:%M:%S")

    # File handler (DEBUG level)
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    # Console handler (INFO level)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    # Remove any existing handlers
    logger.handlers = []

    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    logging.info(f"Logging initialized. Log file: {log_file}")


def acquire_wakelock():
    try:
        result = subprocess.run(["termux-wake-lock"], capture_output=True, text=True)
        if result.returncode == 0:
            logging.info("Wakelock acquired successfully")
            return True
        else:
            logging.error(f"Failed to acquire wakelock: {result.stderr}")
            return False
    except Exception as e:
        logging.error(f"Error acquiring wakelock: {str(e)}")
        return False


def release_wakelock():
    try:
        result = subprocess.run(["termux-wake-unlock"], capture_output=True, text=True)
        if result.returncode == 0:
            logging.info("Wakelock released successfully")
        else:
            logging.error(f"Failed to release wakelock: {result.stderr}")
    except Exception as e:
        logging.error(f"Error releasing wakelock: {str(e)}")


# Register wakelock release on script exit
atexit.register(release_wakelock)


def keyboard_listener():
    global running
    while running:
        if input() == "q":
            running = False


def create_filename():
    # Create records directory if it doesn't exist
    records_dir = "records"
    if not os.path.exists(records_dir):
        os.makedirs(records_dir)
        logging.info("Created records directory")

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    return os.path.join(records_dir, f"{timestamp}.geojson")


def get_location(provider):
    try:
        start_time = time.time()
        logging.debug(f"Starting location request with provider: {provider}")

        # Run termux-location with a 5-second timeout
        process = subprocess.Popen(
            ["termux-location", "-p", provider], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )

        try:
            stdout, stderr = process.communicate(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            stdout, stderr = process.communicate()
            logging.warning("Location request timed out after 5 seconds")
            return None

        elapsed_time = time.time() - start_time

        if process.returncode == 0 and stdout:
            logging.debug(f"Location request completed in {elapsed_time:.2f} seconds")
            return stdout
        else:
            logging.error(f"Location request failed after {elapsed_time:.2f} seconds")
            if stderr:
                logging.error(f"Error output: {stderr}")
            if stdout:
                logging.debug(f"Command output: {stdout}")
            return None

    except Exception as e:
        logging.error(f"Error during location request: {str(e)}")
        return None


def main(
    interval: Annotated[int, typer.Option("--time", "-t", help="Time interval in seconds.")] = 4,
    provider: Annotated[Provider, typer.Option("--provider", "-p", help="Location provider.")] = Provider.network,
):
    global running

    provider_name = PROVIDER_MAP[provider.value]

    # Setup for keyboard listener thread
    keyboard_thread = threading.Thread(target=keyboard_listener, daemon=True)
    keyboard_thread.start()

    # Create a new GeoJSON file for each run
    filename = create_filename()

    # Setup logging after we have the filename
    setup_logging(filename)

    # Acquire wakelock before starting
    if not acquire_wakelock():
        logging.warning("Could not acquire wakelock. Script may not work properly when screen is locked.")

    # Initialize the GeoJSON file
    with open(filename, "w") as file:
        feature_collection = geojson.FeatureCollection([])
        geojson.dump(feature_collection, file, indent=4)

    logging.info(f"Created new tracking file: {filename}")

    # Main execution loop
    while running:
        logging.debug(f"Reading gps data using {provider_name} provider...")

        result = get_location(provider_name)

        if not running:
            break

        if result is None:
            logging.warning("Skipping this reading due to error")
            time.sleep(interval)
            continue

        try:
            location_data = geojson.loads(result)
        except ValueError:
            logging.error("Error decoding JSON from termux-location")
            logging.debug(f"Raw output: {result}")
            time.sleep(interval)
            continue

        feature = geojson.Feature(
            geometry=geojson.Point((location_data["longitude"], location_data["latitude"])),
            properties={
                "timestamp": int(time.time()),
                "provider": provider_name,
                "additional_info": location_data,
            },
        )

        with open(filename, "r+") as file:
            data = geojson.load(file)
            data["features"].append(feature)
            file.seek(0)
            geojson.dump(data, file, indent=4)
            file.truncate()

        logging.info(f"New record appended to {filename}")

        time.sleep(interval)

    keyboard_thread.join(timeout=1)
    logging.info("Script terminated gracefully.")


if __name__ == "__main__":
    typer.run(main)
