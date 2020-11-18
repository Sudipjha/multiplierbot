from flask import Flask, request, make_response, jsonify
import os
import dialogflow
from google.api_core.exceptions import InvalidArgument
import requests
import pandas as pd

import pygsheets
#authorization
gc = pygsheets.authorize(service_file='muliplier-bot-iyl9-ccd96b75d437.json')

url = "https://api.gupshup.io/sm/api/v1/msg"


os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = 'muliplier-bot-iyl9-9eb882cf51fe.json'

DIALOGFLOW_PROJECT_ID = 'muliplier-bot-iyl9'
DIALOGFLOW_LANGUAGE_CODE = 'en'
SESSION_ID = 'me'


app = Flask(__name__)

@app.route('/')
def index():
    return 'Hello World!'

# function for responses
def results():
    # build a request object
    req = request.get_json(force=True)
   
    try:
        text_to_be_analyzed = req['payload']['payload']['text']

        session_client = dialogflow.SessionsClient()
        session = session_client.session_path(DIALOGFLOW_PROJECT_ID, SESSION_ID)
        text_input = dialogflow.types.TextInput(text=text_to_be_analyzed, language_code=DIALOGFLOW_LANGUAGE_CODE)
        query_input = dialogflow.types.QueryInput(text=text_input)
        try:
            response = session_client.detect_intent(session=session, query_input=query_input)
        except InvalidArgument:
            raise

        headers = {'Content-Type': 'application/x-www-form-urlencoded','apikey': '350a75be8fc2402ec09c6f812591846e'}
        data = {'channel':'whatsapp','source':'917995984446','destination':req['payload']['sender']['phone'],'message':response.query_result.fulfillment_messages[0].text.text[0],'src.name':'MultiplierAISolutions'}
        r = requests.post(url, data=data, headers=headers)
        sh = gc.open('multiplier_bot_data')
        wks = sh[0]
        old_df = wks.get_as_df()
        #select the first sheet 
        df = pd.DataFrame()

        df['Session id'] = [response.response_id]
        df['Mobile_Number'] = [req['payload']['sender']['phone']]
        df['User_message'] = [req['payload']['payload']['text']]
        df['Bot_message'] = [response.query_result.fulfillment_messages[0].text.text[0]]
        df['Timestamp'] = [req['timestamp']]
        df['User_name'] = [req['payload']['sender']['name']]
        df['Status'] = '0'
        new_df = pd.concat([old_df,df])
        # #update the first sheet with df, starting at cell B2. 
        wks.set_dataframe(new_df,(1,1))

    except:
        pass

    
@app.route('/webhook_gupshup/', methods=['GET', 'POST'])
def webhook():
    # return response
    return make_response(jsonify(results()))

if __name__ == '__main__':
    app.run()