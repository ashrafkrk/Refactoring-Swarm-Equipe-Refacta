import os

# Define the directory for our test batch
TEST_DIR = "sandbox/test_batch"
os.makedirs(TEST_DIR, exist_ok=True)

# 1. SYNTAX ERROR (The Judge's Favorite)
# Missing colon and indentation error
code_syntax = """
def greet(name)
print("Hello " + name)
"""

# 2. SECURITY VULNERABILITY (The Auditor's Favorite)
# Using eval() is dangerous
code_security = """
def calculate_price(user_input):
    # DANGEROUS: executing raw string as code
    return eval(user_input)

print(calculate_price("10 + 20"))
"""

# 3. LOGIC BUG (The Fixer's Challenge)
# Infinite loop risk (i is never incremented)
code_logic = """
def count_to_five():
    i = 0
    while i < 5:
        print(i)
        # BUG: Forgot to increment i, infinite loop!
"""

# 4. MESSY STYLE (PEP8 Nightmare)
# Bad names, no spaces, mixed imports
code_style = """
import os,sys
def F(x,y): return x+y
print( F( 10,20 ) )
"""

# 5. DEPRECATED CODE
# Using old python patterns
code_legacy = """
def process_data(data):
    # Old way to format strings
    print "Processing: %s" % data 
    return True
"""

# Dictionary mapping filenames to content
tests = {
    "test_syntax.py": code_syntax,
    "test_security.py": code_security,
    "test_logic.py": code_logic,
    "test_style.py": code_style,
    "test_legacy.py": code_legacy
}

# Write files
print(f"🚀 Generating 5 test files in {TEST_DIR}...")
for filename, content in tests.items():
    path = os.path.join(TEST_DIR, filename)
    with open(path, "w") as f:
        f.write(content)
    print(f"   📄 Created: {filename}")

print("\n✅ Done! Now run: python main.py --target_dir ./sandbox/test_batch")