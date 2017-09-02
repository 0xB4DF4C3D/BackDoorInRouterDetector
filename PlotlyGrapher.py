import plotly.plotly as py
import plotly.tools as tls
import plotly.graph_objs as go

class Graph():
    """
    More easy accessible functions for plotly.
    This is Facade pattern for complex plotly plot.
    """
    
    def __init__(self):
        pass

    def getTrace(self, **kwargs):
        # init kwargs default value
        kwargs['x'] = kwargs.get('x',[])
        kwargs['y'] =kwargs.get('y',[])
        kwargs['mode'] = kwargs.get('mode','lines+markers')
        
        return go.Scatter(kwargs)

    def getFigure(self, _data, _title):
        data = go.Data(_data)
        layout = go.Layout(title=_title)
        return go.Figure(data=data, layout=layout)

    def plot(self, fig, title):
        py.plot(fig, filename=title)


class StreamPool():
    """
    This automate get/free stream token.
    and make managing streams easier
    """
    def __init__(self, names = []):
        
        # This need `Stream Token` at .credential
        stream_ids =  tls.get_credentials_file()['stream_ids']

        # Initialize a stream ids pool
        self.__stream_ids = dict((i,False) for i in stream_ids)
        
        self.__pool = {}
        for name in names:
            self.addStream(name, self.getStream())

    def getStream(self):
        streamID = self.__getStreamID()
        
        stream = py.Stream(streamID)
        return stream

    def freeStream(self, stream):
        stream.close()
        self.__freeStreamToken(stream)


    def getStreamDict(self, name, maxPoints):
        return dict(token = self.__pool[name].stream_id, maxpoints=maxPoints)

        
    def addStream(self, name, stream):
        self.__pool[name] = stream


    def clearStream(self, name):
        self.__pool[name].write(dict(x=[],y=[]))

    # Internal function start -=-=-=-=-=-=-=-=-=-=-=-=-=
    def __getStreamID(self):
        # Get a first free stream id from stream ids pool
        freeStreamID = next((k for k, v in self.__stream_ids.items() if v == False), None)

        if(freeStreamID == None):
            raise IndexError
        self.__stream_ids[freeStreamID] = True
        return freeStreamID

    def __freeStreamID(self, stream):
        self.__stream_ids[stream.stream_id] = False

    def __getitem__(self, name):
        return self.__pool[name]

    def __iter__(self):
        return iter(self.__pool)

