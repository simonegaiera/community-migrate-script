import os
import json
import re
from dotenv import load_dotenv
import os
import sys

# Load environment variables from .env file
dotenv_path = '.env'
if not os.path.exists(dotenv_path):
    print(f"Error: .env file not found at path {dotenv_path}", file=sys.stderr)
    sys.exit(1)

load_dotenv(dotenv_path)

directory_path = os.getenv('DATA_PATH')
output_file = os.getenv('JSON_FILE_PATH')

def sanitize_json_block(block):
    # Replace custom MongoDB types with placeholders while extracting values
    block = re.sub(r'Timestamp\(([^,]+), \d+\)', r'\1', block)
    block = re.sub(r'BinData\(\d+,\s*\"([^\"]+)\"\)', r'"\1"', block)
    block = re.sub(r'NumberLong\("(\d+)"\)', r'\1', block)
    block = re.sub(r'NumberLong\((\d+)\)', r'\1', block)
    block = re.sub(r'NumberInt\((\d+)\)', r'\1', block)
    return block

def extract_json_blocks(filepath):
    json_blocks = []
    with open(filepath, 'r', encoding='utf-8') as file:
        content = file.read()
        # Improved regex pattern to match JSON objects more effectively
        json_pattern = re.compile(r'\{(?:[^{}]*|\{(?:[^{}]*|\{[^{}]*\})*\})*\}', re.DOTALL)
        matches = json_pattern.findall(content)
        for match in matches:
            sanitized_block = sanitize_json_block(match)
            try:
                json_obj = json.loads(sanitized_block)
                json_blocks.append(json_obj)
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON from block in file: {filepath}\nBlock:{sanitized_block}\nError: {e}")
    return json_blocks

def read_json_files(directory):
    json_list = []
    
    # Iterate over all files in the directory
    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)
        
        # Check if the current path is a file
        if os.path.isfile(filepath):
            json_blocks = extract_json_blocks(filepath)
            filename_without_ext = os.path.splitext(filename)[0]  # Remove the .txt extension
            for json_obj in json_blocks:
                json_obj['filename'] = filename_without_ext
                json_list.append(json_obj)
    
    return json_list

# Remove the result file if it exists
if os.path.exists(output_file):
    os.remove(output_file)
    print(f"Existing result file '{output_file}' has been removed.")

# Read JSON files and compile them into an array
json_array = read_json_files(directory_path)

# Output the combined array as JSON
with open(output_file, 'w', encoding='utf-8') as outfile:
    json.dump(json_array, outfile, indent=4)

print(f"Combined JSON output has been written to: {output_file}")