# Immich Machine Learning

- CLIP embeddings
- Facial recognition

# Setup

This project uses [Poetry](https://python-poetry.org/docs/#installation), so be sure to install it first.
Running `poetry install --no-root --with dev --with cpu` will install everything you need in an isolated virtual environment.
CUDA and OpenVINO are supported as acceleration APIs. To use them, you can replace `--with cpu` with either of `--with cuda` or `--with openvino`.

To add or remove dependencies, you can use the commands `poetry add $PACKAGE_NAME` and `poetry remove $PACKAGE_NAME`, respectively.
Be sure to commit the `poetry.lock` and `pyproject.toml` files with `poetry lock --no-update` to reflect any changes in dependencies.


# Load Testing

To measure inference throughput and latency, you can use [Locust](https://locust.io/) using the provided `locustfile.py`.
Locust works by querying the model endpoints and aggregating their statistics, meaning the app must be deployed.
You can change the models or adjust options like score thresholds through the Locust UI.

To get started, you can simply run `locust --web-host 127.0.0.1` and open `localhost:8089` in a browser to access the UI. See the [Locust documentation](https://docs.locust.io/en/stable/index.html) for more info on running Locust. 

Note that in Locust's jargon, concurrency is measured in `users`, and each user runs one task at a time. To achieve a particular per-endpoint concurrency, multiply that number by the number of endpoints to be queried. For example, if there are 3 endpoints and you want each of them to receive 8 requests at a time, you should set the number of users to 24.


# How to Add a New Machine Learning Model/Feature

The following steps give a high-level overview on setting up a new machine learning model in Immich.

1. Define the new machine learning model in the **immich-machine-learning** container, i.e., the **machine-learning** folder. Navigate to `machine-learning/models/` and create your new model there.

2. When creating your own model interface and methods, makesure to inherit the  **Inference Model** class provided. 
3. In the backend server, **immich-server**, create corresponding Data Transfer Objects based on the data being returned by the new machine learning model. This will be in the **server** folder.
4. Define correspoding machine learning request handling methods in the machine learning repository file present under **domain** and **infra**.
5. Specify request methods in an existing microservice (such as **smart-info-service**), or create a new microservice which will be responsible for making these machine learning requests. These are usually defined under **server/src/domain/<microservice name>**.
6. Define a controller which will act as the interface to the microservice request methods. This is where you define what the API request to the machine learning model would look like. This is under **server/src/immich/controllers**.
7. After completing the above steps, start Immich on developer mode, and run `make open-api ` to generate new Open API specifications for the new Machine Learning API request.
8. Use the newly defined OpenAPI specifications to build new frontend components to handle your API request to the machine learning server. This is done under **web**.
