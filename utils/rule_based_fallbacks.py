def get_crop_fallback(location, season):
    """Simple rule-based crop suggestions if AI fails."""
    recommendations = {
        "Kharif": ["Rice", "Maize", "Cotton"],
        "Rabi": ["Wheat", "Mustard", "Gram"],
        "Zaid": ["Watermelon", "Cucumber", "Moong Dal"]
    }
    crops = recommendations.get(season, ["General Vegetables", "Millets"])
    return f"Based on common patterns for {season} in {location}, you might consider: {', '.join(crops)}. (Note: This is a rule-based fallback)."

def get_disease_fallback():
    """Fallback if image detection fails."""
    return "I am currently unable to analyze the image. Please ensure the photo is clear and try again, or consult a local agricultural expert."

def get_irrigation_fallback(crop):
    """Fallback for irrigation."""
    return f"Standard irrigation for {crop} usually involves maintaining moderate soil moisture. Avoid overwatering during flowering stages. (Rule-based advice)."
