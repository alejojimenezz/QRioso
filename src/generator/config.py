from pathlib import Path

# Path
DEFAULT_OUTPUT_DIR = Path.home() / "Documents" / "qrioso"

# QR parameters
DEFAULT_FORMAT          = "png"
DEFAULT_BOX_SIZE        = 10
DEFAULT_BORDER          = 2
DEFAULT_DOT_STYLE       = "Cuadrado"
DEFAULT_EYE_STYLE       = "Cuadrado"
EYE_RADIUS_MAX          = 0.3
DEFAULT_ERROR_CORRECTION = "M ~15%"          # L ~7% | M ~15% | Q ~25% | H ~30%
DEFAULT_FILL_COLOR      = "#000000"
DEFAULT_BACK_COLOR      = "#FFFFFF"

# UI
APP_NAME        = "QRioso"
APP_WIDTH       = 950
APP_HEIGHT      = 650
APP_APPEARANCE  = "System"
APP_COLOR_THEME = "blue"

# Ranges
# Limit sliders/spinboxes
BOX_SIZE_MIN  = 1
BOX_SIZE_MAX  = 20
BORDER_MIN    = 0
BORDER_MAX    = 10