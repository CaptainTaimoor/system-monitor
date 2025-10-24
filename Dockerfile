# Step 1: Base image
FROM python:3.10-slim

# Step 2: Set working directory
WORKDIR /app

# Step 3: Copy all files into the container
COPY . .

# Step 4: Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Step 5: Expose Flask port
EXPOSE 5000

# Step 6: Run the Flask app
CMD ["python", "app.py"]
