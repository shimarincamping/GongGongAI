import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import gonggongai

import streamlit as st
from audiorecorder import audiorecorder #https://github.com/theevann/streamlit-audiorecorder
import streamlit_scrollable_textbox as stx #https://github.com/RobertoFN/streamlit-scrollable-textbox
from streamlit_text_rating.st_text_rater import st_text_rater #https://github.com/TVS-Motor-Company/streamlit-text-rating/blob/main/README.md

APPLICATION_MODE = 1
##############################################################################################

st.title("Navigate UIs")

st.header(":grey[Upload UI Screenshots]", divider="grey")
uploaded_image = st.file_uploader("Upload a screenshot of the UI you need help with.", type=["jpg", "jpeg", "png"])

if uploaded_image:
    st.image(uploaded_image)
    st.success("Image uploaded successfully!")

    gonggongai.cache_uploaded_image(uploaded_image)

    st.subheader("Record an audio to explain the problem you are facing.")
    audio = audiorecorder("Click to record", "Click to stop recording")

    if len(audio) > 0:
        recorded_audio = audio.export().read()
        audio.export("audio.mp3", format="mp3")
        st.success("Audio recorded successfully!")
        st.audio(recorded_audio)

        gemini_response = gonggongai.get_ai_output(audio_file_path="audio.mp3", image_file_path="image.png", application_mode=APPLICATION_MODE) 
        recorded_transc, output_json = gemini_response["transcription"], gemini_response["data"]

        st.text_area("Transcribed Audio in Text", recorded_transc, height=150)
        generate_instruction = st.button("Generate Solution")
    
        if generate_instruction: 
            st.header(":grey[Solutions & Instructions]", divider="grey")

            instruction = "\n".join(["{}. {}".format(x[0], x[1]) for x in enumerate(output_json["possible_approaches"][0]["steps"], 1)])
            stx.scrollableTextbox(instruction, height=500)

            response = st_text_rater(text="Is this text helpful?")

else:
    st.info("Please upload an image file.")