import sys
import os
import json

# Fix imports to allow importing from src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.utils.logger import log_experiment, ActionType

def test_logging():
    print("🧪 Testing Logger...")

    # 1. Try to log a fake experiment
    try:
        log_experiment(
            agent_name="Data_Officer_Verified", # Changed name to confirm new run
            model_used="Test-Model-1.0",
            action=ActionType.ANALYSIS,
            details={
                "file_analyzed": "test_file.py",
                "input_prompt": "System Check",
                "output_response": "System OK"
            },
            status="SUCCESS"
        )
        print("✅ Function executed without crashing.")
    except Exception as e:
        print(f"❌ CRASH: Logger failed to run. Error: {e}")
        return

    # 2. Verify the file was actually created
    log_path = os.path.join("logs", "experiment_data.json")
    if os.path.exists(log_path):
        print(f"✅ Log file found at: {log_path}")
        
        # 3. Verify JSON content integrity
        try:
            with open(log_path, 'r') as f:
                data = json.load(f)
                # Check the LAST entry
                last_entry = data[-1]
                
                # Check for the correct key "agent" (not agent_name)
                if "agent" in last_entry and last_entry['agent'] == "Data_Officer_Verified":
                    print("✅ Data integrity verified: Entry saved correctly.")
                else:
                    print(f"❌ ERROR: Data mismatch! Found: {last_entry}")
        except json.JSONDecodeError:
            print("❌ ERROR: File exists but contains invalid JSON!")
    else:
        print("❌ ERROR: Log file was NOT created.")

if __name__ == "__main__":
    test_logging()