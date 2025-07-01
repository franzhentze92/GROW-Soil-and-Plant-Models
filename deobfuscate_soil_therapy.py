#!/usr/bin/env python3
"""
Deobfuscation script for soil-therapy.js
This script extracts the string array and reconstructs readable JavaScript code.
"""

import re
import json

def extract_string_array(js_content):
    """Extract the string array from the obfuscated code."""
    # Find the string array pattern - look for the _0x4cf6 function
    pattern = r'function _0x4cf6\(\)\{const _0x56f4d9=\[(.*?)\];return _0x56f4d9;\}'
    match = re.search(pattern, js_content, re.DOTALL)
    
    if not match:
        print("Could not find string array")
        return None
    
    # Extract the array content
    array_content = match.group(1)
    
    # Parse the array (remove quotes and split by comma)
    strings = []
    current_string = ""
    in_string = False
    escape_next = False
    
    for char in array_content:
        if escape_next:
            current_string += char
            escape_next = False
        elif char == '\\':
            escape_next = True
            current_string += char
        elif char == "'" or char == '"':
            if in_string:
                strings.append(current_string)
                current_string = ""
                in_string = False
            else:
                in_string = True
        elif in_string:
            current_string += char
    
    return strings

def deobfuscate_code(js_content, strings):
    """Replace obfuscated function calls with their string values."""
    if not strings:
        return js_content
    
    # Replace _0x22e629(0xXXX) calls with actual strings
    def replace_func(match):
        try:
            index = int(match.group(1), 16) - 0x18d  # Adjust for offset
            if 0 <= index < len(strings):
                return f'"{strings[index]}"'
            else:
                return match.group(0)
        except:
            return match.group(0)
    
    # Replace the obfuscated function calls
    deobfuscated = re.sub(r'_0x22e629\(0x([0-9a-fA-F]+)\)', replace_func, js_content)
    
    return deobfuscated

def main():
    # Read the original file
    with open('static/js/soil-therapy.js', 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("Extracting string array...")
    strings = extract_string_array(content)
    
    if strings:
        print(f"Found {len(strings)} strings in the array")
        print("First 10 strings:")
        for i, s in enumerate(strings[:10]):
            print(f"  {i}: {repr(s)}")
        
        print("\nDeobfuscating code...")
        deobfuscated = deobfuscate_code(content, strings)
        
        # Write the deobfuscated version
        with open('static/js/soil-therapy-deobfuscated.js', 'w', encoding='utf-8') as f:
            f.write(deobfuscated)
        
        print("Deobfuscated version saved to soil-therapy-deobfuscated.js")
        
        # Also save the string array for reference
        with open('static/js/soil-therapy-strings.json', 'w', encoding='utf-8') as f:
            json.dump(strings, f, indent=2, ensure_ascii=False)
        
        print("String array saved to soil-therapy-strings.json")
    else:
        print("Failed to extract string array")

if __name__ == "__main__":
    main() 