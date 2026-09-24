"""Stage 2: generate a 1080x1920 background image per quote with Pollinations.ai."""
import io
import os
import sys
import time
import urllib.parse

import requests
from PIL import Image, ImageOps

import config
from utils import load_quotes, quote_id


def image_path(index, quote):
    return os.path.join(config.BACKGROUNDS_DIR, quote_id(index, quote) + ".jpg")


def fetch_image(prompt):
    url = config.POLLINATIONS_URL.format(prompt=urllib.parse.quote(prompt, safe=""))
    params = {
        "width": config.VIDEO_WIDTH,
        "height": config.VIDEO_HEIGHT,
        "model": config.IMAGE_MODEL,
        "nologo": "true",
    }
    if config.IMAGE_SEED is not None:
        params["seed"] = config.IMAGE_SEED
    resp = requests.get(url, params=params, timeout=config.IMAGE_TIMEOUT)
    resp.raise_for_status()
    if not resp.headers.get("content-type", "").startswith("image/"):
        raise ValueError(f"expected an image, got {resp.headers.get('content-type')!r}")
    img = Image.open(io.BytesIO(resp.content)).convert("RGB")
    # The API doesn't always honour the exact size; crop/scale to fill 1080x1920.
    return ImageOps.fit(img, (config.VIDEO_WIDTH, config.VIDEO_HEIGHT), Image.LANCZOS)


def generate_image(index, quote):
    """Return the image path, downloading it unless it already exists."""
    path = image_path(index, quote)
    if os.path.exists(path):
        print(f"  [skip] {path} already exists")
        return path

    os.makedirs(config.BACKGROUNDS_DIR, exist_ok=True)
    last_error = None
    for attempt in range(1, config.IMAGE_RETRIES + 1):
        try:
            img = fetch_image(quote["image_prompt"])
            tmp = path + ".part"
            img.save(tmp, "JPEG", quality=95)
            os.replace(tmp, path)  # atomic, so a crash never leaves a half-written image
            print(f"  [ok]   {path}")
            return path
        except Exception as e:
            last_error = e
            print(f"  [retry] attempt {attempt}/{config.IMAGE_RETRIES} failed: {str(e)[:150]}")
            if attempt < config.IMAGE_RETRIES:
                time.sleep(2 ** attempt)
    raise RuntimeError(f"image generation failed after {config.IMAGE_RETRIES} attempts: {last_error}")


def main(only=None):
    quotes = load_quotes()
    failed = []
    for i, q in enumerate(quotes):
        if only is not None and i != only:
            continue
        print(f"[{i + 1}/{len(quotes)}] {q['quote'][:60]}...")
        try:
            generate_image(i, q)
        except Exception as e:
            print(f"  [fail] {e}")
            failed.append(i + 1)
    if failed:
        print(f"Failed quotes: {failed}")
    return not failed


if __name__ == "__main__":
    # Optional argument: 1-based quote number to generate just that one.
    only = int(sys.argv[1]) - 1 if len(sys.argv) > 1 else None
    sys.exit(0 if main(only) else 1)
