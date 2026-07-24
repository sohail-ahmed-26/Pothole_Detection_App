import streamlit as st
from ultralytics import YOLO
from PIL import Image
import tempfile
import numpy as np
import pandas as pd
import cv2
import time

# ----------------------------
# PAGE CONFIG
# ----------------------------

st.set_page_config(
    page_title="AI Road Pothole Detection",
    page_icon="🛣️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ----------------------------
# CUSTOM CSS
# ----------------------------

st.markdown("""
<style>

.main{
    background:#f5f7fb;
}

.block-container{
    padding-top:1rem;
}

.title{
    font-size:45px;
    font-weight:800;
    text-align:center;
    color:white;
}

.subtitle{
    text-align:center;
    color:white;
    font-size:18px;
}

.header{

background:linear-gradient(90deg,#2563eb,#7c3aed);

padding:30px;

border-radius:20px;

box-shadow:0px 5px 25px rgba(0,0,0,.20);

margin-bottom:25px;

}

.metric-card{

background:white;

padding:18px;

border-radius:15px;

box-shadow:0px 5px 20px rgba(0,0,0,.12);

text-align:center;

transition:0.3s;

}

.metric-card:hover{

transform:scale(1.02);

}

.footer{

text-align:center;

padding:25px;

color:gray;

}

</style>
""",unsafe_allow_html=True)

# ----------------------------
# HEADER
# ----------------------------

st.markdown("""

<div class="header">

<div class="title">

🛣️ AI Road Pothole Detection System

</div>

<div class="subtitle">

Computer Vision using YOLOv8 • Developed by Sohail Ahmed

</div>

</div>

""",unsafe_allow_html=True)

# ----------------------------
# SIDEBAR
# ----------------------------

st.sidebar.image(
"https://img.icons8.com/color/96/artificial-intelligence.png",
width=80
)

st.sidebar.title("Navigation")

st.sidebar.success("AI Powered Road Inspection")

st.sidebar.info("""

Upload any road image.

The trained YOLOv8 model

will automatically detect

road potholes.

""")

st.sidebar.write("---")

st.sidebar.markdown("""

### Model Information

• YOLOv8 Nano

• Object Detection

• Computer Vision

• Streamlit Deployment

""")

# ----------------------------
# LOAD MODEL
# ----------------------------

@st.cache_resource

def load_model():

    return YOLO("best.pt")

model=load_model()

# ----------------------------
# FILE UPLOADER
# ----------------------------

uploaded_file=st.file_uploader(

"📤 Upload Road Image",

type=["jpg","jpeg","png"]

)
st.markdown("---")

st.subheader("📷 Live Camera Detection")

run_camera = st.checkbox("Start Live Camera")
if run_camera:

    st.info("📷 Press 'q' in the camera window to stop.")

    cap = cv2.VideoCapture(0)

    frame_window = st.empty()

    while cap.isOpened():

        success, frame = cap.read()

        if not success:
            st.error("Camera not found!")
            break

        # YOLO Prediction
        results = model.predict(frame, conf=0.5)

        annotated_frame = results[0].plot()

        # Convert BGR → RGB
        annotated_frame = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)

        frame_window.image(
            annotated_frame,
            channels="RGB",
            use_container_width=True
        )

    cap.release()

# ----------------------------
# DETECTION
# ----------------------------

if uploaded_file:

    image = Image.open(uploaded_file)

    col1, col2 = st.columns(2)

    with col1:

        st.markdown("## 📷 Original Image")

        st.image(image, use_container_width=True)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:

        image.save(tmp.name)

        temp_path = tmp.name

    start = time.time()

    with st.spinner("🔍 AI is detecting potholes..."):

        results = model.predict(
            temp_path,
            conf=0.50,
            save=False
        )

    end = time.time()

    result = results[0].plot()

    with col2:

        st.markdown("## ✅ Detection Result")

        st.image(result, use_container_width=True)

    # ----------------------------
    # METRICS
    # ----------------------------

    boxes = results[0].boxes

    pothole_count = len(boxes)

    if pothole_count > 0:

        conf = boxes.conf.cpu().numpy()

        avg_conf = np.mean(conf) * 100

    else:

        avg_conf = 0

    detection_time = round(end - start, 2)

    st.write("")

    c1, c2, c3, c4 = st.columns(4)

    with c1:

        st.markdown(f"""

        <div class="metric-card">

        <h3>🕳️ Potholes</h3>

        <h1>{pothole_count}</h1>

        </div>

        """, unsafe_allow_html=True)

    with c2:

        st.markdown(f"""

        <div class="metric-card">

        <h3>🎯 Confidence</h3>

        <h1>{avg_conf:.1f}%</h1>

        </div>

        """, unsafe_allow_html=True)

    with c3:

        st.markdown("""

        <div class="metric-card">

        <h3>🤖 Model</h3>

        <h1>YOLOv8n</h1>

        </div>

        """, unsafe_allow_html=True)

    with c4:

        st.markdown(f"""

        <div class="metric-card">

        <h3>⚡ Time</h3>

        <h1>{detection_time}s</h1>

        </div>

        """, unsafe_allow_html=True)

    st.write("")

    # ----------------------------
    # DETECTION DETAILS
    # ----------------------------

    st.write("")
    st.markdown("## 📊 Detection Summary")

    if pothole_count > 0:

        data = []

        for i, box in enumerate(boxes):

            confidence = float(box.conf[0]) * 100

            cls = int(box.cls[0])

            data.append({
                "ID": i + 1,
                "Object": "Pothole",
                "Confidence": f"{confidence:.2f}%"
            })

        df = pd.DataFrame(data)

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )

    else:

        st.warning("No potholes detected.")

    # ----------------------------
    # DOWNLOAD IMAGE
    # ----------------------------

    result_rgb = cv2.cvtColor(result, cv2.COLOR_BGR2RGB)

    result_image = Image.fromarray(result_rgb)

    output = tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".png"
    )

    result_image.save(output.name)

    with open(output.name, "rb") as file:

        st.download_button(
            label="📥 Download Detection Result",
            data=file,
            file_name="Detected_Potholes.png",
            mime="image/png",
            use_container_width=True
        )

    st.success("✅ Detection Completed Successfully!")

# ----------------------------
# FOOTER
# ----------------------------

st.write("")

st.markdown("---")

st.markdown(
"""
<div class='footer'>

<h3>🛣️ AI Road Pothole Detection System</h3>

<p>
Powered by <b>YOLOv8</b> • Built with <b>Streamlit</b>
</p>

<p>
Developed by <b>Sohail Ahmed</b>
</p>

</div>
""",
unsafe_allow_html=True
)