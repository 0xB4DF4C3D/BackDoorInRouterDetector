import numpy as np
import plotly.plotly as py
import plotly.tools as tls
import plotly.graph_objs as go

stream_ids = tls.get_credentials_file()['stream_ids']
stream_id1 = stream_ids[0]
stream_id2 = stream_ids[1]

stream_1 = dict(token=stream_id1, maxpoints=60)
stream_2 = dict(token=stream_id2, maxpoints=60)
s1 = py.Stream(stream_id1)
s2 = py.Stream(stream_id2)
trace1 = go.Scatter(
    x=[],
    y=[],
    mode='lines+markers',
    stream=stream_1         # (!) embed stream id, 1 per trace
)

trace2 = go.Scatter(
    x=[],
    y=[],
    mode='lines+markers',
    stream=stream_2         # (!) embed stream id, 1 per trace
)

data = go.Data([trace1, trace2])


# Add title to layout object
layout = go.Layout(title='Time Series')

# Make a figure object
fig = go.Figure(data=data, layout=layout)

# Send fig to Plotly, initialize streaming plot, open new tab
py.plot(fig, filename='python-streaming')


s1.open()
s2.open()

import datetime
import time

i = 0    # a counter
k = 5    # some shape parameter

# Delay start of stream by 5 sec (time to switch tabs)

while True:

    # Current time on x-axis, random numbers on y-axis
    x = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
    y1 = (np.cos(k*i/50.)*np.cos(i/50.)+np.random.randn(1))[0]
    y2 = (np.cos(k*i/50.)*np.cos(i/50.)+np.random.randn(1))[0]

    # Send data to your plot
    s1.write(dict(x=x, y=y1))
    s2.write(dict(x=x, y=y1))

    #     Write numbers to stream to append current data on plot,
    #     write lists to overwrite existing data on plot

    time.sleep(1)  # plot a point every second    
# Close the stream when done plotting
s1.close()
s2.close()

#tls.embed('streaming-demos','12')
