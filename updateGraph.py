import plotly.plotly as py
import plotly.graph_objs as go

trace1 = go.Scatter(
    x=[0, 1, 2, 3, 4, 5, 6, 7, 8],
    y=[0, 1, 3, 2, 4, 3, 4, 6, 5]
)
trace2 = go.Scatter(
    x=[0, 1, 2, 3, 4, 5, 6, 7, 8],
    y=[0, 4, 5, 1, 2, 2, 3, 4, 2]
)
data = [trace1, trace2]
layout = go.Layout(
    showlegend=False,
    annotations=[{'x': 0, 'y': 0, 'text': 'hello', 'xref': 'x', 'yref': 'y', 'showarrow': True, 'arrowhead': 7, 'ax': 0, 'ay': -40}, {'x': 10, 'y': 0, 'text': 'bye', 'xref': 'x', 'yref': 'y', 'showarrow': True, 'arrowhead': 7, 'ax': 0, 'ay': -40}, {'x': 30, 'y': 0, 'text': 'lol', 'xref': 'x', 'yref': 'y', 'showarrow': True, 'arrowhead': 7, 'ax': 10, 'ay': -40}]
)
fig = go.Figure(data=data, layout=layout)
plot_url = py.plot(fig, filename='simple-annotation')
