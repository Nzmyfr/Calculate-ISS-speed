#!/usr/bin/env python3.11
"""
Script to enrich CSV data with photo links and reverse geocoding information.
Adds two columns:
1. photo_link: Path to JPG file matching the datetime via EXIF data
2. location: Reverse geocoded address for the given latitude/longitude
"""

import csv
import os
from pathlib import Path
from datetime import datetime
from PIL import Image
from PIL.ExifTags import TAGS
from geopy.geocoders import Nominatim
import time

# Configuration
CURRENT_DIR = Path(__file__).parent
CSV_FILE = CURRENT_DIR / "data.csv"
OUTPUT_FILE = CURRENT_DIR / "data_enriched.csv"

# Initialize geocoder
geocoder = Nominatim(user_agent="astro_pi_geocoder")


def get_exif_datetime(image_path):
    """
    Extract datetime from EXIF data of an image.
    Returns datetime object or None if not found.
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


def find_matching_photo(target_datetime, photos_dict):
    """
    Find a JPG file with matching EXIF datetime.
    Returns the filename or None.
    """
    for photo_name, photo_datetime in photos_dict.items():
        if photo_datetime == target_datetime:
             return photo_name
    return None


def reverse_geocode(latitude, longitude):
    """
    Perform reverse geocoding for given coordinates.
    Returns address string or "Unknown" if failed.
    """
    try:
        location = geocoder.reverse(f"{latitude}, {longitude}", language="en")
        return location.address
    except Exception as e:
        print(f"Error reverse geocoding ({latitude}, {longitude}): {e}")
        return "Unknown"


def build_photos_dict():
    """
    Build a dictionary of all JPG files with their EXIF datetimes.
    Returns {filename: datetime}.
    """
    photos = {}
    for jpg_file in CURRENT_DIR.glob("Photo*.jpg"):
        exif_dt = get_exif_datetime(jpg_file)
        if exif_dt:
            photos[jpg_file.name] = exif_dt
    
    print(f"Found {len(photos)} JPG files with EXIF datetime")
    return photos


def main():
    """Main function to process the CSV file."""
    print("Starting data enrichment process...")
    
    # Build photos dictionary
    photos_dict = build_photos_dict()
    
    # Read the CSV file
    print(f"Reading {CSV_FILE}...")
    rows = []
    with open(CSV_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    print(f"Read {len(rows)} rows from CSV")
    
    # Add new columns
    print("Processing rows...")
    for i, row in enumerate(rows):
        print(f"{i + 1}/{len(rows)} ",end="")
        
        # Parse datetime from CSV
        try:
            csv_datetime = datetime.fromisoformat(row['datetime'])
            dt_str = csv_datetime.strftime("%Y:%m:%d %H:%M:%S")
            print(f"{dt_str} ", end="")
        except (ValueError, KeyError) as e:
            print(f"Error parsing datetime in row {i}: {e}")
            row['photo_link'] = ""
            row['location'] = ""
            continue
        
        # Find matching photo
        matching_photo = find_matching_photo(dt_str, photos_dict)
        row['photo_link'] = matching_photo if matching_photo else ""
        
        # Reverse geocode coordinates
        try:
            latitude = float(row['iss_latitude'])
            longitude = float(row['iss_longitude'])
            row['location'] = reverse_geocode(latitude, longitude)
            # Add delay to avoid rate limiting from Nominatim
            time.sleep(1)
        except (ValueError, KeyError) as e:
            print(f"Error processing coordinates in row {i}: {e}")
            row['location'] = ""
    
    # Write enriched data
    print(f"Writing enriched data to {OUTPUT_FILE}...")
    fieldnames = list(rows[0].keys()) if rows else []
    
    with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    
    print(f"Done! Enriched CSV saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
