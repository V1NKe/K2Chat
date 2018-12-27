#coding=utf-8
import socket
import json

server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server.bind(('127.0.0.1', 8888))

user_list = []
conn_list = {}

while True :
    try :
        data, addr = server.recvfrom(1024)
        data_de = json.loads(data)
        if data_de['type'] == 'login' :
            nickname = str(data_de['nickname'])
            if nickname in user_list :
                server.sendto(json.dumps({'type':'login',
                                          'state':'Fail!',
                                          'message':'Name exist.'}),addr)
            else :
                conn_list[nickname] = addr
                user_list.append(nickname)
                for i in user_list :
                    server.sendto(json.dumps({'type':'login',
                                              'state':'Success!',
                                              'message':nickname+' is online!'}),conn_list[i])

        elif data_de['type'] == 'messageall' :
            if 'offline' in data_de['message'] :
                user_list.remove(str(data_de['fromname']))       #删除用户列表
                del conn_list[str(data_de['fromname'])]          #删除用户，client字典
            try :
                for i in user_list :
                    if i != str(data_de['fromname']) :
                        server.sendto(json.dumps({'type':'servermsg',
                                                  'fromname':str(data_de['fromname']),
                                                  'message':str(data_de['message'])}), conn_list[i])
            except Exception as e :
                print e

        elif data_de['type'] == 'messageprivate' :
            try :
                toname = data_de['toname']
                if toname in user_list :
                    server.sendto(json.dumps({'type':'privatemessage',
                                              'fromname':str(data_de['fromname']),
                                              'toname':str(data_de['toname']),
                                              'message':str(data_de['message'])}),conn_list[toname])
                else :
                    server.sendto('[!] This user is not exist!',addr)
            except Exception as e :
                print e

        elif data_de['type'] == 'catusers' :
            try :
                userlist = ''
                for i in user_list :
                    userlist += '-> ' + str(i) + '\n'
                server.sendto(json.dumps({'type':'catusers',
                                          'message':'All USER:\n'+userlist}),addr)
            except Exception as e :
                print e

        else :
            pass

    except Exception as e :
        print e