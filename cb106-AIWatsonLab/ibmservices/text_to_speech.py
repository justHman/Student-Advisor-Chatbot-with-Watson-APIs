from ibm_watson import TextToSpeechV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
import os

class TextToSpeech:
    def __init__(self):
        self.authenticator = IAMAuthenticator(os.getenv('TTS_APIKEY'))
        self.tts = TextToSpeechV1(authenticator=self.authenticator)
        self.tts.set_service_url(os.getenv('TTS_URL'))

    def synthesize(self, text):
        """Chuyển text thành audio WAV"""
        audio = self.tts.synthesize(text, accept='audio/wav', voice='en-US_AllisonV3Voice').get_result()
        return audio.content