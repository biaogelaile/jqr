from socketIO_client import SocketIO, BaseNamespace
import requests, json
import threading

#serverip = 'http://127.0.0.1:5000'
serverip = 'http://nginx-server:5001'
socket = SocketIO('nginx-server',5001)
#socket = SocketIO('127.0.0.1',5001)
apiurl =  serverip + '/api/v1/login'
apigetmonitorurl = serverip + '/api/v1/zabbixmonitor'
#payload = {"password": "ppy6rQ3iAMKNzpDjpqYdP29g1STvoz6t0", "mobile": "c2YDSc5nIO7u0Bxjy7JHj0VOy"}
payload = {"password": "youke-chatbot", "mobile": "youke-chatbot"}
header = {'Content-Type': 'application/json'}

loginrs = requests.post(apiurl, data=json.dumps(payload), headers=header)
token = loginrs.json()['token']
companyid = None

def botjoinroot(message):
    sendmsg = {'token': token,'role':'chatbot', 'msg': message, "companyid":companyid}
    socket.emit('talk', sendmsg)

def conn_response(*args):
    print(args[0])


def talk_response(*args):
    print('talk zzzzzzzzzzz')
    print(args[0])


def botsendmsgtype2(username):
    sendmsgtype2 = {'data': {'type': 2,'companyid': companyid,'token': token, 'rootbean':
            {'msg': '你好，'+ username + ' 需要我帮你做点什么？', 'actions':
                [{'name': '查看主机CPU', 'type': '3'},
                 {'name': '查看主机内存', 'type': '4'},
                 {'name': '查看磁盘状态', 'type': '6'},
                 {'name': '查看入网带宽', 'type': '8'},
                 {'name': '查看出网带宽', 'type': '8'}
                 ]}}}
    socket.emit('chatbot', sendmsgtype2)
    print('ooooooh yes')



def botsendmsgtype3(host):
    sendmsgtype3 = {
        "data": {
            "type": 3,
            "token": token,
            'companyid': companyid,
            "rootbean": {
            "msg": "当前" + host + "(ip:" + host + "）CPU运行情况：",
            "actions": [
                {
                "title": "CPU",
                "ratio": '30',
                }
            ]}}}

    socket.emit('chatbot', sendmsgtype3)
    print('ooooooh yes')

def botsendmsgtype4(host):
    sendmsgtype4 = {
        "data": {
            "type": 4,
            "token": token,
            'companyid': companyid,
            "rootbean": {
            "msg": "当前" + host + "(ip:" + host + "）内存运行情况：",
            "actions": [
                {
                "title": "内存",
                "ratio": '32GB',
                }
            ]}}}

    socket.emit('chatbot', sendmsgtype4)
    print('ooooooh yes')

def botsendmsgtype8(host):
    sendmsgtype8 = {
        "data": {
            "type": 8,
            "token": token,
            'companyid': companyid,
            "rootbean": {
            "msg": "当前" + host + "(ip:" + host + "）网络状况：",
            "actions": [
                {
                "netDrive": "eth0",
                "outNet": "55",
                "inNet": '22',
                },
                {
                    "netDrive": "eth1",
                    "outNet": "552",
                    "inNet": '223',
                }
            ]}}}

    socket.emit('chatbot', sendmsgtype8)
    print('ooooooh yes')


def botsendmsgtype1(username):
    sendmsgtype1 = {'data': {'type':1, 'token': token,'companyid': companyid, 'rootbean':{'msg': '你好，'+ username}}}
    socket.emit('chatbot', sendmsgtype1)
    print('ooooooh yes')


def chatbot_response(*args):
    print('chatbot zzzzzzzzzzz')
    botmsgdict = args[0]
    print(botmsgdict)
    username = botmsgdict['data']['username']
    if username is None:
        username = '游客'

    if botmsgdict['data']['userid'] != 'youkechatbot' and botmsgdict['data']['type'] == 1:
        botsendmsgtype1(username)
        print('lalalalalalalalal')
    elif botmsgdict['data']['userid'] != 'youkechatbot' and botmsgdict['data']['type'] == 2:
        botsendmsgtype2(username)
    elif botmsgdict['data']['userid'] != 'youkechatbot' and botmsgdict['data']['type'] == 3:
            print(botmsgdict['data'])
            host = botmsgdict['data']['msg']
            print(host)
            botsendmsgtype3(host)
    elif botmsgdict['data']['userid'] != 'youkechatbot' and botmsgdict['data']['type'] == 4:
            print(botmsgdict['data'])
            host = botmsgdict['data']['msg']
            print(host)
            botsendmsgtype4(host)
    elif botmsgdict['data']['userid'] != 'youkechatbot' and botmsgdict['data']['type'] == 8:
            print(botmsgdict['data'])
            host = botmsgdict['data']['msg']
            print(host)
            botsendmsgtype8(host)





def chatbots():
    while True:
        socket.on('chatbotstatus', chatbot_response)
        socket.wait(seconds=1)


tada = threading.Thread(target=chatbots)
tada.start()


def conn():
    socket.emit('conn', 'test')
    botjoinroot('join room')
    socket.on('connstatus', conn_response)
    socket.wait(seconds=1)


def botsendmsgtypehello():
    sendmsgtype1 = {'data': {'type':1, 'token': token,'companyid': companyid, 'rootbean':{'msg': 'joinchatbotroom'}}}
    socket.emit('chatbot', sendmsgtype1)
    print('ooooooh yes')



conn()
botsendmsgtypehello()
