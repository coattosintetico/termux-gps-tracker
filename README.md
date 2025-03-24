# gps-tracker
Save location locally periodically.

I had to enable Termux to run on the background so that the script doesn't stop working when putting device to sleep:
```
battery > battery usage by app > termux > allow background activity
```

FUCK and also it requires to grant permission to Termux to ALWAYS have access to location:
```
Apps > Termux:API > Permissions > Location > Allow all the time
```

It also acquires the wakelock at the beginning of the script in order to prevent it from shutting down.

Otherwise, alternative: [GPSLogger](https://f-droid.org/en/packages/com.mendhak.gpslogger/). But seems like for now it's working properly :).

## Transferring GeoJSON files

To transfer the latest .geojson file from your phone to your computer:

1. Run the transfer script:
```
python transfer.py
```

2. By default, it starts an HTTP server on port 8000. You'll see output like:
```
[HH:MM:SS] [INFO] Latest .geojson file: records/YYYY-MM-DD_HH-MM-SS.geojson
[HH:MM:SS] [INFO] HTTP server started on port 8000
[HH:MM:SS] [INFO] Access the file at: http://192.168.x.x:8000/YYYY-MM-DD_HH-MM-SS.geojson
```

3. On your computer, download the file using your browser or a command like:
```
curl -o latest.geojson http://192.168.x.x:8000/YYYY-MM-DD_HH-MM-SS.geojson
```
or
```
wget http://192.168.x.x:8000/YYYY-MM-DD_HH-MM-SS.geojson
```

4. Press Ctrl+C in Termux to stop the server when done.

### Alternative methods

You can also use the termux-share feature:
```
python transfer.py --method share
```
This will open Android's share dialog, where you can select how to share the file (email, cloud storage, etc.).

For HTTP server on a different port:
```
python transfer.py --port 8080
```
