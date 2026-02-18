#!/usr/bin/env python3
import http.server
import logging
import os
import socket
import socketserver
import subprocess
from enum import Enum
from pathlib import Path
from typing import Annotated

import typer

# Setup logging
logging.basicConfig(level=logging.INFO, format="[%(asctime)s] [%(levelname)s] %(message)s", datefmt="%H:%M:%S")


class Method(str, Enum):
    http = "http"
    share = "share"


def get_latest_geojson():
    """Find the latest .geojson file in the records directory."""
    records_dir = Path("records")
    if not records_dir.exists():
        logging.error(f"Records directory '{records_dir}' does not exist")
        return None

    geojson_files = list(records_dir.glob("*.geojson"))
    if not geojson_files:
        logging.error("No .geojson files found in records directory")
        return None

    # Sort by modification time (newest last)
    latest_file = max(geojson_files, key=lambda f: f.stat().st_mtime)
    logging.info(f"Latest .geojson file: {latest_file}")
    return latest_file


def get_local_ip():
    """Get the local IP address."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception as e:
        logging.error(f"Failed to determine local IP: {str(e)}")
        return "127.0.0.1"


def start_http_server(file_path, port=8000):
    """Start a simple HTTP server to share the file."""
    directory = os.path.dirname(os.path.abspath(file_path))
    os.chdir(directory)

    file_name = os.path.basename(file_path)
    local_ip = get_local_ip()

    class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
        def log_message(self, format, *args):
            if args[0].startswith("GET") and file_name in args[0]:
                logging.info(f"File download requested: {file_name}")
            super().log_message(format, *args)

    handler = CustomHTTPRequestHandler
    with socketserver.TCPServer(("", port), handler) as httpd:
        logging.info(f"HTTP server started on port {port}")
        logging.info(f"Access the file at: http://{local_ip}:{port}/{file_name}")
        logging.info("On your computer, you can download the file using:")
        logging.info(f"  curl -o latest.geojson http://{local_ip}:{port}/{file_name}")
        logging.info(f"  wget http://{local_ip}:{port}/{file_name}")
        logging.info("Press Ctrl+C to stop the server")

        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            logging.info("Server stopped")


def share_via_termux(file_path):
    """Share the file using termux-share."""
    try:
        result = subprocess.run(["termux-share", str(file_path)], capture_output=True, text=True)
        if result.returncode == 0:
            logging.info(f"File shared successfully: {file_path}")
            return True
        else:
            logging.error(f"Failed to share file: {result.stderr}")
            return False
    except Exception as e:
        logging.error(f"Error sharing file: {str(e)}")
        return False


def main(
    method: Annotated[Method, typer.Option(help="Transfer method.")] = Method.http,
    port: Annotated[int, typer.Option(help="Port for HTTP server (only used with --method=http).")] = 8000,
):
    latest_file = get_latest_geojson()
    if not latest_file:
        raise typer.Exit(1)

    if method == Method.http:
        start_http_server(latest_file, port)
    elif method == Method.share:
        share_via_termux(latest_file)


if __name__ == "__main__":
    typer.run(main)
