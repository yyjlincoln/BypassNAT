#Server
import functools
import socket
from socket import *
import _thread
import time

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
    

class BNATObject: #After established the connection Server and CServer
    @funlog
    def __init__(self,ServeOnPort):
        self.ServeOnPort=ServeOnPort
        # self.CtrlSocket=CtrlSocket #Server to CServer Socket
        self.TempSocket=None
        self.WaitConTrigger=False
        self.WaitCtrl=True
    
    @funlog
    def recv_thread(self,ConnectionSocket,SendToSocket): #Recv外部
        try:
            while True:
                dat=ConnectionSocket.recv(2048)
                if dat!=b'':
                    SendToSocket.send(dat)
                else:
                    raise Exception('Connection Lost')
        except:
            print('Connection Broke - 连接已断开')
            try:
                ConnectionSocket.close() #拒绝接收Client-Server
                SendToSocket.close() #拒绝接收Server-CServer的SendTo
            except:
                pass
            _thread.exit()

    @funlog
    def wait_thread(self):
        So=socket()
        So.bind(('',self.ServeOnPort))
        So.listen(10)
        while True:
            sx,addr=So.accept()
            #Connection Established.
            _thread.start_new(self.identify_conn_thread,(sx,addr)) #防止阻塞形成TimeOut
    
    @funlog
    def identify_conn_thread(self,sx,addr):
            print('Connection Established',addr[0]+':'+str(addr[1]))
            if self.WaitConTrigger==True: #CServer-Server
                self.TempSocket=sx
                self.WaitConTrigger=False
                _thread.exit()
            elif self.WaitCtrl==True and self.valid_control(sx)==True:
                self.CtrlSocket=sx
                self.WaitCtrl=False
            else: #SEND-TO
                sendto=self.NewSendToConn()
                if sendto==None:
                    print('Can\'t Establish SendTo Object!')
                    return
                _thread.start_new(self.recv_thread,(sx,sendto)) #外部->Recv->内部
                _thread.start_new(self.recv_thread,(sendto,sx)) #内部->Recv->外部

    @funlog
    def NewSendToConn(self): #内部,即Server-CServer方向socket,通过对Ctrl发消息,客户端处理然后连接来建立连接.
        try:
            self.CtrlSocket.send('EstablishConnection'.encode('utf-8'))
            self.WaitConTrigger=True
            calc=0
            while self.WaitConTrigger==True:
                time.sleep(0.1)
                calc+=1
                if calc==100:
                    print('TimeOut!')
                    self.WaitConTrigger=False
                    self.CtrlSocket.close()
                    return #CtrlTimeOut
            return self.TempSocket
        except:
            print('Unable to establish NewSendToConn! Ctrl Not OK!')
            self.CtrlSocket.close()
            self.WaitCtrl=True
            self.WaitConTrigger=False
            return
    
    @funlog
    def valid_control(self,so):
        return True

a=BNATObject(122)
a.wait_thread()