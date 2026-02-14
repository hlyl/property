#!/bin/bash

# Script to refresh property data
# Clears the database and fetches fresh data based on current search criteria

echo "======================================================================"
echo "Property Data Refresh Script"
echo "======================================================================"
echo ""

# Step 1: Clear the database
echo "Step 1: Clearing test database..."
uv run python clear_database.py
if [ $? -ne 0 ]; then
    echo "Failed to clear database. Exiting."
    exit 1
fi

echo ""

# Step 2: Reset first_observed.json
echo "Step 2: Resetting first_observed.json..."
if [ -f "first_observed.json" ]; then
    mv first_observed.json first_observed.json.backup.$(date +%Y%m%d_%H%M%S)
    echo "Backed up existing first_observed.json"
fi
echo "{}" > first_observed.json
echo "Reset first_observed.json to empty"

echo ""

# Step 3: Fetch fresh data
echo "Step 3: Fetching fresh property data..."
echo "This may take a few minutes..."
uv run python main.py

if [ $? -eq 0 ]; then
    echo ""
    echo "======================================================================"
    echo "✓ Data refresh completed successfully!"
    echo "======================================================================"
    echo ""
    echo "You can now start the Streamlit app:"
    echo "  uv run streamlit run 01_Home.py"
    echo ""
else
    echo ""
    echo "======================================================================"
    echo "✗ Data fetch failed. Check errors above."
    echo "======================================================================"
    exit 1
fi
