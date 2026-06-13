"""
UI Manager v4.0
===============
Dark neon HUD to match the dark canvas.
Color swatches show neon glow ring when selected.
Trail uses additive blending for extra luminosity.
"""

import cv2
import time
import math
import numpy as np
from config.settings import (
    COLORS, UI_BUTTON_SIZE, UI_BUTTON_MARGIN,
    CANVAS_WIDTH, CANVAS_HEIGHT, HOVER_TIME, UI_HEIGHT,
)

_BG    = (14,  12,  20)        # ultra-dark panel
_LINE  = (60,  220, 180)       # teal separator
_DIM   = (60,  60,  70)
_TEXT  = (190, 190, 205)
_HBAR  = (40,  200, 120)       # hover progress bar

_BS  = UI_BUTTON_SIZE          # 44
_BM  = UI_BUTTON_MARGIN        # 5
_R1Y = 8
_R2Y = _R1Y + _BS + _BM
_R3Y = _R2Y + _BS + _BM        # ~106

_BTN_H = 28


def _btn(name, x, y, w, h, color):
    return dict(name=name, x=x, y=y, width=w, height=h, color=color)


class UIManager:

    def __init__(self):
        color_items = list(COLORS.items())
        row1 = color_items[:8]
        row2 = color_items[8:]

        self._color_btns = []
        for i, (name, bgr) in enumerate(row1):
            x = 8 + i * (_BS + _BM)
            self._color_btns.append(_btn(name, x, _R1Y, _BS, _BS, bgr))
        for i, (name, bgr) in enumerate(row2):
            x = 8 + i * (_BS + _BM)
            self._color_btns.append(_btn(name, x, _R2Y, _BS, _BS, bgr))

        # Eraser (spans both color rows, right side)
        ex = 8 + 8 * (_BS + _BM) + 4
        self._eraser_btn = _btn('ERASER', ex, _R1Y, _BS + 10, _BS * 2 + _BM, (35, 30, 50))

        # Row 3 action buttons
        x = 8
        self._brush_up   = _btn('B+',   x,  _R3Y, 42, _BTN_H, (25, 100, 40));  x += 48
        self._brush_down = _btn('B-',   x,  _R3Y, 42, _BTN_H, (100,25, 40));   x += 52
        self._undo_btn   = _btn('UNDO', x,  _R3Y, 58, _BTN_H, (30, 50, 120));  x += 64
        self._redo_btn   = _btn('REDO', x,  _R3Y, 58, _BTN_H, (30, 50, 120));  x += 68
        self._opa_up     = _btn('O+',   x,  _R3Y, 40, _BTN_H, (60, 30, 110));  x += 46
        self._opa_down   = _btn('O-',   x,  _R3Y, 40, _BTN_H, (60, 30, 110));  x += 52

        shapes    = ['FREE', 'LINE', 'RECT', 'CIRC', 'ELPS', 'TRI', 'ARRW', 'STAR']
        shape_map = {
            'FREE':'FREE','LINE':'LINE','RECT':'RECT','CIRC':'CIRCLE',
            'ELPS':'ELLIPSE','TRI':'TRIANGLE','ARRW':'ARROW','STAR':'STAR'
        }
        self._shape_map  = shape_map
        self._shape_btns = []
        x += 4
        for s in shapes:
            self._shape_btns.append(_btn(s, x, _R3Y, 52, _BTN_H, (28, 25, 45)))
            x += 58

        self._clear_btn = _btn('CLEAR', CANVAS_WIDTH - 130, _R3Y, 60, _BTN_H, (70, 20, 20))
        self._save_btn  = _btn('SAVE',  CANVAS_WIDTH - 64,  _R3Y, 58, _BTN_H, (20, 90, 40))

        self._all = (
            self._color_btns +
            [self._eraser_btn,
             self._brush_up, self._brush_down,
             self._undo_btn, self._redo_btn,
             self._opa_up,   self._opa_down] +
            self._shape_btns +
            [self._clear_btn, self._save_btn]
        )

        self._hbtn   = None
        self._ht0    = None
        self._last_t = 0.0
        self._cool   = 0.25

    # ── draw HUD ──────────────────────────────────────────────────────────────

    def draw_ui(self, frame, current_color, brush_size, current_mode,
                gesture, eraser_mode=False, draw_mode='FREE',
                opacity=255, trail=None):

        _PANEL = _R3Y + _BTN_H + 8

        # Panel bg
        ov = frame.copy()
        cv2.rectangle(ov, (0, 0), (CANVAS_WIDTH, _PANEL), _BG, -1)
        cv2.addWeighted(ov, 0.88, frame, 0.12, 0, frame)

        # Glowing separator line
        cv2.line(frame, (0, _PANEL), (CANVAS_WIDTH, _PANEL), _LINE, 1)

        # Color swatches
        for btn in self._color_btns:
            active = (btn['color'] == current_color) and not eraser_mode
            _draw_neon_swatch(frame, btn, active)

        # Eraser
        _draw_eraser_btn(frame, self._eraser_btn, eraser_mode)

        # Action buttons
        for btn, label in [
            (self._brush_up,   'B+'),
            (self._brush_down, 'B-'),
            (self._undo_btn,   'UNDO'),
            (self._redo_btn,   'REDO'),
            (self._opa_up,     'O+'),
            (self._opa_down,   'O-'),
            (self._clear_btn,  'CLEAR'),
            (self._save_btn,   'SAVE'),
        ]:
            self._draw_btn(frame, btn)
            _clabel(frame, label, btn)

        # Shape buttons
        for btn in self._shape_btns:
            active = self._shape_map.get(btn['name']) == draw_mode
            self._draw_btn(frame, btn, active=active)
            _clabel(frame, btn['name'], btn)

        # Brush preview
        _draw_brush_preview(frame, brush_size, current_color, eraser_mode)

        # Opacity bar
        _draw_opacity_bar(frame, opacity, self._opa_down)

        # Status text
        by = CANVAS_HEIGHT - 56
        _txt(frame, f'MODE: {current_mode}',   12, by,      _LINE,         0.50)
        _txt(frame, f'GESTURE: {gesture}',      12, by + 20, (150,210,100), 0.44)
        _txt(frame,
             u'\u261d DRAW  |  \u270c SELECT/HOVER  |  \u270b CLEAR  |  z=undo  y=redo  s=save  q=quit',
             12, CANVAS_HEIGHT - 12, _DIM, 0.37)

        # Neon trail
        if trail:
            _draw_neon_trail(frame, list(trail), current_color if not eraser_mode else (100,100,120))

        return frame

    # ── hover ─────────────────────────────────────────────────────────────────

    def check_hover_activation(self, point):
        if point is None:
            self._reset_hover(); return None

        now = time.time()
        if now - self._last_t < self._cool:
            return None

        hit, action = None, None

        for btn in self._color_btns:
            if _hit(point, btn):
                hit    = btn['name']
                action = {'type': 'color', 'value': btn['name']}
                break

        if not hit:
            for btn, act in [
                (self._eraser_btn,   {'type':'tool',    'value':'eraser'}),
                (self._brush_up,     {'type':'brush',   'value':'increase'}),
                (self._brush_down,   {'type':'brush',   'value':'decrease'}),
                (self._undo_btn,     {'type':'action',  'value':'undo'}),
                (self._redo_btn,     {'type':'action',  'value':'redo'}),
                (self._opa_up,       {'type':'opacity', 'value':'increase'}),
                (self._opa_down,     {'type':'opacity', 'value':'decrease'}),
                (self._clear_btn,    {'type':'action',  'value':'clear'}),
                (self._save_btn,     {'type':'action',  'value':'save'}),
            ]:
                if _hit(point, btn):
                    hit, action = btn['name'], act; break

        if not hit:
            for btn in self._shape_btns:
                if _hit(point, btn):
                    hit    = btn['name']
                    action = {'type':'mode', 'value':self._shape_map[btn['name']]}
                    break

        if hit:
            if self._hbtn != hit:
                self._hbtn = hit; self._ht0 = now
            else:
                if now - self._ht0 >= HOVER_TIME:
                    self._reset_hover(); self._last_t = now
                    return action
        else:
            self._reset_hover()
        return None

    def get_hover_progress(self):
        if self._hbtn and self._ht0:
            return min((time.time() - self._ht0) / HOVER_TIME, 1.0)
        return 0.0

    # ── private ───────────────────────────────────────────────────────────────

    def _draw_btn(self, frame, btn, active=False):
        bx, by, bw, bh = btn['x'], btn['y'], btn['width'], btn['height']
        cv2.rectangle(frame, (bx, by), (bx+bw, by+bh), btn['color'], -1)
        border = _LINE if active else _DIM
        cv2.rectangle(frame, (bx, by), (bx+bw, by+bh), border, 2 if active else 1)
        if self._hbtn == btn['name'] and self._ht0:
            pw = int(bw * self.get_hover_progress())
            cv2.rectangle(frame, (bx, by+bh-3), (bx+pw, by+bh), _HBAR, -1)

    def _reset_hover(self):
        self._hbtn = None; self._ht0 = None


# ── module helpers ────────────────────────────────────────────────────────────

def _hit(pt, btn):
    x, y = pt
    return btn['x'] <= x <= btn['x']+btn['width'] and btn['y'] <= y <= btn['y']+btn['height']

def _draw_neon_swatch(frame, btn, active):
    bx, by, bw, bh = btn['x'], btn['y'], btn['width'], btn['height']
    # Filled swatch
    cv2.rectangle(frame, (bx+2, by+2), (bx+bw-2, by+bh-2), btn['color'], -1)
    # Glow border when active
    if active:
        # outer glow ring
        glow = tuple(min(255, c + 80) for c in btn['color'])
        cv2.rectangle(frame, (bx-3, by-3), (bx+bw+3, by+bh+3), glow, 2)
        cv2.rectangle(frame, (bx-1, by-1), (bx+bw+1, by+bh+1), (255,255,255), 1)
    else:
        cv2.rectangle(frame, (bx, by), (bx+bw, by+bh), _DIM, 1)

def _draw_eraser_btn(frame, btn, active):
    bx, by, bw, bh = btn['x'], btn['y'], btn['width'], btn['height']
    cv2.rectangle(frame, (bx, by), (bx+bw, by+bh), btn['color'], -1)
    border = (0, 200, 180) if active else _DIM
    cv2.rectangle(frame, (bx, by), (bx+bw, by+bh), border, 2 if active else 1)
    cx, cy = bx + bw//2, by + bh//2
    m = 10
    cv2.line(frame, (cx-m,cy-m), (cx+m,cy+m), (160,160,180), 2)
    cv2.line(frame, (cx+m,cy-m), (cx-m,cy+m), (160,160,180), 2)
    col = (0,200,180) if active else (100,100,120)
    _txt(frame, 'ERASER', bx+4, by+bh-4, col, 0.30)

def _clabel(frame, text, btn):
    cx = btn['x'] + btn['width']//2
    cy = btn['y'] + btn['height']//2 + 5
    sz, _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.38, 1)
    cv2.putText(frame, text, (cx-sz[0]//2, cy),
                cv2.FONT_HERSHEY_SIMPLEX, 0.38, _TEXT, 1, cv2.LINE_AA)

def _txt(frame, text, x, y, color, scale=0.48, thick=1):
    cv2.putText(frame, text, (x, y), cv2.FONT_HERSHEY_SIMPLEX,
                scale, color, thick, cv2.LINE_AA)

def _draw_brush_preview(frame, size, color, eraser):
    px, py = 4, _R3Y + _BTN_H//2
    c = (120, 120, 140) if eraser else color
    r = max(4, min(size, 13))
    # glow ring
    if not eraser:
        glow = tuple(min(255, ch + 60) for ch in color)
        cv2.circle(frame, (px+r, py), r+3, glow, 1, cv2.LINE_AA)
    cv2.circle(frame, (px+r, py), r, c, -1, cv2.LINE_AA)

def _draw_opacity_bar(frame, opacity, ref_btn):
    x  = ref_btn['x'] + ref_btn['width'] + 5
    y  = ref_btn['y']
    bh = ref_btn['height']
    w  = 7
    cv2.rectangle(frame, (x, y), (x+w, y+bh), _DIM, -1)
    filled = int(bh * opacity / 255)
    cv2.rectangle(frame, (x, y+bh-filled), (x+w, y+bh), _LINE, -1)

def _draw_neon_trail(frame, pts, color):
    """Additive-style neon trail — each point brighter and larger toward tip."""
    n = len(pts)
    for i, pt in enumerate(pts):
        frac  = (i + 1) / n
        r     = max(1, int(5 * frac))
        alpha = frac * 0.75
        # brighten color
        c = tuple(min(255, int(ch * 0.4 + 255 * alpha * 0.6)) for ch in color)
        cv2.circle(frame, pt, r, c, -1, cv2.LINE_AA)
