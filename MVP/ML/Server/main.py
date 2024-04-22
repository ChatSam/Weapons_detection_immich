from typing import Union
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from PIL import Image
from io import BytesIO
from pathlib import Path
import os
import sys 
from fastapi.staticfiles import StaticFiles
from predict import ThreatDetector

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)


app = FastAPI()
templates = Jinja2Templates(directory="templates")
model_path = Path('../Models/train9_model_v1.pt')
threat_detector = ThreatDetector(model_path)

# to source saved images from folder
app.mount("/static", 
          StaticFiles(directory="/Users/chatsam/P_Dev/Weapons_detection_immich/MVP/ML/Test"), 
          name="static")


@app.get("/")
def read_root():
    return {"message":"This is the root page for Weapons detections"}


# @app.get("/items/{item_id}")
# def read_item(item_id: int, q: Union[str, None] = None):
#     return {"item_id": item_id, "q": q}


# @app.get("/items/{item_id}")
# def read_item(item_id: int, q: Union[str, None] = None):
#     return {"item_id": item_id, "q": q}


def initialize_ml_model(model_path):
    #TODO: adopt a lazy loading approach. Also introduce caching 
    return ThreatDetector(model_path)


@app.get("/detect_threats/{image_id}")
def detect_threats(request: Request, image_id:str):
    image_path = Path(f'../Test/{image_id}.jpg')
    #detection_save_path = Path(f'../Test/detected_{image_id}.jpg')
    detection_save_path = f'/Users/chatsam/P_Dev/Weapons_detection_immich/MVP/ML/Test/detected_{image_id}.jpg'
    static_path = f'/static/detected_{image_id}.jpg'

    test_image = Image.open(image_path)
    byte_image = BytesIO()
    test_image.save(byte_image, format="jpeg")
    detection = threat_detector.run_prediction_bitstream(byte_image, save_path=detection_save_path)

    html_template = templates.TemplateResponse("result.html", 
                                               {"request": request, 
                                                "image_id": image_id,  
                                                "image_url": static_path})
    
    return html_template