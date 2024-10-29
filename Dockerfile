FROM python:3.9-slim

ARG OPENAI_API_KEY
ENV OPENAI_API_KEY=${OPENAI_API_KEY}

RUN mkdir -p /app
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl wget \
    && rm -rf /var/lib/apt/lists/*

RUN pip install -U pip
COPY requirements_full.txt run.py /app/
COPY website/ /app/website/
RUN pip install --no-cache-dir -r requirements_full.txt


EXPOSE 5000
ENTRYPOINT [ "python3", "run.py"]