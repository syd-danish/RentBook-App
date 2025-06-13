# Use the official Python base image
FROM python:3.11-slim

# Set working directory inside container
WORKDIR /app

# Copy all files to the working directory
COPY . .


# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port Flask runs on (optional, but good practice)
EXPOSE 80

# Run the Flask app
CMD ["python", "main.py"]
