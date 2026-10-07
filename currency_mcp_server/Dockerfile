# Use the official Python lightweight image
FROM python:3.11-slim

WORKDIR /app

# Allow statements and log messages to immediately appear in the logs
ENV PYTHONUNBUFFERED=1 \
    PORT=8080

# Copy application files
COPY . /app

# Install dependencies directly using standard pip
RUN pip install --no-cache-dir "fastmcp>=4.0.0" "httpx>=0.28.1"

EXPOSE 8080

# Run the FastMCP server directly with python
CMD ["python", "server.py"]
