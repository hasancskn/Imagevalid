# Image Transformation Service

This is a basic image transformation service built with FastAPI. The service can perform image validation, and basic transformations like grayscale, rotation, and resizing. 

## Getting Started

### Prerequisites

- Docker
- Docker Compose

### Running the Service

1. Build the Docker image:

    ```bash
    docker-compose build
    ```

2. Start the service:

    ```bash
    docker-compose up
    ```

3. The service will be available at `http://localhost:8000`.

### API Endpoints

- `POST /transform/`: Apply transformations to an uploaded image.
- `GET /health/`: Check the health of the service.

### Example Request

```bash
for transformation_type = grayscale

curl -X POST "http://localhost:8000/transform/" \                                                                                                                                   ✔ 
  -F "transformation_type=grayscale" \
  -F "file=@test.jpeg"


for transformation_type = resize

curl -X POST "http://localhost:8000/transform/" \
  -F "transformation_type=resize" \
  -F "width=200" \
  -F "height=200" \
  -F "file=@test.jpeg"
  
for transformation_type = rotate

curl -X POST "http://localhost:8000/transform/" \
  -F "transformation_type=rotate" \
  -F "angle=45" \
  -F "file=@test.jpeg"
