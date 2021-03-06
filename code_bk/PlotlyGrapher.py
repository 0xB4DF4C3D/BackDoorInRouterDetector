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

    def getFigure(self, _data, _title, **kwargs):
        data = go.Data(_data)
        layout = go.Layout(title=_title,**kwargs)
        return go.Figure(data=data, layout=layout)

    def plot(self, fig, title):
        py.plot(fig, filename=title)

class TracePool():

    def __init__(self, names):
        self.__tracePool = {}
        self.__dataPool = {}

        for name in names:
            self.__tracePool[name] = None
            self.__dataPool[name] = {'x':[], 'y':[]}

    
    def getTrace(self, name, info):
        return go.Scatter({**info,'mode':'lines','name':name, **self.__dataPool[name]})

    def addData(self, name, data):
        for i in data:
            if i in self.__dataPool[name]:
                self.__dataPool[name][i] += data[i]
            else:
                self.__dataPool[name][i] = data[i]
            
    def delDataElement(self, name, dataName, idx):
        del self.__dataPool[name][dataName][idx]

    def __getitem__(self, name):
        return self.__tracePool[name]

    def __iter__(self):
        return iter(self.__tracePool)

class AnnotationList():

    def __init__(self, **kwargs):
        self.__setting = {
                          **dict(
                              xref='x',
                              yref='y',
                              showarrow=True,
                              arrowhead=7,
                              ax=0,
                              ay=-40
                              ),
                          **kwargs
                          }
        self.__annotationList = []

    def addAnnotation(self, x, y, text, **kwargs):
        self.__annotationList += [{
            **dict(
            x=x,
            y=y,
            text=text),
            **self.__setting, **kwargs
                                 }]

    def getAnnotationList(self):
        return self.__annotationList

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
