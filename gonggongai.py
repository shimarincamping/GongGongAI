import os
import json
import PIL.Image as PImage
import google.generativeai as GEMINI_CLIENT
import streamlit as st

GEMINI_CLIENT.configure(api_key=st.secrets["GEMINI_API_KEY"])

##### CONSTANTS #################################################################################################

MAX_OUTPUT_TOKENS = 500
APPLICATION_MODES = {
    1 : "UI_HELPER",
    2 : "SCAM_IDENTIFIER",
    3 : "SLANG_TRANSLATOR"
}

CURRENT_MODEL = "gemini-1.5-flash"

##### PROMPTS ###################################################################################################

CONTEXT_PROMPT = "You are an assistant that helps the elderly or less technologically savvy users to navigate the Internet easily and safely. You will be given a screenshot by the user along with a question from the user. Use the information inside the picture to help them with their questions. Remember your target audience: use casual, easy-to-understand language and inject relevant analogies whenever appropriate to accomplish your objective. Output ONLY a JSON object and nothing else. All numbers CANNOT be in fractions."

JSON_SCHEMAS = {

    "UI_HELPER" : """{
    "possible_approaches" : list[{
        "steps" : list[str]
    }]
}""",

    "SCAM_IDENTIFIER" : """{
    "red_flags" : list[str],
    "scam_risk_score" : int,
    "advice" : str
}""",

    "SLANG_TRANSLATOR" : """{
    "word" : str,
    "definition" : str,
    "context" : str,
    "usage_example" : str,
    "analogy" : str
}"""

}



SYSTEM_PROMPTS = {
    
    "UI_HELPER" : """Context: 
{}

Specific task:
Help the user to locate or accomplish a task based on information obtained from the attached screenshot.
If you cannot find the right place to click on, suggest the most likely next course of action. Make a good educated guess similar to how a technologicaly-savvy person would explore a website for the first time.

Your response should include:
- Several sets of step-by-step instructions in simple language

Your response MUST follow this JSON schema:
{}
""".format(CONTEXT_PROMPT, JSON_SCHEMAS["UI_HELPER"]),

    
    "SCAM_IDENTIFIER" : """Context: 
{}

Specific task:
Help the user by identifying whether the screenshot attached is likely to be a scam or not. This can be in the form of financial scams, phishing links, or any other similar tactics. While it is not possible to definitively ascertain, simply perform a risk assessment so that the user can be better informed. Explain some red flags or points of suspicion as to why it may be likely to be a scam. 
Based on this analysis, generate an arbitrary 'Scam Risk' score on a scale of 0 (not likely at all) to 100 (must be a scam)
Make sure your analysis is objective. Do not be afraid to give high or low scores.

Your response should include:
- Red flags or points of suspicion, if any
- Scam risk score as decimal number only between 0 and 100
- Advice on how to proceed with caution as one short paragraph

Your response MUST follow this JSON schema:
{}
""".format(CONTEXT_PROMPT, JSON_SCHEMAS["SCAM_IDENTIFIER"]),


    "SLANG_TRANSLATOR" : """Context: 
{}

Specific task:
Help the user make sense of new-age slang and vocabulary used by the younger generations. Based on the provided input,give a shortened straightforward definition with the necessary context, usage examples, and analogies with other words or concepts that the older generation may be familiar with. 

Your response should include:
- One definition statement
- Context surrounding the word
- One usage example
- Optionally, one analogy (leave the string empty if none)

Your response MUST follow this JSON schema:
{}
""".format(CONTEXT_PROMPT, JSON_SCHEMAS["SLANG_TRANSLATOR"])

}

TRANSCRIBER_PROMPT = "You are a text transcriber. Listen to the audio and write a word-by-word transcription. Add appropriate punctuation such as commas, periods, and question marks. Output only the text and nothing else"

##### GEMINI API CALLS #############################################################################################

# From the audio clip, call Gemini to return a string of the text that it thinks the user is saying
def get_text_from_audio(audio_file_path):
    GEMINI_MODEL = GEMINI_CLIENT.GenerativeModel(
        CURRENT_MODEL,
        system_instruction=TRANSCRIBER_PROMPT
    )
    return GEMINI_MODEL.generate_content(GEMINI_CLIENT.upload_file(audio_file_path)).text


# Remove ```json{] ``` from output string
def sanitise_ai_output(ai_output):
    return ai_output[ai_output.find("{") : ai_output.rfind("}") + 1]

# For all three features, call Gemini with the text prompt (if exists) and image file (if exists)
def generate_gemini_response(system_prompt, content_list):
    GEMINI_MODEL = GEMINI_CLIENT.GenerativeModel(
        CURRENT_MODEL,
        system_instruction=system_prompt
    )

    return sanitise_ai_output(
        GEMINI_MODEL.generate_content(content_list, 
                                      generation_config=GEMINI_CLIENT.GenerationConfig(max_output_tokens=MAX_OUTPUT_TOKENS)
        ).text
    )

# Build the text prompt that will be sent to Gemini
def get_user_text_prompt(user_text_input, transcribed_text):
    user_text_prompt = ""
    if user_text_input:
        user_text_prompt += "The user typed the following text:\n\n" + user_text_input + "\n\n"
    if transcribed_text:
        user_text_prompt += "The user spoke the following text:\n\n" + transcribed_text + "\n\n"

    return user_text_prompt


# Obtain data from UI elements and initiate the generation of the prompt; returns JSON object of response
def get_ai_output(user_text_input=None, audio_file_path=None, image_file_path=None, application_mode=None):

    transcribed_text = get_text_from_audio(audio_file_path) if audio_file_path else None   # handling null audio condition
    user_text_prompt = get_user_text_prompt(user_text_input, transcribed_text)

    image_file_obj = PImage.open(image_file_path) if image_file_path else None  # handling null image condition

    json_output_str = generate_gemini_response(
        SYSTEM_PROMPTS[APPLICATION_MODES[application_mode]], 
        [x for x in [user_text_prompt, image_file_obj] if x]
    )

    return {
        "transcription" : transcribed_text,
        "data": json.loads(json_output_str) 
    }


# Cache uploaded image to file
def cache_uploaded_image(image_data):
    temp_img = open("image.png", "wb")
    temp_img.write(image_data.read())