from ibm_watson import AssistantV2
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
import os

class WatsonAssistant:
    def __init__(self):
        self.authenticator = IAMAuthenticator(os.getenv('ASSISTANT_APIKEY'))
        self.assistant = AssistantV2(version='2021-06-14', authenticator=self.authenticator)
        self.assistant.set_service_url(os.getenv('ASSISTANT_URL'))
        self.assistant_id = os.getenv('ASSISTANT_ID')

    def create_session(self):
        """Tạo session mới với Watson Assistant"""
        response = self.assistant.create_session(self.assistant_id).get_result()
        return response['session_id']

    def send_message(self, session_id, text):
        """Gửi message đến Assistant và nhận response"""
        response = self.assistant.message(
            assistant_id=self.assistant_id,
            session_id=session_id,
            input={'text': text}
        ).get_result()
        return response['output']['generic']

    def delete_session(self, session_id):
        """Xóa session"""
        self.assistant.delete_session(assistant_id=self.assistant_id, session_id=session_id)