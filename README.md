# 🎨 Gesture Drawing Application v3.0

> Draw with your hands in real-time — no mouse, no pen, just gestures.

Built with Python, OpenCV, and MediaPipe. Features Catmull-Rom spline smoothing, 8 shape modes, 18 colors, undo/redo, opacity control, and a polished dark HUD.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=flat-square)
![OpenCV](https://img.shields.io/badge/OpenCV-4.8.1-green?style=flat-square)
![MediaPipe](https://img.shields.io/badge/MediaPipe-0.10.9-red?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)

> Always run this project from the local `venv`.
> Use `venv\Scripts\activate.bat` or `venv\Scripts\python.exe main.py` on Windows to avoid broken MediaPipe imports.

---

## 📁 Project Structure

```
gesture_drawing_v3/
│
├── main.py                      ← Entry point — run this
│
├── config/
│   ├── __init__.py
│   └── settings.py              ← All tunable constants
│
├── utils/
│   ├── __init__.py
│   ├── hand_detector.py         ← MediaPipe hand tracking wrapper
│   ├── canvas.py                ← Drawing canvas (undo/redo, shapes, opacity)
│   └── smoother.py              ← 3-layer Catmull-Rom smoothing pipeline
│
├── gestures/
│   ├── __init__.py
│   └── recognizer.py            ← Gesture classification (DRAW/SELECT/CLEAR)
│
├── ui/
│   ├── __init__.py
│   └── manager.py               ← Dark HUD: 2-row colors, 8 shapes, hover system
│
├── requirements.txt
├── README.md                    ← This file
├── SETUP.md                     ← Step-by-step installation guide
└── CHANGELOG.md
```

---

## 🤚 Gestures

| Gesture            | Fingers        | Action                                   |
| ------------------ | -------------- | ---------------------------------------- |
| ☝️ **One Finger**  | Index only     | **DRAW** / ERASE                         |
| ✌️ **Two Fingers** | Index + Middle | **SELECT** — hover over UI buttons 0.65s |
| 🖐️ **Open Palm**   | All 5          | **CLEAR** canvas                         |

---

## ⌨️ Keyboard

| Key   | Action                                                          |
| ----- | --------------------------------------------------------------- |
| `Z`   | Undo (40 levels)                                                |
| `Y`   | Redo                                                            |
| `S`   | Save PNG                                                        |
| `C`   | Clear                                                           |
| `1–8` | Shape modes (Free/Line/Rect/Circle/Ellipse/Triangle/Arrow/Star) |
| `Q`   | Quit                                                            |

---

## ✨ v3.0 — What's New vs v2

### Bug Fixes

- **Black color now works** — canvas is white (was black), so all dark colors show correctly
- **Pinch gesture removed** — was triggering accidentally; brush size now controlled via B+/B– buttons in the HUD

### Smoother Strokes

The smoothing pipeline now has **3 layers**:

1. **Jitter gate** — sub-pixel noise (< 2.5px) discarded before anything else
2. **Double-exponential smoothing** with predictive velocity assist — adaptive alpha (slow hand = silkier, fast hand = more responsive)
3. **Catmull-Rom spline** — the last 4 smoothed points are used to generate a continuous curve. This is what makes strokes look drawn with a pen on paper rather than jagged line segments.

### More Colors — 18 total

White, Black, Red, Orange, Yellow, Gold, Lime, Green, Cyan, Sky Blue, Blue, Navy, Purple, Violet, Magenta, Pink, Brown, Gray — displayed in a 2-row palette in the HUD.

### More Shapes — 8 total

FREE · LINE · RECTANGLE · CIRCLE · ELLIPSE · TRIANGLE · ARROW · STAR

All shapes show a live preview while dragging and commit cleanly when you lift your finger.

---

## 🏗️ Architecture

```
Webcam Frame
     │
     ▼
HandDetector ──────────────────────────────────────────► landmarks (21 pts)
     │
     ▼
GestureRecognizer ─────────────────────────────────────► DRAW | SELECT | CLEAR
     │
     ▼
Main App
  ├── DRAW   ──► PointSmoother (jitter gate → double-exp → Catmull-Rom)
  │                            ──► Canvas.draw()
  ├── SELECT ──► UIManager.check_hover_activation() ──► action
  │                                                      ──► color/mode/brush changes
  └── CLEAR  ──► Canvas.clear()
                   │
                   ▼
             Canvas.get_canvas()    (shape preview overlay when active)
                   │
                   ▼
             cv2.addWeighted(frame, canvas)
                   │
                   ▼
             UIManager.draw_ui() ──► cv2.imshow()
```

---

## 📊 Specs

| Metric           | Value                                             |
| ---------------- | ------------------------------------------------- |
| Target FPS       | 30–60                                             |
| Gesture latency  | < 50 ms                                           |
| Undo depth       | 40 steps                                          |
| Smoothing layers | 3 (jitter gate + double-exp + Catmull-Rom spline) |
| Colors           | 18                                                |
| Shape modes      | 8                                                 |

---

## 👨‍💻 Author

Created by **Ahmad** — v3.0 with professor-grade smoothing, 18 colors, 8 shapes.

## 📝 License

MIT — free to use, modify, distribute.
