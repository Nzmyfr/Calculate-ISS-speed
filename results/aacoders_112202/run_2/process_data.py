#!/usr/bin/env python3.11
"""Enrich a CSV file with photo links and reverse-geocoded locations.

The script reads EXIF timestamps from JPEG files, matches each photo to the
nearest later row in the CSV file, and writes the resulting photo path and
reverse-geocoded address back into the output CSV.
"""

import csv
import os
from pathlib import Path
from datetime import datetime, timedelta
from PIL import Image
from PIL.ExifTags import TAGS
from geopy.geocoders import Nominatim
import time

# Configuration
CURRENT_DIR = Path(__file__).parent
CSV_FILE = CURRENT_DIR / "data.csv"
OUTPUT_FILE = CURRENT_DIR / "processed_data.csv"

def get_exif_datetime(image_path):
    """Return the EXIF timestamp for an image file.

    Args:
        image_path: Path to the JPEG file to inspect.

    Returns:
        A datetime object when the EXIF timestamp is available; otherwise None.
    """
    try:
        image = Image.open(image_path)
        exif_data = image._getexif()
        
        if exif_data is None:
            return None
        
        # EXIF tag 36867 is DateTime
        for tag_id, value in exif_data.items():
            tag_name = TAGS.get(tag_id, tag_id)
            if tag_name == "DateTime":
                # EXIF datetime format: "YYYY:MM:DD HH:MM:SS"
                return datetime.strptime(value, "%Y:%m:%d %H:%M:%S")
    except Exception as e:
        print(f"Error reading EXIF from {image_path}: {e}")
    
    return None

def parse_csv_datetime(value):
    """Parse a CSV datetime string into a datetime object.

    Args:
        value: The datetime value read from the CSV file.

    Returns:
        A datetime object parsed from the input string.

    Raises:
        ValueError: If the input string is empty or invalid.
    """
    if not value:
        raise ValueError("Empty datetime")
    return datetime.fromisoformat(value)


def find_matching_row_index(photo_datetime, rows, used_indices):
    """Find the best unused CSV row for a photo timestamp.

    The function scans the CSV rows and returns the index of the first unused
    row whose datetime is later than or equal to the photo timestamp and is the
    closest match.

    Args:
        photo_datetime: The EXIF datetime taken from the image.
        rows: The CSV rows loaded from the input file.
        used_indices: Indices already matched to a photo.

    Returns:
        The index of the best matching row, or None if no suitable row exists.
    """
    best_index = None
    best_dt = None

    for idx, row in enumerate(rows):
        if idx in used_indices:
            continue

        try:
            csv_dt = parse_csv_datetime(row['datetime'])
        except (ValueError, KeyError):
            continue

        if csv_dt < photo_datetime:
            continue

        if best_dt is None or csv_dt < best_dt:
            best_dt = csv_dt
            best_index = idx

    return best_index


def reverse_geocode(geocoder, latitude, longitude):
    """Return a human-readable address for a latitude and longitude pair.

    Args:
        geocoder: A geopy geocoder instance.
        latitude: Latitude of the location.
        longitude: Longitude of the location.

    Returns:
        The reverse-geocoded address, or "Unknown" if the lookup fails.
    """
    try:
        location = geocoder.reverse(f"{latitude}, {longitude}", language="en")
        print(f"Reverse geocoding result for ({latitude:.8f}, {longitude:.8f}): {location.address}")
        return location.address
    except Exception as e:
        print(f"No reverse geocoding result for ({latitude:.8f}, {longitude:.8f})")
        return "Unknown"


def build_photos_dict():
    """Collect JPEG files and their EXIF timestamps.

    Returns:
        A dictionary mapping each photo filename to its EXIF datetime.
    """
    photos = {}
    for jpg_file in sorted(CURRENT_DIR.glob("Photo*.jpg")):
        exif_dt = get_exif_datetime(jpg_file)
        if exif_dt:
            photos[jpg_file.name] = exif_dt

    print(f"Found {len(photos)} JPG files with EXIF datetime")
    return photos


def main():
    """Process the photo and CSV files to create an enriched output CSV."""
    # Initialize the geocoder used for reverse geocoding.
    geocoder = Nominatim(user_agent="astro_pi_geocoder")

    print("Starting data enrichment process...")

    # Build a mapping of photo filenames to their EXIF timestamps.
    photos_dict = build_photos_dict()
    print(f"Photos dictionary built with {len(photos_dict)} entries")

    # Read the input CSV file into memory.
    print(f"Reading {CSV_FILE}...")
    rows = []
    with open(CSV_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    print(f"Read {len(rows)} rows from CSV")

    # Prepare each output row with empty enrichment fields.
    for row in rows:
        row['photo_link'] = ""
        row['location'] = ""


    # Match each photo to the nearest later CSV row and enrich that row.
    print("Processing photos...")
    used_indices = set()
    for i, (photo_name, photo_datetime) in enumerate(photos_dict.items(), start=1):
        print(f"{i}/{len(photos_dict)} {photo_name} -> {photo_datetime}. ", end="")

        matching_row_index = find_matching_row_index(photo_datetime, rows, used_indices)
        if matching_row_index is None:
            print("  No matching CSV row found")
            continue

        used_indices.add(matching_row_index)
        rows[matching_row_index]['photo_link'] = str(photo_name)

        try:
            latitude = float(rows[matching_row_index]['iss_latitude'])
            longitude = float(rows[matching_row_index]['iss_longitude'])
            rows[matching_row_index]['location'] = reverse_geocode(geocoder, latitude, longitude)
            time.sleep(1)
        except (ValueError, KeyError) as e:
            print(f"  Error processing coordinates for row {matching_row_index}: {e}")
            rows[matching_row_index]['location'] = ""

    # Write the enriched rows to a new CSV file.
    print(f"Writing enriched data to {OUTPUT_FILE}...")
    fieldnames = list(rows[0].keys()) if rows else []

    with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Done! Enriched CSV saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
