# src/theme.py

from PySide6.QtCore import QSize

# ==================================================================================================
#  COLOR PALETTE
#  A dark, modern, and vibrant theme inspired by high-contrast IDEs and media applications.
# ==================================================================================================
BG_VOID        = "#000000"  # Absolute black, for video backgrounds and main window
BG_SURFACE     = "#0D0D0D"  # Off-black, for top bars and elevated surfaces
BG_CARD        = "#141414"  # Dark grey, for individual card items
BG_CONTROLS    = "#111111"  # Slightly lighter than surface for player controls
ACCENT_PRIMARY = "#E8FF00"  # Electric lime/yellow, the main interactive color
ACCENT_MUTED   = "#2A2A2A"  # Muted grey, for borders, dividers, and disabled states
TEXT_PRIMARY   = "#FFFFFF"  # Pure white, for primary text and active icons
TEXT_SECONDARY = "#5A5A5A"  # Grey, for secondary labels, timestamps, and inactive text
TEXT_DIM       = "#303030"  # Very dark grey, for placeholder text or empty states
SOCIAL_HOVER   = "#1F1F1F"  # Hover state for non-accented buttons
PROGRESS_BG    = "#1A1A1A"  # Background of progress bars
PROGRESS_FILL  = "#E8FF00"  # Fill color for progress bars, matches accent

# ==================================================================================================
#  TYPOGRAPHY & SPACING
# ==================================================================================================
FONT_SANS = "SF Pro Display, Helvetica Neue, Helvetica, Arial, sans-serif"
FONT_MONO = "SF Mono, Consolas, Courier New, monospace"
SKIP_MS   = 10_000  # 10 seconds for video skip forward/back

# ==================================================================================================
#  ICONOGRAPHY
# ==================================================================================================
# --- Asset Paths ---
ICON_PLAY      = "assets/icons/play.svg"
ICON_PAUSE     = "assets/icons/pause.svg"
ICON_SKIP_BACK = "assets/icons/skip_back.svg"
ICON_SKIP_FWD  = "assets/icons/skip_fwd.svg"
ICON_BACK      = "assets/icons/back.svg"

# --- Icon Sizes ---
ICON_SIZE_TRANSPORT = QSize(18, 18)  # For player controls (play, pause, skip)
ICON_SIZE_NAV       = QSize(16, 16)  # For navigation icons (back button)

# ==================================================================================================
#  PLATFORM-SPECIFIC COLORS
# ==================================================================================================
PLATFORM_COLORS = {
    "instagram": ("#E1306C", "IG"),
    "facebook":  ("#1877F2", "FB"),
    "fb.watch":  ("#1877F2", "FB"),
    "tiktok":    ("#FFFFFF", "TT"),
    "default":   (ACCENT_MUTED, "DL"),
}