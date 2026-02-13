import json
import os
from datetime import datetime

DATA_FILE = "data/farmers_data.json"

def get_farmer_data(farmer_id=None):
    """Load farmer data from JSON file. If farmer_id provided, returns specific data."""
    if not os.path.exists(DATA_FILE):
        return {}
    
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if farmer_id:
                return data.get(str(farmer_id), {})
            return data
    except Exception as e:
        print(f"Error loading data: {e}")
        return {}

def save_farmer_data(farmer_id, data):
    """Save farmer data to JSON file keyed by farmer_id."""
    try:
        # Load existing
        all_data = get_farmer_data()
        
        # Update specific farmer
        all_data[str(farmer_id)] = data
        
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(all_data, f, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error saving data: {e}")
        return False

def clear_farmer_data(farmer_id=None):
    """Clear the tracking data. If farmer_id provided, clears only that farmer."""
    if not os.path.exists(DATA_FILE): return True
    
    try:
        if farmer_id:
            all_data = get_farmer_data()
            if str(farmer_id) in all_data:
                del all_data[str(farmer_id)]
                with open(DATA_FILE, "w", encoding="utf-8") as f:
                    json.dump(all_data, f, indent=4, ensure_ascii=False)
        else:
            # Clear all
            os.remove(DATA_FILE)
        return True
    except OSError as e:
        print(f"Error deleting data file: {e}")
        return False
    return True
