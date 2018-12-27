#coding=utf-8
from socket import *
import json
import threading
from cmd import Cmd
import time

class Client(Cmd) :

    nickname = ''
    host = []
    prompt = 'K2 Chat >'
    intro = 'Welcome to the K2 ChatRoom!\n' \
            'Enter the "help" to get information.'
    #recv_msg = None

    def __init__(self,ipport):
        Cmd.__init__(self)
        self.ipport = ipport
        self.client = socket(AF_INET, SOCK_DGRAM)
        self.recvchoice = False
        #self.client.settimeout(2)

    def __send_all_msg(self,msg):
        try:
            self.client.sendto(json.dumps({'type':'messageall',
                                           'fromname':self.nickname,
                                           'message':msg}),self.ipport)
        except Exception as e:
            print e

    def _send_private_msg(self,msg):
        try :
            list_msg = msg.split(' ',1)
            nickname = list_msg[0]
            data = list_msg[1]
            self.client.sendto(json.dumps({'type':'messageprivate',
                                           'fromname':self.nickname,
                                           'toname':nickname,
                                           'message':data}),self.ipport)
        except Exception as e :
            print '[!] Please input name!'

    def do_send(self,msg):
        if self.nickname != '':
            t = threading.Thread(target=self.__send_all_msg, args=(msg,))
            t.setDaemon(True)
            t.start()
        else:
            print '[!] Please login!'

    def do_sendto(self,msg):
        if self.nickname != '' :
            t = threading.Thread(target=self._send_private_msg,args=(msg,))
            t.setDaemon(True)
            t.start()
        else :
            print '[!] Please login!'

    def do_login(self,nickname):
        self.client.sendto(json.dumps({'type':'login',
                                       'nickname':nickname}),self.ipport)
        print 'Wait...'
        time.sleep(1.5)
        data, addr = self.client.recvfrom(1024)
        data_de = json.loads(data)
        if data_de['state'] == 'Fail!':
            print '[!] Login fail! ' + str(data_de['message'])
        else:
            print str(data_de['message'])
            self.nickname = nickname
            self.recvchoice = True
            t = threading.Thread(target=self.__recv_msg)
            t.setDaemon(True)
            t.start()

    def do_exit(self,args):
        try :
            if self.nickname != '':
                msg = str(self.nickname) + ' is offline!'
                t = threading.Thread(target=self.__send_all_msg, args=(msg,))
                t.setDaemon(True)
                t.start()
                print '[!] Bye!'
                self.recvchoice = False
                time.sleep(5)
                #self.recv_msg.join()
                self.client.close()
                return True
            else:
                print '[!] You have not login! Bye Bye!'
                return  True
        except Exception as e :
            print e

    def do_catusers(self,args):
        if self.nickname != '' :
            self.client.sendto(json.dumps({'type': 'catusers'}), self.ipport)
            print 'Wait...'
            time.sleep(1.5)
        else :
            print '[!] Please login!'

    def __recv_msg(self):
        while self.recvchoice :
            data,addr = self.client.recvfrom(1024)
            data_de = json.loads(data)
            if data_de['type'] == 'login' :
                print '\n' + '[*] ' + str(data_de['message'])

            elif data_de['type'] == 'servermsg' :
                if 'offline' in str(data_de['message']) :
                    print '\n' + '[*] ' + str(data_de['message'])
                else :
                    print '\n' + '[*] ' + str(data_de['fromname']) + ' :' + str(data_de['message'])

            elif data_de['type'] == 'privatemessage' :
                print '\n' + '[*] ' + str(data_de['fromname']) + ' pm you :' + str(data_de['message'])

            elif data_de['type'] == 'catusers' :
                print '\n' + '[*] ' + str(data_de['message'])

            else :
                pass

    def do_help(self, arg):
        print '[*] login (nickname)            -- 用户登陆，nickname为你自己创建的昵称\n'
        print '[*] send (content)              -- 广播发送，content为你要发送的内容\n'
        print '[*] sendto (nickname) (content) -- 私聊发送，nickname,content同上\n'
        print '[*] catusers                    -- 查看所有在线用户\n'
        print '[*] exit                        -- 退出K2聊天室'

    def default(self, line):
        print 'I do not understand what you input..'

    def emptyline(self):
        print 'I do not understand what you input..'

    def start(self):
        self.cmdloop()

client = Client(('127.0.0.1',8888))
client.start()