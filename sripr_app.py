import streamlit as st
import google.generativeai as genai
from PIL import Image
import io

# --- AI SETUP ---
# Replace with your actual key from Google AI Studio
API_KEY = "AIzaSyCq9KogNV9eeKrA_7DAfxyyMeub_VMRx8c"
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-2.5-flash')

# --- STYLE THE BUTTONS ---
st.markdown("""
    <style>
    div.stButton > button {
        border-radius: 20px;
        background-color: #4CAF50;
        color: white;
        font-weight: bold;
        height: 3em;
        width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)

# --- APP STATE MANAGEMENT ---
if 'step' not in st.session_state:
    st.session_state.step = 'home'
if 'image' not in st.session_state:
    st.session_state.image = None

# --- HOME PAGE ---
if st.session_state.step == 'home':
    st.title("Physics Visualizer 2026")
    
    # 1. Album Selection
    uploaded_file = st.file_uploader("Select from Album", type=["jpg", "jpeg", "png"])
    if uploaded_file:
        st.session_state.image = Image.open(uploaded_file)
        st.session_state.step = 'process'
        st.rerun()

    st.write("--- OR ---")
    
    # 2. Camera Input
    cam_image = st.camera_input("Take a picture of your question")
    if cam_image:
        st.session_state.image = Image.open(cam_image)
        st.session_state.step = 'process'
        st.rerun()

# --- PROCESSING PAGE ---
elif st.session_state.step == 'process':
    st.title("Visualized Question")
    st.image(st.session_state.image, caption="Your Question", use_container_width=True)
    
    if st.button("Analyze & Solve"):
        with st.spinner("AI is thinking..."):
            prompt = """
            Analyze this physics image. 
            1. Explain the question in simple language.
            2. Create a simple SVG code to draw a diagram of the problem.
            3. Provide a step-by-step solution.
            Format response with headers: [EXPLANATION], [SVG], [SOLUTION].
            """
            try:
                response = model.generate_content([prompt, st.session_state.image])
                res_text = response.text
                
                # Safer parsing
                if "[SVG]" in res_text:
                    explanation = res_text.split("[EXPLANATION]")[1].split("[SVG]")[0]
                    svg_code = res_text.split("[SVG]")[1].split("[SOLUTION]")[0]
                    solution = res_text.split("[SOLUTION]")[1]
                    
                    st.subheader("What's happening?")
                    st.write(explanation)
                    
                    st.subheader("Diagram")
                    st.components.v1.html(svg_code, height=300)
                    
                    with st.expander("See Step-by-Step Solution"):
                        st.write(solution)
                else:
                    st.write(res_text) # Fallback if AI doesn't use tags
            except Exception as e:
                st.error(f"AI Error: {e}")

    if st.button("Start Over"):
        st.session_state.step = 'home'
        st.rerun()