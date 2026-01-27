import argparse
import sys
import os
from dotenv import load_dotenv
# We must import ActionType to satisfy the strict logger
from src.utils.logger import log_experiment, ActionType 

load_dotenv()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--target_dir", type=str, required=True)
    args = parser.parse_args()

    if not os.path.exists(args.target_dir):
        print(f"❌ Dossier {args.target_dir} introuvable.")
        sys.exit(1)

    print(f"🚀 DEMARRAGE SUR : {args.target_dir}")
    
    # --- CORRECTED LOGGING CALL ---
    # The logger is strict. We must provide all 5 arguments.
    # We use ActionType.DEBUG because 'STARTUP' is not a valid action.
    log_experiment(
        agent_name="System",
        model_used="Setup",     # Just a label
        action=ActionType.DEBUG, # Must be a valid Enum
        details={
            "info": f"Target: {args.target_dir}",
            # These 2 keys are MANDATORY for ActionType.DEBUG or the logger crashes again
            "input_prompt": "System Init", 
            "output_response": "Ready"
        },
        status="SUCCESS"
    )
    # ------------------------------

    print("✅ MISSION_COMPLETE")

if __name__ == "__main__":
    main()