from fastapi import FastAPI, File, UploadFile, HTTPException, Form, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from PIL import Image, ImageOps
import io
import base64
import logging
import time

app = FastAPI()


logging.basicConfig(
    level=logging.DEBUG,  
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("app.log"),  
        logging.StreamHandler()          
    ]
)

class ImageTransformation(BaseModel):
    transformation_type: str
    angle: int = 0  # used only for rotation
    width: int = 0  # used only for resizing
    height: int = 0  # used only for resizing

def validate_image(image_data: bytes) -> Image.Image:
    try:
        image = Image.open(io.BytesIO(image_data))
        return image
    except Exception as e:
        logging.error("Failed to validate image: %s", e)
        raise HTTPException(status_code=400, detail="Invalid image file")

def process_image(image: Image.Image, transformation: ImageTransformation) -> Image.Image:
    try:
        if transformation.transformation_type == "grayscale":
            logging.info("Applying grayscale transformation")
            return ImageOps.grayscale(image)
        elif transformation.transformation_type == "rotate":
            logging.info("Rotating image by %d degrees", transformation.angle)
            return image.rotate(transformation.angle)
        elif transformation.transformation_type == "resize":
            logging.info("Resizing image to %dx%d", transformation.width, transformation.height)
            return image.resize((transformation.width, transformation.height))
        else:
            raise ValueError("Invalid transformation type")
    except Exception as e:
        logging.error("Failed to process image: %s", e)
        raise HTTPException(status_code=400, detail="Invalid transformation type")

def image_to_base64(image: Image.Image) -> str:
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time

    logging.info(
        f"{request.method} {request.url} - "
        f"Status: {response.status_code} - "
        f"Time: {process_time:.2f}s"
    )
    return response

@app.post("/transform/")
async def transform_image(
    transformation_type: str = Form(...), 
    angle: int = Form(0), 
    width: int = Form(0), 
    height: int = Form(0),
    file: UploadFile = File(None),
    image_base64: str = Form(None)
):
    logging.info("Received image transformation request")

    # Validate image
    if file:
        image_data = await file.read()
        logging.debug("File uploaded with filename: %s", file.filename)
    elif image_base64:
        try:
            image_data = base64.b64decode(image_base64)
            logging.debug("Base64 image received")
        except Exception as e:
            logging.error("Failed to decode Base64 string: %s", e)
            raise HTTPException(status_code=400, detail="Invalid Base64 string")
    else:
        logging.warning("No image file or Base64 string provided")
        raise HTTPException(status_code=400, detail="No image file or Base64 string provided")

    image = validate_image(image_data)

    # Process image
    try:
        transformation = ImageTransformation(
            transformation_type=transformation_type,
            angle=angle,
            width=width,
            height=height
        )
        transformed_image = process_image(image, transformation)
    except Exception as e:
        logging.error("Error during image transformation: %s", e)
        raise e

    # Convert back to Base64
    transformed_base64 = image_to_base64(transformed_image)
    
    logging.info("Image transformation successful")
    
    return JSONResponse(content={"transformed_image": transformed_base64})

# Additional endpoint for health check
@app.get("/health/")
async def health_check():
    logging.info("Health check endpoint accessed")
    return {"status": "healthy"}

