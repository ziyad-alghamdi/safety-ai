Safety AI: Proactive Industrial Monitoring
Mufakker Safety AI is an advanced computer vision solution designed to enhance industrial safety by providing a "tireless eye" over construction and manufacturing environments. The system monitors real-time video feeds to ensure compliance with Personal Protective Equipment (PPE) protocols, specifically detecting the presence of safety helmets.

🚀 Key Features
Real-Time PPE Detection: Uses a custom-trained YOLOv8 model to detect workers and safety helmets with high precision.

Face Recognition & Accountability: Identifies specific workers (e.g., qaswarah) to link safety violations to individual profiles.

Dynamic Safety Scoring: Calculates a real-time safety percentage (0-100%) based on current site conditions and worker compliance.

Automated Alert System: Instantly triggers visual and data alerts via Socket.io when a safety violation is detected.

Web Dashboard: A modern, minimalist interface built with Next.js to display live feeds, scores, and worker status.

🛠️ Technical Stack
AI/ML: Python, YOLOv8 (Ultralytics), Face_Recognition.

Backend: Node.js, Socket.io (for real-time data bridging).

Frontend: Next.js, Tailwind CSS, Lucide React (for modern UI icons).

Tools: OpenCV (Camera stream management).

📂 Project Structure
Plaintext
safety-ai/
├── main.py              # Main AI Engine (YOLO + Face Recognition)
├── train.py             # ML Training script for PPE model
├── data.yaml            # Dataset configuration for YOLO training
├── users/               # Database of registered worker photos
└── safety-dashboard/    # Next.js web application
    ├── app/             # Frontend routes and components
    └── server.js        # Socket.io bridge server
⚙️ Installation & Setup
Clone the Repository:

Bash
git clone https://github.com/YourUsername/mufakker-safety-ai.git
cd mufakker-safety-ai
Install Python Dependencies:

Bash
pip install ultralytics face_recognition opencv-python flask flask-cors python-socketio
Install Frontend Dependencies:

Bash
cd safety-dashboard
npm install
🚦 How to Run
To start the full system, open three separate terminals:

Terminal 1 (Bridge Server):

Bash
node server.js
Terminal 2 (AI Engine):

Bash
python main.py
Terminal 3 (Dashboard):

Bash
npm run dev
Open http://localhost:3000 to view the live safety monitor.

📊 System Workflow
The system follows a 6-stage process: Video Input -> AI Detection -> Worker Recognition -> Violation Detection -> Safety Score Calculation -> Real-time Dashboard Update.

Developed by Mufakker Community Turning AI into a tool for safety and thinking.
