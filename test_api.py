#!/usr/bin/env python3
"""
Test script for the Person Measurement API.

Usage:
    python test_api.py path/to/image.jpg 183
"""

import sys
import requests
import json

def test_api(endpoint, image_path, height_cm):
    """Test an API endpoint with an image."""
    try:
        with open(image_path, 'rb') as f:
            files = {'file': f}
            data = {'height_cm': height_cm}

            print(f"Testing {endpoint} with {image_path}...")
            response = requests.post(f"http://localhost:8000{endpoint}", files=files, data=data)

            if response.status_code == 200:
                result = response.json()
                print("Success!")
                print(json.dumps(result, indent=2))
            else:
                print(f"Error: {response.status_code}")
                print(response.text)

    except FileNotFoundError:
        print(f"Image file not found: {image_path}")
    except requests.exceptions.ConnectionError:
        print("Connection error: Is the API server running?")
    except Exception as e:
        print(f"Error: {e}")

def main():
    if len(sys.argv) < 3:
        print("Usage: python test_api.py <image_path> <height_cm>")
        print("Example: python test_api.py person.jpg 183")
        sys.exit(1)

    image_path = sys.argv[1]
    height_cm = float(sys.argv[2])

    # Test both endpoints
    test_api("/measure_person", image_path, height_cm)
    print("\n" + "="*50 + "\n")
    test_api("/measure_person_sam2", image_path, height_cm)

if __name__ == "__main__":
    main()