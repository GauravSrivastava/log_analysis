
# Use official Python image
FROM python:3.10-slim-bullseye

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y git && apt-get upgrade -y && rm -rf /var/lib/apt/lists/*

# Clone the GitHub repository containing the Streamlit app and logs
RUN git clone https://github.com/GauravSrivastava/log_analysis.git repo

# Copy app files from cloned repo
COPY /src/ ./src/
COPY /sample_data/logs ./sample_data/logs

# Install Python dependencies
RUN pip install --no-cache-dir pandas numpy matplotlib seaborn streamlit scipy

# Expose Streamlit port
EXPOSE 8501

# Run the Streamlit app
CMD ["streamlit", "run", "src/main_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
