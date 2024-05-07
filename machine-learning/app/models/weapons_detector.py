from pathlib import Path
from typing import Any

import cv2
import numpy as np
from insightface.model_zoo import ArcFaceONNX, RetinaFace
from insightface.utils.face_align import norm_crop
from numpy.typing import NDArray
from typing import Any, Literal

from app.config import clean_name
from app.schemas import Face, ModelType, is_ndarray

from .base import InferenceModel
import base64
from app.schemas import ModelType, DetectedWeapons

from .base import InferenceModel

from PIL import Image
from ultralytics import YOLO
from pathlib import Path
import os

class WeaponsDetector(InferenceModel):
    _model_type = ModelType.WEAPONS_DETECTION

    def __init__(
        self,
        model_name: str,
        cache_dir: Path | str | None = None,
        mode: Literal["image", "video"] | None = None,
        **model_kwargs: Any,
    ) -> None:
        self.mode = mode
        super().__init__(model_name, cache_dir, **model_kwargs)

    def _load(self) -> None:
        if self.mode == "image" or self.mode is None:
            log.debug(f"Loading model '{self.model_name}'")
            self.image_model = None
            log.debug(f"Loaded model '{self.model_name}'")

        if self.mode == "video" or self.mode is None:
            log.debug(f"Loading model '{self.model_name}'")
            self.video_model = None
            log.debug(f"Loaded model '{self.model_name}'")

    def _predict(self, image: NDArray[np.uint8] | str) -> NDArray[np.float32]:
        if isinstance(image, bytes):
            decoded_image = cv2.imdecode(np.frombuffer(image, np.uint8), cv2.IMREAD_COLOR)
        else:
            decoded_image = image

        # Encode image to base64 string
        _, buffer = cv2.imencode('.jpg', decoded_image)
        encoded_string = base64.b64encode(buffer).decode('utf-8')

        outputs = []
        weapon: DetectedWeapons = {
                "image": "data:image/jpeg;base64," + encoded_string,  # Prefix with data URI"
                "score": 0.7
            }
        outputs.append(weapon)
        # match image_or_text:
        #     case Image.Image():
        #         if self.mode == "text":
        #             raise TypeError("Cannot encode image as text-only model")
        #         outputs: NDArray[np.float32] = self.vision_model.run(None, self.transform(image_or_text))[0][0]
        #     case str():
        #         if self.mode == "vision":
        #             raise TypeError("Cannot encode text as vision-only model")
        #         outputs = self.text_model.run(None, self.tokenize(image_or_text))[0][0]
        #     case _:
        #         raise TypeError(f"Expected Image or str, but got: {type(image_or_text)}")

        return outputs

    def configure(self, **model_kwargs: Any) -> None:
        self.det_model.det_thresh = model_kwargs.pop("minScore", self.det_model.det_thresh)


class ThreatDetector:
    def __init__(self, model_path=None):
        if model_path:
            self.initialize_model(model_path)
        else:
            model_path = './app/models/train9_model_v1.pt'
            self.initialize_model(model_path)


    def run_prediction_image(self, image, confidence=0.15):
        #model(source=1, show=True, conf=0.4, save=True)
        prediction_result = self.model(image, conf=confidence)
        return prediction_result 
    

    def run_image_prediction_byte_stream(self, image, asset_id, save_directory, confidence):
        file_path = save_directory / f"{asset_id}.jpg"
        detection_made = False
    
        if file_path.exists():
            weapon_detection_res = {
                "filePath": str(file_path)
            }
            
        else:
            if isinstance(image, bytes):
                image = cv2.imdecode(np.frombuffer(image, np.uint8), cv2.IMREAD_COLOR)
                detection_result = self.run_prediction_image(image, confidence)[0]
                detection_made = bool(len(detection_result))
                detected_image = detection_result.plot()
            else:
                detected_image = image

            if asset_id and detection_made:
                cv2.imwrite(str(file_path), detected_image)
            
                weapon_detection_res = {
                        "filePath": str(file_path)
                    }
            else:
                weapon_detection_res = {
                        "filePath": ""
                    }
        
        return weapon_detection_res


    def run_prediction_video(self, video_path, save_directory, confidence=0.2):
        video_save_file_path = save_directory / f"detected_{video_path.name}"
        detection_made = False 

        if not video_save_file_path.exists():
            detection_made = self.predict_video(str(video_path), str(video_save_file_path), confidence)

        if detection_made:
            weapon_detection_res = {
                "filePath": str(video_save_file_path)
            }
        else:
             weapon_detection_res = {
                "filePath": ""
            }
       
        return weapon_detection_res
        
        
    def predict_video(self, video_path, output_path, confidence):
        video_cap = cv2.VideoCapture(str(video_path))
        fps = video_cap.get(cv2.CAP_PROP_FPS)
        frame_size = (int(video_cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(video_cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        detection_made = False

        out = cv2.VideoWriter(output_path, fourcc, fps, frame_size)

        ret = True 
        while ret:
            ret, frame = video_cap.read()

            if ret:
                results = self.model.track(frame, persist=True, conf=confidence)
                frame_ = results[0].plot()
                out.write(frame_)

                if detection_made is False:
                    detection_made = bool(len(results[0]))

        video_cap.release()
        out.release()

        # if no weapons are detected, delete the processed video
        if detection_made is False:
            os.remove(output_path)

        # remove the copied resource in ml results volume
        os.remove(video_path)

        return detection_made


    def run_prediction_bitstream_deprecated(self, byte_image, save_path=None):
        reconstructed_image = Image.open(byte_image)
        prediction_result = self.run_prediction_image(reconstructed_image)[0]

        if save_path:
            detection_image = self.create_detected_image(prediction_result, save_path)
            print (f"Detection saved at {save_path}")

        return prediction_result, detection_image


    def create_detected_image(self, detected_result, save_path):
        """ Saves the thumbnails of detection
        """
        return detected_result.plot(save=True, filename=save_path)
         

    def initialize_model(self, model_path):
        self.model = YOLO(model_path)


    # @abstractmethod
    # def tokenize(self, text: str) -> dict[str, NDArray[np.int32]]:
    #     pass

    # @abstractmethod
    # def transform(self, image: Image.Image) -> dict[str, NDArray[np.float32]]:
    #     pass

    # @property
    # def textual_dir(self) -> Path:
    #     return self.cache_dir / "textual"

    # @property
    # def visual_dir(self) -> Path:
    #     return self.cache_dir / "visual"

    # @property
    # def model_cfg_path(self) -> Path:
    #     return self.cache_dir / "config.json"

    # @property
    # def textual_path(self) -> Path:
    #     return self.textual_dir / f"model.{self.preferred_runtime}"

    # @property
    # def visual_path(self) -> Path:
    #     return self.visual_dir / f"model.{self.preferred_runtime}"

    # @property
    # def tokenizer_file_path(self) -> Path:
    #     return self.textual_dir / "tokenizer.json"

    # @property
    # def tokenizer_cfg_path(self) -> Path:
    #     return self.textual_dir / "tokenizer_config.json"

    # @property
    # def preprocess_cfg_path(self) -> Path:
    #     return self.visual_dir / "preprocess_cfg.json"

    # @property
    # def cached(self) -> bool:
    #     return self.textual_path.is_file() and self.visual_path.is_file()

    # @cached_property
    # def model_cfg(self) -> dict[str, Any]:
    #     log.debug(f"Loading model config for CLIP model '{self.model_name}'")
    #     model_cfg: dict[str, Any] = json.load(self.model_cfg_path.open())
    #     log.debug(f"Loaded model config for CLIP model '{self.model_name}'")
    #     return model_cfg

    # @cached_property
    # def tokenizer_file(self) -> dict[str, Any]:
    #     log.debug(f"Loading tokenizer file for CLIP model '{self.model_name}'")
    #     tokenizer_file: dict[str, Any] = json.load(self.tokenizer_file_path.open())
    #     log.debug(f"Loaded tokenizer file for CLIP model '{self.model_name}'")
    #     return tokenizer_file

    # @cached_property
    # def tokenizer_cfg(self) -> dict[str, Any]:
    #     log.debug(f"Loading tokenizer config for CLIP model '{self.model_name}'")
    #     tokenizer_cfg: dict[str, Any] = json.load(self.tokenizer_cfg_path.open())
    #     log.debug(f"Loaded tokenizer config for CLIP model '{self.model_name}'")
    #     return tokenizer_cfg

    # @cached_property
    # def preprocess_cfg(self) -> dict[str, Any]:
    #     log.debug(f"Loading visual preprocessing config for CLIP model '{self.model_name}'")
    #     preprocess_cfg: dict[str, Any] = json.load(self.preprocess_cfg_path.open())
    #     log.debug(f"Loaded visual preprocessing config for CLIP model '{self.model_name}'")
    #     return preprocess_cfg
