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

consumer_key = '********'
consumer_secret = '*******'

access_token_key = '*********'
access_token_secret = '*********'

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token_key, access_token_secret)

api = tweepy.API(auth)

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
colors = {
    'background': '#ffffff',
    'text': '#7FDBFF'
}
app.layout = html.Div(style={'backgroundColor': colors['background']}, children=[
    html.H1(
        children='twitter feel',
        style={
            'textAlign': 'center',
            'color': colors['text']
        }
    ),

    html.Div(children='Discover the Twitter sentiment for a product or brand..', style={
        'textAlign': 'center',
        'color': colors['text']
    }),

    dcc.Input(id='username', value='', type='text' , style={'width': '30%', 'margin': '0%', 'textAlign': 'left'}),
    html.Button(id='submit-button', type='submit', children='Submit' ,style={'width': '20%', 'margin': '0%', 'align-items': 'center'}),
    html.Div(id='output_div',  style={
        'textAlign': 'center',
        'color': colors['text']
    })

])




def generate_table(dataframe, max_rows=100):
    return dash_table.DataTable(
        data=dataframe.to_dict('records'),
        columns=[{'id': c, 'name': c} for c in dataframe.columns],
        style_as_list_view=True,
        style_cell={'textAlign': 'left', 'padding': '5px'},
        style_header={
            'backgroundColor': 'rgb(230, 230, 230)',
            'fontWeight': 'bold'
        },
        style_data_conditional=[
            {
                'if': {
                    'filter_query': '{Sentiment} eq "Positive"'
                },

                'backgroundColor': 'green',
                'color': 'white'

            },
            {
                'if': {
                    'filter_query': '{Sentiment} eq "Negative"'
                },

                'backgroundColor': 'red',
                'color': 'white'

            },
            {
                'if': {
                    'filter_query': '{Sentiment} eq "Neutral"'
                },

                'backgroundColor': 'blue',
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


def percentage(part, whole):
    temp = 100 * float(part) / float(whole)
    return format(temp)


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
        positive = 0
        negative = 0
        neutral = 0

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
            dic = {'Tweet': cleanedTweet, 'Sentiment': polarity, 'Polarity': analysis.sentiment.polarity,
                   'Subject': analysis.sentiment.subjectivity}
            data.append(dic)
            if analysis.sentiment.polarity > 0.2:
                positive += 1
            if -0.2 <= analysis.sentiment.polarity <= 0.2:
                neutral += 1
            if analysis.sentiment.polarity < -0.2:
                negative += 1
        df = pd.DataFrame(data)
        words = df.Tweet
        iplot(plotly_wordcloud(words))
        labels = ['Positive', 'Negative', 'Neutral']
        led = len(df)
        print("****longour", led)
        print("*****", positive)
        print("*****", negative)
        print("----", neutral)
        positive = float(percentage(positive, led))
        negative = float(percentage(negative, led))
        neutral = float(percentage(neutral, led))

        print("*****", positive)
        print("*****", negative)
        print("*****", neutral)

        values = [positive, negative, neutral]
        colors = ['green', 'red', 'blue']

        return html.Div(children=[
            dcc.Graph(id='TPiePlot',
                      figure={
                          'data': [go.Pie(labels=labels,
                                          values=values,
                                          marker=dict(colors=colors, line=dict(color='#fff', width=1)),
                                          hoverinfo='label+value+percent', textinfo='value',
                                          domain={'x': [0, .25], 'y': [0, 1]}
                                          )
                                   ],
                          'layout': go.Layout(title='Tweet Sentiment Visualization',
                                              autosize=True
                                              )

                      }
                      ),
            generate_table(df)

        ])


if __name__ == '__main__':
    app.run_server(debug=True)
