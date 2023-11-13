# restgdf_api

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![python](https://img.shields.io/badge/Python-3.11-3776AB.svg?style=flat&logo=python&logoColor=white)](https://www.python.org)

[![Push to Docker Hub](https://github.com/joshuasundance-swca/restgdf_api/actions/workflows/docker-hub.yml/badge.svg)](https://github.com/joshuasundance-swca/restgdf_api/actions/workflows/docker-hub.yml)
[![Docker Image Size (tag)](https://img.shields.io/docker/image-size/joshuasundance/restgdf_api/latest)](https://hub.docker.com/r/joshuasundance/restgdf_api)

[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/charliermarsh/ruff/main/assets/badge/v1.json)](https://github.com/charliermarsh/ruff)
[![Checked with mypy](http://www.mypy-lang.org/static/mypy_badge.svg)](http://mypy-lang.org/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

[![security: bandit](https://img.shields.io/badge/security-bandit-yellow.svg)](https://github.com/PyCQA/bandit)


🤖 This `README` was written by GPT-4. 🤖

## Overview
`restgdf_api` is an asynchronous server powered by [FastAPI](https://github.com/tiangolo/fastapi) and the open-source [restgdf](https://github.com/joshuasundance-swca/restgdf) library. It acts as an efficient, user-friendly proxy for ArcGIS servers, offering high-speed interactions with ArcGIS FeatureLayers. With comprehensive OpenAPI documentation, this API simplifies and accelerates the process of accessing and managing GIS data, making it an ideal alternative to the traditional ArcGIS API for Python.

## Key Features
- **Asynchronous Operations**: Optimized for speed and efficiency, leveraging the power of restgdf for non-blocking data operations.
- **Open-Source and Community-Focused**: Contributions are welcome, fostering a collaborative environment for continuous improvement.
- **Comprehensive OpenAPI Documentation**: Detailed and interactive documentation for easy integration and usage.
- **Versatile GIS Data Management**: Enables discovery, fetching, and manipulation of GIS data across various ArcGIS services.

## Use Cases
- **Data Discovery**: Explore content in ArcGIS Services Directory, including feature layers, rasters, and more.
- **Data Retrieval**: Fetch individual or multiple FeatureLayers, with flexible querying capabilities.
- **Administrative Data Access**: Access GIS data for states, counties, cities, and towns using data from [Mapping Support](https://mappingsupport.com/).
- **Proxy for ArcGIS Servers**: Can serve as a documented proxy for any ArcGIS server, providing a streamlined interface for external data sources.

## System Requirements
- Python 3.11 or higher
- Docker (optional, for containerized deployment)

## Installation

### Option 1: Docker Hub Deployment
```bash
docker run --name restgdf_api -p 8080:8080 joshuasundance/restgdf_api:latest
```

### Option 2: Clone the Repository
```bash
git clone https://github.com/joshuasundance-swca/restgdf_api.git
cd restgdf_api
docker compose up
```

### Option 3: Deploy on Kubernetes
```bash
git clone https://github.com/joshuasundance-swca/restgdf_api.git
cd restgdf_api
kubectl apply -f kubernetes/resources.yaml
```

### Option 4: Manual Local Installation
```bash
git clone https://github.com/joshuasundance-swca/restgdf_api.git
cd restgdf_api
pip install -r requirements.txt
cd restgdf_api
gunicorn app:app
```

## API Endpoints Overview
- `mappingsupport`: Leverages data from [Mapping Support](https://mappingsupport.com/) to provide GIS server listings and specific geographic area data.
- `directory`: Discover content in ArcGIS directories, including feature layers and raster data.
- `layer`: Retrieve specific FeatureLayers, supporting single and multiple queries.
- `server`: Add and configure ArcGIS servers, enhancing flexibility and control.


## Contributing
Your contributions are welcome! To contribute, please follow the standard fork and pull request workflow.

## License
This project is licensed under the MIT License.
