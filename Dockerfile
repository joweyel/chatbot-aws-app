FROM python:3.9-slim


RUN mkdir -p /app/models
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl wget \
    && rm -rf /var/lib/apt/lists/*

# Get the model files
COPY download_models.sh .
RUN chmod +x download_models.sh
RUN bash download_models.sh

# Install dependencies
COPY "requirements.txt" .
RUN pip install --no-cache-dir -r requirements.txt

COPY "streamlit_app.py" .
EXPOSE 8501
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health
ENTRYPOINT ["streamlit", "run", "streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]