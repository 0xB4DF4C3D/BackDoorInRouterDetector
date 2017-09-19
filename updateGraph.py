import plotly.plotly as py
from plotly.graph_objs import *

trace0 = Scatter(
    x=[1, 2],
    y=[1, 2]
)

trace1 = Scatter(
    x=[1, 2],
    y=[2, 3]
)

trace2 = Scatter(
    x=[1, 2],
    y=[3, 4]
)

data = Data([trace0, trace1, trace2])

# Take 1: if there is no data in the plot, 'extend' will create new traces.
plot_url = py.plot(data, filename='extend plot', fileopt='extend')

input('next')

trace0 = Scatter(
    x=[3, 4],
    y=[2, 1]
)

trace1 = Scatter(
    x=[3, 4],
    y=[3, 2]
)

trace2 = Scatter(
    x=[3, 4],
    y=[4, 3]
)

data = Data([trace0, trace1, trace2])

# Take 2: extend the traces on the plot with the data in the order supplied.
plot_url = py.plot(data, filename='extend plot', fileopt='extend')
