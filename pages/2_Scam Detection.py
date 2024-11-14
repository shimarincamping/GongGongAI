import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import gonggongai

import streamlit as st
import streamlit_scrollable_textbox as stx #https://github.com/RobertoFN/streamlit-scrollable-textbox
from streamlit_text_rating.st_text_rater import st_text_rater #https://github.com/TVS-Motor-Company/streamlit-text-rating/blob/main/README.md

APPLICATION_MODE = 2
##############################################################################################

st.title("Scam Detection")

st.header(":grey[Upload Screenshots]", divider="grey")
uploaded_image = st.file_uploader("Upload a screenshot of the UI you want to check.", type=["jpg", "jpeg", "png"])

if uploaded_image:
    st.image(uploaded_image)
    st.success("Image uploaded successfully!")

    gonggongai.cache_uploaded_image(uploaded_image)

    detect = st.button("Detect Scam")
    if detect:
        st.header(":grey[Scam Detection Results]", divider="grey")

        gemini_response = gonggongai.get_ai_output(image_file_path="image.png", application_mode=APPLICATION_MODE)
        output_json = gemini_response["data"]

        red_flags = output_json["red_flags"]
        score = int(output_json["scam_risk_score"])
        advice = output_json["advice"]

        color = "red" if score >= 70 else "#FFC300" if score >= 30 else "#35a71a"

        st.subheader(":grey[Scam Risk Score]")
        st.markdown("<p style='margin-bottom: -30px;'>Likelihood of Scam</p>", unsafe_allow_html=True)
        st.markdown(f"<h1 style='color:{color}; font-size:64px;'>{score}%</h3>", unsafe_allow_html=True)

        st.subheader(":grey[Advice]")
        stx.scrollableTextbox(advice, height=200)

        if len(red_flags):
            st.subheader(":grey[Red Flags]")
            stx.scrollableTextbox("\n".join(["• " + i for i in red_flags]), height=250)
    
        response = st_text_rater(text="Is this text helpful?")
        
else: 
    st.info("Please upload an image file.")


