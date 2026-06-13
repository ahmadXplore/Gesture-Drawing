# 🛠️ SETUP GUIDE — Gesture Drawing v3.0

Follow this guide to get drawing with your hands in under 5 minutes.

---

## ✅ Requirements

- Python **3.10 or 3.11** (recommended — 3.12 may have mediapipe issues)
- A working **webcam**
- Windows 10/11, macOS 12+, or Ubuntu 20.04+
- ~500 MB disk space

---

## 📥 Step 1 — Extract Files

Unzip `gesture_drawing_v3.zip` anywhere:

```
Windows : C:\Users\YourName\gesture_drawing_v3\
Mac/Linux: ~/gesture_drawing_v3/
```

Open a terminal and navigate there:

```bash
# Windows CMD
cd C:\Users\YourName\gesture_drawing_v3

# Windows Git Bash / PowerShell
cd /c/Users/YourName/gesture_drawing_v3

# Mac / Linux
source venv/bin/activate
cd ~/gesture_drawing_v3
```

---

## 🐍 Step 2 — Create Virtual Environment

```bash
python -m venv venv
```

**Activate:**

```bash
# Windows CMD
venv\Scripts\activate

# Windows Git Bash / PowerShell
source venv/Scripts/activate

# Mac / Linux
source venv/bin/activate
```

You'll see `(venv)` at the start of your prompt.

---

## 📦 Step 3 — Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

> Important: install and run the project from the repository's local virtual environment.
> If you use Windows, call `venv\Scripts\activate.bat` first or run `venv\Scripts\python.exe main.py` directly.

> ⏳ First install takes 2–5 minutes.

### If you hit errors:

**mediapipe / protobuf conflict:**

```bash
pip uninstall mediapipe protobuf -y
pip cache purge
pip install protobuf==4.25.3
pip install mediapipe==0.10.9
```

**Python 3.12:**

```bash
pip install mediapipe==0.10.11
```

---

## 🚀 Step 4 — Run

```bash
python main.py
```

If your terminal is already showing `(venv)`, this runs the project Python. If not, use the venv Python directly on Windows:

```bash
./venv/Scripts/python.exe main.py
```

Window titled **"✋ Gesture Drawing v3.0"** opens with your camera feed.

---

## 🎮 How to Use

Position yourself **30–70 cm** from the camera, hand clearly visible.

### Gestures

| Gesture                      | Action                                               |
| ---------------------------- | ---------------------------------------------------- |
| ☝️ **Index finger only**     | DRAW (or ERASE if eraser active)                     |
| ✌️ **Index + Middle finger** | SELECT — hover over UI buttons for 0.65s to activate |
| 🖐️ **Open palm (all 5)**     | CLEAR canvas instantly                               |

### Keyboard Shortcuts

| Key | Action         |
| --- | -------------- |
| `Z` | Undo           |
| `Y` | Redo           |
| `S` | Save as PNG    |
| `C` | Clear canvas   |
| `1` | Free draw mode |
| `2` | Line mode      |
| `3` | Rectangle mode |
| `4` | Circle mode    |
| `5` | Ellipse mode   |
| `6` | Triangle mode  |
| `7` | Arrow mode     |
| `8` | Star mode      |
| `Q` | Quit           |

---

## 🖥️ HUD Layout

```
┌─────────────────────────────────────────────────────────────────┐
│ [W][K][R][O][Y][G][L][G][C]    ← 9 colors row 1    [ERASER]    │
│ [S][B][N][P][V][M][P][B][G]    ← 9 colors row 2               │
│ [B+][B-][UNDO][REDO][O+][O-] [FREE][LINE][RECT][CIRC][ELPS]   │
│                                [TRI][ARRW][STAR]  [CLEAR][SAVE] │
└─────────────────────────────────────────────────────────────────┘
```

**To use a button:** raise 2 fingers (SELECT gesture) and hover your hand over the button for 0.65 seconds — a green progress bar fills up and it activates.

---

## 🎨 18 Available Colors

White, Black, Red, Orange, Yellow, Gold, Lime, Green,
Cyan, Sky Blue, Blue, Navy, Purple, Violet, Magenta, Pink, Brown, Gray

---

## ✏️ Shape Modes

Draw all shapes by pointing with **1 finger**:

- **FREE** — freehand drawing (default)
- **LINE** — straight line (drag from start to end)
- **RECT** — rectangle (drag corner to corner)
- **CIRCLE** — circle (drag to set radius)
- **ELLIPSE** — oval (drag to set axes)
- **TRIANGLE** — equilateral-style triangle
- **ARROW** — directional arrow
- **STAR** — 5-pointed star

---

## 💡 Tips for Best Results

1. **Good lighting** — face a light source, avoid backlight
2. **Plain background** — a blank wall behind your hand helps MediaPipe a lot
3. **Rest your elbow** — steadies the hand for smoother strokes
4. **Extend fingers clearly** — make gestures deliberate
5. **Move slowly for details** — the smoother tracks fast movement too, but slow = most precise

---

## ⚙️ Tuning (`config/settings.py`)

```python
# Smoothing — increase for smoother, decrease if it feels laggy
SMOOTH_POS = 0.72      # 0.0 = raw  ←→  1.0 = frozen

# Camera index (try 1 or 2 if camera not found)
CAMERA_INDEX = 0

# Hover time to activate a button (seconds)
HOVER_TIME = 0.65

# Canvas background (default white so black ink is visible)
CANVAS_BG_COLOR = (255, 255, 255)
```

---

## 🐛 Troubleshooting

| Problem                     | Fix                                                                                                                |
| --------------------------- | ------------------------------------------------------------------------------------------------------------------ |
| `No module named mediapipe` | Activate venv, run `pip install -r requirements.txt`; if activation fails, run `./venv/Scripts/python.exe main.py` |
| Camera black / not found    | Change `CAMERA_INDEX` to `1` or `2`                                                                                |
| Low FPS                     | Close other apps; set `CAMERA_WIDTH = 640` in settings                                                             |
| Hand not detected           | Better lighting; lower `DETECTION_CONFIDENCE = 0.5`                                                                |
| Strokes still jittery       | Increase `SMOOTH_POS` to `0.80` in settings                                                                        |
| Strokes feel laggy          | Decrease `SMOOTH_POS` to `0.55` in settings                                                                        |
| protobuf error              | `pip install protobuf==4.25.3`                                                                                     |
| DLL error (Windows)         | Install [VC++ Redistributable](https://aka.ms/vs/17/release/vc_redist.x64.exe)                                     |

---

## 📁 Saved Drawings

Saved as PNG in the same folder as `main.py`:

```
drawing_20240318_143022.png
```

---

**Happy drawing! 🎨✋**
