# Use Next.js lightweight base
FROM node:20-slim

# Install Python 3, pip, virtualenv, and build-essential
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set up Python virtual environment to avoid PEP 668 external-package blocks
ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Install Python library requirements
RUN pip3 install --no-cache-dir \
    google-cloud-bigquery \
    google-cloud-storage \
    openai \
    google-auth \
    langgraph

# Set working directory
WORKDIR /app

# Copy dependency configs
COPY ui/package*.json ./

# Install frontend dependencies
RUN npm install --silent

# Copy parent workspace coding agents to the container's execution space
COPY agents/ ./agents/
COPY generated_code/ ./generated_code/

# Copy the remaining Next.js source code
COPY ui/ .

# Build production Next.js app
RUN npm run build

# Expose Port for Google Cloud Run (always default to 8080 for seamless Cloud Run binding)
EXPOSE 8080
ENV PORT=8080
ENV HOSTNAME="0.0.0.0"

# Run next server using virtualenv PATH execution context
CMD ["npm", "run", "start"]
