import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table

import tweepy
from pandas import DataFrame
from textblob import TextBlob
import re
import sys
import pandas as pd
from dash.dependencies import Output, State, Input
consumer_key = '2TZ1K5IosiWpBB1AgRzUN2OYe'
consumer_secret = 'wYB8KHMlK6IRSf7Rr1Chl1jx2chaRqzPa4HVKoZsHVWIMJ7g4d'

access_token_key = '1184232235488219136-bFjHLEHvbLcBt9SJ5PqXvNhfmd2wX4'
access_token_secret = '3GLCtypZ0ibi2DVMY9sgQwnVuooBE90raAxtUik4luNfv'

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token_key, access_token_secret)

api = tweepy.API(auth)


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)


app.layout = html.Div([
    dcc.Input(id='username', value='', type='text'),
    html.Button(id='submit-button', type='submit', children='Submit'),
    html.Div(id='output_div')
])

def generate_table(dataframe, max_rows=100):
    return  dash_table.DataTable(
    data=dataframe.to_dict('records'),
    columns=[{'id': c, 'name': c} for c in dataframe.columns],
    style_cell={'textAlign': 'left'},

        style_data_conditional=[
            {
                'if': {
                    'filter_query': '{Sentiment} eq "Positive"'
                },

                    'backgroundColor': '#3D9970',
                    'color': 'white'

            },
            {
                'if': {
                    'filter_query': '{Sentiment} eq "Negative"'
                },

                'backgroundColor': 'red',
                'color': 'white'

            }
        ]
)



@app.callback(Output('output_div', 'children'),
              [Input('submit-button', 'n_clicks')],
              [State('username', 'value')],)



def update_output(clicks, input_value):
    # data = []
    if clicks is not None:
            data = []
            topic=input_value
            topicname = topic
            pubic_tweets = api.search(topicname)
            for tweet in pubic_tweets:
                    text = tweet.text

                    textWords = text.split()

                    cleanedTweet = ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)|(RT)", " ", text).split())
                    print(cleanedTweet)

                    analysis = TextBlob(cleanedTweet)
                    print(analysis.sentiment)
                    polarity = 'Positive'

                    if (analysis.sentiment.polarity < 0):
                        polarity = 'Negative'

                    if (0 <= analysis.sentiment.polarity <= 0.2):
                        polarity = 'Neutral'
                    dic = {'Sentiment': polarity, 'Tweet': cleanedTweet}
                    data.append(dic)
            df = pd.DataFrame(data)

            return html.Div(children=[
                html.H4(children='twitter sentmient analyses'),
                generate_table(df)
            ])




if __name__ == '__main__':
    app.run_server(debug=True)
