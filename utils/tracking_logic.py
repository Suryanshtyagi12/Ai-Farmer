from datetime import datetime, date

# Simple crop stage logic based on days
# This is a general approximation. Real logic would depend on specific crop type.
STAGES = {
    "Wheat": [
        (0, 7, "Germination"),
        (8, 25, "Crown Root Initiation"),
        (26, 45, "Tillering"),
        (46, 65, "Jointing"),
        (66, 85, "Flowering"),
        (86, 105, "Milking"),
        (106, 120, "Dough"),
        (121, 140, "Maturity")
    ],
    "Rice": [
        (0, 10, "Germination"),
        (11, 30, "Seedling"),
        (31, 60, "Tillering"),
        (61, 90, "Panicle Initiation"),
        (91, 110, "Flowering"),
        (111, 140, "Grain Filling"),
        (141, 150, "Maturity")
    ],
    "General": [
        (0, 15, "Germination/Seedling"),
        (16, 45, "Vegetative Growth"),
        (46, 75, "Flowering/Reproductive"),
        (76, 105, "Fruit Setting/Grain Filling"),
        (106, 140, "Maturity/Harvest")
    ]
}

def calculate_crop_age(plantation_date_str):
    """
    Calculate age in days.
    plantation_date_str: "YYYY-MM-DD"
    """
    try:
        if isinstance(plantation_date_str, date):
            p_date = plantation_date_str
        else:
            p_date = datetime.strptime(plantation_date_str, "%Y-%m-%d").date()
            
        today = date.today()
        delta = today - p_date
        return max(0, delta.days)
    except Exception as e:
        print(f"Error calculating age: {e}")
        return 0

def get_crop_stage(crop_name, age_days):
    """
    Determine crop stage based on age.
    """
    # Normalize crop name match
    crop_key = "General"
    for key in STAGES:
        if key.lower() in crop_name.lower():
            crop_key = key
            break
            
    schedule = STAGES[crop_key]
    
    current_stage = "Unknown"
    for start, end, stage_name in schedule:
        if start <= age_days <= end:
            current_stage = stage_name
            break
    
    if current_stage == "Unknown" and age_days > schedule[-1][1]:
        current_stage = "Harvested / Post-Maturity"
        
    return current_stage

def get_mock_weather(location):
    """
    Mock weather data for demo purposes.
    In a real app, this would call an API like OpenWeatherMap.
    """
    return {
        "temp": "28°C",
        "condition": "Sunny",
        "humidity": "60%",
        "forecast": "No rain expected in next 3 days"
    }
