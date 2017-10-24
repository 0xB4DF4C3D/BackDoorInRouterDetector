from multiprocessing import Process, Manager, Value
from ctypes import c_char_p

def greet(string):
    string.value = string.value + ", World!"
