# Streamlit App for facial landmark detection
This is a simple app for facial landmark detection using lightweight pre-trained models with OpenCV. The goal of this app is to be deployed to AWS.


## Running the app locally
Create and activate a virtual environment
```bash
python3.9 -m venv venv
source venv/bin/activate
```

Install dependencies
```bash
pip install -r requirements.txt
# (Optional): dependencies for development
pip install -r requirements-dev.txt
```

Download the models
```bash
mkdir -p models
chmod +x download_models.sh
./download_models.sh
```
Run the app locally
```bash
streamlit run streamlit_app.py
```
Open the app in the browser at http://localhost:8501
   
## Running the app locally with Docker
Building the docker container
```bash
docker build -t face-landmark-app:v1.0 .
```
Running the app locally using Docker
```bash
docker run -it -p 8501:8501 face-landmark-app:v1.0
```

# Deploy the app on AWS using a CI-CD pipeline with Jenkins

The instructions can be found in the [devops](./devops/)-folder
