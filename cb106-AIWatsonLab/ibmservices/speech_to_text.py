from ibm_watson import SpeechToTextV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
import os

class SpeechToText:
    def __init__(self):
        self.authenticator = IAMAuthenticator(os.getenv('STT_APIKEY'))
        self.stt = SpeechToTextV1(authenticator=self.authenticator)
        self.stt.set_service_url(os.getenv('STT_URL'))

    def transcribe(self, audio_file):
        """Chuyển audio thành text"""
        try:
            result = self.stt.recognize(audio=audio_file, content_type='audio/wav').get_result()
            if result['results']:
                return result['results'][0]['alternatives'][0]['transcript']
        except Exception as e:
            print(f"Error in STT: {e}") # For debugging
        return ""