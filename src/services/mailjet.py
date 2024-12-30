from mailjet_rest import Client
import os

class MailJetClient():
    def __init__(self) -> None:
        try:
            API_KEY = os.environ['MJ_APIKEY_PUBLIC']
            API_SECRET = os.environ['MJ_APIKEY_PRIVATE']

            mailjet = Client(auth=(API_KEY, API_SECRET))                
        except:
            print('OK')
        finally:
            print('Finally')