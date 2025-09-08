#!/bin/bash

# Get port from Railway environment variable, default to 8501
PORT=${PORT:-8501}

# Start Streamlit
streamlit run main.py --server.port=$PORT --server.address=0.0.0.0
