FROM python:3.11-slim
WORKDIR /app

# Install tools needed to download Coral
RUN apt-get update && apt-get install -y curl tar && rm -rf /var/lib/apt/lists/*

# Download and install the Coral Linux binary
RUN curl -L https://github.com/withcoral/coral/releases/download/v0.4.1/coral-x86_64-unknown-linux-gnu.tar.gz \
    | tar -xz && mv coral /usr/local/bin/coral && chmod +x /usr/local/bin/coral

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all your project files into the cloud container
COPY . .
RUN chmod +x start.sh

# Open the port and run the start script
EXPOSE 8501
CMD ["bash", "start.sh"]