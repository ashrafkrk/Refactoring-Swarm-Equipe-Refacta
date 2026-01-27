import argparse
import sys
import os
import google.generativeai as genai  # <--- NEW IMPORT
from dotenv import load_dotenv
from src.utils.logger import log_experiment, ActionType

load_dotenv()

# --- 1. SETUP GEMINI (The part we just tested) ---
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    print("❌ CRITICAL ERROR: API Key missing.")
    sys.exit(1)

genai.configure(api_key=api_key)
# We use the specific alias that worked for you:
MODEL_NAME = 'models/gemini-flash-latest' 
model = genai.GenerativeModel(MODEL_NAME)
# -------------------------------------------------

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--target_dir", type=str, required=True)
    args = parser.parse_args()

    if not os.path.exists(args.target_dir):
        print(f"❌ Dossier {args.target_dir} introuvable.")
        sys.exit(1)

    print(f"🚀 DEMARRAGE SUR : {args.target_dir}")

    # Log the startup success
    log_experiment(
        agent_name="System",
        model_used=MODEL_NAME, # Logs the correct model
        action=ActionType.DEBUG,
        details={
            "info": f"Target: {args.target_dir}",
            "input_prompt": "System Init",
            "output_response": "Ready"
        },
        status="SUCCESS"
    )

    print("✅ MISSION_COMPLETE (System Ready)")

if __name__ == "__main__":
    main()