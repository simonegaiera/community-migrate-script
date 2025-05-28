import json
from pymongo import MongoClient, errors
from bson import json_util
from dotenv import load_dotenv
import os
import sys
import csv

# Load environment variables from .env file
dotenv_path = '.env'
if not os.path.exists(dotenv_path):
    print(f"Error: .env file not found at path {dotenv_path}", file=sys.stderr)
    sys.exit(1)

load_dotenv(dotenv_path)

# Get variables from environment
required_variables = [
    'MONGO_URL',
    'MONGO_DATABASE_NAME',
    'MONGO_COLLECTION_NAME',
    'JSON_FILE_PATH',
    'RESULT_FILE_PATH'
]

missing_variables = [var for var in required_variables if os.getenv(var) is None]
if missing_variables:
    print(f"Error: Missing required environment variables: {', '.join(missing_variables)}", file=sys.stderr)
    sys.exit(1)

cluster_url = os.getenv('MONGO_URL')
database_name = os.getenv('MONGO_DATABASE_NAME')
collection_name = os.getenv('MONGO_COLLECTION_NAME')
json_file_path = os.getenv('JSON_FILE_PATH')
result_file_path = os.getenv('RESULT_FILE_PATH')

# Load JSON data from the file, parsing EJSON Extended JSON (so $numberLong → int/Int64)
try:
    # first try UTF-8, if that fails fall back to UTF-16
    try:
        with open(json_file_path, 'r', encoding='utf-8') as file:
            raw = file.read()
    except UnicodeDecodeError:
        with open(json_file_path, 'r', encoding='utf-16') as file:
            raw = file.read()
    data = json_util.loads(raw)
except FileNotFoundError:
    print(f"Error: JSON file not found at path {json_file_path}", file=sys.stderr)
    sys.exit(1)
except (json.JSONDecodeError, ValueError) as e:
    print(f"Error: Failed to decode JSON/EJSON from file {json_file_path}: {e}", file=sys.stderr)
    sys.exit(1)

# Connect to MongoDB Atlas
try:
    client = MongoClient(cluster_url)
    db = client.get_database(database_name)
except errors.ConnectionFailure as e:
    print(f"Error: Failed to connect to MongoDB Atlas: {e}", file=sys.stderr)
    sys.exit(1)

# Drop the collection if it exists
if collection_name in db.list_collection_names():
    db.drop_collection(collection_name)
    print(f"Collection {collection_name} dropped.")

collection = db[collection_name]

# Insert the loaded data into MongoDB
try:
    if isinstance(data, list):
        collection.insert_many(data)
    elif isinstance(data, dict):
        collection.insert_one(data)
    else:
        raise ValueError("Unexpected JSON format")
    print('Data successfully saved to MongoDB Atlas!')
except Exception as e:
    print(f"Error: Failed to insert data into MongoDB: {e}.", file=sys.stderr)
    sys.exit(1)


result = db[collection_name].aggregate([
    {
        '$match': {
            'db': {
                '$exists': True
            }
        }
    }, {
        '$group': {
            '_id': '$db', 
            'fsTotalSize': {
                '$max': '$fsTotalSize'
            }, 
            'indexSize': {
                '$sum': '$indexSize'
            }
        }
    }, {
        '$project': {
            '_id': 0, 
            'project': '$_id', 
            'fsTotalSize': {
                '$round': [
                    {
                        '$divide': [
                            '$fsTotalSize', 1024 * 1024 * 1024
                        ]
                    }, 3
                ]
            }, 
            'indexSize': {
                '$round': [
                    {
                        '$divide': [
                            '$indexSize', 1024 * 1024 * 1024
                        ]
                    }, 3
                ]
            }
        }
    }
])

# Convert the result to a list
result_list = list(result)

# Extract the fieldnames from the first document
fieldnames = result_list[0].keys() if result_list else []

# Write the results to a CSV file
with open(result_file_path, mode="w", newline="") as file:
    writer = csv.DictWriter(file, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(result_list)

print(f"Aggregation result written to {result_file_path}")
