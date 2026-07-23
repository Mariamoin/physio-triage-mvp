import streamlit as st
from google import genai
from google.genai import types

# Page Config
st.set_page_config(page_title="PhysioCare AI", page_icon="🏥", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f8fafc; }
    .stButton>button { background: linear-gradient(135deg, #0d9488 0%, #0284c7 100%); color: white; border-radius: 8px; font-weight: bold; width: 100%; }
    </style>
""", unsafe_allow_html=True)

st.title("🏥 PhysioCare Express Triage")
st.caption("Doctor-verified first-aid & local care guidance for sports and physio injuries")

# Safe Secrets Handling
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    api_key = None

if not api_key:
    api_key = st.sidebar.text_input("Enter Gemini API Key", type="password")

if api_key:
    client = genai.Client(api_key=api_key)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🎙️ 1. Describe Injury")
        audio_val = st.audio_input("Record Voice Note (Any Language)")
        text_val = st.text_input("Or type symptoms (e.g. 'Mera ghutna soojh gaya hai')")
        
        st.subheader("📷 2. Upload Visual")
        img_val = st.file_uploader("Upload Injury Photo (Optional)", type=["jpg", "png", "jpeg"])
        
        st.subheader("📍 3. Location")
        city_val = st.text_input("Your City / Area", value="Karachi")
        
        submit = st.button("⚡ Get Immediate First-Aid & Care Plan")

    with col2:
        st.subheader("📋 Clinical Triage & Action Plan")
        if submit:
            if not (audio_val or text_val or img_val):
                st.warning("Please provide voice, text, or an image.")
            else:
                with st.spinner("Analyzing condition with Gemini..."):
                    system_instruction = """
                    You are an expert Musculoskeletal & Sports Physical Therapy Triage Assistant.
                    CRITICAL RULE: Respond ENTIRELY in the EXACT SAME language/dialect as the user (Urdu, Roman Urdu, English, etc.).
                    1. Emergency Red-Flag Check: If severe trauma/deformity, alert ER immediately.
                    2. Primary First-Aid Action: Give ONE primary, safe home remedy (Icing with towel barrier, elevation).
                    3. What NOT To Do: Warn against applying heat/massage on acute swelling.
                    4. 4-Hour Reassessment Timer: Advise checking back in 4 hours.
                    """
                    
                    contents = []
                    if text_val: 
                        contents.append(text_val)
                    if audio_val:
                        contents.append(types.Part.from_bytes(data=audio_val.read(), mime_type="audio/wav"))
                    if img_val:
                        contents.append(types.Part.from_bytes(data=img_val.read(), mime_type=img_val.type))
                    
                    try:
                        response = client.models.generate_content(
                            model='gemini-2.5-flash',
                            contents=contents,
                            config=types.GenerateContentConfig(system_instruction=system_instruction)
                        )
                        st.markdown(response.text)
                        
                        st.subheader("📍 Nearby Clinics (< 5km)")
                        map_html = f"""
                        <iframe width="100%" height="280" frameborder="0" src="https://www.google.com/maps?q=physiotherapy+clinic+near+{city_val}&output=embed"></iframe>
                        """
                        st.components.v1.html(map_html, height=300)
                    except Exception as e:
                        st.error(f"Error: {e}")
