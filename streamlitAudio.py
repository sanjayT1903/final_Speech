import streamlit as st
from audiorecorder import audiorecorder
import azure.cognitiveservices.speech as speechsdk
import gspread
from oauth2client.service_account import ServiceAccountCredentials

st.title("Audio Recorder")

# Add input fields for the subscription key and JSON credentials file
subscription_key = st.text_input("Enter your Azure subscription key", type="password")
json_file = st.file_uploader("Upload your Google service account JSON file", type="json")
region = "westus"

audio = audiorecorder("Click to record", "Click to stop recording")

if subscription_key and json_file:
    if len(audio) > 0:
        # To play audio in frontend:
        #st.audio(audio.export().read())  

        # To save audio to a file, use pydub export method:
        audio.export("audio.wav", format="wav")
        file_path = 'audio.wav'
        # To get audio properties, use pydub AudioSegment properties:
        #st.write(f"Frame rate: {audio.frame_rate}, Frame width: {audio.frame_width}, Duration: {audio.duration_seconds} seconds")

        # Create an instance of a speech config with specified subscription key and service region.
        speech_config = speechsdk.SpeechConfig(subscription=subscription_key, region=region)

        # Specify the audio file to be recognized
        audio_input = speechsdk.AudioConfig(filename=file_path)

        # Create a recognizer with the given settings
        speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_input)

        # Perform recognition. `result` will be an instance of `SpeechRecognitionResult`
        result = speech_recognizer.recognize_once()

        # Check the result
        if result.reason == speechsdk.ResultReason.RecognizedSpeech:
            st.write("Recognized: {}".format(result.text))
            
            # Save the uploaded JSON file to a temporary location
            with open("service_account.json", "wb") as f:
                f.write(json_file.getbuffer())

            scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
            creds = ServiceAccountCredentials.from_json_keyfile_name('service_account.json', scope)
            client = gspread.authorize(creds)
            
            sh = client.open('ResultsSpeech').worksheet('Sheet1')
            
            # Add buttons for feedback
            col1, col2 = st.columns(2)
            with col1:
                if st.button('Bad', key='bad', type='primary', help='Click if the recognition was bad', use_container_width=True):
                    row = [result.text, "False"]
                    sh.append_row(row)
                    st.write("Feedback recorded: Bad")
            with col2:
                if st.button('Good', key='good', type='secondary', help='Click if the recognition was good', use_container_width=True):
                    row = [result.text, "True"]
                    sh.append_row(row)
                    st.write("Feedback recorded: Good")

        else:
            st.write("Speech could not be recognized. Reason: {}".format(result.reason))
else:
    if not subscription_key:
        st.warning("Please enter your Azure subscription key.")
    if not json_file:
        st.warning("Please upload your Google service account JSON file.")
