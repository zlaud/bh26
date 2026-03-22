import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.risk_engine import compute_all_food_risks

def main():
    print("Recomputing food risks...")
    risks = compute_all_food_risks()
    high = [f for f, r in risks.items() if r["risk_label"] == "HIGH"]
    medium = [f for f, r in risks.items() if r["risk_label"] == "MEDIUM"]
    low = [f for f, r in risks.items() if r["risk_label"] == "LOW"]
    print(f"Done: {len(risks)} foods scored")
    print(f"HIGH:   {', '.join(high) or 'none'}")
    print(f"MEDIUM: {', '.join(medium) or 'none'}")
    print(f"LOW:    {', '.join(low) or 'none'}")

main()