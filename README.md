# Face Recognition Attendance System

A Python-based **Face Recognition Attendance System** that uses OpenCV and K-Nearest Neighbors (KNN) to recognize faces and automatically record attendance with the person's name and timestamp.

## Features

- Real-time face detection using OpenCV
- Face recognition using K-Nearest Neighbors (KNN)
- Automatic attendance recording
- Attendance saved in CSV format
- Date-wise attendance files
- Live camera preview
- Background UI for the camera feed
- Streamlit support for a web-based interface

## Technologies Used

- **Python**
- **OpenCV**
- **NumPy**
- **Scikit-learn**
- **Pickle**
- **CSV**
- **Streamlit**

## Project Structure

```text
jarvis/
│
├── app.py
├── test.py
├── GitHub Attendance System Infographic.png
│
├── data/
│   ├── names.pkl
│   ├── faces_data.pkl
│   └── haarcascade_frontalface_default.xml
│
└── attendance/
    └── attendance_DD-MM-YY.csv
```

## Installation

### 1. Clone or download the project

Open PowerShell or Command Prompt and navigate to the project folder:

```bash
cd "C:\Users\hkdew\Desktop\New folder\jarvis"
```

### 2. Install required packages

```bash
python -m pip install opencv-python numpy scikit-learn streamlit
```

If you are using a virtual environment, activate it before installing the packages.

## Running the Project

### OpenCV Version

To run the camera-based attendance system:

```bash
python test.py
```

A camera window should open.

- Show your face to the camera.
- The system detects and recognizes the face.
- Press **`O`** to save attendance.
- Press **`Q`** to quit.

Attendance will be stored in:

```text
attendance/
```

For example:

```text
attendance/attendance_03-10-26.csv
```

The CSV file contains:

```text
NAME,TIME
John,10:30:25
Alex,10:35:42
```

### Streamlit Version

If you are using `app.py`, run it with:

```bash
python -m streamlit run app.py
```

Do **not** normally run a Streamlit application using:

```bash
python app.py
```

After starting Streamlit, open the URL shown in the terminal, usually:

```text
http://localhost:8501
```

## How Face Recognition Works

The system follows these basic steps:

```text
Camera
   ↓
Face Detection
   ↓
Crop Face
   ↓
Resize Face
   ↓
Convert to Feature Data
   ↓
KNN Classifier
   ↓
Recognized Name
   ↓
Save Attendance
```

### Face Detection

OpenCV's Haar Cascade classifier is used to detect faces:

```python
facedetect = cv2.CascadeClassifier(
    'data/haarcascade_frontalface_default.xml'
)
```

### Face Recognition

The stored face data is loaded from:

```text
data/faces_data.pkl
```

Names are loaded from:

```text
data/names.pkl
```

A KNN classifier is then trained:

```python
knn = KNeighborsClassifier(n_neighbors=5)
knn.fit(FACES, LABELS)
```

### Attendance

When a face is recognized, the system records:

- Name
- Date
- Time

The attendance is stored as a CSV file.

## Important Keyboard Controls

| Key | Action |
|---|---|
| `O` | Save attendance |
| `Q` | Quit application |

Make sure the OpenCV camera window is focused before pressing the keys.

## Troubleshooting

### `ModuleNotFoundError: No module named 'streamlit'`

Install Streamlit:

```bash
python -m pip install streamlit
```

Then run:

```bash
python -m streamlit run app.py
```

### `ModuleNotFoundError: No module named 'cv2'`

Install OpenCV:

```bash
python -m pip install opencv-python
```

### `ModuleNotFoundError: No module named 'sklearn'`

Install scikit-learn:

```bash
python -m pip install scikit-learn
```

### Camera is not opening

Check that:

- Your webcam is connected.
- No other application is using the camera.
- Your Python program has permission to access the camera.

The camera is opened using:

```python
video = cv2.VideoCapture(0)
```

If you have multiple cameras, try:

```python
video = cv2.VideoCapture(1)
```

### `csv.writer()` error

Make sure you pass the opened CSV file:

```python
with open(filename, "a", newline="") as csvfile:
    writer = csv.writer(csvfile)
```

Not:

```python
writer = csv.writer()
```

### Background image error

If you use:

```python
frame = cv2.resize(frame, (800, 600))

imgBackground[162:762, 55:855] = frame
```

your background image must be large enough to contain that region.

You can check its dimensions with:

```python
print(imgBackground.shape)
```

## Requirements

Recommended:

- Python 3.9+
- Webcam
- Windows/Linux/macOS
- At least 4 GB RAM

## Future Improvements

Possible improvements include:

- Add a face-registration interface
- Add a database instead of CSV files
- Add login/authentication
- Add attendance history
- Add an admin dashboard
- Export attendance reports
- Prevent duplicate attendance on the same day
- Add multiple camera support
- Improve recognition accuracy
- Add a modern Streamlit interface

## Disclaimer

This project is intended for educational and demonstration purposes. Face recognition systems can produce incorrect matches, so attendance records should be reviewed when accuracy is important.

## Author

**HKDEW**

---

### Quick Start

```bash
python -m pip install opencv-python numpy scikit-learn streamlit
```

For the OpenCV application:

```bash
python test.py
```

For the Streamlit application:

```bash
python -m streamlit run app.py
```