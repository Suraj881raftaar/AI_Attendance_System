# Mobile Phone Camera Test Adapter Documentation

## 1. Purpose & Overview

The **Mobile Phone Camera Test Adapter** (`MobileCameraFrameProvider`) is a **developer-only test utility** designed to stream live video frames from an Android mobile phone over a local Wi-Fi network into the existing AI Attendance Recognition pipeline.

It allows developers to test live recognition flows without requiring physical USB webcam hardware connected to the development PC.

> [!IMPORTANT]
> **TEST-ONLY COMPONENT**: The Mobile Phone Camera Adapter is an optional test component. It does NOT modify the production AI architecture, face detection, face embedding, cosine matching, attendance logic, or database schema. Removing this adapter leaves the core system 100% operational.

---

## 2. Requirements & Setup Procedure

### Android Phone Requirements
1. An Android phone connected to the **same Wi-Fi network** as the development PC.
2. Any standard local IP camera app (e.g. IP Webcam, DroidCam, or any app providing a standard HTTP/MJPEG/RTSP stream URL).

### How to Use
1. Open the IP camera application on the Android phone and start the local video server.
2. Note the stream URL shown on the phone screen (e.g., `http://192.168.1.105:8080/video`).
3. Launch the desktop AI Attendance application (`python main.py`).
4. Navigate to the **AI Attendance Engine** view tab.
5. Click the **"Mobile Camera (TEST)"** button in the provider selection panel.
6. Enter the mobile stream URL into the input dialog and click OK.
7. The live stream from the phone will render in the recognition canvas with green/red bounding boxes.
8. To stop streaming, click **"Stop Stream"**.

---

## 3. Privacy & Security Assurance

- **Local Wi-Fi Only**: Stream traffic flows directly between the phone and laptop over the local area network (LAN). No cloud services or external APIs are used.
- **Zero Raw Image Storage**: Incoming frames are processed in memory (RAM) and immediately discarded. No video recordings or facial photographs are saved to disk or committed to Git.
- **Biometric Security**: Only standard recognition metadata (similarity scores, student ID references) interact with the local SQLite database.

---

## 4. Troubleshooting & Fallback

- **Stream Unreachable / Failed to Open**: Verify that both the phone and laptop are connected to the same Wi-Fi network and that the port number in the URL matches the phone app.
- **Camera-less Fallback**: If the mobile stream is disconnected or unreachable, the application displays a friendly error label without crashing. The system continues supporting static image file (`ImageFrameProvider`) and pre-recorded video file (`VideoFrameProvider`) modes.
