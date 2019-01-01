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
    users_query = User.query.filter(
        User.mobile.like('1%')).all()
    totalusers = len(users_query)

    #当天新增用户
    newusers_query = User.query.filter(User.createtime >= todays_datetime, User.mobile.like('1%')).all()
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
    db.session.close()
    return rs

def AdminInfo(username, password):
    #所有用户信息

    admin_query = Backstage.query.filter_by(rootname='root').first()
    adminpassword = admin_query.rootpassword
    if username == 'root' and password == adminpassword:
        db.session.close()
        return {'status':0, 'msg': '登录成功', 'token':'xxx-11111'}
    else:
        db.session.close()
        return {'status':1, 'msg':'用户名或密码错误'}

def adminpatch(adminuserid, admintoken, oldpassword, newpassword):
    #所有用户信息
    if admintoken != '11111':
        return {'status':1, 'msg':'token不可用'}

    admin_query = Backstage.query.filter_by(rootname='root').first()
    adminpassword = admin_query.rootpassword
    if oldpassword == adminpassword:
        admin_query.rootpassword = newpassword
        db.session.commit()
        db.session.close()
        return {'status':0, 'msg': '修改成功'}
    else:
        db.session.close()
        return {'status':2, 'msg':'旧密码错误'}

def userdelete(adminuserid, adminusertoken, userid):
    try:
        if adminusertoken != '11111':
            return {'status':1, 'msg':'token不可用'}
        user_query = User.query.filter_by(userid=userid).first()
        db.session.delete(user_query)
        db.session.commit()
        return {'status':0, 'msg': '修改成功'}
    except sqlalchemy.exc.OperationalError:
        db.session.close()
        return {'Oooops': 'There is a problem with the database'}

def userdisable(adminuserid,adminusertoken,userstatus,userid):
    try:
        if adminusertoken != '11111':
            return {'status':1, 'msg':'token不可用'}
        user_query = User.query.filter_by(userid=userid).first()
        if userstatus:
            user_query.mark = userstatus
        db.session.commit()
        return {'status':0, 'msg': '修改成功'}
    except sqlalchemy.exc.OperationalError:
        db.session.close()
        return {'Oooops': 'There is a problem with the database'}
