"""
Point Smoothing Module v4.0
===========================
Triple-exponential pipeline + larger Catmull-Rom buffer for maximum silkiness.

  L1 — Jitter gate         : raw noise < JITTER_PX discarded instantly
  L2 — Triple-exponential  : position + velocity + acceleration EMAs
                             adaptive alpha; very slow ceiling for ultra-smooth
  L3 — Catmull-Rom spline  : SPLINE_BUF control points → continuous curves
"""

import math
from config.settings import SMOOTH_POS, SMOOTH_VEL, JITTER_PX, INTERP_STEPS, ADAPTIVE, SPLINE_BUF


class PointSmoother:

    def __init__(self):
        self._sx  = None
        self._sy  = None
        self._vx  = 0.0
        self._vy  = 0.0
        self._ax  = 0.0    # acceleration EMA
        self._ay  = 0.0
        self._buf = []

    def smooth(self, raw: tuple) -> tuple:
        rx, ry = float(raw[0]), float(raw[1])

        if self._sx is None:
            self._sx, self._sy = rx, ry
            self._buf = [(int(rx), int(ry))]
            return (int(rx), int(ry))

        # L1 jitter gate
        dist = math.hypot(rx - self._sx, ry - self._sy)
        if dist < JITTER_PX:
            return (int(round(self._sx)), int(round(self._sy)))

        # L2 triple-exponential
        raw_vx = rx - self._sx
        raw_vy = ry - self._sy
        speed  = math.hypot(raw_vx, raw_vy)

        self._vx = SMOOTH_VEL * self._vx + (1 - SMOOTH_VEL) * raw_vx
        self._vy = SMOOTH_VEL * self._vy + (1 - SMOOTH_VEL) * raw_vy

        self._ax = 0.88 * self._ax + 0.12 * (self._vx - raw_vx)
        self._ay = 0.88 * self._ay + 0.12 * (self._vy - raw_vy)

        if ADAPTIVE:
            # speed=0  -> alpha~0.07  (ultra silky)
            # speed=80 -> alpha~0.55  (still controlled)
            alpha = min(0.55, 0.07 + speed / 130.0)
        else:
            alpha = 1.0 - SMOOTH_POS

        pred_x = self._sx + self._vx * 0.45 + self._ax * 0.10
        pred_y = self._sy + self._vy * 0.45 + self._ay * 0.10

        self._sx = alpha * rx + (1 - alpha) * pred_x
        self._sy = alpha * ry + (1 - alpha) * pred_y

        pt = (int(round(self._sx)), int(round(self._sy)))

        # L3 spline buffer
        self._buf.append(pt)
        if len(self._buf) > SPLINE_BUF:
            self._buf.pop(0)

        return pt

    def get_spline_points(self, new_pt: tuple) -> list:
        all_pts = self._buf[-3:] + [new_pt]
        if len(all_pts) < 4:
            return [new_pt]
        return _catmull_rom(all_pts, steps=INTERP_STEPS)

    def reset(self):
        self._sx = None
        self._sy = None
        self._vx = 0.0
        self._vy = 0.0
        self._ax = 0.0
        self._ay = 0.0
        self._buf = []

    @staticmethod
    def interpolate(p1: tuple, p2: tuple, steps: int = 8) -> list:
        if steps <= 0:
            return [p2]
        pts = []
        for i in range(1, steps + 1):
            t = i / (steps + 1)
            pts.append((int(p1[0] + t*(p2[0]-p1[0])),
                        int(p1[1] + t*(p2[1]-p1[1]))))
        pts.append(p2)
        return pts


def _catmull_rom(pts: list, steps: int = 8) -> list:
    if len(pts) < 4:
        return pts
    p0, p1, p2, p3 = pts[0], pts[1], pts[2], pts[3]
    result = []
    for i in range(steps + 1):
        t  = i / steps
        t2 = t * t
        t3 = t2 * t
        x = int(0.5 * ((2*p1[0]) +
                       (-p0[0] + p2[0]) * t +
                       (2*p0[0] - 5*p1[0] + 4*p2[0] - p3[0]) * t2 +
                       (-p0[0] + 3*p1[0] - 3*p2[0] + p3[0]) * t3))
        y = int(0.5 * ((2*p1[1]) +
                       (-p0[1] + p2[1]) * t +
                       (2*p0[1] - 5*p1[1] + 4*p2[1] - p3[1]) * t2 +
                       (-p0[1] + 3*p1[1] - 3*p2[1] + p3[1]) * t3))
        result.append((x, y))
    return result
