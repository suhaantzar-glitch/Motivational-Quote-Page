"""Settings for the quote video pipeline. Edit these values to customise output."""

# --- Paths -------------------------------------------------------------------
QUOTES_FILE = "quotes.json"
BACKGROUNDS_DIR = "backgrounds"

# --- Video frame -------------------------------------------------------------
VIDEO_WIDTH = 1080
VIDEO_HEIGHT = 1920

# --- Background images (Pollinations.ai, free, no key) -----------------------
POLLINATIONS_URL = "https://image.pollinations.ai/prompt/{prompt}"
IMAGE_MODEL = "flux"
IMAGE_SEED = 42            # fixed seed = reproducible images; set to None for random
IMAGE_RETRIES = 4          # attempts per image before giving up
IMAGE_TIMEOUT = 120        # seconds per request (generation can be slow)
