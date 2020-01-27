import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import plotly as py
import tweepy
from wordcloud import WordCloud, STOPWORDS
from textblob import TextBlob
import re
import pandas as pd
from dash.dependencies import Output, State, Input
import preprocessor as p
import plotly.graph_objs as go
import random
from plotly.offline import iplot

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
    return dash_table.DataTable(
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


# clean tweets

def clean_tweets(txt):
    txt = " ".join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t]) | (\w +:\ / \ / \S +)", "", txt).split())
    p.set_options(p.OPT.URL, p.OPT.EMOJI, p.OPT.NUMBER)
    tweet_cleean = p.clean(txt)
    return tweet_cleean


# world Cloud
def plotly_wordcloud(text):
    wc = WordCloud(stopwords=set(STOPWORDS),
                   max_words=500,
                   max_font_size=100)
    wc.generate(str(text))
    word_list = []
    freq_list = []
    fontsize_list = []
    position_list = []
    orientation_list = []
    color_list = []

    for (word, freq), fontsize, position, orientation, color in wc.layout_:
        word_list.append(word)
        freq_list.append(freq)
        fontsize_list.append(fontsize)
        position_list.append(position)
        orientation_list.append(orientation)
        color_list.append(color)
    length = len(text)


    # get the positions
    x = []
    y = []
    for i in position_list:
        x.append(i[0])
        y.append(i[1])

    # get the relative occurence frequencies
    new_freq_list = []
    for i in freq_list:
        new_freq_list.append(i * 100)
    new_freq_list
    colors = [py.colors.DEFAULT_PLOTLY_COLORS[random.randrange(1, 10)] for i in range(length)]
    data = go.Scatter(x=random.choices(range(length), k=length),
                      y=random.choices(range(length), k=length),
                      mode='text',
                      text=word_list,
                      textfont={'size': new_freq_list, 'color': colors},
                      hoverinfo='text',
                      hovertext=['{0}{1}'.format(w, f) for w, f in zip(word_list, freq_list)]

                      )

    layout = go.Layout(
        xaxis=dict(showgrid=False,
                   showticklabels=False,
                   zeroline=False,
                   automargin=True),
        yaxis=dict(showgrid=False,
                   showticklabels=False,
                   zeroline=False,
                   automargin=True)
    )
    fig = go.Figure(data=[data], layout=layout)
    return fig


@app.callback(Output('output_div', 'children'),
              [Input('submit-button', 'n_clicks')],
              [State('username', 'value')], )
def update_output(clicks, input_value):
    # data = []
    if clicks is not None:
        data = []
        topic = input_value
        topicname = topic
        # input Number Search Terms
        noOfSearchTerms = 3200
        pubic_tweets = api.search(q=topicname, lang="en", count=noOfSearchTerms, tweet_mode="extended")

        for tweet in pubic_tweets:
            text = tweet.full_text
            cleanedTweet = clean_tweets(text)
            analysis = TextBlob(cleanedTweet)
            print(analysis.sentiment)
            polarity = 'Negative'
            if analysis.sentiment.polarity > 0.2:
                polarity = 'Positive'
            if -0.2 <= analysis.sentiment.polarity <= 0.2:
                polarity = 'Neutral'
            dic = {'Sentiment': polarity, 'Polarity': analysis.sentiment.polarity,
                   'Subject': analysis.sentiment.subjectivity, 'Tweet': cleanedTweet}
            data.append(dic)
        df = pd.DataFrame(data)
        words = df.Tweet
        iplot(plotly_wordcloud(words))

        return html.Div(children=[
            html.H4(children='twitter sentmient analyses'),
            generate_table(df)
        ])


if __name__ == '__main__':
    app.run_server(debug=True)
