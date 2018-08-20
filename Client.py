import socket
from socket import *
import _thread
import functools
Servip='localhost'
Port=122
Local=('localhost',80)


x=socket()
x.connect((Servip,Port))

def funlog(func):
    @functools.wraps(func)
    def wrap(*args,**kw):
        print('[%s]\tStarting...'%func.__name__)
        print('[%s]\t*args:'%func.__name__,*args)
        print('[%s]\t**kw:'%func.__name__,**kw)
        print('[%s]\tNow Starting...'%func.__name__)
        ret=func(*args,**kw)
        print('[%s]\tFinished with return:'%func.__name__,ret)
        return ret
    return wrap

@funlog
def r():
    while True:
        try:
            if x.recv(2048).decode('utf-8')=='EstablishConnection':
                _thread.start_new(connection,())
        except:
            print('Unable to recieve the message')
            break

@funlog
def fwd(soca,socb):
    while True:
        try:
            dat=soca.recv(2048)
            if dat!=b'':
                socb.send(dat)
            else:
                raise Exception('Connection Break')
        except:
            print('Connection Broke - 连接中断')
            soca.close()
            socb.close()
            _thread.exit()

@funlog
def connection():
    con=socket()
    try:
        con.connect(Local)
    except:
        print('无法连接至Local',Local)
        _thread.exit()
    conx=socket()
    conx.connect((Servip,Port))
    _thread.start_new(fwd,(conx,con))
    _thread.start_new(fwd,(con,conx))

r()
import os
os.system('pause')