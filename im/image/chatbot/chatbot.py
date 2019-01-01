from socketIO_client import SocketIO, BaseNamespace
import requests, json
import threading
import time
import random
import string

#serverip = 'http://127.0.0.1:5000'
serverip = 'http://nginx-server:5001'
socket = SocketIO('nginx-server',5001)
apiurl =  serverip + '/api/v1/login'
apigetmonitorurl = serverip + '/api/v1/zabbixmonitor'
#apiurl = 'http://139.196.107.14:5000/api/v1/login'
#payload = {"password": "ppy6rQ3iAMKNzpDjpqYdP29g1STvoz6t0", "mobile": "c2YDSc5nIO7u0Bxjy7JHj0VOy"}
payload = {"password": "p36GJtZDNGktIhKNk0ouCyxazqKD0l8Zd", "mobile": "cUjAwVDIbBtd4hKtbYZbLHz7s"}
header = {'Content-Type': 'application/json'}


def generate_random_str(randomlength=16):
    """
    生成一个指定长度的随机字符串，其中
    string.digits=0123456789
    string.ascii_letters=abcdefghigklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ
    """
    str_list = [random.choice(string.digits + string.ascii_letters) for i in range(randomlength)]
    random_str = ''.join(str_list)
    return random_str


loginrs = requests.post(apiurl, data=json.dumps(payload), headers=header)
print("login...")
token = loginrs.json()['token']
companyid = loginrs.json()['companyid']

def botjoinroot(message):
    msgid = generate_random_str(48)
    sendmsg = {'token': token,'role':'chatbot', 'companyid':companyid, 'msg': message, 'msgid':msgid}
    socket.emit('talk', sendmsg)

def sendmsg(message):
    msgid = generate_random_str(48)
    sendmsg = {'token': token, 'companyid':companyid, 'msg': message, 'msgid':msgid}
    socket.emit('talk', sendmsg)


def conn_response(*args):
    print(args[0])


def talk_response(*args):
    print('talk zzzzzzzzzzz')
    print(args[0])


def botsendmsgtype2(username):
    msgid = generate_random_str(48)
    sendmsgtype2 = {'data': {'type': 2,'companyid':companyid,'msgid':msgid, 'token': token, 'rootbean':
            {'msg': '你好，'+ username + ' 需要我帮你做点什么？', 'actions':
                [{'name': '查看主机CPU', 'type': '3'},
                 {'name': '查看主机内存', 'type': '4'},
                 {'name': '查看磁盘状态', 'type': '6'},
                 {'name': '查看网络流量', 'type': '8'},
                 {'name': '重启主机', 'type': '10'},
                 {'name': '查看磁盘读写', 'type': '12'},
                 ]}}}
    socket.emit('chatbot', sendmsgtype2)
    print('ooooooh yes')



def botsendmsgtype3(host):
    msgid = generate_random_str(48)
    getinfo = requests.get(apigetmonitorurl + '/' + host + '?token=' + token + '&companyid=' + companyid, headers=header)
    if getinfo.status_code != 200:
        pass
    else:
        print('hhhhhhhhhhh', getinfo.json())
        if 'status' in getinfo.json():
            print('不存在host', host)
            sendmsgtype3 = {
                'data': {'type': 1, 'token': token,'msgid':msgid, 'companyid': companyid, 'rootbean':
                    {'msg': "Ooops，未找到此主机：" + host + "，请检查输入的hostid/hostname/hostip"}}}

        else:
            lastvalue_str = getinfo.json()['cpu'][0]['lastvalue']
            lastvalue_float = float(lastvalue_str)
            lastvalue_float2 = round(lastvalue_float, 2)
            hostip = getinfo.json()['hostip']

            sendmsgtype3 = {
            "data": {
                "type": 3,
                "msgid":msgid,
                "token": token,
                'companyid': companyid,
                "rootbean": {
                "msg": "当前" + host + "(ip:" + hostip + "）CPU运行情况：",
                "actions": [
                    {
                    "title": "CPU",
                    "ratio": lastvalue_float2,
                    }
                ]}}}

        socket.emit('chatbot', sendmsgtype3)
        print('ooooooh yes')

def botsendmsgtype4(host):
    msgid = generate_random_str(48)
    getinfo = requests.get(apigetmonitorurl + '/' + host + '?token=' + token + '&companyid=' + companyid, headers=header)
    print('hhhhhhhhhhh', getinfo.json())
    if 'status' in getinfo.json():
        print('不存在host', host)
        sendmsgtype4 = {
            'data': {'type': 1, 'token': token, 'msgid':msgid,'companyid': companyid, 'rootbean':
                {'msg': "Ooops，未找到此主机：" + host + "，请检查输入的hostid/hostname/hostip"}}}
    else:
        total_memory_lastvalue = getinfo.json()['total_memory'][0]['lastvalue']
        available_memory_lastvalue = getinfo.json()['available_memory'][0]['lastvalue']
        used_memory_lastvalue = total_memory_lastvalue - available_memory_lastvalue
        print(total_memory_lastvalue)
        print(available_memory_lastvalue)
        ratiolastvalue_float = used_memory_lastvalue / total_memory_lastvalue * 100
        ratiolastvalue = round(ratiolastvalue_float, 2)
        hostip = getinfo.json()['hostip']

        sendmsgtype4 = {
        "data": {
            "type": 4,
            "token": token,
            "msgid":msgid,
            'companyid': companyid,
            "rootbean": {
            "msg": "当前" + host + "(ip:" + hostip + "）内存运行情况：",
            "actions": [
                {
                "title": "内存",
                "ratio": ratiolastvalue,
                }
            ]}}}

    socket.emit('chatbot', sendmsgtype4)
    print('ooooooh yes')


def botsendmsgtype8(host):
    msgid = generate_random_str(48)
    getinfo = requests.get(apigetmonitorurl + '/' + host + '?token=' + token + '&companyid=' + companyid, headers=header)
    print('hhhhhhhhhhh', getinfo.json())
    if 'status' in getinfo.json():
        print('不存在host', host)
        sendmsgtype8 = {
            'data': {'type': 1, 'token': token,'msgid':msgid, 'companyid': companyid, 'rootbean':
                {'msg': "Ooops，未找到此主机：" + host + "，请检查输入的hostid/hostname/hostip"}}}

    else:
        monitorinfo = getinfo.json()
        hostip = getinfo.json()['hostip']
        innetworkinfo_list = monitorinfo['in_network']
        outnetworkinfo_list = monitorinfo['out_network']
        print(innetworkinfo_list)
        print(outnetworkinfo_list)

        allinnetworkinfo_list = []
        for innetworkinfo in innetworkinfo_list:
            allinnetworkinfo_dict = {}
            drivename_source = innetworkinfo['key_']
            wangkalastvalue = innetworkinfo['lastvalue']
            drivename = drivename_source.strip('net.if.in').strip('[').strip(']')
            allinnetworkinfo_dict['netDrive'] = drivename
            allinnetworkinfo_dict['inNet'] = wangkalastvalue
            allinnetworkinfo_list.append(allinnetworkinfo_dict)

        alloutnetworkinfo_list = []
        for outnetworkinfo in outnetworkinfo_list:
            alloutnetworkinfo_dict = {}
            outdrivename_source = outnetworkinfo['key_']
            outwangkalastvalue = outnetworkinfo['lastvalue']
            outdrivename = outdrivename_source.strip('net.if.out').strip('[').strip(']')
            alloutnetworkinfo_dict['netDrive'] = outdrivename
            alloutnetworkinfo_dict['outNet'] = outwangkalastvalue
            alloutnetworkinfo_list.append(alloutnetworkinfo_dict)

        print(alloutnetworkinfo_list)
        print(allinnetworkinfo_list)

        allnetworkinfo_list = []
        for networkinfo in allinnetworkinfo_list:
            innetworkdrivename = networkinfo['netDrive']
            for outnetworkinfo_check in alloutnetworkinfo_list:
                if outnetworkinfo_check['netDrive'] == innetworkdrivename:
                    print('1111111', outnetworkinfo_check)

                    print('networkinfo', networkinfo)
                    print('outnetworkinfo_check[outNet]', outnetworkinfo_check['outNet'])
                    outnetvalue = outnetworkinfo_check['outNet']
                    networkinfo['outNet'] = outnetvalue
                    allnetworkinfo_list.append(networkinfo)

        print(allnetworkinfo_list)
        sendmsgtype8 = {
        "data": {
            "type": 8,
            "token": token,
            "msgid":msgid,
            'companyid': companyid,
            "rootbean": {
            "msg": "当前" + host + "(ip:" + hostip + "）网络状况：",
            "actions": allnetworkinfo_list
            }}}

    socket.emit('chatbot', sendmsgtype8)
    print('ooooooh yes')


def botsendmsgtype6(host):
    msgid = generate_random_str(48)
    getinfo = requests.get(apigetmonitorurl + '/' + host + '?token=' + token + '&companyid=' + companyid, headers=header)
    print('hhhhhhhhhhh', getinfo.json())
    hostip = getinfo.json()['hostip']
    if 'status' in getinfo.json():
        print('不存在host', host)
        sendmsgtype6 = {
            'data': {'type': 1, 'token': token, 'msgid':msgid,'companyid': companyid, 'rootbean':
                {'msg': "Ooops，未找到此主机：" + host + "，请检查输入的hostid/hostname/hostip"}}}

    else:
        monitorinfo = getinfo.json()
        diskinfo_list = monitorinfo['disk']
        print(diskinfo_list)
        useddiskinfo_list = []
        for diskinfo in diskinfo_list:
            useddiskinfo_dict = {}
            drivename_source = diskinfo['key_']
            drivename = drivename_source.strip('vfs.fs.size').strip('[').strip(']')
            diskdrivename = drivename.split(',')

            if drivename.find('used') != -1:
                diskuseddrivelastvalue = diskinfo['lastvalue']
                useddiskinfo_dict['usedSize'] = diskuseddrivelastvalue
                useddiskinfo_dict['title'] = diskdrivename[0]
                useddiskinfo_list.append(useddiskinfo_dict)

        totaldiskinfo_list = []
        for totaldiskinfo in diskinfo_list:
            totaldiskinfo_dict = {}
            totaldrivename_source = totaldiskinfo['key_']
            totaldrivename = totaldrivename_source.strip('vfs.fs.size').strip('[').strip(']')
            diskdrivename = totaldrivename.split(',')
            if totaldrivename.find('total') != -1:
                disktotaldrivelastvalue = totaldiskinfo['lastvalue']
                totaldiskinfo_dict['totalSize'] = disktotaldrivelastvalue
                totaldiskinfo_dict['title'] = diskdrivename[0]
                totaldiskinfo_list.append(totaldiskinfo_dict)

        alldisknfo_list = []
        for lastuseddiskinfo in useddiskinfo_list:
            lastuseddiskdrivename = lastuseddiskinfo['title']
            for lasttotaldiskinfo_check in totaldiskinfo_list:
                if lasttotaldiskinfo_check['title'] == lastuseddiskdrivename:

                    alldiskvalue = lasttotaldiskinfo_check['totalSize']
                    useddiskvalue = lastuseddiskinfo['usedSize']
                    diskratio = useddiskvalue / alldiskvalue * 100

                    int_diskratio = int(diskratio)
                    float_alldiskvalue = '%.2f' % alldiskvalue
                    float_useddiskvalue = '%.2f' % useddiskvalue

                    totalSize = str(float_alldiskvalue) + 'G'
                    usedSize = str(float_useddiskvalue) + 'G'
                    lastuseddiskinfo['ratio'] = int_diskratio
                    lastuseddiskinfo['totalSize'] = totalSize
                    lastuseddiskinfo['usedSize'] = usedSize
                    alldisknfo_list.append(lastuseddiskinfo)

        print(alldisknfo_list)

        sendmsgtype6 = {
        "data": {
            "type": 6,
            "token": token,
            "msgid": msgid,
            'companyid': companyid,
            "rootbean": {
            "msg": "当前" + host + "(ip:" + hostip + "）磁盘状况：",
            "actions": alldisknfo_list
            }}}

    socket.emit('chatbot', sendmsgtype6)
    print('ooooooh yes')



def botsendmsgtype1(username):
    msgid = generate_random_str(48)
    sendmsgtype1 = {'data': {'type':1, 'token': token,'msgid':msgid,'companyid':companyid, 'rootbean':{'msg': '你好，'+ username}}}
    socket.emit('chatbot', sendmsgtype1)
    print('ooooooh yes')


def botsendmsgtype11(host,role, oprole, action):
    msgid = generate_random_str(32)
    if role == '8':
        botjoinroot("Oooops, 用户已被禁用")
    if oprole == '3' and action == 'request':

        sendmsgtype11 = {'data': {'type':11, 'token': token,'msgid':msgid, 'companyid':companyid,
                              'rootbean':{'msg': '我需要执行 重启服务器 ' + host + '(ip:' + host + ')的命令',
                                          'hostip':host, 'msgid':msgid}}}
        socket.emit('chatbot', sendmsgtype11)
    elif oprole == '4' or oprole == '6':
        if action == 'agree' or action == 'request':
            print('执行中...')

            rebooturl = serverip + '/api/v1/salt/command'
            usertoken = token.split('-')[1]
            userid = token.split('-')[0]
            payload = {"usertoken": usertoken,
                       "userid":userid,
                        "clientip":host,
                        "command":"reboot",
                        "companyid":companyid}

            rebootrs = requests.post(url=rebooturl, data=json.dumps(payload), headers=header)

            if rebootrs.status_code == 200:
                rebootrs_dict_str = rebootrs.json()
                rebootrs_dict = eval(rebootrs_dict_str)
                status = rebootrs_dict['status']
                if status == 0:
                    sendmsg(host + " 重启成功!")
                else:
                    sendmsg(host + " 重启失败!, " + rebootrs_dict['result'])
        else:
            print('已拒绝...')
            sendmsg(host + " ： 此主机重启申请已被拒绝!")

    print('ooooooh yes')


def botsendmsgtype12(host, role, oprole):
    msgid = generate_random_str(48)
    getinfo = requests.get(apigetmonitorurl + '/' + host + '?token=' + token + '&companyid=' + companyid, headers=header)
    print('hhhhhhhhhhh', getinfo.json())
    if 'status' in getinfo.json():
        print('不存在host', host)
        sendmsgtype12 = {
            'data': {'type': 1, 'token': token,'msgid':msgid, 'companyid': companyid, 'rootbean':
                {'msg': "Ooops，没找到服务器：" + host + "，请重新输入。"}}}

    else:
        hostip = getinfo.json()['hostip']
        #
        # if action == 'agree' or action == 'request':
        print('执行中...')
        diskperformanceurl = serverip + '/api/v1/salt/diskperformance'
        data = {

            "token": token,
            "oprole": oprole,
            "role": role,
            "clientip": host,
            "commandid": "4",
            "companyid": companyid
        }

        diskperformance_request = requests.post(url=diskperformanceurl, data=json.dumps(data), headers=header)

        assert diskperformance_request.status_code == 200
        command_result = diskperformance_request.json()
        print(command_result)
        if command_result["status"] == 0:
            result_temp = command_result["result"]["command_result"]
            socket.emit('chatbot', result_temp)
        else:
            result_temp = command_result["msg"]
            socket.emit('chatbot', result_temp)

        sendmsgtype12 = {
            "data": {
                "type": 12,
                "token": token,
                "msgid": msgid,
                'companyid': companyid,
                "rootbean": {
                    "msg": "当前" + host + "(ip:" + hostip + "）磁盘IO：",
                    "actions": result_temp
                }}}
    print(sendmsgtype12)
    socket.emit('chatbot', sendmsgtype12)
    print('ooooooh yes')



def chatbot_response(*args):
    try:
        print('chatbot zzzzzzzzzzz')
        botmsgdict = args[0]
        print(botmsgdict)
        username = botmsgdict['data']['username']

        if botmsgdict['data']['oprole'] != '5' and botmsgdict['data']['type'] == 1:
            botsendmsgtype1(username)
            print('lalalalalalalalal')
        elif botmsgdict['data']['oprole'] != '5' and botmsgdict['data']['type'] == 2:
            botsendmsgtype2(username)
        elif botmsgdict['data']['oprole'] != '5' and botmsgdict['data']['type'] == 3:
                print(botmsgdict['data'])
                host = botmsgdict['data']['msg']
                print(host)
                botsendmsgtype3(host)
        elif botmsgdict['data']['oprole'] != '5' and botmsgdict['data']['type'] == 4:
                print(botmsgdict['data'])
                host = botmsgdict['data']['msg']
                print(host)
                botsendmsgtype4(host)
        elif botmsgdict['data']['oprole'] != '5' and botmsgdict['data']['type'] == 8:
                print(botmsgdict['data'])
                host = botmsgdict['data']['msg']
                print(host)
                botsendmsgtype8(host)
        elif botmsgdict['data']['oprole'] != '5' and botmsgdict['data']['type'] == 6:
                print(botmsgdict['data'])
                host = botmsgdict['data']['msg']
                print(host)
                botsendmsgtype6(host)
        elif botmsgdict['data']['oprole'] != '5' and botmsgdict['data']['type'] == 10:
                print(botmsgdict['data'])
                host = botmsgdict['data']['rootbean']['msg']
                role = botmsgdict['data']['role']
                oprole = botmsgdict['data']['oprole']
                action = botmsgdict['data']['rootbean']['action']
                print(host, role, oprole, action)
                botsendmsgtype11(host,role, oprole, action)
        elif botmsgdict['data']['oprole'] != '5' and botmsgdict['data']['type'] == 12:
            print(botmsgdict['data'])
            host = botmsgdict['data']['msg']
            role = botmsgdict['data']['role']
            oprole = botmsgdict['data']['oprole']
            print(host, role, oprole)
            botsendmsgtype12(host=host, role=role, oprole=oprole)
    except:
        print("Ooops, somethings waring") 

def conn():
    socket.emit('conn', 'test')
    botjoinroot('join room')
    socket.on('connstatus', conn_response)
    socket.wait(seconds=1)


def onlyconn():
    socket.emit('conn', 'test')
    socket.on('connstatus', conn_response)
    socket.wait(seconds=1)


def chatbots():
    while True:
        socket.on('chatbotstatus', chatbot_response)
        socket.wait(seconds=1)

def talks():
    while True:
        socket.on('talkstatus', talk_response)
        socket.wait(seconds=1)


tada = threading.Thread(target=chatbots)
tada.start()

talk_thread = threading.Thread(target=talks)
talk_thread.start()

conn()
def connthreading():
    while True:
        time.sleep(2)
        onlyconn()
connth = threading.Thread(target=connthreading)
connth.start()