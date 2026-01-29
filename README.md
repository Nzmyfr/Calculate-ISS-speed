# Calculate-ISS-speed

## Overview

**Calculate-ISS-speed** is a Python program that calculates the average speed of the International Space Station (ISS) by capturing multiple images using a Raspberry Pi camera, analyzing their timestamps, and comparing ISS orbital positions. The program also collects comprehensive sensor data from the Sense HAT module during the measurement period.

## Program Description

### Main Functionality

The program performs the following operations:

1. **Image Capture**: Takes periodic photos using the Picamera module
2. **EXIF Timestamp Extraction**: Extracts precise timestamps from each photo's EXIF metadata
3. **ISS Position Tracking**: Uses the astro_pi_orbit library to determine ISS positions at different times
4. **Speed Calculation**: Compares ISS positions between consecutive measurements to calculate instantaneous speed
5. **Average Calculation**: Computes the average ISS speed over multiple measurements
6. **Sensor Data Collection**: Records environmental and orientation data from the Sense HAT
7. **Data Export**: Saves all measurements to a CSV file and the final result to a text file

### How It Works

- Starts by taking an initial photo and extracting its timestamp
- Enters a timed loop (default: 10 minutes) that:
  - Captures new photos at intervals
  - Extracts timestamps from EXIF data
  - Calculates the time difference between consecutive measurements
  - Determines ISS positions using Skyfield astronomical calculations
  - Computes speed based on distance traveled and time elapsed
  - Records sensor readings (temperature, pressure, humidity, orientation, magnetometer, accelerometer, gyroscope)
  - Manages image files to conserve disk space
- Upon completion, calculates and saves the average ISS speed

## Requirements

### Dependencies

- **picamzero**: Raspberry Pi camera control
- **exif**: EXIF data extraction from images
- **astro_pi_orbit**: ISS position calculations
- **skyfield**: Astronomical calculations and timescale management
- **sense_hat**: Sense HAT sensor data collection

### Hardware

- Raspberry Pi (with camera module)
- Sense HAT board
- Picamera (compatible with Raspberry Pi)

## Output Files

- **data.csv**: Contains all sensor measurements over time:
  - Temperature, pressure, humidity
  - RGB color sensor data
  - Orientation (yaw, pitch, roll)
  - Magnetometer readings
  - Accelerometer data
  - Gyroscope data
  - Timestamp and ISS position data
  - Calculated ISS speed for each measurement

- **result.txt**: Final average ISS speed (in km/s) calculated from all measurements

## Configuration

The following parameters can be modified in `main.py`:

- `time_delta`: Duration to run the program (in minutes, default: 10)
- `file_path`: Output file path for results (default: 'result.txt')
- `sense.color.gain`: Sensor color gain value (default: 60)
- `sense.color.integration_cycles`: Sensor integration cycles (default: 64)

## Authors

- Alexander Tonev
- Alexander Veselinov
- **Mentor**: Nikolay Cholakov

## Version

Version 1.0 (January 29, 2026)