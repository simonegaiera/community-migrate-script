# MongoDB Community to Atlas Sizing Script

## Overview
This script helps you size your MongoDB Community deployment for migration to MongoDB Atlas. Follow the steps below to execute the script and store the results.

## Instructions

### Step 1: Run the Script
- Execute the `script.js` file to generate the necessary data.

### Step 2: Prepare Your Data
- Create a folder and place all the exported `.txt` files into it. Ensure that these files are correctly formatted for processing.

### Step 3: Configure Environment Variables
- Create an `.env` file in the same directory as your script. Modify the file to include the necessary configuration settings for your environment.

### Step 4: Parse the Data
- Run the command `python parse-script.py` to parse the data from the `.txt` files and write it into your MongoDB instance.

### Step 5: Review the Results
- The results of the parsing will be saved in a file named `result.txt`. Check this file for the output of the sizing analysis.

## Additional Notes
- Ensure you have the required permissions and dependencies installed before running the scripts.
