# MongoDB Community to Atlas Sizing Script

## Overview
This tool collects storage and index sizing information from a MongoDB (or Amazon DocumentDB) cluster and produces a CSV report. It is intended to help size a migration to MongoDB Atlas.

The workflow is two steps:
1. **`getMongoInfo.js`** — runs against the source cluster via `mongosh` and dumps stats to a JSON file.
2. **`loading-script.py`** — loads that JSON file into an Atlas collection and writes a per-collection CSV report.

---

## Requirements

Install Python dependencies:
```bash
pip install -r requirements.txt
```

---

## Step 1: Collect stats from the source cluster

### MongoDB / Atlas
```bash
mongosh "mongodb+srv://<user>:<password>@<cluster>.mongodb.net" \
  --file getMongoInfo.js --norc --quiet > output.json
```

### Amazon DocumentDB
```bash
mongosh <cluster-endpoint>:27017 \
  --tls --tlsCAFile global-bundle.pem --retryWrites=false \
  --username <user> --password <password> \
  --file getMongoInfo.js --norc --quiet > output.json
```

The output file defaults to `output.json`. Use any filename you like — you will reference it in the next step.

---

## Step 2: Configure environment variables

Create a `.env` file in the project root with the following variables:

```ini
# Connection string for the Atlas cluster where stats will be loaded
MONGO_URL=mongodb+srv://<user>:<password>@<cluster>.mongodb.net

# Atlas database and collection to store the raw stats
MONGO_DATABASE_NAME=<database>
MONGO_COLLECTION_NAME=<collection>

# Path to the JSON file produced in Step 1
JSON_FILE_PATH=output.json

# Path where the CSV report will be written
RESULT_FILE_PATH=result.csv
```

---

## Step 3: Load and analyse

```bash
python loading-script.py
```

This will:
1. Drop and recreate the target Atlas collection.
2. Insert the raw stats from the JSON file.
3. Run an aggregation that extracts per-collection metrics.
4. Write the results to the CSV file defined in `RESULT_FILE_PATH`.

---

## Output

The CSV report contains one row per collection with the following columns:

| Column | Description |
|---|---|
| `namespace` | `database.collection` |
| `count` | Number of documents |
| `avgObjSize_bytes` | Average document size in bytes |
| `dataSize_MB` | Uncompressed data size in MB |
| `storageSize_MB` | Allocated disk size in MB |
| `totalIndexSize_MB` | Total size of all indexes in MB |
| `totalSize_MB` | `storageSize` + `totalIndexSize` in MB |
| `nindexes` | Number of indexes |
| `capped` | Whether the collection is capped |
