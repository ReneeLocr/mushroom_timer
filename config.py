from pathlib import Path

BASE_DIR = Path(__file__).parent
ASSETS = BASE_DIR / "assets"
QSS_PATH = BASE_DIR / "colorful_style.qss" # change qss name to change the color theme
FONT_PATH = BASE_DIR / "assets/super-joyful-font/super-joyful.ttf" # change font path to change the font

DEFAULT_WORK_MIN = 25
DEFAULT_SHORT_BREAK_MIN = 5
DEFAULT_LONG_BREAK_MIN = 15
DEFAULT_CYCLES = 4

GITHUB_URL = "https://github.com/ReneeLocr"
LINKEDIN_URL = "https://linkedin.com"

EMAIL_ADDRESS = "renee.locreille@uclouvain.be"
EMAIL_SUBJECT = "Mushroom Timer app"

GITHUB_ICON = "github_black.png"
IN_ICON = "linkedin_black.png"
MAIL_ICON = "mail_black.png"
VOLUME_ICON = "volume_black.png"

WORK_MASCOT = "mascot_work.png"
SHORT_BREAK_MASCOT = "mascot_short_break.png"
LONG_BREAK_MASCOT = "mascot_long_break.png"