FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install dependencies (CPU-only PyTorch is heavily recommended for simple embeddings on Railway to save RAM/Disk)
# We install torch first from the CPU index
RUN pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# Copy requirements
COPY requirements.txt .

# Install the rest of the requirements
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download the sentence-transformers model so it's baked into the image
# This prevents downloading it on every startup/restart
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

# Copy the rest of the backend code
COPY . .

# Expose port (Railway provides PORT env variable, defaulting to 8000)
ENV PORT=8000
EXPOSE ${PORT}

# Run the FastAPI app
CMD ["sh", "-c", "uvicorn app:app --host 0.0.0.0 --port ${PORT}"]
