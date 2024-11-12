# Flask App with OpenAI-Chatbot deployed on AWS with DevOps pipeline

This is a OpenAI chat web application that uses flask as backend. The goal of this app is to be deployed to AWS.

## Running the app locally
Create and activate a virtual environment
```bash
python3.9 -m venv venv
source venv/bin/activate
```

Install dependencies
```bash
pip install -r requirements.txt
```

**(Optional): Creating a virtual environment with devops-related dependencies**
```bash
python3.9 -m venv venv-dev
source venv-dev/bin/activate
pip install -r requirements-devtxt
```

Setting the OpenAI api key to access the llm:
```bash
export OPENAI_API_KEY=...
```

Run the app locally
```bash
python3 run.py
```
Open the app in the browser at http://localhost:5000 or https://127.0.0.1:5000
   
## Running the app locally with Docker
Building the docker container
```bash
VERSION=...
docker build --build-arg OPENAI_API_KEY=${OPENAI_API_KEY} -t flaskgpt:${VERSION} .
```
Running the app locally using Docker
```bash
docker run -it -p 5000:5000 flaskgpt:${VERSION}
```

# Deploy the app on AWS using a CI-CD pipeline with Jenkins

The instructions can be found in the [devops](./devops/)-folder
