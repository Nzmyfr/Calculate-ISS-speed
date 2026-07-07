# Processing workflow for the ISS telemetry CSV

This folder contains a small data-enrichment pipeline that takes the sensor telemetry in data.csv and annotates it with information from the photos captured in the same run.

## What the script does

The script in process_data.py reads:

- the telemetry rows from data.csv
- the JPEG images named Photo*.jpg in this folder

For each photo, it extracts the EXIF timestamp from the image metadata and finds the nearest later telemetry row in data.csv. That row is then enriched with:

- photo_link: the photo filename that matches that row
- location: a human-readable address created by reverse geocoding the ISS coordinates from the row

## Processing steps

1. Read all photo files matching Photo*.jpg.
2. Extract the EXIF DateTime value from each image.
3. Parse the datetime column in data.csv.
4. For each photo, find the closest unused CSV row whose timestamp is greater than or equal to the photo timestamp.
5. Write the photo filename into the photo_link field for that matching row.
6. Use the ISS latitude and longitude from that row to perform reverse geocoding with Nominatim.
7. Save the enriched rows into processed_data.csv.

## Output

The output of the date processing are three files in the same folder:

- processed_data.csv: a flat CSV file that keeps the original telemetry columns and adds two new columns:
  - photo_link
  - location
- processed_data.xlsx: an Excel workbook with multiple sheets that contains diagrams created from the enriched data for easier review. The workbook contains sheets for processed_data, Environment, Orientation, Magnetometer, Accelerometer, Gyroscope, ISS position, ISS altitude, ISS speed, and DTLLAV - a data prepared for the creation of the KML file.
- 20260626104447-09241-map.kml: a Google Earth/KML map of the ISS pass. It contains timed waypoint placemarks with the ISS position at each timestamp, and some placemarks include links to the matching photo files such as Photo1.jpg and Photo9.jpg and the names of the locations from the reverse geocoding.

Together, these outputs make it easier to inspect which photo was taken near each telemetry sample, where the ISS was located at that time, and how the environmental and motion-related measurements are grouped across the run.

## Notes

- The matching is one-to-one: each photo is matched to a unique CSV row, and each CSV row can only be used once.
- If a photo has no usable EXIF timestamp, it is skipped.
- If reverse geocoding fails, the location field is left empty or set to Unknown depending on the error handling.
- The script uses Pillow for EXIF extraction and geopy for reverse geocoding.

## Run it

From this folder, run:

```bash
python process_data.py
```

This will generate processed_data.csv in the same directory.
