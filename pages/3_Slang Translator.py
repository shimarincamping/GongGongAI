import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import gonggongai

import streamlit as st
import streamlit_scrollable_textbox as stx #https://github.com/RobertoFN/streamlit-scrollable-textbox
from streamlit_text_rating.st_text_rater import st_text_rater #https://github.com/TVS-Motor-Company/streamlit-text-rating/blob/main/README.md

APPLICATION_MODE = 3
##############################################################################################

st.title("Youth Slang Translator")

st.header(":grey[Tell us what word is confusing you!]", divider="grey")
text_input = st.text_area("Paste the text you want to know more about here:")

if len(text_input):
    st.success("Text uploaded successfully!")

    try:
        gemini_response = gonggongai.get_ai_output(user_text_input=text_input, application_mode=APPLICATION_MODE)
        word_data = gemini_response["data"]

        st.header(f":grey[{word_data['word']}]", divider="grey")  
        final_text = """Definition: 
    {}

    Context: 
    {}

    Usage Example: 
    {} {}
        """.format( 
            word_data["definition"],
            word_data["context"],
            word_data["usage_example"],
            word_data["analogy"]
        )
    
    except ValueError:
        final_text = "Sorry! It looks like Gemini doesn't know this one..."
        
    stx.scrollableTextbox(final_text, height=400)

    response = st_text_rater(text="Is this text helpful?")