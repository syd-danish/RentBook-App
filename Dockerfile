# Use the official Python base image
FROM python:3.11-slim

# Set working directory inside container
WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy rest of the application files
COPY . .

# Ensure SQLite DB is created with correct permissions (optional)
RUN touch rentbook.db && chmod 666 rentbook.db

# Expose the port Flask runs on
EXPOSE 80

# Run the Flask app
CMD ["python", "main.py"]
