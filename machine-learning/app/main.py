import asyncio
import gc
import os
import signal
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator, Callable, Iterator
from zipfile import BadZipFile

import orjson
from fastapi import Depends, FastAPI, Form, HTTPException, UploadFile
from fastapi.responses import ORJSONResponse
from onnxruntime.capi.onnxruntime_pybind11_state import InvalidProtobuf, NoSuchFile
from starlette.formparsers import MultiPartParser

from app.models.base import InferenceModel

from .config import log, settings
from .models.cache import ModelCache
from .schemas import (
    MessageResponse,
    ModelType,
    TextResponse,
    DetectedWeapons,
)

import cv2
import numpy as np
import base64
from pathlib import Path

MultiPartParser.max_file_size = 2**26  # spools to disk if payload is 64 MiB or larger

model_cache = ModelCache(ttl=settings.model_ttl, revalidate=settings.model_ttl > 0)
thread_pool: ThreadPoolExecutor | None = None
lock = threading.Lock()
active_requests = 0
last_called: float | None = None


### -- test code
from .models.weapons_detector import ThreatDetector
threat_detector = ThreatDetector()


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[None, None]:
    global thread_pool
    log.info(
        (
            "Created in-memory cache with unloading "
            f"{f'after {settings.model_ttl}s of inactivity' if settings.model_ttl > 0 else 'disabled'}."
        )
    )

    try:
        if settings.request_threads > 0:
            # asyncio is a huge bottleneck for performance, so we use a thread pool to run blocking code
            thread_pool = ThreadPoolExecutor(settings.request_threads) if settings.request_threads > 0 else None
            log.info(f"Initialized request thread pool with {settings.request_threads} threads.")
        if settings.model_ttl > 0 and settings.model_ttl_poll_s > 0:
            asyncio.ensure_future(idle_shutdown_task())
        yield
    finally:
        log.handlers.clear()
        for model in model_cache.cache._cache.values():
            del model
        if thread_pool is not None:
            thread_pool.shutdown()
        gc.collect()


def update_state() -> Iterator[None]:
    global active_requests, last_called
    active_requests += 1
    last_called = time.time()
    try:
        yield
    finally:
        active_requests -= 1


app = FastAPI(lifespan=lifespan)


@app.get("/", response_model=MessageResponse)
async def root() -> dict[str, str]:
    return {"message": "Immich ML"}


@app.get("/ping", response_model=TextResponse)
def ping() -> str:
    return "pong"


@app.post("/predict", dependencies=[Depends(update_state)])
async def predict(
    model_name: str = Form(alias="modelName"),
    model_type: ModelType = Form(alias="modelType"),
    options: str = Form(default="{}"),
    text: str | None = Form(default=None),
    image: UploadFile | None = None,
    video: UploadFile | None = Form(default=None),
) -> Any:
    if image is not None:
        inputs: str | bytes = await image.read()
    elif video is not None:
        inputs: str | bytes = "meh"
    elif text is not None:
        inputs = text
    else:
        raise HTTPException(400, "Either image or text must be provided")
    try:
        kwargs = orjson.loads(options)
    except orjson.JSONDecodeError:
        raise HTTPException(400, f"Invalid options JSON: {options}")

    if model_type == ModelType.WEAPONS_DETECTION:
        image = inputs
        save_directory = Path("/ml-results/")
        asset_id = kwargs.get("assetId", None)
        detection_response = threat_detector.run_image_prediction_byte_stream(image, 
                                                                              asset_id, 
                                                                              save_directory)

        return ORJSONResponse(detection_response)

    model = await load(await model_cache.get(model_name, model_type, **kwargs))
    model.configure(**kwargs)
    outputs = await run(model.predict, inputs)
    return ORJSONResponse(outputs)


async def run(func: Callable[..., Any], inputs: Any) -> Any:
    if thread_pool is None:
        return func(inputs)
    return await asyncio.get_running_loop().run_in_executor(thread_pool, func, inputs)


async def load(model: InferenceModel) -> InferenceModel:
    if model.loaded:
        return model

    def _load(model: InferenceModel) -> None:
        with lock:
            model.load()

    try:
        await run(_load, model)
        return model
    except (OSError, InvalidProtobuf, BadZipFile, NoSuchFile):
        log.warning(
            (
                f"Failed to load {model.model_type.replace('_', ' ')} model '{model.model_name}'."
                "Clearing cache and retrying."
            )
        )
        model.clear_cache()
        await run(_load, model)
        return model


async def idle_shutdown_task() -> None:
    while True:
        log.debug("Checking for inactivity...")
        if (
            last_called is not None
            and not active_requests
            and not lock.locked()
            and time.time() - last_called > settings.model_ttl
        ):
            log.info("Shutting down due to inactivity.")
            os.kill(os.getpid(), signal.SIGINT)
            break
        await asyncio.sleep(settings.model_ttl_poll_s)
