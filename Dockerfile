# Use the latest official Python image as a base image
FROM python:latest

# Set the working directory in the Docker container
WORKDIR /app

# Copy the content of the local src directory to the working directory
COPY . .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Specify the command to run on container start
ENTRYPOINT ["python", "onet_scraper.py"]