from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson import SpeechToTextV1,TextToSpeechV1, AssistantV2
import os, uuid,json
from dotenv import load_dotenv


load_dotenv()

stt_api = os.environ["stt_api"]
stt_url = os.environ["stt_url"]

tts_api = os.environ["tts_api"]
tts_url = os.environ["tts_url"]

assistant_api = os.environ["assistant_api"]
assistant_url = os.environ["assistant_url"]

ASSISTANT_ID = os.environ["assistant_id"]

def speechToText(filename, extn):
    recognition_service=SpeechToTextV1(IAMAuthenticator(stt_api))
    recognition_service.set_service_url(stt_url)
    SPEECH_EXTENSION="*."+extn
    SPEECH_AUDIOTYPE="audio/"+extn
    audio_file=open(filename,"rb")
    result=recognition_service.recognize(audio=audio_file, content_type=SPEECH_AUDIOTYPE).get_result()
    return result["results"][0]["alternatives"][0]["transcript"]

def getResponseFromAssistant(chat_text):
    assistant=AssistantV2(version='2019-02-28',authenticator=IAMAuthenticator(assistant_api))
    assistant.set_service_url(assistant_url)
    session=assistant.create_session(assistant_id =ASSISTANT_ID)
    session_id=session.get_result()["session_id"]
    response=assistant.message(assistant_id=ASSISTANT_ID,session_id=session_id, 
input={'message_type': 'text','text': chat_text}).get_result()
    response_text = response["output"]["generic"][0]["text"]
    authenticator = IAMAuthenticator(tts_api)
    text_to_speech = TextToSpeechV1(
        authenticator=authenticator
    )
    text_to_speech.set_service_url(tts_url)
    resp_file = "response"+str(uuid.uuid1())[0:4]+".mp3"
    with open(resp_file, 'wb') as audio_file:
        audio_file.write(
            text_to_speech.synthesize(
                response_text,
                voice='en-US_MichaelV3Voice',
                accept='audio/mp3'        
            ).get_result().content)

    return resp_file



