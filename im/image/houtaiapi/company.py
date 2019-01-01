from model import *
from datetime import datetime, timedelta
import time
import requests, json
from urllib.parse import unquote
import math

url = apiserverurl + "/api/v1/hosts?token=xxx-11111"



headers = {'Content-Type': 'application/json-rpc'}

def auth(zabbixusername, zabbixpassword, zabbixurl):

    data = json.dumps(
    {
        "jsonrpc": "2.0",
        "method": "user.login",
        "params": {
            "user": zabbixusername,
            "password": zabbixpassword
        },
        "id": 0
    })

    authrs = requests.post(zabbixurl + '/zabbix/api_jsonrpc.php', data=data, headers=headers)
    token = authrs.json()['result']
    return token


def hostgroups(zabbixtoken, zabbixurl):
    data = json.dumps(
    {
        "jsonrpc":"2.0",
        "method":"hostgroup.get",
        "params":{
            "output":["groupid","name"],
        },
        "auth":zabbixtoken, # theauth id is what auth script returns, remeber it is string
        "id":1,
    })
    hostgroups = requests.post(zabbixurl + '/zabbix/api_jsonrpc.php', data=data, headers=headers)
    group_list = hostgroups.json()['result']
    return group_list

def zabbix_hosts_query(companyid):
        zabbixinfo_query = Zabbix.query.filter_by(companyid=companyid).first()
        if zabbixinfo_query is None:
            db.session.close()
            return {'status': 2, 'msg': '使用监控功能之前，需要先添加zabbix服务器'}
        zabbixusername = zabbixinfo_query.zabbixuser
        zabbixpassword = zabbixinfo_query.zabbixpassword
        zabbixurl = zabbixinfo_query.zabbixserver
        zabbixtoken = auth(zabbixusername, zabbixpassword, zabbixurl)

        group_list = hostgroups(zabbixtoken, zabbixurl)
        print(group_list)
        hostinfo_list = []
        for group in group_list:
            #hostinfo_dict = {}
            hostinfo_list.append(group['groupid'])
            #groupid = group['groupid']
            #groupname = group['name']
        print(hostinfo_list)
        data = json.dumps(
            {
                    "jsonrpc": "2.0",
                    "method": "host.get",
                    "params": {
                        "output": ["hostid", "name", "host"],
                        "groupids": hostinfo_list,
                    },
                    "auth": zabbixtoken,  # theauth id is what auth script returns, remeber it is string
                    "id": 1,
            })
        hosts = requests.post(zabbixurl + '/zabbix/api_jsonrpc.php', data=data, headers=headers)
        hosts_list =  hosts.json()['result']
        checkhosts_list = []
        for checkhost_dict in hosts_list:

            checkhostid = checkhost_dict['hostid']
            checkhost_query = Monitor.query.filter_by(zabbixhostid=checkhostid).first()
            if checkhost_query:
                checkhost_dict['hoststatus'] = 'in'
            else:
                checkhost_dict['hoststatus'] = 'out'
            checkhosts_list.append(checkhost_dict)

        allhostsnumber = len(checkhosts_list)
        inhostsnumber_query = Monitor.query.all()
        inhostsnumber = len(inhostsnumber_query)
        inhostinfo_list = []
        for inhost in inhostsnumber_query:
            inhostinfo_dict = {'hostid':inhost.zabbixhostid, 'host':inhost.zabbixhostip, 'name':inhost.zabbixhostname, 'hoststatus':'in'}
            inhostinfo_list.append(inhostinfo_dict)

        hosts_queryrs = {'status': 0, 'totalamount': allhostsnumber,
                         'inamount':inhostsnumber, 'totalhosts': checkhosts_list,
                         'inhosts':inhostinfo_list,
                         }
        db.session.close()
        return hosts_queryrs

def backstagecms(userid, token, page):
    if token != '11111':
        return {'status':1, 'msg':'token不可用'}

    #公司总数量
    rs_query_list = []
    page = int(page)

    companys_total_query = Company.query.all()
    companys_total =  len(companys_total_query) / 15
    page_total = math.ceil(companys_total)


    companys_query_page = Company.query.order_by(Company.createtime.desc()).paginate(page, per_page=15, error_out=False)
    companys_query = companys_query_page.items
    for company_query in companys_query:
        companyid = company_query.companyid
        zabbixhostinfo = zabbix_hosts_query(companyid)
        if zabbixhostinfo['status'] != 2:
            totalhost = len(zabbixhostinfo['totalhosts'])
        else:
            totalhost = None
        companyname = company_query.companyname
        companyexpire = company_query.companyexpiredate
        companyrole = company_query.companyrole
        user_query = Opuser.query.filter(Opuser.opcompanyid==companyid, Opuser.oprole!=2).all()
        totalcompanyusers = int(len(user_query)) - 1
        adminuser_query = Opuser.query.filter_by(opcompanyid=companyid, oprole='4').first()
        adminusername = adminuser_query.opusername
        defaultcompany = adminuser_query.default
        adminmobile = adminuser_query.opmobile
        companyemail = company_query.companyemail
        companymark = company_query.companymark
        if companyexpire:
            companyexpire = int(round(time.mktime(companyexpire.timetuple()) * 1000))

        rs_query_dict = {'companyid':companyid, 'companyname': companyname, 'adminusername': adminusername,
          'adminmobile': adminmobile,'adminemail':companyemail,
          'companyexpire': companyexpire,'totalhost':totalhost,
            'companyrole':companyrole, 'members':totalcompanyusers,
                         'companymark':companymark,'defaultcompany':defaultcompany
          }
        rs_query_list.append(rs_query_dict)
    db.session.close()
    return {"status":0,"msg":"查询成功",'pagetotal':page_total,"companyinfo": rs_query_list}


def backstagecm(userid, token, urlsearchcompanyname, page):
    if token != '11111':
        return {'status':1, 'msg':'token不可用'}

    searchcompanyname = unquote(urlsearchcompanyname, 'utf-8')
    #公司总数量
    rs_query_list = []
    #companys_query = Company.query.all()
    page = int(page)

    companys_query = Company.query.filter(Company.companyname.like('%' + urlsearchcompanyname + '%')).order_by(Company.createtime.desc()).paginate(page, per_page=15, error_out=False)

    companys_page_query = companys_query.items
    companys_total =  len(companys_page_query) / 15
    page_total = math.ceil(companys_total)

    for company_query in companys_page_query:
        companyid = company_query.companyid
        zabbixhostinfo = zabbix_hosts_query(companyid)
        if zabbixhostinfo['status'] != 2:
            totalhost = len(zabbixhostinfo['totalhosts'])
        else:
            totalhost = None
        companyname = company_query.companyname
        companyexpire = company_query.companyexpiredate
        companyrole = company_query.companyrole
        user_query = Opuser.query.filter_by(opcompanyid=companyid).all()
        totalcompanyusers = len(user_query)
        adminuser_query = Opuser.query.filter_by(opcompanyid=companyid, oprole='4').first()
        adminusername = adminuser_query.opusername
        adminmobile = adminuser_query.opmobile
        defaultcompany = adminuser_query.default
        admimemail = company_query.companyemail
        companymark = company_query.companymark

        if companyexpire:
            companyexpire = int(round(time.mktime(companyexpire.timetuple()) * 1000))
        rs_query_dict = {'companyid':companyid, 'companyname': companyname, 'adminusername': adminusername,
                'adminmobile': adminmobile,'adminemail':admimemail,
                'companyexpire': companyexpire,'totalhost':totalhost,
                'companyrole':companyrole, 'members':totalcompanyusers,
                         'companymark': companymark,'defaultcompany':defaultcompany
                }
        rs_query_list.append(rs_query_dict)
    db.session.close()
    return {"status": 0, "msg":"查询成功", 'pagetotal':page_total,"companyinfo": rs_query_list}

def backstagetryouts(userid, token, page):
    if token != '11111':
        return {'status':1, 'msg':'token不可用'}

    #试用公司
    rs_query_list = []
    page = int(page)
    companys_query = Company.query.filter_by(companyrole='1').order_by(Company.createtime.desc()).paginate(page, per_page=15, error_out=False)
    companys_page_query = companys_query.items

    companys_total =  len(companys_page_query) / 15
    page_total = math.ceil(companys_total)

    print(companys_page_query)

    #companys_query = Company.query.filter_by(companyrole='1').all()
    for company_query in companys_page_query:
        companyid = company_query.companyid
        zabbixhostinfo = zabbix_hosts_query(companyid)
        if zabbixhostinfo['status'] != 2:
            totalhost = len(zabbixhostinfo['totalhosts'])
        else:
            totalhost = None
        companyname = company_query.companyname
        companyexpire = company_query.companyexpiredate
        companyrole = company_query.companyrole
        # user_query = Opuser.query.filter_by(opcompanyid=companyid).all()
        # totalcompanyusers = len(user_query)
        user_query = Opuser.query.filter(Opuser.opcompanyid==companyid, Opuser.oprole!=2).all()
        totalcompanyusers = int(len(user_query)) - 1
        adminuser_query = Opuser.query.filter_by(opcompanyid=companyid, oprole='4').first()
        adminusername = adminuser_query.opusername
        adminmobile = adminuser_query.opmobile
        admimemail = company_query.companyemail
        defaultcompany = adminuser_query.default
        companymark = company_query.companymark

        if companyexpire:
            companyexpire = int(round(time.mktime(companyexpire.timetuple()) * 1000))
        rs_query_dict = {'companyid':companyid, 'companyname': companyname, 'adminusername': adminusername,
          'adminmobile': adminmobile,'adminemail':admimemail,
          'companyexpire': companyexpire,'totalhost':totalhost,
            'companyrole':companyrole, 'members':totalcompanyusers,
                         'companymark': companymark,'defaultcompany':defaultcompany
          }
        rs_query_list.append(rs_query_dict)
    db.session.close()
    return {"status": 0, "msg":"查询成功", 'pagetotal':page_total,"companyinfo": rs_query_list}

def backstageexpiring(userid, token, page):
    if token != '11111':
        return {'status':1, 'msg':'token不可用'}

    #即将过期
    todays_datetime = datetime(datetime.today().year, datetime.today().month, datetime.today().day)
    backstage_expiredate_query = Backstage.query.first()
    backstage_expiredate = backstage_expiredate_query.companyexpire
    expire_date = todays_datetime + timedelta(days=int(backstage_expiredate))
    page = int(page)

    try_expire_companys_query_page = Company.query.filter(Company.companyexpiredate <= expire_date, Company.companyexpiredate >= todays_datetime, Company.companyrole == '2').order_by(Company.createtime.desc()).paginate(page, per_page=15, error_out=False)
    try_expire_companys_query = try_expire_companys_query_page.items
    companys_total =  len(try_expire_companys_query) / 15
    page_total = math.ceil(companys_total)


    if try_expire_companys_query is None:
        db.session.close()
        return {"status": 0, "msg":"查询成功", "companyinfo": []}
    rs_query_list = []
    for company_query in try_expire_companys_query:
        companyid = company_query.companyid
        zabbixhostinfo = zabbix_hosts_query(companyid)
        if zabbixhostinfo['status'] != 2:
            totalhost = len(zabbixhostinfo['totalhosts'])
        else:
            totalhost = None
        companyname = company_query.companyname
        companyexpire = company_query.companyexpiredate
        companyrole = company_query.companyrole
        #user_query = Opuser.query.filter_by(opcompanyid=companyid).all()
        #totalcompanyusers = len(user_query)
        user_query = Opuser.query.filter(Opuser.opcompanyid==companyid, Opuser.oprole!=2).all()
        totalcompanyusers = int(len(user_query)) - 1
        adminuser_query = Opuser.query.filter_by(opcompanyid=companyid, oprole='4').first()
        adminusername = adminuser_query.opusername
        adminmobile = adminuser_query.opmobile
        admimemail = company_query.companyemail
        defaultcompany = adminuser_query.default
        companymark = company_query.companymark

        if companyexpire:
            companyexpire = int(round(time.mktime(companyexpire.timetuple()) * 1000))
        rs_query_dict = {'companyid':companyid, 'companyname': companyname, 'adminusername': adminusername,
          'adminmobile': adminmobile,'adminemail':admimemail,
          'companyexpire': companyexpire,'totalhost':totalhost,
            'companyrole':companyrole, 'members':totalcompanyusers,
                         'companymark': companymark,'defaultcompany':defaultcompany
          }
        rs_query_list.append(rs_query_dict)
    db.session.close()
    return {"status": 0, "msg":"查询成功",'pagetotal':page_total, "companyinfo": rs_query_list}


def backstageexpired(userid, token, page):
    if token != '11111':
        return {'status':1, 'msg':'token不可用'}
    #已过期
    page = int(page)
    todays_datetime = datetime(datetime.today().year, datetime.today().month, datetime.today().day)
    try_expire_companys_query_page = Company.query.filter(Company.companyexpiredate <= todays_datetime, Company.companyrole == '2').order_by(Company.createtime.desc()).paginate(page, per_page=15, error_out=False)
    try_expire_companys_query = try_expire_companys_query_page.items
    companys_total =  len(try_expire_companys_query) / 15
    page_total = math.ceil(companys_total)

    if try_expire_companys_query is None:
        db.session.close()
        return {"status": 0, "msg": "查询成功", "companyinfo": []}
    rs_query_list = []
    for company_query in try_expire_companys_query:
        companyid = company_query.companyid
        zabbixhostinfo = zabbix_hosts_query(companyid)
        if zabbixhostinfo['status'] != 2:
            totalhost = len(zabbixhostinfo['totalhosts'])
        else:
            totalhost = None
        companyname = company_query.companyname
        companyexpire = company_query.companyexpiredate
        companyrole = company_query.companyrole
        #user_query = Opuser.query.filter_by(opcompanyid=companyid).all()
        #totalcompanyusers = len(user_quer
        user_query = Opuser.query.filter(Opuser.opcompanyid==companyid, Opuser.oprole!=2).all()
        totalcompanyusers = int(len(user_query)) - 1
        adminuser_query = Opuser.query.filter_by(opcompanyid=companyid, oprole='4').first()
        adminusername = adminuser_query.opusername
        adminmobile = adminuser_query.opmobile
        defaultcompany = adminuser_query.default
        admimemail = company_query.companyemail
        companymark = company_query.companymark

        if companyexpire:
            companyexpire = int(round(time.mktime(companyexpire.timetuple()) * 1000))
        rs_query_dict = {'companyid':companyid, 'companyname': companyname, 'adminusername': adminusername,
          'adminmobile': adminmobile,'adminemail':admimemail,
          'companyexpire': companyexpire,'totalhost':totalhost,
            'companyrole':companyrole, 'members':totalcompanyusers,
                         'companymark': companymark,'defaultcompany':defaultcompany
          }
        rs_query_list.append(rs_query_dict)
        db.session.close()
        return {"status": 0, "msg": "查询成功",'pagetotal':page_total, "companyinfo": rs_query_list}

def backstagenewcompanytoday(userid, token, page):
    if token != '11111':
        return {'status':1, 'msg':'token不可用'}

    #即将过期
    todays_datetime = datetime(datetime.today().year, datetime.today().month, datetime.today().day)
    print(todays_datetime)
    page = int(page)

    try_expire_companys_query_page = Company.query.filter(Company.createtime >= todays_datetime).order_by(Company.createtime.desc()).paginate(page, per_page=15, error_out=False)
    try_expire_companys_query = try_expire_companys_query_page.items
    companys_total =  len(try_expire_companys_query) / 15
    page_total = math.ceil(companys_total)

    if try_expire_companys_query is None:
        db.session.close()
        return {"status": 0, "msg":"查询成功", "companyinfo": []}
    rs_query_list = []
    for company_query in try_expire_companys_query:
        companyid = company_query.companyid
        zabbixhostinfo = zabbix_hosts_query(companyid)
        if zabbixhostinfo['status'] != 2:
            totalhost = len(zabbixhostinfo['totalhosts'])
        else:
            totalhost = None
        companyname = company_query.companyname
        companyexpire = company_query.companyexpiredate
        companyrole = company_query.companyrole
        user_query = Opuser.query.filter_by(opcompanyid=companyid).all()
        totalcompanyusers = len(user_query)
        adminuser_query = Opuser.query.filter_by(opcompanyid=companyid, oprole='4').first()
        adminusername = adminuser_query.opusername
        adminmobile = adminuser_query.opmobile
        admimemail = company_query.companyemail
        defaultcompany = adminuser_query.default
        companymark = company_query.companymark

        if companyexpire:
            companyexpire = int(round(time.mktime(companyexpire.timetuple()) * 1000))
        rs_query_dict = {'companyid':companyid, 'companyname': companyname, 'adminusername': adminusername,
          'adminmobile': adminmobile,'adminemail':admimemail,
          'companyexpire': companyexpire,'totalhost':totalhost,
            'companyrole':companyrole, 'members':totalcompanyusers,
                         'companymark': companymark,'defaultcompany':defaultcompany
          }
        rs_query_list.append(rs_query_dict)
    db.session.close()
    return {"status": 0, "msg":"查询成功", 'pagetotal':page_total,"companyinfo": rs_query_list}

def companymemberinfo(adminuserid, token, page, searchcompanyname):
    if token != '11111':
        return {'status':1, 'msg':'token不可用'}
    #所有用户信息
    page = int(page)
    search_companyid_list = []
    companys_query_page = Company.query.filter(Company.companyname.like('%' + searchcompanyname + '%')).order_by(
        Company.createtime.desc()).paginate(page, per_page=20, error_out=False)
    companys_query = companys_query_page.items
    companys_total =  len(companys_query) / 15
    page_total = math.ceil(companys_total)

    for company_query in companys_query:
        search_company_dict = {}
        search_company_dict['companyid'] = company_query.companyid
        search_company_dict['companyname'] = company_query.companyname

        search_companyid_list.append(search_company_dict)

    search_opuserid_list = []
    for searchcompanyidinfo in search_companyid_list:

        opusers_query = Opuser.query.filter_by(opcompanyid=searchcompanyidinfo['companyid']).all()
        for opuser_query in opusers_query:
            searchopuserid = opuser_query.opuserid
            searchopuserrole = opuser_query.oprole
            userstatus = opuser_query.userstatus
            if searchopuserrole != '5' and searchopuserrole != '2' and searchopuserid:
                searchopuser_dict = {
                            "companyname": searchcompanyidinfo['companyname'],
                            "userallinfo": {
                                "userid": searchopuserid,
                                "oprole": searchopuserrole,
                                "userstatus": userstatus,
                                    }
                                }
                search_opuserid_list.append(searchopuser_dict)
    lastuserinfo_list = []
    print(search_opuserid_list)
    for useridinfo in search_opuserid_list:

        queryuserid = useridinfo['userallinfo']['userid']
        userinfo_query = User.query.filter_by(userid=queryuserid).first()
        username = userinfo_query.username
        usermobile = userinfo_query.mobile
        userlogintime = userinfo_query.logintime
        if userlogintime:
            userlogintime = int(round(time.mktime(userlogintime.timetuple()) * 1000))
        userrole = userinfo_query.role
        useridinfo['userallinfo']['username'] = username
        useridinfo['userallinfo']['mobile'] = usermobile
        useridinfo['userallinfo']['logintime'] = userlogintime
        useridinfo['userallinfo']['role'] = userrole

        lastuserinfo_list.append(useridinfo)
    db.session.close()
    return {"status":0, "msg": "查询成功", 'pagetotal':page_total,"userinfo": lastuserinfo_list}

def companyhostsinfo(adminuserid, token, page, companyname):
    if token != '11111':
        return {'status': 1, 'msg': 'token不可用'}
    else:
        companyid_query = Company.query.filter_by(companyname=companyname).first()

        if companyid_query is None:
            db.session.close()
            return {'status': 2, 'msg': '未找到相关公司'}
        companyid = companyid_query.companyid
        zabbixinfo_query = Zabbix.query.filter_by(companyid=companyid).first()
        if zabbixinfo_query is None:
            db.session.close()
            return {'status': 3, 'msg': '使用监控功能之前，需要先添加zabbix服务器'}
        zabbixusername = zabbixinfo_query.zabbixuser
        zabbixpassword = zabbixinfo_query.zabbixpassword
        zabbixurl = zabbixinfo_query.zabbixserver
        zabbixtoken = auth(zabbixusername, zabbixpassword, zabbixurl)

        group_list = hostgroups(zabbixtoken, zabbixurl)
        print(group_list)
        hostinfo_list = []
        for group in group_list:
            # hostinfo_dict = {}
            hostinfo_list.append(group['groupid'])
            # groupid = group['groupid']
            # groupname = group['name']
        print(hostinfo_list)
        data = json.dumps(
            {
                "jsonrpc": "2.0",
                "method": "host.get",
                "params": {
                    "output": ["hostid", "name", "host"],
                    "groupids": hostinfo_list,
                },
                "auth": zabbixtoken,  # theauth id is what auth script returns, remeber it is string
                "id": 1,
            })
        hosts = requests.post(zabbixurl + '/zabbix/api_jsonrpc.php', data=data, headers=headers)
        hosts_list = hosts.json()['result']
        checkhosts_list = []
        for checkhost_dict in hosts_list:

            checkhostid = checkhost_dict['hostid']
            checkhost_query = Monitor.query.filter_by(zabbixhostid=checkhostid).first()
            if checkhost_query:
                checkhost_dict['hoststatus'] = 'in'
            else:
                checkhost_dict['hoststatus'] = 'out'
            checkhosts_list.append(checkhost_dict)

        allhostsnumber = len(checkhosts_list)
        inhostsnumber_query = Monitor.query.all()
        inhostsnumber = len(inhostsnumber_query)
        inhostinfo_list = []
        for inhost in inhostsnumber_query:
            inhostinfo_dict = {'hostid': inhost.zabbixhostid, 'host': inhost.zabbixhostip,
                               'name': inhost.zabbixhostname, 'hoststatus': 'in'}
            inhostinfo_list.append(inhostinfo_dict)

        hosts_queryrs = {'status': 0, 'totalamount': allhostsnumber,
                         'inamount': inhostsnumber, 'totalhosts': checkhosts_list,
                         }
        db.session.close()
        return hosts_queryrs


def companyexpire(adminuserid, token, companyname, time_chuo):
    if token != '11111':
        return {'status': 1, 'msg': 'token不可用'}
    else:
        companyid_query = Company.query.filter_by(companyname=companyname).first()

        if companyid_query is None:
            db.session.close()
            return {'status': 2, 'msg': '未找到相关公司'}
        else:
            time_chuo_zhuan = int(time_chuo) / 1000
            userinfologintime = time.localtime(time_chuo_zhuan)
            userinfologintime_dt = time.strftime("%Y-%m-%d %H:%M:%S", userinfologintime)
            companyid_query.companyexpiredate = userinfologintime_dt
            companyid_query.companyrole = 2
            db.session.commit()
            db.session.close()
            return {'status': 0, 'msg': '修改成功'}

def companypatch(userid, usertoken,oldcompanyname, newcompanyname,companyemail, mark, disable):
    if usertoken != '11111':
        return {'status': 1, 'msg': 'token不可用'}
    else:
        companyid_query = Company.query.filter_by(companyname=oldcompanyname).first()

        if companyid_query is None:
            db.session.close()
            return {'status': 2, 'msg': '未找到相关公司'}
        else:
            companyid_query.companyname = newcompanyname
            companyid_query.companyemail = companyemail
            companyid_query.companymark = mark
            #companyid_query.companyrole = 2

            db.session.commit()
            db.session.close()
            return {'status': 0, 'msg': '修改成功'}

def companydelete(userid, usertoken,companyname):
    if usertoken != '11111':
        return {'status': 1, 'msg': 'token不可用'}

    return {'status': 0, 'msg': '暂未支持'}

