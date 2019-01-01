from model import *
import sqlalchemy
import re
import random
import string
import os
import datetime
import time

def phonecheck(mobile):
    n = mobile
    if len(n) != 11:
        return 'failure'
    if re.match(r'1[3,4,5,7,8]\d{9}',n):
        print("手机号码是：\n",n)
        #中国联通：
        #  130，131，132，155，156，185，186，145，176
        if re.match(r'13[0,1,2]\d{8}',n) or \
                re.match(r"15[5,6]\d{8}",n) or \
                re.match(r"18[5,6]",n) or \
                re.match(r"145\d{8}",n) or \
                re.match(r"166\d{8}", n) or \
                re.match(r"176\d{8}",n):
            print("该号码属于：中国联通")
            #中国移动
            #  134, 135 , 136, 137, 138, 139, 147, 150, 151,
            #  152, 157, 158, 159, 178, 182, 183, 184, 187, 188；
        elif re.match(r"13[4,5,6,7,8,9]\d{8}",n) or \
                re.match(r"147\d{8}|178\d{8}",n) or \
                re.match(r"15[0,1,2,7,8,9]\d{8}",n) or \
                re.match(r"18[2,3,4,7,8]\d{8}",n):
            print("该号码属于：中国移动")
        else:
            #中国电信
            # #133,153,189
            print("该号码属于：中国电信")
    else:
        return 'failure'

def generate_random_str(randomlength=16):
    """
    生成一个指定长度的随机字符串，其中
    string.digits=0123456789
    string.ascii_letters=abcdefghigklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ
    """
    str_list = [random.choice(string.digits + string.ascii_letters) for i in range(randomlength)]
    random_str = ''.join(str_list)
    return random_str


def generate_random_int(randomlength=16):
    str_list = [random.choice(string.digits) for i in range(randomlength)]
    random_str = ''.join(str_list)
    return random_str

def smsvc(mobile):
    smsvc = generate_random_int(6)
    data = u'本次验证码为' + smsvc
    command = '/bin/sh sms.sh ' + data + ' ' + mobile
    print('hhhhhhhhhhhhhhhh', command)
    comand_status = os.system(command)
    if comand_status == 0:
        delete_mobile = Sms.query.filter_by(user_mobile=mobile).first()
        if delete_mobile:
            delete_mobile.query.filter_by(user_mobile=mobile).delete()
        insert_sms = Sms(user_mobile=mobile, user_sms=smsvc)
        db.session.add(insert_sms)
        db.session.commit()
        db.session.close()
        return {'status': 0, 'msg': '发送成功'}
    else:
        return {'status': 1, 'msg': '发送失败'}


def forget_smsvc(mobile):
    db.session.rollback()
    mobileexsitcheck = User.query.filter_by(mobile=mobile).first()
    if mobileexsitcheck is None:
        return {'status': 3, 'msg': '用户未注册'}

    smsvc = generate_random_int(6)
    data = u'本次验证码为' + smsvc
    command = '/bin/sh sms.sh ' + data + ' ' + mobile
    print('hhhhhhhhhhhhhhhh', command)
    comand_status = os.system(command)
    if comand_status == 0:
        delete_mobile = Sms.query.filter_by(user_mobile=mobile).first()
        if delete_mobile:
            delete_mobile.query.filter_by(user_mobile=mobile).delete()
        insert_sms = Sms(user_mobile=mobile, user_sms=smsvc)
        db.session.add(insert_sms)
        db.session.commit()
        db.session.close()
        return {'status': 0, 'msg': '发送成功'}
    else:
        return {'status': 1, 'msg': '发送失败'}

def insert_chatbot(companyid):
    try:
        i_username = 'chatbot'
        i_userid = 'c' + generate_random_str(24)
        i_password = 'p' + generate_random_str(32)
        i_mobile = companyid
        i_role = '0'
        companyid = companyid
        email = '359594776@qq.com'
        insert_mobile = User(username=i_username, userid=i_userid,
                             mobile=i_mobile, password=i_password,
                             role=i_role)
        insert_opuser = Opuser(opusername=i_username, opuserid=i_userid,
                               opmobile=i_mobile, opcompanyid=companyid,
                               default='true', oprole='5', opemail=email,
                               )
        db.session.add(insert_mobile)
        db.session.add(insert_opuser)
        db.session.commit()
        db.session.close()

        return {'chatbotid':i_userid,'chatbotusername': i_mobile, 'chatbotpassword': i_password}
    except sqlalchemy.exc.OperationalError:
        return {'status': 3, 'Oooops': '数据库连接出现错误'}

def user_info(userid, token, companyid):
    try:
        if token != '11111':
            return {'status': 1, 'msg': 'token 无效'}
        user_query = User.query.filter_by(userid=userid).first()
        print(companyid)
        if companyid:
            oprole_query = Opuser.query.filter_by(opuserid=userid, opcompanyid=companyid).first()
            oprole = oprole_query.oprole
        else:
            oprole = None
        user_mobile = user_query.mobile
        user_profile = user_query.profile
        user_role = user_query.role
        user_name = user_query.username
        if user_role != '1' and user_role != '2':
            company_query = Company.query.filter_by(companyid=companyid).first()
            user_companyname = company_query.companyname
            user_companyexpiredate = company_query.companyexpiredate
            if company_query.companyrole:
                user_companyrole = company_query.companyrole
            else:
                user_companyrole = '1'
        else:
            user_companyname = None
            user_companyexpiredate = None
            user_companyrole = None
        db.session.close()
        return {'status': 0, 'msg': '查询成功','userid': userid, 'companyname': user_companyname,
                    'companyrole':user_companyrole, 'companyexpiredate':user_companyexpiredate,
                    'companyid':companyid,'username':user_name, 'email': None,'oprole':oprole,
                    'mobile': user_mobile, 'role':user_role, 'imageUrl':user_profile}


    #except AttributeError:
    #    return {'status': 2, 'msg': '用户名或密码错误'}
    except sqlalchemy.exc.OperationalError:
        return {'status':3, 'Oooops': '数据库连接出现错误'}


def mobile_insert(smsvc, password, mobile):
    try:
        mobilecheck = re.findall(r"1\d{10}", mobile)
        print(mobilecheck)
        passwordlen = len(password)
        user_sms_query = Sms.query.filter_by(user_mobile=mobile).first()

        if user_sms_query:
            smsvcode = user_sms_query.user_sms
        else:
            smsvcode = None
        #0 为注册成功
        #1 为手机号码为空，请先填写手机号码
        #2 为手机号码格式不正确
        #3 为验证码为空
        #4 为验证码不正确
        #5 为密码长度不符合要求，长度需为6-20位
        #6 为手机号码已经被注册

        if mobile == 'null':
            return {'status': 1, 'msg': '请先填写手机号码'}
        elif phonecheck(mobile) == 'failure':
            return {'status': 2, 'msg': '手机号码格式不正确'}
        elif smsvc == 'null':
            return {'status':3, 'msg':'验证码不能为空'}
        elif smsvc != smsvcode and smsvc != '11111':
            return {'status': 4, 'msg': '短信验证码不正确'}
        elif passwordlen < 6 or passwordlen > 20:
            return {'status':5, 'msg':'密码长度需为6-20位'}

        verification_mobile = User.query.filter_by(mobile=mobile).first()
        if verification_mobile:
            return {'status': 6, 'msg': '手机号码已被注册'}

        userid = 'u' + generate_random_str(24)

        insert_mobile = User(username=mobile, mobile=mobile, password=password, role='1', userid=userid)
        db.session.add(insert_mobile)
        db.session.commit()
        check_opuser_querys = Opuser.query.filter_by(opmobile=mobile).all()
        if check_opuser_querys:
            change_user_role_query = User.query.filter_by(mobile=mobile).first()
            change_user_role_query.role = '0'
            for check_opuser in check_opuser_querys:
                check_opuser.userstatus = 'register'
                check_opuser.opuserid = userid
                db.session.commit()

        userinfors = User.query.filter_by(userid=userid).first()
        q_username = userinfors.username
        q_userid = userinfors.userid
        q_role = userinfors.role
        q_mobile = userinfors.mobile
        q_profile = userinfors.profile
        db.session.close()
        return {'status': 0, 'msg': '注册成功', 'mobile': q_mobile,
                    'userid':q_userid, 'username':q_username,
                    'role':q_role,'mobile':mobile,
                    'imageUrl': q_profile, 'token':q_userid+ '-11111'}
    except sqlalchemy.exc.OperationalError:
        return {'Oooops': '数据库连接似乎出了问题'}

def password_jiaoyan(token, userid, password):
    try:
        if token != '11111':
            return {'status': 1, 'msg': 'Ooooops, token不可用'}
        else:
            user_password_query = User.query.filter_by(userid=userid).first()
            user_password = user_password_query.password
            if user_password == password:
                db.session.close()
                return {'status': 0, 'msg': '校验成功'}
            else:
                db.session.close()
                return {'status': 2, 'msg': '密码错误'}

    except AttributeError:
        return {'status': 2, 'msg': 'Oooops, something is wrong'}

    except sqlalchemy.exc.OperationalError:
        return {'status':3, 'Oooops': '数据库似乎出了问题'}

def user_forget_password(smsvc, password, mobile):
    try:
        passwordlen = len(password)
        userexsitcheck = User.query.filter_by(mobile=mobile).first()

        if userexsitcheck is None:
            db.session.close()
            return {'status': 4, 'msg': '用户不存在'}

        user_sms_query = Sms.query.filter_by(user_mobile=mobile).first()
        if user_sms_query:
            smsvcode = user_sms_query.user_sms
        else:
            smsvcode = None

        if smsvc != smsvcode and smsvc != '11111':
            db.session.close()
            return {'status': 1, 'msg':'验证码错误'}
        elif smsvc == 'null':
            db.session.close()
            return {'status': 2, 'msg': '验证码不能为空'}
        elif passwordlen < 6 or passwordlen > 20:
            db.session.close()
            return {'status': 3, 'msg': '密码长度需为6-20位'}
        else:
            change_password_userid = User.query.filter_by(mobile=mobile).first()
            change_password_userid.password = password
            db.session.commit()
            return_userinfo = User.query.filter_by(mobile=mobile).first()
            q_username = return_userinfo.username
            q_userid = return_userinfo.userid
            return_usercompanyinfo = Opuser.query.filter_by(opmobile=mobile, default='true').first()
            q_companyid = return_usercompanyinfo.opcompanyid
            retuen_company_query = Company.query.filter_by(companyid=q_companyid).first()
            q_companyname = retuen_company_query.companyname
            q_companyrole = retuen_company_query.companyrole
            q_companyexpiredate = retuen_company_query.companyexpiredate
            q_role = return_userinfo.role
            q_mobile = return_userinfo.mobile
            q_profile = return_userinfo.profile
            db.session.close()
            return {'status': 0, 'msg': '修改成功','mobile':q_mobile,'username': q_username,
                    'companyname': q_companyname, 'role': q_role, 'companyid': q_companyid,
                    'companyrole':q_companyrole,
                    'companyexpiredate':q_companyexpiredate, 'userid':q_userid, 'imageUrl': q_profile}
    except sqlalchemy.exc.OperationalError:
        return {'Oooops': 'There is a problem with the database'}


def change_password(token, userid, newpassword, oldpassword):
    try:
        passwordlen = len(newpassword)
        if token != '11111':
            return {'status': 1, 'msg':'token无效'}
        elif passwordlen < 6 or passwordlen > 20:
            return {'status': 3, 'msg': '密码长度需为6-20位'}
        else:
            return_userinfo = User.query.filter_by(userid=userid).first()
            password = return_userinfo.password
            if oldpassword == password:
                return_userinfo.password = newpassword
                db.session.commit()
                db.session.close()
                return {'status': 0, 'msg': '修改成功'}
            else:
                db.session.close()
                return {'status': 2, 'msg': '旧密码错误'}
    except sqlalchemy.exc.OperationalError:
        return {'Oooops': '数据库连接似乎出了问题'}

def user_update_username(token, userid, newusername):
    try:
        if token != '11111':
            return {'status': 1, 'msg':'token无效'}
        elif len(newusername) > 12:
            return {'status': 2, 'msg': '用户名长度不符合要求，用户名应在12字以内'}
        else:
            # return_userinfo = User.query.filter_by(userid=userid).first()
            return_userinfo = Opuser.query.filter_by(opuserid=userid).first()
            return_userinfo.opusername = newusername
            db.session.commit()
            db.session.close()

            return {'status': 0, 'msg': '修改成功'}
    except sqlalchemy.exc.OperationalError:
        return {'Oooops': '数据库连接似乎出了问题'}

def user_update_mobile(smsvc, token, userid, newmobile):
    try:
        mobilecheck = re.findall(r"1\d{10}", newmobile)
        print(mobilecheck)
        db.session.rollback()
        user_mobile_query = User.query.filter_by(mobile=newmobile).first()

        if user_mobile_query:
            db.session.close()
            return {'status': 4, 'msg':'手机号码已存在'}

        user_sms_query = Sms.query.filter_by(user_mobile=newmobile).first()
        if user_sms_query:
            smsvcode = user_sms_query.user_sms
        else:
            smsvcode = None

        if smsvc != smsvcode and smsvc != '11111':
            return {'status': 1, 'msg':'验证码错误'}
        elif token != '11111':
            return {'status': 2, 'msg': 'token无效'}
        elif phonecheck(newmobile) == 'failure':
            return {'status': 3, 'msg': '请输入正确的手机号码'}
        else:
            return_userinfo = User.query.filter_by(userid=userid).first()
            return_userinfo.mobile = newmobile
            db.session.commit()
            db.session.close()
            return {'status': 0, 'msg': '修改成功'}
    except sqlalchemy.exc.OperationalError:
        return {'Oooops': '数据库连接似乎出了问题'}

def user_default_company(token, userid):
    try:
        if token != '11111':
            return {'status': 1, 'msg': 'token不可用'}
        user_query = User.query.filter_by(userid=userid).first()

        mobile = user_query.mobile
        user_id = user_query.userid
        user_role = user_query.role
        user_name = user_query.username
        user_profile = user_query.profile
        if user_query.role == '1':
            db.session.close()
            return {
                "companyexpiredate": None,
                "companyid": None,
                "companyname": None,
                "companyrole": None,
                "email": None,
                "imageUrl": user_profile,
                "mobile": mobile,
                "msg": "登录成功",
                "role": user_role,
                "status": 0,
                "token": user_id + "-11111",
                "userid": user_id,
                "username": user_name,
            }
        if user_query.role == '2':
            user_youke_company_query = Opuser.query.filter_by(opuserid=userid).first()
            youkecompanyid = user_youke_company_query.opcompanyid
            youkecompanyinfo = Company.query.filter_by(companyid=youkecompanyid).first()
            youke_companyexpiredate = youkecompanyinfo.companyexpiredate
            youke_companyname = youkecompanyinfo.companyname
            youke_companrole = youkecompanyinfo.companyrole

            if youke_companyexpiredate:
                request_create_time_chuo = int(time.mktime(youke_companyexpiredate.timetuple()))
            else:
                request_create_time_chuo = None
            db.session.close()
            return {
                "companyexpiredate": request_create_time_chuo,
                "companyid": youkecompanyid,
                "companyname": youke_companyname,
                "companyrole": youke_companrole,
                "email": None,
                "imageUrl": user_profile,
                "mobile": mobile,
                "msg": "登录成功",
                "role": user_role,
                "status": 0,
                "token": user_id + "-11111",
                "userid": user_id,
                "username": user_name,
            }


        user_default_company_query = Opuser.query.filter_by(opuserid=userid, default='true').first()

        if user_default_company_query:
            user_oprole = user_default_company_query.oprole
            defaultcompanyid = user_default_company_query.opcompanyid
            default_companyinfo = Company.query.filter_by(companyid=defaultcompanyid).first()
            default_companyexpiredate = default_companyinfo.companyexpiredate
            default_companyname = default_companyinfo.companyname
            default_companrole = default_companyinfo.companyrole
            if default_companyexpiredate:
                request_create_time_chuo = int(time.mktime(default_companyexpiredate.timetuple()))
            else:
                request_create_time_chuo = None

            db.session.close()
            return {
                "companyexpiredate": request_create_time_chuo,
                "companyid": defaultcompanyid,
                "companyname": default_companyname,
                "companyrole": default_companrole,
                "imageUrl": user_profile,
                "mobile": mobile,
                "msg": "查询成功",
                "oprole": user_oprole,
                "role": user_role,
                "status": 0,
                "userid": user_id,
                "username": user_name,
            }
        else:
            user_default_allcompany_query = Opuser.query.filter_by(opuserid=userid).all()

            opcompany_list = []
            for opuser_company_query in user_default_allcompany_query:
                if opuser_company_query.oprole != '2':
                    opcompany_dict = {}
                    opcompanyid = opuser_company_query.opcompanyid
                    opuserid = opuser_company_query.opuserid
                    opusername = opuser_company_query.opusername
                    opmobile = opuser_company_query.opmobile
                    oprole = opuser_company_query.oprole
                    opcompanyinfo_query = Company.query.filter_by(companyid=opcompanyid).first()
                    opcompanyname = opcompanyinfo_query.companyname
                    opcompanyrole = opcompanyinfo_query.companyrole
                    companyexpiredate = opcompanyinfo_query.companyexpiredate

                    if companyexpiredate:
                        request_create_time_chuo = int(time.mktime(companyexpiredate.timetuple()))
                    else:
                        request_create_time_chuo = None


                    opcompany_dict['companyid'] = opcompanyid
                    opcompany_dict['userid'] = opuserid
                    opcompany_dict['username'] = opusername
                    opcompany_dict['companyname'] = opcompanyname
                    opcompany_dict['companyrole'] = opcompanyrole
                    opcompany_dict['companyexpiredate'] = request_create_time_chuo
                    opcompany_dict['mobile'] = opmobile
                    opcompany_dict['oprole'] = oprole
                    opcompany_list.append(opcompany_dict)
            db.session.close()
            return {'status': 0, 'msg': '查询成功', 'choice': {'status': 'false', 'companyinfo': opcompany_list}}
    except sqlalchemy.exc.OperationalError:
        return {'status':3, 'Oooops': '数据库连接出现错误'}
"""
def user_default_company(token, userid):

    try:
        if token != '11111':
            return {'status': 1, 'msg': 'token不可用'}
        user_query = User.query.filter_by(userid=userid).first()

        mobile = user_query.mobile
        user_id = user_query.userid
        user_role = user_query.role
        user_name = user_query.username
        user_profile = user_query.profile
        if user_query.role == '1':
            db.session.close()
            return {
                "companyexpiredate": None,
                "companyid": None,
                "companyname": None,
                "companyrole": None,
                "email": None,
                "imageUrl": user_profile,
                "mobile": mobile,
                "msg": "登录成功",
                "role": user_role,
                "status": 0,
                "token": user_id + "-11111",
                "userid": user_id,
                "username": user_name,
            }
        if user_query.role == '2':
            user_youke_company_query = Opuser.query.filter_by(opuserid=userid).first()
            youkecompanyid = user_youke_company_query.opcompanyid
            youkecompanyinfo = Company.query.filter_by(companyid=youkecompanyid).first()
            youke_companyexpiredate = youkecompanyinfo.companyexpiredate
            youke_companyname = youkecompanyinfo.companyname
            youke_companrole = youkecompanyinfo.companyrole

            if youke_companyexpiredate:
                request_create_time_chuo = int(time.mktime(youke_companyexpiredate.timetuple()))
            else:
                request_create_time_chuo = None
            db.session.close()
            return {
                "companyexpiredate": request_create_time_chuo,
                "companyid": youkecompanyid,
                "companyname": youke_companyname,
                "companyrole": youke_companrole,
                "email": None,
                "imageUrl": user_profile,
                "mobile": mobile,
                "msg": "登录成功",
                "role": user_role,
                "status": 0,
                "token": user_id + "-11111",
                "userid": user_id,
                "username": user_name,
            }


        # user_default_company_query = Opuser.query.filter_by(opuserid=userid, default='true').first()
        #
        # if user_default_company_query:
        #     user_oprole = user_default_company_query.oprole
        #     defaultcompanyid = user_default_company_query.opcompanyid
        #     default_companyinfo = Company.query.filter_by(companyid=defaultcompanyid).first()
        #     default_companyexpiredate = default_companyinfo.companyexpiredate
        #     default_companyname = default_companyinfo.companyname
        #     default_companrole = default_companyinfo.companyrole
        #     if default_companyexpiredate:
        #         request_create_time_chuo = int(time.mktime(default_companyexpiredate.timetuple()))
        #     else:
        #         request_create_time_chuo = None
        #
        #     db.session.close()
        #     return {
        #         "companyexpiredate": request_create_time_chuo,
        #         "companyid": defaultcompanyid,
        #         "companyname": default_companyname,
        #         "companyrole": default_companrole,
        #         "imageUrl": user_profile,
        #         "mobile": mobile,
        #         "msg": "查询成功",
        #         "oprole": user_oprole,
        #         "role": user_role,
        #         "status": 0,
        #         "userid": user_id,
        #         "username": user_name,
        #     }

        user_default_company_query = Opuser.query.filter_by(opuserid=userid).all()
        if user_default_company_query:

            if len(user_default_company_query) == 1:
                user_oprole = user_default_company_query.oprole
                defaultcompanyid = user_default_company_query.opcompanyid
                default_companyinfo = Company.query.filter_by(companyid=defaultcompanyid).first()
                default_companyexpiredate = default_companyinfo.companyexpiredate
                default_companyname = default_companyinfo.companyname
                default_companrole = default_companyinfo.companyrole
                if default_companyexpiredate:
                    request_create_time_chuo = int(time.mktime(default_companyexpiredate.timetuple()))
                else:
                    request_create_time_chuo = None

                db.session.close()
                return {
                    "companyexpiredate": request_create_time_chuo,
                    "companyid": defaultcompanyid,
                    "companyname": default_companyname,
                    "companyrole": default_companrole,
                    "imageUrl": user_profile,
                    "mobile": mobile,
                    "msg": "查询成功",
                    "oprole": user_oprole,
                    "role": user_role,
                    "status": 0,
                    "userid": user_id,
                    "username": user_name,
                }

            else:
                user_default_allcompany_query = Opuser.query.filter_by(opuserid=userid).all()

                opcompany_list = []
                for opuser_company_query in user_default_allcompany_query:
                    if opuser_company_query.oprole != '2':
                        opcompany_dict = {}
                        opcompanyid = opuser_company_query.opcompanyid
                        opuserid = opuser_company_query.opuserid
                        opusername = opuser_company_query.opusername
                        opmobile = opuser_company_query.opmobile
                        oprole = opuser_company_query.oprole
                        opcompanyinfo_query = Company.query.filter_by(companyid=opcompanyid).first()
                        opcompanyname = opcompanyinfo_query.companyname
                        opcompanyrole = opcompanyinfo_query.companyrole
                        companyexpiredate = opcompanyinfo_query.companyexpiredate

                        if companyexpiredate:
                            request_create_time_chuo = int(time.mktime(companyexpiredate.timetuple()))
                        else:
                            request_create_time_chuo = None


                        opcompany_dict['companyid'] = opcompanyid
                        opcompany_dict['userid'] = opuserid
                        opcompany_dict['username'] = opusername
                        opcompany_dict['companyname'] = opcompanyname
                        opcompany_dict['companyrole'] = opcompanyrole
                        opcompany_dict['companyexpiredate'] = request_create_time_chuo
                        opcompany_dict['mobile'] = opmobile
                        opcompany_dict['oprole'] = oprole
                        opcompany_list.append(opcompany_dict)
                db.session.close()
                return {'status': 0, 'msg': '查询成功', 'choice': {'status': 'false', 'companyinfo': opcompany_list}}
    except sqlalchemy.exc.OperationalError:
        return {'status':3, 'Oooops': '数据库连接出现错误'}
"""

def user_login(mobile, password):
    try:
        user_query = User.query.filter_by(mobile=mobile).first()

        if user_query is None:
            db.session.close()
            return {'status': 1, 'msg': '用户名或密码错误'}
        user_mark = user_query.mark
        if user_mark == "userdisabled":
            return {'status': 10, 'msg': '用户已被禁用'}
            
        user_password = user_query.password

        if user_password != password:
            return {'status': 1, 'msg': '用户名或密码错误'}

        user_id = user_query.userid
        user_role = user_query.role
        user_name = user_query.username
        user_profile = user_query.profile
        #当用户申请加入公司但是处于审核状态
        if user_query.role == '2':
            user_youke_company_query = Opuser.query.filter_by(opuserid=user_id).first()
            youkecompanyid = user_youke_company_query.opcompanyid
            youkecompanyinfo = Company.query.filter_by(companyid=youkecompanyid).first()
            youke_companyexpiredate = youkecompanyinfo.companyexpiredate
            if youke_companyexpiredate:
                request_create_time_chuo = int(time.mktime(youke_companyexpiredate.timetuple()))
            else:
                request_create_time_chuo = None

            youke_companyname = youkecompanyinfo.companyname
            youke_companrole = youkecompanyinfo.companyrole
            db.session.close()
            return {
                "companyexpiredate": request_create_time_chuo,
                "companyid": youkecompanyid,
                "companyname": youke_companyname,
                "companyrole": youke_companrole,
                "email": None,
                "imageUrl": user_profile,
                "mobile": mobile,
                "msg": "登录成功",
                "role": user_role,
                "status": 0,
                "token": user_id + "-11111",
                "userid": user_id,
                "username": user_name,
            }

        opuser_company_default_querys = Opuser.query.filter_by(opmobile=mobile).first()
        #当用户未加入公司
        if opuser_company_default_querys is None:
            logintime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            user_query.logintime = logintime
            db.session.commit()
            db.session.close()
            return {
                  "companyexpiredate": None,
                  "companyid": None,
                  "companyname": None,
                  "companyrole": None,
                  "email": None,
                  "imageUrl": user_profile,
                  "mobile": mobile,
                  "msg": "登录成功",
                  "role": user_role,
                  "status": 0,
                  "token": user_id + "-11111",
                  "userid": user_id,
                  "username": user_name,
                }

        opuser_company_default_querys = Opuser.query.filter_by(opmobile=mobile, default='true').first()
        #当用户已经加入公司，并且没有默认公司
        if opuser_company_default_querys is None:
            opuser_company_querys = Opuser.query.filter_by(opmobile=mobile).all()
            opcompany_list = []
            checkopcompany = []
            for opuser_company_query in opuser_company_querys:
                if opuser_company_query.oprole != '2':
                    opcompany_dict = {}
                    opcompanyid = opuser_company_query.opcompanyid
                    opuserid = opuser_company_query.opuserid
                    opusername = opuser_company_query.opusername
                    opmobile = opuser_company_query.opmobile
                    oprole = opuser_company_query.oprole
                    opcompanyinfo_query = Company.query.filter_by(companyid=opcompanyid).first()
                    opcompanyname = opcompanyinfo_query.companyname
                    opcompanyrole = opcompanyinfo_query.companyrole
                    companyexpiredate = opcompanyinfo_query.companyexpiredate
                    if companyexpiredate:
                        request_create_time_chuo = int(time.mktime(companyexpiredate.timetuple()))
                    else:
                        request_create_time_chuo = None
                    opcompany_dict['companyid'] = opcompanyid
                    opcompany_dict['userid'] = opuserid
                    opcompany_dict['username'] = opusername
                    opcompany_dict['companyname'] = opcompanyname
                    opcompany_dict['companyrole'] = opcompanyrole
                    opcompany_dict['companyexpiredate'] = request_create_time_chuo
                    opcompany_dict['mobile'] = opmobile
                    opcompany_dict['oprole'] = oprole
                    opcompany_list.append(opcompany_dict)
                else:
                    checkopcompany.append('check')
            if len(opuser_company_querys) == len(checkopcompany):
                db.session.close()
                return {
                  "companyexpiredate": None,
                  "companyid": None,
                  "companyname": None,
                  "companyrole": None,
                  "email": None,
                  "imageUrl": user_profile,
                  "mobile": mobile,
                  "msg": "登录成功",
                  "role": user_role,
                  "status": 0,
                  "token": user_id + "-11111",
                  "userid": user_id,
                  "username": user_name,
                }
            else:
                db.session.close()
                return {'status': 0, 'msg': '登录成功','choice': {'status':'false', 'companyinfo': opcompany_list}, 'token':user_id + '-11111'}

        if opuser_company_default_querys:
            # 当用户已经加入公司，并且有默认公司
            print(opuser_company_default_querys.opmobile)
            opusercompanyid_default = opuser_company_default_querys.opcompanyid
            opuseremail_default = opuser_company_default_querys.opemail
            opusercompanyinfo_default = Company.query.filter_by(companyid=opusercompanyid_default).first()
            opusercompanyname_default = opusercompanyinfo_default.companyname
            opusercompanyrole_default = opusercompanyinfo_default.companyrole
            opusercompanyexpire_default = opusercompanyinfo_default.companyexpiredate

            if opusercompanyexpire_default:
                request_create_time_chuo = int(time.mktime(opusercompanyexpire_default.timetuple()))
            else:
                request_create_time_chuo = None
            myloginopmobile = opuser_company_default_querys.opmobile
            myloginoprole = opuser_company_default_querys.oprole
            myloginopusername = opuser_company_default_querys.opusername
            db.session.close()
            return {
                "companyexpiredate": request_create_time_chuo,
                "companyid": opusercompanyid_default,
                "companyname": opusercompanyname_default,
                "companyrole": opusercompanyrole_default,
                "email": opuseremail_default,
                "imageUrl": user_profile,
                "opmobile": myloginopmobile,
                "mobile": mobile,
                "msg": "登录成功",
                "role": user_role,
                "oprole": myloginoprole,
                "status": 0,
                "token": user_id + "-11111",
                "userid": user_id,
                "username": user_name,
                "opusername": myloginopusername,

            }
        #0 为 登录成功
        #1 为用户名或密码错误
        #2 为用户名或密码错误
        #3 为数据库连接错误
    except sqlalchemy.exc.OperationalError:
        return {'status':3, 'Oooops': '数据库连接似乎出了问题'}

"""
def user_login(mobile, password):
    try:
        user_query = User.query.filter_by(mobile=mobile).first()

        if user_query is None:
            db.session.close()
            return {'status': 1, 'msg': '用户名或密码错误'}
        user_mark = user_query.mark
        if user_mark == "userdisabled":
            return {'status': 10, 'msg': '用户已被禁用'}

        user_password = user_query.password

        if user_password != password:
            return {'status': 1, 'msg': '用户名或密码错误'}

        user_id = user_query.userid
        user_role = user_query.role
        user_name = user_query.username
        user_profile = user_query.profile
        # 当用户申请加入公司但是处于审核状态
        if user_query.role == '2':
            user_youke_company_query = Opuser.query.filter_by(opuserid=user_id).first()
            youkecompanyid = user_youke_company_query.opcompanyid
            youkecompanyinfo = Company.query.filter_by(companyid=youkecompanyid).first()
            youke_companyexpiredate = youkecompanyinfo.companyexpiredate
            if youke_companyexpiredate:
                request_create_time_chuo = int(time.mktime(youke_companyexpiredate.timetuple()))
            else:
                request_create_time_chuo = None

            youke_companyname = youkecompanyinfo.companyname
            youke_companrole = youkecompanyinfo.companyrole
            db.session.close()
            return {
                "companyexpiredate": request_create_time_chuo,
                "companyid": youkecompanyid,
                "companyname": youke_companyname,
                "companyrole": youke_companrole,
                "email": None,
                "imageUrl": user_profile,
                "mobile": mobile,
                "msg": "登录成功",
                "role": user_role,
                "status": 0,
                "token": user_id + "-11111",
                "userid": user_id,
                "username": user_name,
            }

        opuser_company_default_querys = Opuser.query.filter_by(opmobile=mobile).first()
        # 当用户未加入公司
        if opuser_company_default_querys is None:
            logintime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            user_query.logintime = logintime
            db.session.commit()
            db.session.close()
            return {
                "companyexpiredate": None,
                "companyid": None,
                "companyname": None,
                "companyrole": None,
                "email": None,
                "imageUrl": user_profile,
                "mobile": mobile,
                "msg": "登录成功",
                "role": user_role,
                "status": 0,
                "token": user_id + "-11111",
                "userid": user_id,
                "username": user_name,
            }

        opuser_company_default_querys = Opuser.query.filter_by(opmobile=mobile).all()
        
        # 当用户已经加入公司，并且没有默认公司
        if opuser_company_default_querys is not None:
            
            if len(opuser_company_default_querys)!=1:
                opuser_company_querys = Opuser.query.filter_by(opmobile=mobile).all()
                opcompany_list = []
                checkopcompany = []
                for opuser_company_query in opuser_company_querys:
                    if opuser_company_query.oprole != '2':
                        opcompany_dict = {}
                        opcompanyid = opuser_company_query.opcompanyid
                        opuserid = opuser_company_query.opuserid
                        opusername = opuser_company_query.opusername
                        opmobile = opuser_company_query.opmobile
                        oprole = opuser_company_query.oprole
                        opcompanyinfo_query = Company.query.filter_by(companyid=opcompanyid).first()
                        opcompanyname = opcompanyinfo_query.companyname
                        opcompanyrole = opcompanyinfo_query.companyrole
                        companyexpiredate = opcompanyinfo_query.companyexpiredate
                        if companyexpiredate:
                            request_create_time_chuo = int(time.mktime(companyexpiredate.timetuple()))
                        else:
                            request_create_time_chuo = None
                        opcompany_dict['companyid'] = opcompanyid
                        opcompany_dict['userid'] = opuserid
                        opcompany_dict['username'] = opusername
                        opcompany_dict['companyname'] = opcompanyname
                        opcompany_dict['companyrole'] = opcompanyrole
                        opcompany_dict['companyexpiredate'] = request_create_time_chuo
                        opcompany_dict['mobile'] = opmobile
                        opcompany_dict['oprole'] = oprole
                        opcompany_list.append(opcompany_dict)
                    else:
                        checkopcompany.append('check')
                if len(opuser_company_querys) == len(checkopcompany):
                    db.session.close()
                    return {
                        "companyexpiredate": None,
                        "companyid": None,
                        "companyname": None,
                        "companyrole": None,
                        "email": None,
                        "imageUrl": user_profile,
                        "mobile": mobile,
                        "msg": "登录成功",
                        "role": user_role,
                        "status": 0,
                        "token": user_id + "-11111",
                        "userid": user_id,
                        "username": user_name,
                    }
                else:
                    db.session.close()
                    return {'status': 0, 'msg': '登录成功', 'choice': {'status': 'false', 'companyinfo': opcompany_list},
                            'token': user_id + '-11111'}
            
            elif len(opuser_company_default_querys)==1:
                
		opuser_company_default_querys = Opuser.query.filter_by(opmobile=mobile).all()
                print(opuser_company_default_querys.opmobile)
                opusercompanyid_default = opuser_company_default_querys.opcompanyid
                opuseremail_default = opuser_company_default_querys.opemail
                opusercompanyinfo_default = Company.query.filter_by(companyid=opusercompanyid_default).first()
                opusercompanyname_default = opusercompanyinfo_default.companyname
                opusercompanyrole_default = opusercompanyinfo_default.companyrole
                opusercompanyexpire_default = opusercompanyinfo_default.companyexpiredate

                if opusercompanyexpire_default:
                    request_create_time_chuo = int(time.mktime(opusercompanyexpire_default.timetuple()))
                else:
                    request_create_time_chuo = None
                myloginopmobile = opuser_company_default_querys.opmobile
                myloginoprole = opuser_company_default_querys.oprole
                myloginopusername = opuser_company_default_querys.opusername
                db.session.close()
                return {
                    "companyexpiredate": request_create_time_chuo,
                    "companyid": opusercompanyid_default,
                    "companyname": opusercompanyname_default,
                    "companyrole": opusercompanyrole_default,
                    "email": opuseremail_default,
                    "imageUrl": user_profile,
                    "opmobile": myloginopmobile,
                    "mobile": mobile,
                    "msg": "登录成功",
                    "role": user_role,
                    "oprole": myloginoprole,
                    "status": 0,
                    "token": user_id + "-11111",
                    "userid": user_id,
                    "username": user_name,
                    "opusername": myloginopusername,
                }         
        # 0 为 登录成功
        # 1 为用户名或密码错误
        # 2 为用户名或密码错误
        # 3 为数据库连接错误
        
    except sqlalchemy.exc.OperationalError:
        return {'status': 3, 'Oooops': '数据库连接似乎出了问题'}
"""
def company_query(companyname, token):
    try:
        #2 代表邮箱为空
        #3 代表用户名为空
        #4 代表公司名称为空
        #5 该公司已经被注册

        if token != '11111':
            print(token)
            return {'status': 1, 'msg': 'token无效'}
        verification_company = Company.query.all()
        if verification_company:
            companylist = []
            for company in verification_company:
                companyinfo_dict = {}
                company_id = company.companyid
                print(company_id)
                admin_query = Opuser.query.filter_by(opcompanyid=company_id, oprole='4').first()
                admin_username = admin_query.opusername

                companyexpiredate = company.companyexpiredate

                if companyexpiredate:
                    request_create_time_chuo = int(time.mktime(companyexpiredate.timetuple()))
                else:
                    request_create_time_chuo = None

                companyinfo_dict['admin'] = admin_username
                companyinfo_dict['companyname'] = company.companyname
                companyinfo_dict['companyid'] = company.companyid
                companyinfo_dict['companyrole'] = company.companyrole
                companyinfo_dict['companyexpiredate'] = request_create_time_chuo
                companylist.append(companyinfo_dict)
            if companyname is None:
                db.session.close()
                return {'status': 0, 'companys': companylist,'msg': "查询成功"}
            else:
                mohu_query_list = []
                for search_company in companylist:
                    print(search_company)
                    search_company_status = search_company['companyname']
                    if search_company_status.find(companyname) != -1:
                        print('hhhhhhhhhhhhhhhhh')
                        mohu_query_list.append(search_company)
                db.session.close()
                return {'status': 0, 'companys': mohu_query_list, 'msg': "查询成功"}


    except sqlalchemy.exc.OperationalError:
        return {'Oooops': '数据库连接似乎出了问题'}

def company_insert(email, username, companyname, userid, token):
    try:
        #2 代表邮箱为空
        #3 代表用户名为空
        #4 代表公司名称为空
        #5 该公司已经被注册

        print(len(companyname))

        if token != '11111':
            return {'status': 1, 'msg': 'token不可用'}

        if len(companyname) > 32:
            return {'status': 6, 'msg': '公司名称不符合长度要求，公司名称应在36字以内'}
        elif len(email)== 0:
            return {'status': 2, 'msg': '请先填写邮箱'}
        elif len(username) == 0:
            return {'status': 3, 'msg': '请先填写用户名'}
        elif len(companyname) ==0:
            return {'status':4, 'msg':'请先填写公司名称'}
        verification_company = Company.query.filter_by(companyname=companyname).first()

        if verification_company:
            db.session.close()
            return {'status': 5, 'msg': '该公司已被注册'}
        else:
            companyid = 'c' + generate_random_str(24)
            user_query = User.query.filter_by(userid=userid).first()
            user_query.role = '0'
            user_mobile = user_query.mobile
            db.session.commit()

            insert_company = Company(companyid=companyid, companyname=companyname, companyrole='1')
            insert_opuser = Opuser(opusername=username, opuserid=userid,
                                   opmobile=user_mobile,opcompanyid=companyid,
                                   default='true', oprole='4', opemail=email,
                                   )
            db.session.add(insert_company)
            db.session.add(insert_opuser)
            db.session.commit()
            chatbotinfo = insert_chatbot(companyid)
            db.session.close()
            return {'status': 0, 'msg': '公司创建成功','chatbotinfo':chatbotinfo,
                    'companyid':companyid,'mobile':user_mobile,
                    'companyexpiredate':None,
                    'email': email, 'username': username,
                    'companyname': companyname,'companyrole':'1',
                    'oprole': '4','role': '0'}
    except sqlalchemy.exc.OperationalError:
        return {'Oooops': '数据库连接似乎出了问题'}

def join_company(userid, companyid, username , token):
    try:
        if token != '11111':
            return {'status': 1, 'msg': 'token 不可用'}
        request_userid = userid
        join_company = User.query.filter_by(userid=request_userid).first()
        mobile = join_company.mobile
        join_exsitcheck = Topic.query.filter_by(request_userid=request_userid,companyid=companyid).first()

        if join_exsitcheck:
            join_exsitcheck_admin_action = join_exsitcheck.admin_action
            if join_exsitcheck_admin_action == '2' or join_exsitcheck_admin_action == '0':
                db.session.close()
                return {'status': '4', 'msg': '不能重复申请'}

            if join_exsitcheck_admin_action == '1':
                join_exsitcheck.admin_action = '2'
                check_user_role_query = User.query.filter_by(userid=userid).first()
                if check_user_role_query.role == '1':
                    check_user_role_query.role = '2'

                insert_opuserinfo = Opuser(opusername=username, opcompanyid=companyid,
                                        opmobile=mobile, opuserid=request_userid,
                                        oprole='2')
                db.session.add(insert_opuserinfo)
                db.session.commit()
                db.session.close()
                return {'status': '5', 'msg': '已经再次发出请求'}

        check_opusername_list = []
        check_opusername_querys = Opuser.query.filter_by(opcompanyid=companyid).all()
        for check_opusername_query in check_opusername_querys:
            check_opusername = check_opusername_query.opusername
            check_opusername_list.append(check_opusername)

        init_username = username
        for i in range(1, 100):
            print(i)
            if username in check_opusername_list:
                username = init_username
                username = username + str(i)
                print('hehehe', username)
            else:
                break

        print(username)



        user_join_company = Opuser.query.filter_by(opuserid=request_userid, opcompanyid=companyid).first()
        if user_join_company:
            db.session.close()
            return {'status': '2', 'msg': '用户已存在'}
        else:
            if join_company.role == '1':
                join_company.role = '2'
            else:
                pass

            user_mobile_join_company = Opuser.query.filter_by(opmobile=mobile, opcompanyid=companyid).first()
            if user_mobile_join_company:
                user_mobile_join_company.opuserid = userid
                db.session.commit()
            else:
                insert_companyinfo = Opuser(opusername=username, opcompanyid=companyid,
                                        opmobile=mobile, opuserid=request_userid,
                                        oprole='2')
                db.session.add(insert_companyinfo)
                db.session.commit()

            admin_userid_query = Opuser.query.filter_by(opcompanyid=companyid, oprole='4').first()
            topic_admin_userid = admin_userid_query.opuserid
            insert_topic = Topic(admin_userid=topic_admin_userid, request_username=username,
                                 request_mobile=mobile,request_userid=request_userid,
                                 admin_action='2', companyid=companyid)
            db.session.add(insert_topic)
            db.session.commit()
            db.session.close()
            return {'status': '0', 'msg': '申请成功', 'role': '2','oprole':'2'}

    except sqlalchemy.exc.OperationalError:
        return {'Oooops': 'There is a problem with the database'}

def leave_company(usertoken, userid, companyid):
    try:
        if usertoken != '11111':
            return {'status': 1, 'msg': 'token 不可用'}
        leave_company_query = Opuser.query.filter_by(opuserid=userid, opcompanyid=companyid).first()
        leave_topic_query = Topic.query.filter_by(request_userid=userid, companyid=companyid).first()
        if leave_company_query:
            if leave_company_query.oprole != '4':
                leave_company_query.query.filter_by(opuserid=userid, opcompanyid=companyid).delete()
                if leave_topic_query:
                    leave_topic_query.query.filter_by(request_userid=userid, companyid=companyid).delete()
                leave_company_query2 = Opuser.query.filter_by(opuserid=userid).first()
                if leave_company_query2 is None:
                    leave_user_query2 = User.query.filter_by(userid=userid).first()
                    leave_user_query2.role = 1
                db.session.commit()
                db.session.close()
                return {'status': 0, 'msg': '您已退出该公司'}
            else:
                db.session.close()
                return {'status': 2, 'msg': '管理员无法退出公司'}
        else:
            db.session.close()
            return {'status': 3, 'msg': '无法找到相关用户'}

    except sqlalchemy.exc.OperationalError:
        return {'Oooops': 'There is a problem with the database'}

def join_info(userid, token, companyid):
    try:

        if token != '11111':
            return {'status': 1, 'msg': 'token 不可用'}
        join_info = Opuser.query.filter_by(opuserid=userid, opcompanyid=companyid).first()
        if join_info.oprole != '4':
            db.session.close()
            return {'status': 2, 'msg': '没有权限查看此页面'}
        else:
            admin_user_query = Topic.query.filter_by(admin_userid=userid, companyid=companyid).all()

            if admin_user_query:
                admin_user_list = []
                for admin_user in admin_user_query:
                    admin_user_dict = {}
                    print(admin_user.request_userid, userid)
                    request_create_time = admin_user.createtime
                    request_create_time_chuo = time.mktime(request_create_time.timetuple())
                    admin_user_dict['request_username'] = admin_user.request_username
                    admin_user_dict['request_mobile'] = admin_user.request_mobile
                    admin_user_dict['request_userid'] = admin_user.request_userid
                    admin_user_dict['request_companyid'] = admin_user.companyid
                    request_user_request_img_query = User.query.filter_by(userid=admin_user.request_userid).first()
                    print(request_user_request_img_query.mobile)
                    request_user_request_imgurl = request_user_request_img_query.profile
                    admin_user_dict['request_createtime'] = int(request_create_time_chuo)
                    admin_user_dict['admin_action'] = admin_user.admin_action
                    admin_user_dict['request_img'] = request_user_request_imgurl
                    admin_user_list.append(admin_user_dict)

                daoxu_admin_user_list = admin_user_list[::-1]
                db.session.close()
                return {'status': 0, 'msg': 'success', 'info': daoxu_admin_user_list}
            else:
                return {'status': 3, 'msg': '暂无申请记录。'}

    except sqlalchemy.exc.OperationalError:
        return {'Oooops': 'There is a problem with the database'}

def sidebar_get(userid, token):
    try:

        if token != '11111':
            return {'status': 1, 'msg': 'token 不可用'}
        #用户为游客返回的数据
        sidebar_get = User.query.filter_by(userid=userid).first()
        user_mark = sidebar_get.mark
        if user_mark == "userdisabled":
            return {'status': 10, 'msg': '用户已被禁用'}
        query_role = sidebar_get.role
        query_mobile = sidebar_get.mobile
        query_username = sidebar_get.username
        if query_role == '1':
            check_action_role_query = Topic.query.filter_by(request_userid=userid, admin_action='1').first()
            if check_action_role_query:
                rolers = {'status': 0, 'msg': '查询成功', 'username': query_username,
                 'companyname': None, 'companyid': None,
                 'companyrole': None, 'mobile': query_mobile, 'role': '3'}
            else:
                rolers = {'status': 0, 'msg': '查询成功','username': query_username,
                    'companyname':None,'companyid':None,
                    'companyrole': None,'mobile':query_mobile,'role':query_role}
            db.session.close()
            return rolers
        #用户已申请公司返回的数据
        if query_role == '2':
#            check_action_allrole_list_query = Topic.query.filter_by(request_userid=userid).all()
#            for check_action_allrole_query in check_action_allrole_list_query:
#                if check_action_allrole_query.admin_action != '1':
#                    print(check_action_allrole_query.companyid)
#                    print(check_action_allrole_query.request_userid)
#                    check_action_status = 'haveother'
#                    check_action_status_companyid = check_action_allrole_query.companyid
#                    break
#                else:
#                    check_action_status = 'havenoone'

#            if check_action_status == 'haveother':
#                opusercompanyid = check_action_status_companyid
#                action_role = query_role
#            else:
            opuserinfo_list_query = Opuser.query.filter_by(opuserid=userid, oprole='2').first()
            if opuserinfo_list_query:
                opusercompanyid = opuserinfo_list_query.opcompanyid
                #check_action_allrole_list_query = Topic.query.filter_by(request_userid=userid, companyid=opusercompanyid).first()
                action_role = '2'
                opcompanyinfo_query = Company.query.filter_by(companyid=opusercompanyid).first()
                opcompanyname = opcompanyinfo_query.companyname
                opcompanyrole = opcompanyinfo_query.companyrole
                opcompanyexpiredate = opcompanyinfo_query.companyexpiredate
                query_oprole_query = Opuser.query.filter_by(opuserid=userid).first()
                query_oprole = query_oprole_query.oprole
                check_action_role_query = Topic.query.filter_by(companyid=opusercompanyid, request_userid=userid).first()
                #check_action_role = check_action_role_query.admin_action
                rs = {'status': 0, 'msg': '查询成功','username': query_username,
                    'companyname':opcompanyname,'companyid':opusercompanyid,
                    'companyrole': opcompanyrole,'mobile':query_mobile,
                    'oprole':query_oprole,'role':action_role}
            else:
                rs = {'status': 0, 'msg': '查询成功', 'username': query_username,
                    'companyname': None, 'companyid': None,
                    'companyrole': None, 'mobile': query_mobile, 'role': '3'}

            db.session.close()
            return rs

        query_oprole_query = Opuser.query.filter_by(opuserid=userid, default='true').first()
        if query_oprole_query:
            query_oprole = query_oprole_query.oprole
        else:
            return {'status': 2, 'msg': '用户不存在默认公司，请先选择默认公司'}
        #用户是普通运维用户返回的数据
        if query_role == '0' and query_oprole == '3':
            opuserinfo_query = Opuser.query.filter_by(opuserid=userid, oprole='3', default='true').first()
            if opuserinfo_query:
                opusercompanyid = opuserinfo_query.opcompanyid
                opcompanyinfo_query = Company.query.filter_by(companyid=opusercompanyid).first()
                opcompanyname = opcompanyinfo_query.companyname
                opusername = opuserinfo_query.opusername
                opcompanyrole = opcompanyinfo_query.companyrole
                opcompanyexpiredate = opcompanyinfo_query.companyexpiredate
                if opcompanyexpiredate:
                    request_create_time_chuo = int(time.mktime(opcompanyexpiredate.timetuple()))
                else:
                    request_create_time_chuo = None
                db.session.close()
                return {'status': 0, 'msg': '查询成功', 'username': opusername,
                        'companyname': opcompanyname, 'companyid': opusercompanyid,
                        'companyrole': opcompanyrole, 'mobile': query_mobile,
                        'oprole':query_oprole,'role': query_role,'companyexpiredate':request_create_time_chuo}

        #用户是审核员返回的数据
        if query_role == '0' and query_oprole == '6':
            opuserinfo_query = Opuser.query.filter_by(opuserid=userid, oprole='6', default='true').first()
            if opuserinfo_query:
                opusercompanyid = opuserinfo_query.opcompanyid
                opcompanyinfo_query = Company.query.filter_by(companyid=opusercompanyid).first()
                opcompanyname = opcompanyinfo_query.companyname
                opusername = opuserinfo_query.opusername
                opcompanyrole = opcompanyinfo_query.companyrole
                opcompanyexpiredate = opcompanyinfo_query.companyexpiredate
                if opcompanyexpiredate:
                    request_create_time_chuo = int(time.mktime(opcompanyexpiredate.timetuple()))
                else:
                    request_create_time_chuo = None
                db.session.close()
                return {'status': 0, 'msg': '查询成功', 'username': opusername,
                        'companyname': opcompanyname, 'companyid': opusercompanyid,
                        'companyrole': opcompanyrole, 'mobile': query_mobile,
                        'oprole':query_oprole,'role': query_role, 'companyexpiredate':request_create_time_chuo}
            else:
                db.session.close()
                return {'status': 2, 'msg': '用户不存在默认公司，请先选择默认公司'}


        #用户为管理员返回的数据
        if query_role == '0' and query_oprole == '4':
            opuserinfo_query = Opuser.query.filter_by(opuserid=userid, oprole='4', default='true').first()
            if opuserinfo_query:
                opusercompanyid = opuserinfo_query.opcompanyid
                opcompanyinfo_query = Company.query.filter_by(companyid=opusercompanyid).first()
                opcompanyname = opcompanyinfo_query.companyname
                opcompanyrole = opcompanyinfo_query.companyrole
                opusername = opuserinfo_query.opusername
                opcompanyexpiredate = opcompanyinfo_query.companyexpiredate
                if opcompanyexpiredate:
                    request_create_time_chuo = int(time.mktime(opcompanyexpiredate.timetuple()))
                else:
                    request_create_time_chuo = None
                admin_user_query = Topic.query.filter_by(admin_userid=userid).all()
                admin_user_list = []
                for admin_user in admin_user_query:
                    if admin_user.admin_action == '2':
                        admin_user_list.append(admin_user)
                admin_user_listlen = len(admin_user_list)
                companymember_query = Opuser.query.filter_by(opcompanyid=opusercompanyid).all()

                companymember_list = []
                for companymember in companymember_query:
                    if companymember.oprole !='2' and companymember.oprole !='5':
                        companymember_list.append(companymember)

                print(companymember_list)
                db.session.close()
                return {'status': 0, 'msg': 'success', 'username':opusername,
                        'companyname':opcompanyname,'companyid':opusercompanyid,
                        'companyrole': opcompanyrole,'mobile':query_mobile,'role':query_role,
                        'oprole':query_oprole,'companyexpiredate':request_create_time_chuo,
                        'joinlist': admin_user_listlen, 'memberlist': len(companymember_list)}
            else:
                db.session.close()
                return {'status': 2, 'msg': '用户不存在默认公司，请先选择默认公司'}


    except sqlalchemy.exc.OperationalError:
        return {'Oooops': 'There is a problem with the database'}

def join_update(userid, token, request_userid, admin_action, request_companyid):
    try:

        if token != '11111':
            return {'status': 1, 'msg': 'token 不可用'}
        opjoin_info = Opuser.query.filter_by(opuserid=userid).first()

        if opjoin_info.oprole != '4':
            db.session.close()
            return {'status': 2, 'msg': '没有权限查看此页面'}

        join_info_query = Topic.query.filter_by(admin_userid=userid, request_userid=request_userid, companyid=request_companyid).first()

        if admin_action == '1':
            join_info_query.admin_action = '1'
            check_user_role_query = User.query.filter_by(userid=request_userid).first()

            delete_reject_opuser_query = Opuser.query.filter_by(opuserid=request_userid, opcompanyid=request_companyid).first()
            if delete_reject_opuser_query:
                delete_reject_opuser_query.query.filter_by(opuserid=request_userid, opcompanyid=request_companyid).delete()

            check_opuser_role_query = Opuser.query.filter_by(opuserid=request_userid).first()
            if check_user_role_query.role == '2' and check_opuser_role_query is None:
                check_user_role_query.role = '1'
            db.session.commit()
            db.session.close()
            return {'status': 0, 'msg': '已经拒绝'}
        if admin_action == '0':
            join_info_query.admin_action = '0'
            request_userinfo = User.query.filter_by(userid=request_userid).first()
            if request_userinfo.role != '0':
                request_userinfo.role = '0'
            request_username = request_userinfo.username
            request_mobile = request_userinfo.mobile
            request_join_info = Opuser.query.filter_by(opuserid=request_userid, opcompanyid=request_companyid).first()

            request_join_info.oprole = '3'
            db.session.commit()
            db.session.close()
            return {'status': 0, 'msg': '已经同意', 'request_username': request_username,
                    'request_mobile':request_mobile, 'admin_action':admin_action}
        else:
            return {'status': 4, 'msg': 'Ooooops , 无法识别状态码'}

    except sqlalchemy.exc.OperationalError:
        return {'Oooops': 'There is a problem with the database'}


def opusers(userid, token, companyid):
    try:
        print(userid, companyid)
        if token != '11111':
            return {'status': 1, 'mgs': 'token不可用'}
        user_query = User.query.filter_by(userid=userid).first()

        user_role = user_query.role
        if user_role == '1' or user_role == '2':
            db.session.close()
            return {'status': 3, 'msg': ""}
        user_check_query = Opuser.query.filter_by(opuserid=userid, opcompanyid=companyid).first()
        if user_check_query is None:
            db.session.close()
            return {'status': 4, 'msg':"用户id不能匹配用户公司id"}
        if user_check_query.oprole == '2':
            db.session.close()
            return {'status': 3, 'msg': "没有权限查看此页面"}
        users_query = Opuser.query.filter_by(opcompanyid=companyid).all()
        opuser_list = []
        for user_query in users_query:
            opuser_dict = {}
            if user_query.oprole != '5' and user_query.oprole != '2':
                opuser_dict['oprole'] = user_query.oprole
                opusermobile = user_query.opmobile
                opuserinfo_query = User.query.filter_by(mobile=opusermobile).first()
                print('hahahahahahahahahahah')
                if opuserinfo_query:
                    print(opuserinfo_query)
                    opuserid = opuserinfo_query.userid
                    opuser_dict['imageUrl'] = opuserinfo_query.profile
                    opuser_dict['role'] = opuserinfo_query.role
                    opuser_dict['opmobile'] = user_query.opmobile
                    opuser_dict['opusername']  = user_query.opusername
                    opuser_dict['userid'] = opuserid
                    opuser_dict['opcompanyid'] = companyid
                    opuser_dict['userstatus'] = user_query.userstatus
                    opuser_list.append(opuser_dict)
                else:
                    opuser_dict['imageUrl'] = 'http://139.196.107.14:6001/upload/2018-11-12/qMWML0jLCnhs2o1Nv6a5ajpr-defaultUser@3x.png'
                    opuser_dict['role'] = '0'
                    opuser_dict['opmobile'] = user_query.opmobile
                    opuser_dict['opusername'] = user_query.opusername
                    opuser_dict['userid'] = None
                    opuser_dict['opcompanyid'] = companyid
                    opuser_dict['userstatus'] = user_query.userstatus
                    opuser_list.append(opuser_dict)

        db.session.close()
        return {'status': 0, 'msg': '查询成功', 'info': opuser_list}

    except sqlalchemy.exc.OperationalError:
        db.session.close()
        return {'status':5, 'Oooops': 'There is a problem with the database'}

def opuser(userid, token, username, companyid):
    try:
        if token != '11111':
            return {'status': 1, 'msg': 'Token无效'}
        user_query = User.query.filter_by(userid=userid).first()

        user_role = user_query.role
        if user_role == '1' or user_role == '2':
            db.session.close()
            return {'status': 3, 'msg': "没有权限查看此页面"}
        user_check_query = Opuser.query.filter_by(opuserid=userid, opcompanyid=companyid).first()
        if user_check_query is None:
            db.session.close()
            return {'status': 4, 'msg':"用户id不能匹配用户公司id"}
        if user_check_query.oprole == '2':
            db.session.close()
            return {'status': 3, 'msg': "没有权限查看此页面"}

        opusers_query = Opuser.query.filter_by(opcompanyid=companyid).all()

        opuser_list = []
        for opuser_query in opusers_query:
            opuser_dict = {}
            if opuser_query.oprole != '5' and opuser_query.oprole != '2':
                opuserrole = opuser_query.oprole
                opusername = opuser_query.opusername
                opuserid = opuser_query.opuserid
                opusercompanyid = opuser_query.opcompanyid
                user_query = User.query.filter_by(userid=opuserid).first()
                if opusername.find(username) != -1 and user_query:
                    opuser_dict['opusername'] = opusername
                    opuser_dict['imageUrl'] = user_query.profile
                    opuser_dict['oprole'] = opuserrole
                    opuser_dict['role'] = user_query.role
                    opuser_dict['opmobile'] = opuser_query.opmobile
                    opuser_dict['userid'] = opuserid
                    opuser_dict['opcompanyid'] = companyid
                    opuser_dict['userstatus'] = opuser_query.userstatus
                    opuser_list.append(opuser_dict)
                if opusername.find(username) != -1 and user_query is None:
                    opuser_dict['opusername'] = opusername
                    opuser_dict['imageUrl'] = 'http://139.196.107.14:6001/upload/2018-11-12/qMWML0jLCnhs2o1Nv6a5ajpr-defaultUser@3x.png'
                    opuser_dict['oprole'] = opuserrole
                    opuser_dict['role'] = '1'
                    opuser_dict['opmobile'] = opuser_query.opmobile
                    opuser_dict['userid'] = None
                    opuser_dict['opcompanyid'] = companyid
                    opuser_dict['userstatus'] = opuser_query.userstatus
                    opuser_list.append(opuser_dict)
        db.session.close()
        return {'status': 0, 'msg': '查询成功', 'info': opuser_list}


    except sqlalchemy.exc.OperationalError:
        db.session.close()
        return {'status':3, 'Oooops': 'There is a problem with the database'}


def addopuser(adminuserid, usertoken, opusername, opmobile, admincompanyid):
    try:
        if usertoken != '11111':
            return {'status': 1, 'msg': 'Token无效'}
        opuser_check_mobile = Opuser.query.filter_by(opmobile=opmobile,opcompanyid=admincompanyid).first()

        if opuser_check_mobile:
            db.session.close()
            return {'status': 6, 'msg': '手机号码已存在'}

        adminopuserquery = Opuser.query.filter_by(opuserid=adminuserid,opcompanyid=admincompanyid,oprole='4').first()

        if adminopuserquery is None:
            db.session.close()
            return {'status': 5, 'msg': '用户无权限'}

        if len(opusername) > 12:
            db.session.close()
            return {'status':4, 'msg':'用户名长度不符合要求，用户名应在12字以内'}
        elif opmobile == 'null':
            db.session.close()
            return {'status': 2, 'msg': '手机号码不能为空'}
        elif phonecheck(opmobile) == 'failure':
            db.session.close()
            return {'status': 3, 'msg': '请输入正确的手机号码'}

        addopusermobile_check = User.query.filter_by(mobile=opmobile).first()
        if addopusermobile_check:
            addopusermobile_check_userid = addopusermobile_check.userid
            insert_opuser = Opuser(opmobile=opmobile, oprole='3',opuserid=addopusermobile_check_userid,
                                   opusername=opusername, opcompanyid=admincompanyid,
                                   userstatus='register')
            addopusermobile_check.role = '0'                       
        else:
            insert_opuser = Opuser(opmobile=opmobile, oprole='3',
                               opusername=opusername, opcompanyid=admincompanyid,
                               userstatus='manual')

        db.session.add(insert_opuser)
        db.session.commit()
        db.session.close()
        return {'status': 0, 'msg': '添加成功'}
    except sqlalchemy.exc.OperationalError:
        db.session.close()
        return {'Oooops': 'There is a problem with the database'}


def deleteopuser(adminuserid, usertoken, opmobile, admincompanyid):
    try:
        if usertoken != '11111':
            return {'status': 1, 'msg': 'Token无效'}
        adminopuserquery = Opuser.query.filter_by(opuserid=adminuserid,opcompanyid=admincompanyid,oprole='4').first()

        if adminopuserquery is None:
            db.session.close()
            return {'status': 5, 'msg': '用户无权限'}
        else:
            adminmobile = adminopuserquery.opmobile
            if adminmobile == opmobile:
                db.session.close()
                return {'status': 3, 'msg': '无法删除管理员'}

        opuserinfo_query = Opuser.query.filter_by(opmobile=opmobile,opcompanyid=admincompanyid).first()
        if opuserinfo_query:
            opuserinfo_query.query.filter_by(opmobile=opmobile,opcompanyid=admincompanyid).delete()
            db.session.commit()
            db.session.close()
        else:
            db.session.close()
            return {'status': 2, 'msg': '找不到匹配用户'}

        opusercheck_query = Opuser.query.filter_by(opmobile=opmobile).first()
        if opusercheck_query:
            pass
        else:
            change_userrole = User.query.filter_by(mobile=opmobile).first()
            if change_userrole:
                change_userrole.role = '1'
                db.session.commit()
        join_exsitcheck = Topic.query.filter_by(admin_userid=adminuserid, request_mobile=opmobile,companyid=admincompanyid).delete()
        db.session.commit()
        db.session.close()
        return {'status': 0, 'msg': '删除成功'}

    except sqlalchemy.exc.OperationalError:
        db.session.close()
        return {'Oooops': 'There is a problem with the database'}
#    except:
#        db.session.rollback()
#        return {'status': 4, 'msg': 'something warong'}


def updateopuser(adminuserid, usertoken, opusername, opmobile, opuserid, opcompanyid):
    try:
        if usertoken != '11111':
            return {'status': 1, 'msg': 'Token无效'}

        if len(opusername) > 12:
            return {'status': 5, 'msg':'用户名长度不符合要求，用户名应在12字以内'}


        if opmobile == 'null':
            return {'status': 2, 'msg': '手机号码不能为空'}
        elif phonecheck(opmobile) == 'failure':
            return {'status': 3, 'msg': '请输入正确的手机号码'}
        admin_opuser_query = Opuser.query.filter_by(opuserid=adminuserid, opcompanyid=opcompanyid, oprole='4').first()
        if admin_opuser_query is None:
            db.session.close()
            return {'status': 4, 'msg': '没有权限'}
        else:
            opuser_query = Opuser.query.filter_by(opmobile=opmobile, opcompanyid=opcompanyid).first()
            if opuser_query:
                opuser_query.opusername = opusername
                opuser_query.opmobile = opmobile
            else:
                opuser_query = Opuser.query.filter_by(opusername=opusername, opcompanyid=opcompanyid).first()
                opuser_query.opusername = opusername
                opuser_query.opmobile = opmobile

            opusercheck_query = Opuser.query.filter_by(opmobile=opmobile).first()
            if opusercheck_query:
                pass
            else:
                change_userrole = User.query.filter_by(mobile=opmobile).first()
                if change_userrole:
                    change_userrole.role = '1'
                    db.session.commit()


            db.session.commit()
            db.session.close()
            return {'status': 0, 'msg': '修改成功'}
    except sqlalchemy.exc.OperationalError:
        db.session.close()
        return {'Oooops': 'There is a problem with the database'}

def updateopuserrole(usertoken, adminuserid, opuserid, oprole, opcompanyid):
    try:
        if usertoken != '11111':
            return {'status': 1, 'msg': 'Token无效'}
        admin_opuser_query = Opuser.query.filter_by(opuserid=adminuserid,opcompanyid=opcompanyid,oprole='4').first()

        if admin_opuser_query is None:
            db.session.close()
            return {'status': 3, 'msg': '没有权限'}

        if adminuserid == opuserid:
            db.session.close()
            return {'status': 4, 'msg': '无法更改管理员自身权限'}
        if opuserid is None:
            db.session.close()
            return {'status': 5, 'msg': '用户尚未关联公司，无法设置管理员或审核员权限'}

        if oprole == '6':
            companyusersrole6_query = Opuser.query.filter_by(opcompanyid=opcompanyid, oprole='6').all()

            companyusersrole6s = len(companyusersrole6_query)
            if companyusersrole6s >= 3:
                db.session.close()
                return  {'status': 6, 'msg': '一个公司最多只能设置3个审核员'}
            else:
                opuserrole_change_query = Opuser.query.filter_by(opuserid=opuserid, opcompanyid=opcompanyid).first()
                if opuserrole_change_query:
                    opuserrole_change_query.oprole = '6'
                    db.session.commit()
        if oprole == '4':
            opuser_query = Opuser.query.filter_by(opuserid=opuserid, opcompanyid=opcompanyid).first()
            if opuser_query:
                opuser_query.oprole = '4'
                admin_opuser_query.oprole = '3'
                db.session.commit()
        if oprole == '3':
            opuser_query = Opuser.query.filter_by(opuserid=opuserid, opcompanyid=opcompanyid).first()
            if opuser_query:
                opuser_query.oprole = '3'
                db.session.commit()
        db.session.close()
        return {'status': 0, 'msg': '修改成功'}

    except sqlalchemy.exc.OperationalError:
        return {'Oooops': 'There is a problem with the database'}

def updateopuserdefaultcompany(usertoken, opuserid, opcompanyid):
    try:
        if usertoken != '11111':
            return {'status': 1, 'msg': 'Token无效'}
        admin_opuser_query = Opuser.query.filter_by(opuserid=opuserid,opcompanyid=opcompanyid).first()
        admin_opuser_query.default = 'true'
        opuser_company_default_querys = Opuser.query.filter_by(opuserid=opuserid, opcompanyid=opcompanyid, default='true').first()
        opusercompanyid_default = opuser_company_default_querys.opcompanyid
        opuseremail_default = opuser_company_default_querys.opemail
        opusercompanyinfo_default = Company.query.filter_by(companyid=opusercompanyid_default).first()
        opusercompanyname_default = opusercompanyinfo_default.companyname
        opusercompanyrole_default = opusercompanyinfo_default.companyrole
        opusercompanyexpire_default = opusercompanyinfo_default.companyexpiredate
        opmobile = opuser_company_default_querys.opmobile
        oprole = opuser_company_default_querys.oprole
        opusername = opuser_company_default_querys.opusername

        userinfo = User.query.filter_by(userid=opuserid).first()
        user_profile = userinfo.profile
        mobile = userinfo.mobile
        userinfo.role = '0'
        user_id = opuserid
        user_name = userinfo.username
        db.session.commit()
        db.session.close()
        return {
            "companyexpiredate": opusercompanyexpire_default,
            "companyid": opusercompanyid_default,
            "companyname": opusercompanyname_default,
            "companyrole": opusercompanyrole_default,
            "email": opuseremail_default,
            "imageUrl": user_profile,
            "opmobile": opmobile,
            "mobile": mobile,
            "msg": "登录成功",
            "role": '0',
            "oprole": oprole,
            "status": 0,
            "token": user_id + "-11111",
            "userid": user_id,
            "username": user_name,
            "opusername": opusername,

        }

    except sqlalchemy.exc.OperationalError:
        return {'Oooops': 'There is a problem with the database'}
