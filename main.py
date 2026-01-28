import argparse
import sys
import os
import google.generativeai as genai
from dotenv import load_dotenv

# --- CUSTOM MODULES ---
from src.utils.logger import log_experiment, ActionType
from src.tools.toolbox import scan_directory, read_file_content, save_file_content
from src.prompts.instructions import SYSTEM_ROLE, ANALYSIS_TEMPLATE, REFACTOR_TEMPLATE

# --- CONFIGURATION ---
load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    print("❌ CRITICAL ERROR: API Key missing in .env")
    sys.exit(1)

# Use the working free model we found
genai.configure(api_key=api_key)
MODEL_NAME = 'models/gemini-flash-latest'
model = genai.GenerativeModel(MODEL_NAME)

def clean_ai_response(text):
    """
    Removes Markdown formatting (```python ... ```) if the AI ignores our strict prompt.
    """
    clean = text.replace("```python", "").replace("```", "").strip()
    return clean

def process_file(file_path):
    """
    The Core Loop: Read -> Analyze -> Refactor -> Save
    """
    print(f"\n📄 Processing: {file_path}...")
    
    # 1. READ
    original_code = read_file_content(file_path)
    if not original_code:
        return # Skip if read failed

    # 2. ANALYZE (Log Only)
    try:
        print("   👀 Agent analyzing...")
        analysis_prompt = ANALYSIS_TEMPLATE.format(code_content=original_code)
        
        # Call Gemini
        response = model.generate_content(analysis_prompt)
        analysis_result = response.text

        # Log the Analysis
        log_experiment(
            agent_name="Analyst_Agent",
            model_used=MODEL_NAME,
            action=ActionType.ANALYSIS,
            details={
                "file": file_path,
                "input_prompt": "Analyze Code Issues", # Simplified for log readability
                "output_response": analysis_result
            },
            status="SUCCESS"
        )
    except Exception as e:
        print(f"   ❌ Analysis Failed: {e}")
        return # If analysis fails, we probably shouldn't refactor blind

    # 3. REFACTOR (The Fix)
    try:
        print("   🛠️  Agent refactoring...")
        # Combine Persona + Task + Code
        full_prompt = f"{SYSTEM_ROLE}\n{REFACTOR_TEMPLATE.format(code_content=original_code)}"
        
        # Call Gemini
        response = model.generate_content(full_prompt)
        refactored_code = clean_ai_response(response.text)

        # Log the Fix
        log_experiment(
            agent_name="Refactor_Agent",
            model_used=MODEL_NAME,
            action=ActionType.FIX,
            details={
                "file": file_path,
                "input_prompt": "Refactor Code (Strict Mode)",
                "output_response": "Code replaced with refactored version."
            },
            status="SUCCESS"
        )

        # 4. SAVE
        save_file_content(file_path, refactored_code)
        print("   ✅ File updated successfully.")

    except Exception as e:
        print(f"   ❌ Refactoring Failed: {e}")
        log_experiment(
            agent_name="Refactor_Agent",
            model_used=MODEL_NAME,
            action=ActionType.DEBUG,
            details={"error": str(e)},
            status="FAILED"
        )

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--target_dir", type=str, required=True, help="Path to the folder to refactor")
    args = parser.parse_args()

    target = args.target_dir

    if not os.path.exists(target):
        print(f"❌ Error: Target directory '{target}' does not exist.")
        sys.exit(1)

    print(f"🚀 STARTING SWARM ON: {target}")
    
    # Get all code files
    files = scan_directory(target)
    
    if not files:
        print("⚠️  No code files found to refactor.")
        sys.exit(0)

    # Run the swarm on every file
    for file in files:
        process_file(file)

    print("\n🏁 MISSION COMPLETE. All files processed.")

if __name__ == "__main__":
    main()