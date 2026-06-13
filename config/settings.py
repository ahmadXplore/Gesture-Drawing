"""
Configuration — Gesture Drawing v4.0
"""

# ── Camera ────────────────────────────────────────────────────────────────────
CAMERA_WIDTH  = 1280
CAMERA_HEIGHT = 720
CAMERA_INDEX  = 0

# ── MediaPipe ─────────────────────────────────────────────────────────────────
DETECTION_CONFIDENCE = 0.75
TRACKING_CONFIDENCE  = 0.75
MAX_HANDS = 1

# ── Canvas ────────────────────────────────────────────────────────────────────
CANVAS_WIDTH    = 1280
CANVAS_HEIGHT   = 720
# Deep dark background — makes neon colors glow vividly, easy on eyes
CANVAS_BG_COLOR = (22, 20, 32)      # dark navy-charcoal (BGR)

# ── Brush ─────────────────────────────────────────────────────────────────────
DEFAULT_BRUSH_SIZE = 8
MIN_BRUSH_SIZE     = 1
MAX_BRUSH_SIZE     = 60

# ── Smoothing (maximum silkiness) ─────────────────────────────────────────────
# SMOOTH_POS   position EMA (higher = smoother, slightly more lag)
# SMOOTH_VEL   velocity EMA (predictive look-ahead; higher = more assist)
# JITTER_PX    discard raw noise smaller than this (pixels)
# INTERP_STEPS sub-frame interpolation points (higher = denser, no gaps)
# ADAPTIVE     slow hand → ultra-smooth; fast hand → more responsive
SMOOTH_POS    = 0.82       # ↑ from 0.72  — significantly silkier
SMOOTH_VEL    = 0.85       # ↑ from 0.80
JITTER_PX     = 3.0        # ↑ from 2.5   — kills more micro-jitter
INTERP_STEPS  = 8          # ↑ from 5     — denser fill, no gaps
ADAPTIVE      = True
SPLINE_BUF    = 6          # Catmull-Rom buffer size (was 4) — smoother curves

# ── Neon / Glow colors (BGR) ──────────────────────────────────────────────────
# All chosen to look luminous / glittery on a dark background.
# BLACK removed — invisible on dark canvas.
COLORS = {
    # ── Neons ────────────────────────────────────────────
    'NEON GREEN':   (20,  255, 80),    # electric green
    'NEON CYAN':    (255, 240, 0),     # electric cyan
    'NEON BLUE':    (255, 80,  20),    # electric blue
    'NEON PINK':    (180, 20,  255),   # hot pink / magenta
    'NEON PURPLE':  (230, 0,   180),   # plasma purple
    'NEON RED':     (30,  30,  255),   # laser red
    'NEON YELLOW':  (0,   255, 230),   # acid yellow
    'NEON ORANGE':  (0,   160, 255),   # hyper orange
    # ── Glitter / metallic ───────────────────────────────
    'GOLD':         (0,   210, 255),   # bright gold
    'ROSE GOLD':    (130, 140, 255),   # rose gold
    'SILVER':       (210, 210, 220),   # chrome silver
    'AQUA':         (255, 220, 80),    # aquamarine
    'LAVENDER':     (255, 150, 200),   # soft lavender glow
    'CORAL':        (80,  100, 255),   # coral
    'MINT':         (180, 255, 180),   # mint glow
    'UV WHITE':     (255, 240, 230),   # near-white / UV glow
}

DEFAULT_COLOR = 'NEON CYAN'

# ── Glow effect ───────────────────────────────────────────────────────────────
# Each stroke is drawn twice: a wide soft outer halo + sharp inner line.
# This gives the "glowing neon pen" look on the dark canvas.
GLOW_ENABLED    = True
GLOW_RADIUS     = 3        # extra radius added to outer glow pass
GLOW_ALPHA      = 0.38     # opacity of the outer glow layer (0–1)

# ── UI ────────────────────────────────────────────────────────────────────────
UI_HEIGHT           = 130
UI_BACKGROUND_COLOR = (14, 12, 20)    # very dark purple-black panel
UI_TEXT_COLOR       = (200, 200, 210)
UI_BUTTON_SIZE      = 44
UI_BUTTON_MARGIN    = 5
HOVER_TIME          = 0.65

# ── Undo / Redo ───────────────────────────────────────────────────────────────
MAX_UNDO_STEPS = 40

# ── Opacity ───────────────────────────────────────────────────────────────────
DEFAULT_OPACITY = 255
MIN_OPACITY     = 30
MAX_OPACITY     = 255

# ── Gestures ──────────────────────────────────────────────────────────────────
PINCH_THRESHOLD = 45

# ── FPS ───────────────────────────────────────────────────────────────────────
SHOW_FPS     = True
FPS_POSITION = (10, 30)
FPS_COLOR    = (60, 220, 100)

# ── Landmark indices ──────────────────────────────────────────────────────────
THUMB_TIP  = 4
INDEX_TIP  = 8
MIDDLE_TIP = 12
RING_TIP   = 16
PINKY_TIP  = 20
THUMB_IP   = 3
INDEX_PIP  = 6
MIDDLE_PIP = 10
RING_PIP   = 14
PINKY_PIP  = 18
WRIST      = 0

# ── Drawing modes ─────────────────────────────────────────────────────────────
MODES        = ['FREE', 'LINE', 'RECT', 'CIRCLE', 'ELLIPSE', 'TRIANGLE', 'ARROW', 'STAR']
DEFAULT_MODE = 'FREE'

# ── Particle trail ────────────────────────────────────────────────────────────
PARTICLE_TRAIL = True
TRAIL_LENGTH   = 16        # longer trail for neon glow look
