"""
Text-Based Disease Advisory System
Provides helpful disease detection guidance when vision APIs are unavailable
"""

class TextDiseaseAdvisor:
    def __init__(self):
        self.disease_guide = """
**Common Crop Diseases - Visual Identification Guide:**

🌾 **WHEAT:**
- **Rust**: Orange/brown pustules on leaves
- **Blight**: Dark brown/black spots on leaves
- **Mildew**: White powdery coating on leaves

🌾 **RICE:**
- **Blast**: Diamond-shaped lesions with gray centers
- **Bacterial Blight**: Water-soaked lesions turning yellow
- **Sheath Rot**: Rotting of leaf sheaths

🌾 **TOMATO:**
- **Early Blight**: Dark spots with concentric rings
- **Late Blight**: Water-soaked lesions, white mold
- **Leaf Curl**: Curling and yellowing of leaves

🌾 **POTATO:**
- **Late Blight**: Brown/blackspots, white fungal growth
- **Early Blight**: Circular spots with target pattern
- **Scab**: Rough, corky spots on tubers

**General Disease Signs:**
- Spots (yellow, brown, black, or white)
- Wilting or drooping leaves
- Discoloration or yellowing
- Mold or fungal growth
- Stunted growth
- Holes or eaten areas

**Treatment Recommendations:**
1. Remove affected plant parts
2. Apply appropriate fungicide/pesticide
3. Improve air circulation
4. Avoid overhead watering
5. Rotate crops seasonally
6. Consult local agricultural extension office
"""
    
    def get_advisory(self, prompt="", crop_mention=""):
        """Returns disease identification guide and advisory"""
        return f"""
🔍 **Disease Detection Guide**

{self.disease_guide}

📝 **Your Question:** {prompt}

**Recommended Actions:**
1. Compare your crop's symptoms with the guide above
2. Take a clear photo and show it to your local agricultural expert
3. Contact your nearest agricultural extension office
4. Consider using government agricultural helplines

**Note:** Vision AI is temporarily unavailable. For accurate disease identification, please consult a local agricultural expert or extension service.
"""

text_disease_advisor = TextDiseaseAdvisor()
