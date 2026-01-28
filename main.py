import argparse
import sys
import os
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from dotenv import load_dotenv

# --- CUSTOM MODULES ---
from src.utils.logger import log_experiment, ActionType
from src.tools.toolbox import scan_directory, read_file_content, save_file_content, check_syntax
from src.prompts.instructions import SYSTEM_ROLE, ANALYSIS_TEMPLATE, REFACTOR_TEMPLATE

# --- CONFIGURATION ---
load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    print("❌ CRITICAL ERROR: API Key missing in .env")
    sys.exit(1)

genai.configure(api_key=api_key)
MODEL_NAME = 'models/gemini-flash-latest'
model = genai.GenerativeModel(MODEL_NAME)

# --- SAFETY SETTINGS (CRITICAL FOR CODE ANALYSIS) ---
# We disable safety filters because analyzing buggy/virus code triggers false positives.
safety_settings = {
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
}

def get_response_text(response):
    """Safely extracts text from Gemini response to prevent crashes."""
    try:
        return response.text
    except ValueError:
        # If blocked or complex response, try to get parts or return empty
        if response.candidates:
            parts = response.candidates[0].content.parts
            if parts:
                return parts[0].text
        return ""

def clean_ai_response(text):
    """Cleans Markdown tags from generated code."""
    if not text: return ""
    clean = text.replace("```python", "").replace("```", "").strip()
    return clean

def process_file(file_path):
    print(f"\n📄 Processing: {file_path}...")
    
    original_code = read_file_content(file_path)
    if not original_code: return

    # --- 1. ANALYSIS (L'Auditeur) ---
    try:
        print("   👀 Agent Auditor: Analyzing...")
        # We capture the EXACT text sent to the AI
        analysis_prompt = ANALYSIS_TEMPLATE.format(code_content=original_code)
        
        response = model.generate_content(analysis_prompt, safety_settings=safety_settings)
        analysis_result = get_response_text(response)
        
        if not analysis_result:
            print("   ⚠️  Auditor: Response blocked by safety filters.")
            return

        log_experiment(
            agent_name="Auditor_Agent",
            model_used=MODEL_NAME,
            action=ActionType.ANALYSIS,
            details={
                "file": file_path, 
                "input_prompt": analysis_prompt,  # <--- UPDATED: Logs the FULL prompt
                "output_response": analysis_result[:500] + "..." # Truncate output to keep log readable, or keep full if you prefer
            },
            status="SUCCESS"
        )
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        return

    # --- 2. SELF-HEALING LOOP (Fix -> Test -> Retry) ---
    MAX_RETRIES = 3
    current_code = original_code
    error_context = "" 

    for attempt in range(1, MAX_RETRIES + 1):
        print(f"   🔄 Iteration {attempt}/{MAX_RETRIES}...")

        # --- A. GENERATION (Le Correcteur) ---
        try:
            print("   🛠️  Agent Fixer: Working...")
            
            if error_context:
                prompt = f"{SYSTEM_ROLE}\nFIX THIS ERROR:\n{error_context}\n\nIN CODE:\n{current_code}"
            else:
                prompt = f"{SYSTEM_ROLE}\n{REFACTOR_TEMPLATE.format(code_content=original_code)}"

            response = model.generate_content(prompt, safety_settings=safety_settings)
            new_code = clean_ai_response(get_response_text(response))
            
            if not new_code:
                print("   ❌ Fixer Error: Empty response. Retrying...")
                continue

            save_file_content(file_path, new_code)
            current_code = new_code

            log_experiment(
                agent_name="Fixer_Agent",
                model_used=MODEL_NAME,
                action=ActionType.FIX,
                details={
                    "file": file_path, 
                    "attempt": attempt, 
                    "input_prompt": prompt, # <--- UPDATED: Logs the FULL prompt
                    "output_response": "Code Generated (See file content)"
                },
                status="SUCCESS"
            )

        except Exception as e:
            print(f"   ❌ Fixer crashed: {e}")
            break

        # --- B. TESTING (Le Juge) ---
        print("   ⚖️  Agent Judge: Verifying syntax...")
        is_valid, error_msg = check_syntax(file_path)

        if is_valid:
            print("   ✅ JUDGE: Code is valid. Improvement accepted.")
            log_experiment(
                agent_name="Judge_Agent",
                model_used="System-Compiler",
                action=ActionType.DEBUG,
                details={
                    "file": file_path, 
                    "result": "PASS",
                    "input_prompt": f"check_syntax('{file_path}')", # Internal function call
                    "output_response": "Valid Syntax"
                },
                status="SUCCESS"
            )
            break
        else:
            print(f"   ⚠️ JUDGE: Check failed! Sending back to Fixer...")
            error_context = f"The previous code had a Syntax Error: {error_msg}. Fix it immediately."
            
            log_experiment(
                agent_name="Judge_Agent",
                model_used="System-Compiler",
                action=ActionType.DEBUG,
                details={
                    "file": file_path, 
                    "result": "FAIL", 
                    "error": error_msg,
                    "input_prompt": f"check_syntax('{file_path}')",
                    "output_response": f"Error: {error_msg}"
                },
                status="FAILED"
            )
            
            if attempt == MAX_RETRIES:
                print("   ❌ Maximum retries reached. Reverting file.")
                save_file_content(file_path, original_code)
                
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--target_dir", type=str, required=True, help="Path to the folder to refactor")
    args = parser.parse_args()

    target = args.target_dir

    if not os.path.exists(target):
        print(f"❌ Error: Target directory '{target}' does not exist.")
        sys.exit(1)

    print(f"🚀 STARTING SWARM ON: {target}")
    
    files = scan_directory(target)
    
    if not files:
        print("⚠️  No code files found to refactor.")
        sys.exit(0)

    for file in files:
        process_file(file)

    print("\n🏁 MISSION COMPLETE. All files processed.")

if __name__ == "__main__":
    main()