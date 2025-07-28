import json
import os

def save_json(data, path):
    print(f"Attempting to save JSON to: {path}")
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"Successfully saved JSON to: {path}")
        # Verify the file was created
        if os.path.exists(path):
            print(f"File exists after saving: {path}")
            print(f"File size: {os.path.getsize(path)} bytes")
        else:
            print(f"ERROR: File does not exist after saving: {path}")
    except Exception as e:
        print(f"ERROR saving JSON to {path}: {e}")

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
