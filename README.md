# termux-gps-tracker

Save location locally periodically.

## Setup

### Prerequisites

Install [Termux](https://f-droid.org/en/packages/com.termux/) and [Termux:API](https://f-droid.org/en/packages/com.termux.api/) from F-Droid.

### Android permissions

Allow Termux to run in the background so the script doesn't stop when putting the device to sleep:
```
Settings > Battery > Battery usage by app > Termux > Allow background activity
```
or
```
Settings > Apps > App management > Termux > Battery usage > Allow background activity
```

Grant Termux:API permanent location access:
```
Settings > Apps > Termux:API > Permissions > Location > Allow all the time
```

### Installation

Clone the repo and run:
```
make install
```

This will:
1. Install `python`, `termux-api`, and [uv](https://docs.astral.sh/uv/) via `pkg`
2. Install Python dependencies via `uv sync`

## Usage

Start tracking (defaults to network provider, 4s interval):
```
make run
```

With custom arguments:
```
make run ARGS="-t 30 -p g"
```

| Flag | Description | Default |
|------|-------------|---------|
| `-t` | Interval in seconds | `4` |
| `-p` | Provider: `g`=gps, `n`=network, `p`=passive | `n` |

Press `q` + Enter to stop gracefully. The script acquires a wakelock at startup to prevent Termux from being killed.

## Transferring GeoJSON files

Transfer the latest `.geojson` file from your phone to your computer.

### HTTP server (default)

```
make transfer
```

This starts an HTTP server on port 8000. You'll see output like:
```
[HH:MM:SS] [INFO] Latest .geojson file: records/YYYY-MM-DD_HH-MM-SS.geojson
[HH:MM:SS] [INFO] HTTP server started on port 8000
[HH:MM:SS] [INFO] Access the file at: http://192.168.x.x:8000/YYYY-MM-DD_HH-MM-SS.geojson
```

On your computer, download the file:
```
curl -o latest.geojson http://192.168.x.x:8000/YYYY-MM-DD_HH-MM-SS.geojson
```

Press Ctrl+C in Termux to stop the server.

### Alternative: Android share dialog

```
make transfer ARGS="--method share"
```

### Custom port

```
make transfer ARGS="--port 8080"
```

## Alternatives

[GPSLogger](https://f-droid.org/en/packages/com.mendhak.gpslogger/) is a standalone Android app that does something similar.
