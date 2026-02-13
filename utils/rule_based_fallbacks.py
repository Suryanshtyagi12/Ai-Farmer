def get_crop_fallback(location, season, lang='en'):
    """Simple rule-based crop suggestions if AI fails."""
    recommendations = {
        "Kharif": ["Rice", "Maize", "Cotton"],
        "Rabi": ["Wheat", "Mustard", "Gram"],
        "Zaid": ["Watermelon", "Cucumber", "Moong Dal"]
    }
    
    # Translate season keys if needed (simple mapping)
    season_map = {"खरीफ": "Kharif", "रबी": "Rabi", "जायद": "Zaid"}
    mapped_season = season_map.get(season, season)
    
    crops = recommendations.get(mapped_season, ["General Vegetables", "Millets"])
    crop_list = ', '.join(crops)
    
    if lang == 'hi':
        return f"{location} में {season} के लिए सामान्य रुझानों के आधार पर, आप इन फसलों पर विचार कर सकते हैं: {crop_list}। (नोट: यह एक नियम-आधारित सुझाव है)।"
    else:
        return f"Based on common patterns for {season} in {location}, you might consider: {crop_list}. (Note: This is a rule-based fallback)."

def get_disease_fallback(lang='en'):
    """Fallback if image detection fails."""
    if lang == 'hi':
        return "मैं अभी इस छवि का विश्लेषण करने में असमर्थ हूँ। कृपया सुनिश्चित करें कि फोटो साफ है और पुनः प्रयास करें, या किसी स्थानीय कृषि विशेषज्ञ से सलाह लें।"
    else:
        return "I am currently unable to analyze the image. Please ensure the photo is clear and try again, or consult a local agricultural expert."

def get_irrigation_fallback(crop, soil_type="Unknown", location="Unknown", lang='en'):
    """Fallback for irrigation."""
    if lang == 'hi':
        return f"{crop} (मिट्टी: {soil_type}) के लिए मानक सिंचाई में आमतौर पर मध्यम नमी बनाए रखना शामिल है। फूल आने के समय अधिक पानी देने से बचें। (नियम-आधारित सलाह)।"
    else:
        return f"Standard irrigation for {crop} (Soil: {soil_type}) usually involves maintaining moderate soil moisture. Avoid overwatering during flowering stages. (Rule-based advice)."
