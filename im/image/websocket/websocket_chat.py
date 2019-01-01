from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import requests
import json
import random, string


app = Flask(__name__)
socketio = SocketIO(app)
from flask_socketio import join_room, leave_room

#apiserver = 'http://127.0.0.1:5000'
apiserver = 'http://chatapi:5000'
#apiserver = 'http://139.196.107.14:5000'
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

@socketio.on('conn')
def on_connect(msg):
    print('msg is :', msg)
    emit('connstatus', {'data': 'Connected'})

@socketio.on('talk')
def talk_connect(msg):

    print(msg)
    jieshoumessage = msg['msg']
    print(type(msg))
    if 'msgid' in msg:
        msgid = msg['msgid']
    else:
        msgid = None
    token = msg['token']
    companyid = msg['companyid']
    print('token is', token)
    if companyid:
        user_profile_rs = requests.get(apiserver + '/api/v1/user?token=' + token + '&companyid=' + companyid, headers=header)
    else:
        user_profile_rs = requests.get(apiserver + '/api/v1/youke?token=' + token,headers=header)

    print(user_profile_rs.json())

    user_role = user_profile_rs.json()['role']
    if user_role == '1' or user_role == '2':
        room = generate_random_str(24)
    else:
        room = user_profile_rs.json()['companyname']

    msg['imageUrl'] = user_profile_rs.json()['imageUrl']
    msg['mobile'] = user_profile_rs.json()['mobile']
    msg['username'] = user_profile_rs.json()['username']
    msg['userid'] = user_profile_rs.json()['userid']
    del msg['token']
    join_room(room)
    print('room is:', room)
    if 'role' in msg or jieshoumessage == 'joinroom':
        print('ccccccccccccc')
        pass
    else:
        response = {'data': msg}
        print('uuuuuuuuuuuuu')

        if user_role != '1' and user_role != '2':
            if msgid:
                addlixianmessage_payload = {'token':token, 'companyid':companyid, 'msgid':msgid, 'message': msg}
                addlixianmessage_rs = requests.post(apiserver + '/api/v1/message',data=json.dumps(addlixianmessage_payload),
                                           headers=header)
                if addlixianmessage_rs.status_code == 200:
                    pass
                else:
                    print("Something worang")

        emit('talkstatus', response, room=room)


@socketio.on('chatbot')
def chatbot_connect(msg):

    print('chatbot msg', msg)
    token = msg['data']['token']
    companyid = msg['data']['companyid']
    if 'msgid' in msg['data']:
        msgid = msg['data']['msgid']
    else:
        msgid = None
    if companyid:
        user_profile_rs = requests.get(apiserver + '/api/v1/user?token=' + token + '&companyid=' + companyid, headers=header)
    else:
        user_profile_rs = requests.get(apiserver + '/api/v1/youke?token=' + token,headers=header)
    print(user_profile_rs.json())
    role = user_profile_rs.json()['role']
    oprole = user_profile_rs.json()['oprole']
    print(role)
    if role == '1' or role == '2':
        room = 'chatbotyouke11111'
    else:
        room = user_profile_rs.json()['companyname']
    join_room(room)
    print('room is:', room)
    chatbottype = msg['data']['type']

    if chatbottype == 1:
        print('11111111111111111')
        if 'rootbean' in msg['data'] and msg['data']['rootbean']['msg'] == 'joinchatbotroom':
            print('检查rootbean 是否存在', msg['data']['rootbean']['msg'])
            pass
        else:
            msg['data']['role'] = role
            msg['data']['oprole'] = oprole
            msg['data']['imageUrl'] = user_profile_rs.json()['imageUrl']
            msg['data']['mobile'] = user_profile_rs.json()['mobile']
            msg['data']['username'] = user_profile_rs.json()['username']
            msg['data']['userid'] = user_profile_rs.json()['userid']
            msg['data']['companyid'] = user_profile_rs.json()['companyid']
            del msg['data']['token']
        #response = {'data': {'type':1, 'rootbean':{'msg': '你好'}}}
            if role != '1' and role != '2':
                if msgid:
                    print("到底有没有")
                    addlixianmessage_payload = {'token': token, 'companyid': companyid, 'msgid': msgid, 'message': msg}
                    addlixianmessage_rs = requests.post(apiserver + '/api/v1/message',
                                                        data=json.dumps(addlixianmessage_payload),
                                                        headers=header)
                    if addlixianmessage_rs.status_code == 200:
                        pass
                    else:
                        print("Something worang")
            print('发送数据中')
            emit('chatbotstatus', msg, room=room)
    elif chatbottype == 2:
        print('2222222222222')
        msg['data']['role'] = oprole
        msg['data']['oprole'] = oprole
        msg['data']['imageUrl'] = user_profile_rs.json()['imageUrl']
        msg['data']['mobile'] = user_profile_rs.json()['mobile']
        msg['data']['username'] = user_profile_rs.json()['username']
        msg['data']['userid'] = user_profile_rs.json()['userid']
        del msg['data']['token']
        print(msg)
        print('msgid', msgid)
        if role != '1' and role != '2':
            if msgid:
                print("到底有没有")
                addlixianmessage_payload = {'token':token, 'companyid':companyid, 'msgid':msgid, 'message': msg}
                addlixianmessage_rs = requests.post(apiserver + '/api/v1/message',data=json.dumps(addlixianmessage_payload),
                                               headers=header)
                if addlixianmessage_rs.status_code == 200:
                    pass
                else:
                    print("Something worang")
        emit('chatbotstatus', msg, room=room)


    elif chatbottype >= 3:
        print('333333333')
        print(msg)
        msg['data']['role'] = oprole
        msg['data']['oprole'] = oprole
        msg['data']['imageUrl'] = user_profile_rs.json()['imageUrl']
        msg['data']['mobile'] = user_profile_rs.json()['mobile']
        msg['data']['username'] = user_profile_rs.json()['username']
        msg['data']['userid'] = user_profile_rs.json()['userid']
        del msg['data']['token']
        if role != '1' and role != '2':
            if msgid:
                addlixianmessage_payload = {'token':token, 'companyid':companyid, 'msgid':msgid, 'message': msg}
                addlixianmessage_rs = requests.post(apiserver + '/api/v1/message',data=json.dumps(addlixianmessage_payload),
                                               headers=header)
                if addlixianmessage_rs.status_code == 200:
                    pass
                else:
                    print("Something worang")
        emit('chatbotstatus', msg, room=room)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0',port=5002)
