"""
Canvas Module v4.0
==================
Dark canvas + neon glow strokes.
Every stroke is drawn in two passes:
  Pass 1 — wide soft glow  (GLOW_RADIUS extra, low opacity blended)
  Pass 2 — sharp core line (full opacity, LINE_AA)
This gives all colors a luminous, glittery look on the dark background.
"""

import cv2
import numpy as np
import math
from collections import deque

from config.settings import (
    CANVAS_WIDTH, CANVAS_HEIGHT, CANVAS_BG_COLOR,
    COLORS, DEFAULT_COLOR,
    DEFAULT_BRUSH_SIZE, MIN_BRUSH_SIZE, MAX_BRUSH_SIZE,
    INTERP_STEPS, MAX_UNDO_STEPS,
    DEFAULT_OPACITY, MIN_OPACITY, MAX_OPACITY,
    TRAIL_LENGTH, DEFAULT_MODE,
    GLOW_ENABLED, GLOW_RADIUS, GLOW_ALPHA,
)
from utils.smoother import PointSmoother


class Canvas:

    def __init__(self):
        self._bg    = np.array(CANVAS_BG_COLOR, dtype=np.uint8)
        self.canvas = self._blank()

        self.current_color  = COLORS[DEFAULT_COLOR]
        self.brush_size     = DEFAULT_BRUSH_SIZE
        self.eraser_mode    = False
        self.opacity        = DEFAULT_OPACITY
        self.draw_mode      = DEFAULT_MODE

        self._smoother      = PointSmoother()
        self.previous_point = None
        self.shape_start    = None
        self._shape_overlay = None

        self._undo: deque = deque(maxlen=MAX_UNDO_STEPS)
        self._redo: deque = deque(maxlen=MAX_UNDO_STEPS)
        self.trail: deque = deque(maxlen=TRAIL_LENGTH)

        self._push_undo()

    # ── canvas ────────────────────────────────────────────────────────────────

    def _blank(self):
        c = np.empty((CANVAS_HEIGHT, CANVAS_WIDTH, 3), dtype=np.uint8)
        c[:] = self._bg
        return c

    # ── undo / redo ──────────────────────────────────────────────────────────

    def _push_undo(self):
        self._undo.append(self.canvas.copy())
        self._redo.clear()

    def undo(self):
        if len(self._undo) > 1:
            self._redo.append(self._undo.pop())
            self.canvas = self._undo[-1].copy()
            self._reset_stroke()
            return True
        return False

    def redo(self):
        if self._redo:
            state = self._redo.pop()
            self._undo.append(state)
            self.canvas = state.copy()
            self._reset_stroke()
            return True
        return False

    def clear(self):
        self._push_undo()
        self.canvas = self._blank()
        self._reset_stroke()
        self.trail.clear()

    # ── draw entry ────────────────────────────────────────────────────────────

    def draw(self, raw_point):
        if raw_point is None:
            self._end_stroke()
            return
        pt = self._smoother.smooth(raw_point)
        self.trail.append(pt)
        if self.draw_mode == 'FREE':
            self._free_draw(pt)
        else:
            self._shape_preview(pt)

    # ── free draw with glow ───────────────────────────────────────────────────

    def _free_draw(self, pt):
        color  = self._draw_color()
        size   = self.brush_size * 2 if self.eraser_mode else self.brush_size

        if self.previous_point is None:
            self._push_undo()
            self._draw_point_glow(pt, color, size)
        else:
            curve_pts = self._smoother.get_spline_points(pt)
            prev = self.previous_point
            for cp in curve_pts:
                self._draw_line_glow(prev, cp, color, size)
                prev = cp

        self.previous_point = pt

    def _draw_point_glow(self, pt, color, size):
        if GLOW_ENABLED and not self.eraser_mode:
            glow_size  = size + GLOW_RADIUS
            glow_color = _dim_color(color, GLOW_ALPHA)
            # draw glow on a temp layer, blend
            tmp = self.canvas.copy()
            cv2.circle(tmp, pt, glow_size * 2, glow_color, -1, cv2.LINE_AA)
            cv2.addWeighted(tmp, GLOW_ALPHA, self.canvas, 1 - GLOW_ALPHA, 0, self.canvas)
        cv2.circle(self.canvas, pt, size, color, -1, cv2.LINE_AA)

    def _draw_line_glow(self, p1, p2, color, size):
        if GLOW_ENABLED and not self.eraser_mode:
            glow_size  = size * 2 + GLOW_RADIUS * 2
            glow_color = _dim_color(color, GLOW_ALPHA)
            tmp = self.canvas.copy()
            cv2.line(tmp, p1, p2, glow_color, glow_size, cv2.LINE_AA)
            cv2.addWeighted(tmp, GLOW_ALPHA, self.canvas, 1 - GLOW_ALPHA, 0, self.canvas)
        cv2.line(self.canvas, p1, p2, color, size * 2, cv2.LINE_AA)

    # ── shape preview ─────────────────────────────────────────────────────────

    def _shape_preview(self, pt):
        if self.shape_start is None:
            self.shape_start = pt
            self._push_undo()

        preview = self.canvas.copy()
        color   = self._draw_color()
        thick   = max(2, self.brush_size)

        if GLOW_ENABLED and not self.eraser_mode:
            glow_c = _dim_color(color, 0.5)
            _draw_shape_on(preview, self.draw_mode, self.shape_start, pt, glow_c, thick + GLOW_RADIUS * 2)
        _draw_shape_on(preview, self.draw_mode, self.shape_start, pt, color, thick)

        self._shape_overlay = preview

    def commit_shape(self):
        if self._shape_overlay is not None:
            self.canvas = self._shape_overlay.copy()
        self._shape_overlay = None
        self.shape_start    = None
        self._reset_stroke()

    # ── color helpers ────────────────────────────────────────────────────────

    def _draw_color(self):
        if self.eraser_mode:
            return tuple(int(x) for x in CANVAS_BG_COLOR)
        if self.opacity >= 255:
            return self.current_color
        factor = self.opacity / 255.0
        return tuple(
            int(self.current_color[i] * factor + CANVAS_BG_COLOR[i] * (1 - factor))
            for i in range(3)
        )

    def _reset_stroke(self):
        self._smoother.reset()
        self.previous_point = None

    def _end_stroke(self):
        if self.draw_mode != 'FREE':
            self.commit_shape()
        else:
            self._reset_stroke()
        self.trail.clear()

    # ── setters ───────────────────────────────────────────────────────────────

    def set_color(self, name):
        if name in COLORS:
            self.current_color = COLORS[name]
            self.eraser_mode   = False

    def set_brush_size(self, s):
        self.brush_size = max(MIN_BRUSH_SIZE, min(MAX_BRUSH_SIZE, s))

    def increase_brush_size(self):
        self.brush_size = min(MAX_BRUSH_SIZE, self.brush_size + 1)

    def decrease_brush_size(self):
        self.brush_size = max(MIN_BRUSH_SIZE, self.brush_size - 1)

    def set_opacity(self, v):
        self.opacity = max(MIN_OPACITY, min(MAX_OPACITY, v))

    def increase_opacity(self):
        self.opacity = min(MAX_OPACITY, self.opacity + 15)

    def decrease_opacity(self):
        self.opacity = max(MIN_OPACITY, self.opacity - 15)

    def toggle_eraser(self):
        self.eraser_mode = not self.eraser_mode
        return self.eraser_mode

    def set_eraser_mode(self, v):
        self.eraser_mode = v

    def set_draw_mode(self, mode):
        if self.draw_mode != mode:
            if self.shape_start is not None:
                self._shape_overlay = None
                self.shape_start    = None
            self.draw_mode = mode
            self._reset_stroke()

    def reset_previous_point(self):
        if self.draw_mode != 'FREE' and self.shape_start is not None:
            self.commit_shape()
        else:
            self._reset_stroke()

    # ── getters ───────────────────────────────────────────────────────────────

    def get_canvas(self):
        if self._shape_overlay is not None:
            return self._shape_overlay
        return self.canvas

    def save_canvas(self, filename='drawing.png'):
        cv2.imwrite(filename, self.canvas)
        return filename


# ── module helpers ────────────────────────────────────────────────────────────

def _dim_color(color, alpha):
    """Brighten a color toward white by alpha factor (for glow halo)."""
    return tuple(min(255, int(c + (255 - c) * alpha * 0.6)) for c in color)


def _draw_shape_on(img, mode, start, end, color, thick):
    if mode == 'LINE':
        cv2.line(img, start, end, color, thick, cv2.LINE_AA)

    elif mode == 'RECT':
        cv2.rectangle(img, start, end, color, thick, cv2.LINE_AA)

    elif mode == 'CIRCLE':
        cx = (start[0] + end[0]) // 2
        cy = (start[1] + end[1]) // 2
        r  = max(1, int(math.hypot(end[0]-start[0], end[1]-start[1]) / 2))
        cv2.circle(img, (cx, cy), r, color, thick, cv2.LINE_AA)

    elif mode == 'ELLIPSE':
        cx = (start[0] + end[0]) // 2
        cy = (start[1] + end[1]) // 2
        ax = max(1, abs(end[0] - start[0]) // 2)
        ay = max(1, abs(end[1] - start[1]) // 2)
        cv2.ellipse(img, (cx, cy), (ax, ay), 0, 0, 360, color, thick, cv2.LINE_AA)

    elif mode == 'TRIANGLE':
        x1, y1 = start
        x2, y2 = end
        mx = (x1 + x2) // 2
        pts = np.array([[mx, y1], [x1, y2], [x2, y2]], dtype=np.int32)
        cv2.polylines(img, [pts], True, color, thick, cv2.LINE_AA)

    elif mode == 'ARROW':
        cv2.arrowedLine(img, start, end, color, thick, cv2.LINE_AA, tipLength=0.3)

    elif mode == 'STAR':
        cx = (start[0] + end[0]) // 2
        cy = (start[1] + end[1]) // 2
        r  = max(5, int(math.hypot(end[0]-start[0], end[1]-start[1]) / 2))
        inner = r * 0.4
        pts   = []
        for i in range(10):
            angle = math.radians(-90 + i * 36)
            rad   = r if i % 2 == 0 else inner
            pts.append((int(cx + rad * math.cos(angle)),
                        int(cy + rad * math.sin(angle))))
        cv2.polylines(img, [np.array(pts, dtype=np.int32)], True, color, thick, cv2.LINE_AA)
