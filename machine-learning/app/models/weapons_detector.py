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
