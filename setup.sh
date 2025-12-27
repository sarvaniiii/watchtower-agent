#!/bin/bash
# setup.sh - Fix for Streamlit Cloud dependencies

# Update pip to a compatible version
pip install --upgrade "pip<24.0"

# Install requirements
pip install -r requirements.txt