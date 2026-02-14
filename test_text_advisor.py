"""Test the text-based disease advisor"""
from utils.text_disease_advisor import text_disease_advisor

print("Testing Text-Based Disease Advisor")
print("=" * 60)

advisory = text_disease_advisor.get_advisory(
    prompt="I see brown spots on my tomato leaves",
    crop_mention="tomato"
)

print(advisory)
print("\n" + "=" * 60)
print("✅ Text-based disease advisor working!")
