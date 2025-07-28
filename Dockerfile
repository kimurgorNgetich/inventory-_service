# Use official Python image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy code into container
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose Flask port
EXPOSE 5002

# Set environment variables
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=5002

# Run the Flask app
CMD ["flask", "run"]
