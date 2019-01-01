from model import *
import sqlalchemy
from datetime import datetime, timedelta
import time
from urllib.parse import unquote


def backstage(userid, token):
    if token != '11111':
        return {'status':1, 'msg':'token不可用'}

    #公司总数量
    companys_query = Company.query.all()
    totalcompanys = len(companys_query)

    #当天新增公司数量
    todays_datetime = datetime(datetime.today().year, datetime.today().month, datetime.today().day)
    #todays_datetime = '2018-10-30 00:00:00'
    newcompanys_query = Company.query.filter(Company.createtime >= todays_datetime).all()
    newcompanys = len(newcompanys_query)

    #试用中的公司
    try_companys_query = Company.query.filter_by(companyrole='1').all()
    try_companys = len(try_companys_query)

    #用户总数量
    users_query = User.query.all()
    totalusers = len(users_query)

    #当天新增用户
    newusers_query = User.query.filter(User.createtime >= todays_datetime).all()
    newusers = len(newusers_query)

    backstage_expiredate_query = Backstage.query.first()
    backstage_expiredate = backstage_expiredate_query.companyexpire
    expire_date = todays_datetime + timedelta(days=int(backstage_expiredate))
    try_expire_companys_query = Company.query.filter(Company.companyexpiredate <= expire_date, Company.companyexpiredate >= todays_datetime, Company.companyrole == '2').all()
    expire_companys = len(try_expire_companys_query)
    rs = {'total_companys': totalcompanys, 'new_companys': newcompanys,
          'try_companys': try_companys,'total_users':totalusers,
          'new_users': newusers, 'expiring_companys':expire_companys,
          }
    return rs


def backstagecms(userid, token):
    if token != '11111':
        return {'status':1, 'msg':'token不可用'}

    #公司总数量
    rs_query_list = []
    rs_query_dict = {}
    companys_query = Company.query.all()
    for company_query in companys_query:
        companyid = company_query.companyid
        companyname = company_query.companyname
        companyexpire = company_query.companyexpiredate
        companymark = company_query.companymark
        companyrole = company_query.companyrole
        user_query = Opuser.query.filter_by(opcompanyid=companyid).all()
        totalcompanyusers = len(user_query)
        adminuser_query = Opuser.query.filter_by(opcompanyid=companyid, oprole='4').first()
        adminusername = adminuser_query.opusername
        adminmobile = adminuser_query.opmobile
        admimemail = adminuser_query.opemail

        if companyexpire:
            companyexpire = int(time.mktime(companyexpire.timetuple()))

        rs_query_dict = {'companyname': companyname, 'adminusername': adminusername,
          'adminmobile': adminmobile,'adminemail':admimemail,
          'companyexpire': companyexpire,'companymark':companymark,
            'companyrole':companyrole, 'members':totalcompanyusers,
          }
        rs_query_list.append(rs_query_dict)

    return rs_query_list

def backstagecm(userid, token, urlsearchcompanyname):
    if token != '11111':
        return {'status':1, 'msg':'token不可用'}

    searchcompanyname = unquote(urlsearchcompanyname, 'utf-8')
    #公司总数量
    rs_query_list = []
    rs_query_dict = {}
    companys_query = Company.query.all()
    for company_query in companys_query:
        companyid = company_query.companyid
        companyname = company_query.companyname
        if companyname.find(searchcompanyname) != -1:
            companyexpire = company_query.companyexpiredate
            companyrole = company_query.companyrole
            companymark = company_query.companymark
            user_query = Opuser.query.filter_by(opcompanyid=companyid).all()
            totalcompanyusers = len(user_query)
            adminuser_query = Opuser.query.filter_by(opcompanyid=companyid, oprole='4').first()
            adminusername = adminuser_query.opusername
            adminmobile = adminuser_query.opmobile
            admimemail = adminuser_query.opemail

            if companyexpire:
                companyexpire = int(time.mktime(companyexpire.timetuple()))

            rs_query_dict = {'companyname': companyname, 'adminusername': adminusername,
                'adminmobile': adminmobile,'adminemail':admimemail,
                'companyexpire': companyexpire,'companymark':companymark,
                'companyrole':companyrole, 'members':totalcompanyusers,
                }
            rs_query_list.append(rs_query_dict)

    return rs_query_list

def backstagetryouts(userid, token):
    if token != '11111':
        return {'status':1, 'msg':'token不可用'}

    #试用公司
    rs_query_list = []
    rs_query_dict = {}
    companys_query = Company.query.filter_by(companyrole='1').all()
    for company_query in companys_query:
        companyid = company_query.companyid
        companyname = company_query.companyname
        companyexpire = company_query.companyexpiredate
        companyrole = company_query.companyrole
        user_query = Opuser.query.filter_by(opcompanyid=companyid).all()
        totalcompanyusers = len(user_query)
        adminuser_query = Opuser.query.filter_by(opcompanyid=companyid, oprole='4').first()
        adminusername = adminuser_query.opusername
        adminmobile = adminuser_query.opmobile
        admimemail = adminuser_query.opemail

        if companyexpire:
            companyexpire = int(time.mktime(companyexpire.timetuple()))

        rs_query_dict = {'companyname': companyname, 'adminusername': adminusername,
          'adminmobile': adminmobile,'adminemail':admimemail,
          'companyexpire': companyexpire,
            'companyrole':companyrole, 'members':totalcompanyusers,
          }
        rs_query_list.append(rs_query_dict)

    return rs_query_list

def backstagecmdelete(token,companyid):

    try:
        if token != '11111':
            return {'status': 1, 'msg': 'token不可用'}

        company_query = Company.query.filter_by(companyid=companyid).first()
        opusers_query = Opuser.query.filter_by(opcompanyid=companyid).all()
        for opuser in opusers_query:
            companys_query = Opuser.query.filter_by(opuserid=opuser. opuserid).all()
            if len(companys_query) == 1:
                user_query = User.query.filter_by(userid=opuser.opuserid).first()
                user_query.role = 1
            db.session.delete(opuser)
        db.session.delete(company_query)
        db.session.commit()
        return {'status': 0, 'msg': '删除成功'}

    except sqlalchemy.exc.OperationalError:
        db.session.close()
        return {'Oooops': 'There is a problem with the database'}

def backstageexpiring(userid, token):
    if token != '11111':
        return {'status':1, 'msg':'token不可用'}

    #即将过期
    todays_datetime = datetime(datetime.today().year, datetime.today().month, datetime.today().day)
    print(todays_datetime)
    backstage_expiredate_query = Backstage.query.first()
    backstage_expiredate = backstage_expiredate_query.companyexpire
    print(backstage_expiredate)
    expire_date = todays_datetime + timedelta(days=int(backstage_expiredate))
    print(expire_date)
    try_expire_companys_query = Company.query.filter(Company.companyexpiredate <= expire_date, Company.companyexpiredate >= todays_datetime, Company.companyrole == '2').all()
    print(try_expire_companys_query)
    if try_expire_companys_query is None:
        return []
    rs_query_list = []
    rs_query_dict = {}
    for company_query in try_expire_companys_query:
        companyid = company_query.companyid
        companyname = company_query.companyname
        companyexpire = company_query.companyexpiredate
        companyrole = company_query.companyrole
        user_query = Opuser.query.filter_by(opcompanyid=companyid).all()
        totalcompanyusers = len(user_query)
        adminuser_query = Opuser.query.filter_by(opcompanyid=companyid, oprole='4').first()
        adminusername = adminuser_query.opusername
        adminmobile = adminuser_query.opmobile
        admimemail = adminuser_query.opemail

        if companyexpire:
            companyexpire = int(time.mktime(companyexpire.timetuple()))

        rs_query_dict = {'companyname': companyname, 'adminusername': adminusername,
          'adminmobile': adminmobile,'adminemail':admimemail,
          'companyexpire': companyexpire,
            'companyrole':companyrole, 'members':totalcompanyusers,
          }
        rs_query_list.append(rs_query_dict)

    return rs_query_list


def backstageexpired(userid, token):
    if token != '11111':
        return {'status':1, 'msg':'token不可用'}
    #已过期
    todays_datetime = datetime(datetime.today().year, datetime.today().month, datetime.today().day)
    try_expire_companys_query = Company.query.filter(Company.companyexpiredate <= todays_datetime, Company.companyrole == '2').all()
    if try_expire_companys_query is None:
        return []
    rs_query_list = []
    rs_query_dict = {}
    for company_query in try_expire_companys_query:
        companyid = company_query.companyid
        companyname = company_query.companyname
        companyexpire = company_query.companyexpiredate
        companyrole = company_query.companyrole
        user_query = Opuser.query.filter_by(opcompanyid=companyid).all()
        totalcompanyusers = len(user_query)
        adminuser_query = Opuser.query.filter_by(opcompanyid=companyid, oprole='4').first()
        adminusername = adminuser_query.opusername
        adminmobile = adminuser_query.opmobile
        admimemail = adminuser_query.opemail

        if companyexpire:
            companyexpire = int(time.mktime(companyexpire.timetuple()))

        rs_query_dict = {'companyname': companyname, 'adminusername': adminusername,
          'adminmobile': adminmobile,'adminemail':admimemail,
          'companyexpire': companyexpire,
            'companyrole':companyrole, 'members':totalcompanyusers,
          }
        rs_query_list.append(rs_query_dict)

    return rs_query_list


def backstageusers(adminuserid, token):
    if token != '11111':
        return {'status':1, 'msg':'token不可用'}

    #所有用户信息
    rs_query_list = []
    users_query = User.query.all()
    for user_query in users_query:
        userid = user_query.userid
        username = user_query.username
        usermobile = user_query.mobile
        userrole = user_query.role
        mark =  user_query.mark
        userlogintime = user_query.logintime
        if userlogintime:
            userlogintime = int(time.mktime(userlogintime.timetuple()))
        if username != 'chatbot' or usermobile.find('c') == -1:
            rs_query_dict = {'username': username, 'mobile': usermobile,
                'role': userrole,'logintime':userlogintime,'userid':userid,
                'mark':mark
                }
            rs_query_list.append(rs_query_dict)
    userinfo_list = []
    for userallinfo in rs_query_list:
        userinfo_dict = {}
        queryuserid = userallinfo['userid']
        companyinfos_query = Opuser.query.filter_by(opuserid=queryuserid).all()
        companyid_list = []
        userallinfo_dict = {}
        for companyinfo_query in companyinfos_query:
            companyid = companyinfo_query.opcompanyid
            companyid_list.append(companyid)
        companyname_list = []
        for companyid in companyid_list:
            companyinfos_query = Company.query.filter_by(companyid=companyid).first()
            companyname = companyinfos_query.companyname
            companyname_list.append(companyname)
        userinfo_dict['companynamelist'] = companyname_list
        userinfo_dict['userinfo'] = userallinfo
        userinfo_list.append(userinfo_dict)
    print(userinfo_list)

    return userinfo_list

def disabledUser(userid, token, disabled):
    if token != '11111':
        return {'status':1, 'msg':'token不可用'}
    #修改用户mark
    user_query = User.query.filter_by(userid=userid).first()
    if disabled:
        user_query.mark = disabled

    db.session.commit()

    rs = {'status':0, 'msg':'设置成功','disabled':disabled}
    return rs

def disabledCompany(companyid, token, disabled):
    if token != '11111':
        return {'status':1, 'msg':'token不可用'}
    #修改用户mark
    company_query = Company.query.filter_by(companyid=companyid).first()
    if disabled:
        company_query.mark = disabled

    db.session.commit()

    rs = {'status':0, 'msg':'设置成功','disabled':disabled}
    return rs

def configsGet(userid, token):
    if token != '11111':
        return {'status':1, 'msg':'token不可用'}
    #获取配置
    backstageinfo_query = Backstage.query.first()
    backstageinfo_expire = backstageinfo_query.companyexpire
    backstageinfo_tryoutdate = backstageinfo_query.tryoutdata
    backstageinfo_custom = backstageinfo_query.customerservicemobile
    rs = {'expire':backstageinfo_expire, 'trydate':backstageinfo_tryoutdate, 'customerservice':backstageinfo_custom}
    return rs


def configsChange(userid, token, customerservice, expire, trydate):
    if token != '11111':
        return {'status':1, 'msg':'token不可用'}
    #修改后台配置
    backstageinfo_query = Backstage.query.first()
    if customerservice:
        backstageinfo_query.customerservicemobile = customerservice
    if expire:
        backstageinfo_query.companyexpire = expire
    if trydate:
        backstageinfo_query.tryoutdata = trydate
    db.session.commit()

    rs = {'status':0, 'msg':'设置成功','expire':expire, 'trydate':trydate, 'customerservice':customerservice}
    return rs

def coustomMobile(userid, token):
    if token != '11111':
        return {'status':1, 'msg':'token不可用'}
    #修改后台配置
    backstageinfo_query = Backstage.query.first()
    if backstageinfo_query:
        custommobile = backstageinfo_query.customerservicemobile

    rs = {'status':0, 'msg':'查询成功','customermobile':custommobile}
    return rs

def pageUsers(token, page):
    if token != '11111':
        return {'status':1, 'msg':'token不可用'}

    #所有用户信息
    rs_query_list = []
    #users_query = User.query.all()
    page = int(page)
    users_query = User.query.order_by(User.createtime.desc()).paginate(page, per_page=10, error_out = False)
    users_page_query = users_query.items
    for user_query in users_page_query:
        userid = user_query.userid
        username = user_query.username
        usermobile = user_query.mobile
        userrole = user_query.role
        userlogintime = user_query.logintime
        if userlogintime:
            userlogintime = int(time.mktime(userlogintime.timetuple()))
        if username != 'chatbot' or usermobile.find('c') == -1:
            rs_query_dict = {'username': username, 'mobile': usermobile,
                'role': userrole,'logintime':userlogintime,'userid':userid,
                }
            rs_query_list.append(rs_query_dict)
    userinfo_list = []
    for userallinfo in rs_query_list:
        userinfo_dict = {}
        queryuserid = userallinfo['userid']
        companyinfos_query = Opuser.query.filter_by(opuserid=queryuserid).all()
        companyid_list = []
        userallinfo_dict = {}
        for companyinfo_query in companyinfos_query:
            companyid = companyinfo_query.opcompanyid
            companyid_list.append(companyid)
        companyname_list = []
        for companyid in companyid_list:
            companyinfos_query = Company.query.filter_by(companyid=companyid).first()
            companyname = companyinfos_query.companyname
            companyname_list.append(companyname)
        userinfo_dict['companynamelist'] = companyname_list
        userinfo_dict['userinfo'] = userallinfo
        userinfo_list.append(userinfo_dict)
    print(userinfo_list)

    return userinfo_list



def pageCompanys(token, page):
    if token != '11111':
        return {'status':1, 'msg':'token不可用'}
    rs_query_list = []
    page = int(page)
    companys_query = Company.query.order_by(Company.createtime.desc()).paginate(page, per_page=10, error_out = False)
    companys_page_query = companys_query.items
    for company_query in companys_page_query:
        companyid = company_query.companyid
        companyname = company_query.companyname
        companyexpire = company_query.companyexpiredate
        companyrole = company_query.companyrole
        user_query = Opuser.query.filter_by(opcompanyid=companyid).all()
        totalcompanyusers = len(user_query)
        adminuser_query = Opuser.query.filter_by(opcompanyid=companyid, oprole='4').first()
        adminusername = adminuser_query.opusername
        adminmobile = adminuser_query.opmobile
        admimemail = adminuser_query.opemail

        if companyexpire:
            companyexpire = int(time.mktime(companyexpire.timetuple()))
        rs_query_dict = {'companyname': companyname, 'adminusername': adminusername,
          'adminmobile': adminmobile,'adminemail':admimemail,
          'companyexpire': companyexpire,
            'companyrole':companyrole, 'members':totalcompanyusers,
          }
        rs_query_list.append(rs_query_dict)

    return rs_query_list


def AdminInfo(username, password):
    #所有用户信息

    admin_query = Backstage.query.filter_by(rootname='root').first()
    adminpassword = admin_query.rootpassword
    if username == 'root' and password == adminpassword:
        return {'status':0, 'msg': '登录成功'}
    else:
        return {'status':1, 'msg':'用户名或密码错误'}
