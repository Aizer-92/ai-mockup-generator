#!/bin/bash

# Get port from Railway environment variable, default to 8501
PORT=${PORT:-8501}

# Set Streamlit environment variables
export STREAMLIT_SERVER_PORT=$PORT
export STREAMLIT_SERVER_ADDRESS=0.0.0.0

# Start Streamlit
streamlit run main.py
