import os

# Files we want to refactor
ALLOWED_EXTENSIONS = {'.py', '.java', '.c', '.cpp', '.js', '.ts', '.html', '.css'}

# Folders we MUST ignore to avoid breaking the project
IGNORED_DIRS = {'venv', '.git', '__pycache__', 'logs', 'tests', 'node_modules', '.idea', '.vscode'}

def scan_directory(root_dir):
    """
    Recursively finds all valid code files in the target directory.
    Returns a list of file paths (e.g., ['sandbox/bad_code.py', ...])
    """
    if not os.path.exists(root_dir):
        print(f"❌ Error: Directory '{root_dir}' does not exist.")
        return []

    code_files = []

    print(f"🔍 Scanning directory: {root_dir}...")
    
    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Filter out ignored directories in-place
        dirnames[:] = [d for d in dirnames if d not in IGNORED_DIRS]

        for filename in filenames:
            ext = os.path.splitext(filename)[1].lower()
            if ext in ALLOWED_EXTENSIONS:
                full_path = os.path.join(dirpath, filename)
                # Normalize path separators (fix Windows vs Linux slash issues)
                clean_path = full_path.replace('\\', '/')
                code_files.append(clean_path)

    print(f"✅ Found {len(code_files)} valid files.")
    return code_files

def read_file_content(file_path):
    """
    Reads the content of a file safely.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"❌ Error reading {file_path}: {e}")
        return None

def save_file_content(file_path, new_content):
    """
    Overwrites the file with the new refactored code.
    """
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"💾 Saved changes to: {file_path}")
        return True
    except Exception as e:
        print(f"❌ Error saving {file_path}: {e}")
        return False