#!/usr/bin/env python
#coding=utf-8
import json
import requests
from model import *
import sqlalchemy
import re
import random
import string
import os
import sys
import demjson
import fnmatch
import logging
from logging.handlers import TimedRotatingFileHandler

fmt_str = '%(asctime)s %(name)-12s %(levelname)-8s %(message)s'
logging.basicConfig()
filename_head = os.getcwd() + "/logs/rebot.log"
fileshandle = logging.handlers.TimedRotatingFileHandler(filename_head, when="midnight", interval=1, backupCount=30,
                                                        encoding='utf-8', delay=False, utc=False)
fileshandle.suffix = "%Y-%m-%d"
formatter = logging.Formatter(fmt_str)
fileshandle.setFormatter(formatter)
logger = logging.getLogger("zabbix_quey")
logger.addHandler(fileshandle)
logger.setLevel(logging.INFO)


def generate_random_str(randomlength=16):
    """
    生成一个指定长度的随机字符串，其中
    string.digits=0123456789
    string.ascii_letters=abcdefghigklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ
    """
    str_list = [random.choice(string.digits + string.ascii_letters) for i in range(randomlength)]
    random_str = ''.join(str_list)
    return random_str


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


def zabbixserver_add(userid, usertoken, zabbixserver, zabbixusername, zabbixpassword):
    try:
        if usertoken != '11111':
            return {'status': 1, 'msg': 'token不可用'}

        adminuserinfo_query = User.query.filter_by(userid=userid).first()
        adminuser_companyid = adminuserinfo_query.companyid
        adminuserrole = adminuserinfo_query.role
        if adminuserrole != '4':
            return {'status':2, 'msg':'没有权限'}

        zabbixinfo_query = Zabbix.query.filter_by(companyid=adminuser_companyid).first()
        if zabbixinfo_query:
            return {'status': 3, 'msg': 'zabbix服务器已经存在'}

        zabbixserverid = 'z' + generate_random_str()
        insert_zabbixserver = Zabbix(companyid=adminuser_companyid, zabbixid=zabbixserverid,zabbixserver=zabbixserver, zabbixuser=zabbixusername, zabbixpassword=zabbixpassword)
        db.session.add(insert_zabbixserver)
        db.session.commit()
        return  {'status':0, 'msg': '添加成功'}
    except sqlalchemy.exc.OperationalError:
        return {'status': 3, 'Oooops': '数据库连接出现错误'}

def query_hosts(userid, usertoken, companyid):
    try:
        print(usertoken)
        if usertoken != '11111':
            return {'status':1 ,'msg': 'token不可用'}

        user_youke_check = User.query.filter_by(userid=userid).first()
        if user_youke_check.role == '1' or user_youke_check.role == '2':
            db.session.close()
            return {
                  "inamount": 2,
                  "inhosts": [
                    {
                      "host": "10.0.60.175",
                      "hostid": "10254",
                      "hoststatus": "in",
                      "name": "10.0.60.175"
                    },
                    {
                      "host": "Zabbix server",
                      "hostid": "10084",
                      "hoststatus": "in",
                      "name": "Zabbix server"
                    }
                  ],
                  "status": 0,
                  "totalamount": 5,
                  "totalhosts": [
                    {
                      "host": "Zabbix server",
                      "hostid": "10084",
                      "hoststatus": "in",
                      "name": "Zabbix server"
                    },
                    {
                      "host": "10.0.60.175",
                      "hostid": "10254",
                      "hoststatus": "in",
                      "name": "10.0.60.175"
                    },
                    {
                      "host": "10.0.60.176",
                      "hostid": "10258",
                      "hoststatus": "out",
                      "name": "10.0.60.176"
                    },
                    {
                      "host": "10.0.1.131",
                      "hostid": "10259",
                      "hoststatus": "out",
                      "name": "10.0.1.131"
                    },
                    {
                      "host": "10.0.60.187",
                      "hostid": "10261",
                      "hoststatus": "out",
                      "name": "10.0.60.187-saltstack-test"
                    }
                  ]
                }

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
    #        host_list = hosts.json()['result']
    #        if host_list:
    #            hostinfo_dict['zabbixgroupid'] = groupid
    #            hostinfo_dict['zabbixgroupname'] = groupname
    #            hostinfo_dict['zabbixgrouphosts'] = host_list
    #            hostinfo_list.append(hostinfo_dict)
    #    response = {'result': hostinfo_list}
    #    return response
    except sqlalchemy.exc.OperationalError:
        return {'status':3, 'Oooops': '数据库连接出现错误'}

def query_zabbixhost(userid, usertoken, searchname, companyid):
    try:

        if usertoken != '11111':
            return {'status':1 ,'msg': 'token不可用'}
        user_companyid = companyid
        zabbixinfo_query = Zabbix.query.filter_by(companyid=user_companyid).first()
        zabbixusername = zabbixinfo_query.zabbixuser
        zabbixpassword = zabbixinfo_query.zabbixpassword
        zabbixurl = zabbixinfo_query.zabbixserver
        zabbixtoken = auth(zabbixusername, zabbixpassword, zabbixurl)

        group_list = hostgroups(zabbixtoken, zabbixurl)
        hostinfo_list = []
        for group in group_list:
            hostinfo_list.append(group['groupid'])

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
        host_list = hosts.json()['result']

        searchhost_list = []
        hostinfo_dict = {}
        for query_hostidinfo in  host_list:
            if query_hostidinfo['name'].find(searchname) != -1:
                    searchhost_list.append(query_hostidinfo)

        hostinfo_dict['status'] = 0
        hostinfo_dict['result'] = searchhost_list
        db.session.close()
        return hostinfo_dict
    except sqlalchemy.exc.OperationalError:
        return {'status':3, 'Oooops': '数据库连接出现错误'}

def zabbixmonitor_add(userid, usertoken, hostinfo_list, companyid):
    try:
        if usertoken != '11111':
            return {'status': 1, 'msg': 'token不可用'}

        user_youke_check = User.query.filter_by(userid=userid).first()
        if user_youke_check.role == '1' or user_youke_check.role == '2':
            db.session.close()
            return {'status': 2, 'msg': '游客或者待审核用户无法添加监控主机'}
        # 生成zabbix token
        user_companyid = companyid
        zabbixinfo_query = Zabbix.query.filter_by(companyid=user_companyid).first()
        zabbixusername = zabbixinfo_query.zabbixuser
        zabbixpassword = zabbixinfo_query.zabbixpassword
        zabbixurl = zabbixinfo_query.zabbixserver
        zabbixtoken = auth(zabbixusername, zabbixpassword, zabbixurl)
        zabbixinfoall_query = Monitor.query.filter_by(companyid=user_companyid).first()
        if zabbixinfoall_query:
            zabbixinfoall_query.query.filter_by(companyid=user_companyid).delete()

        if hostinfo_list:
            for hostinfo in hostinfo_list:
                zabbixhostid = hostinfo['hostid']
                zabbixhostip = hostinfo['host']
                zabbixhostname = hostinfo['name']

                data = json.dumps({
                        "jsonrpc": "2.0",
                        "method": "item.get",
                        "params": {
                            "output": ["itemid", "key_"],
                            "hostids": zabbixhostid,
                            },
                        "auth": zabbixtoken,
                        "id": 1,
                        })
                items_response = requests.post(zabbixurl + '/zabbix/api_jsonrpc.php', data=data, headers=headers)

                zabbixitemname_list = ["system.cpu.util[,user]", "vfs.fs.size", "vm.memory.size[available]", "vm.memory.size[total]", "net.if.in", "net.if.out"]

                itemid_list = []
                for itemid_response_value in items_response.json()['result']:
                    for zabbixitemname in zabbixitemname_list:
                        if itemid_response_value['key_'].find(zabbixitemname) != -1:
                            itemid_list.append(itemid_response_value['itemid'])

                insert_zabbixmonitor = Monitor(companyid=user_companyid, zabbixhostid=zabbixhostid, zabbixhostip=zabbixhostip, zabbixhostname=zabbixhostname, zabbixitemname=str(zabbixitemname_list), zabbixitemid=str(itemid_list))
                db.session.add(insert_zabbixmonitor)
                db.session.commit()
                db.session.close()
        db.session.close()
        return  {'status':0, 'msg': '添加成功'}
    except sqlalchemy.exc.OperationalError:
        return {'status':3, 'Oooops': '数据库连接出现错误'}

def zabbixitem_query(userid, usertoken, companyid):
    try:
        if usertoken != '11111':
            return {'status': 1, 'msg': 'token不可用'}
        #生成zabbix token
        user_companyid = companyid
        zabbixinfo_query = Zabbix.query.filter_by(companyid=user_companyid).first()
        zabbixusername = zabbixinfo_query.zabbixuser
        zabbixpassword = zabbixinfo_query.zabbixpassword
        zabbixurl = zabbixinfo_query.zabbixserver
        zabbixtoken = auth(zabbixusername, zabbixpassword, zabbixurl)
        zabbixinfo_querys = Monitor.query.filter_by(companyid=user_companyid).all()
        #zabbixitemid_list = eval(zabbixinfo_querys.zabbixitemid)
        #获取zabbix数据
        zabbixitems_list = []
        for zabbixinfo_query in zabbixinfo_querys:
            zabbixitem_host_dict = {}
            zabbixitemid = zabbixinfo_query.zabbixitemid
            zabbixhostid = zabbixinfo_query.zabbixhostid
            zabbixhostip = zabbixinfo_query.zabbixhostip
            zabbixhostname = zabbixinfo_query.zabbixhostname
            zabbixitemid_query_list = eval(zabbixitemid)
            zabbixitem_host_dict['hostid'] = zabbixhostid
            zabbixitem_host_dict['itemids'] = zabbixitemid_query_list
            zabbixitem_host_dict['host'] = zabbixhostip
            zabbixitem_host_dict['name'] = zabbixhostname
            zabbixitems_list.append(zabbixitem_host_dict)

        items_response_info_list = []
        for zabbixitems in zabbixitems_list:
            items_response_info_dict = {}
            data = json.dumps(
                    {
                    "jsonrpc": "2.0",
                    "method": "item.get",
                    "params": {
                        "output": ["key_", "lastvalue"],
                        "itemids": zabbixitems['itemids'],
                        #"hostids": ['10254', '10258'],
                        },
                    "auth": zabbixtoken,  # theauth id is what auth script returns, remeber it is string
                    "id": 1,
                })
            items_response = requests.post(zabbixurl + '/zabbix/api_jsonrpc.php', data=data, headers=headers)
            items_response_info_dict['host'] = zabbixitems['host']
            items_response_info_dict['name'] = zabbixitems['name']
            items_response_info_dict['result'] = items_response.json()['result']
            items_response_info_list.append(items_response_info_dict)

        for chulihuansuan in items_response_info_list:

            for huansuanzhi in chulihuansuan['result']:
                if huansuanzhi['key_'].find('vm.memory.size') != -1:
                    huansuanzhi['lastvalue'] = float(huansuanzhi['lastvalue'])/1024/1024/1024

                if huansuanzhi['key_'].find('vfs.fs.size') != -1:
                    huansuanzhi['lastvalue'] = float(huansuanzhi['lastvalue']) / 1024 / 1024/ 1024
                if huansuanzhi['key_'].find('net') != -1:
                    huansuanzhi['lastvalue'] = float(huansuanzhi['lastvalue']) / 1024



        for hehe in items_response_info_list:
            print(hehe['name'])
            for heheda in hehe['result']:
                print(heheda)

        db.session.close()
        return items_response_info_list

    except sqlalchemy.exc.OperationalError:
        return {'status':3, 'Oooops': '数据库连接出现错误'}




def zabbixitem_value_query(userid, usertoken, host, companyid):
    try:
        if usertoken != '11111':
            return {'status': 1, 'msg': 'token不可用'}
        #生成zabbix token
        print(host)
        user_companyid = companyid
        zabbixinfo_query = Zabbix.query.filter_by(companyid=user_companyid).first()
        zabbixusername = zabbixinfo_query.zabbixuser
        zabbixpassword = zabbixinfo_query.zabbixpassword
        zabbixurl = zabbixinfo_query.zabbixserver
        zabbixtoken = auth(zabbixusername, zabbixpassword, zabbixurl)

        zabbixinfo_query_hostid = Monitor.query.filter_by(companyid=user_companyid, zabbixhostid=host).first()
        zabbixinfo_query_hostip = Monitor.query.filter_by(companyid=user_companyid, zabbixhostip=host).first()
        zabbixinfo_query_hostname = Monitor.query.filter_by(companyid=user_companyid, zabbixhostname=host).first()

        if not zabbixinfo_query_hostid and not zabbixinfo_query_hostip and not zabbixinfo_query_hostname:
            return {'status':2, 'msg': '没找到主机'}

        if zabbixinfo_query_hostid:
            zabbixinfo_query_item_queryinfo = zabbixinfo_query_hostid.zabbixitemid
            hostinfo = zabbixinfo_query_hostid.zabbixhostip
        elif zabbixinfo_query_hostip:
            zabbixinfo_query_item_queryinfo = zabbixinfo_query_hostip.zabbixitemid
            hostinfo = zabbixinfo_query_hostip.zabbixhostip
        elif zabbixinfo_query_hostname:
            zabbixinfo_query_item_queryinfo = zabbixinfo_query_hostname.zabbixitemid
            hostinfo = zabbixinfo_query_hostname.zabbixhostip
        print('1111111111')
        print(zabbixinfo_query_hostname)
        print(zabbixinfo_query_hostip)
        zabbixinfo_query_item_list = eval(zabbixinfo_query_item_queryinfo)
        print(zabbixinfo_query_item_list)

        data = json.dumps(
                {
                    "jsonrpc": "2.0",
                    "method": "item.get",
                    "params": {
                        "output": ["key_", "lastvalue"],
                        "itemids": zabbixinfo_query_item_list,
                        #"hostids": ['10254', '10258'],
                        },
                    "auth": zabbixtoken,  # theauth id is what auth script returns, remeber it is string
                    "id": 1,
            })
        items_response = requests.post(zabbixurl + '/zabbix/api_jsonrpc.php', data=data, headers=headers)



        memory_available_query_list = []
        memory_total_query_list = []
        disk_query_list = []
        net_in_query_list = []
        net_out_query_list = []
        cpu_query_list = []
        response_queryinfo = {}

        chulihuansuan_response_list = items_response.json()['result']
        for chulihuansuan in chulihuansuan_response_list:
            if chulihuansuan['key_'].find('vm.memory.size[available]') != -1:
                chulihuansuan['lastvalue'] = float(chulihuansuan['lastvalue'])/1024/1024/1024
                memory_available_query_list.append(chulihuansuan)
            if chulihuansuan['key_'].find('vm.memory.size[total]') != -1:
                chulihuansuan['lastvalue'] = float(chulihuansuan['lastvalue'])/1024/1024/1024
                memory_total_query_list.append(chulihuansuan)
            if chulihuansuan['key_'].find('vfs.fs.size') != -1:
                chulihuansuan['lastvalue'] = float(chulihuansuan['lastvalue']) / 1024 / 1024/ 1024
                disk_query_list.append(chulihuansuan)
            if chulihuansuan['key_'].find('net.if.in') != -1:
                chulihuansuan['lastvalue'] = float(chulihuansuan['lastvalue']) / 1024
                net_in_query_list.append(chulihuansuan)
            if chulihuansuan['key_'].find('net.if.out') != -1:
                chulihuansuan['lastvalue'] = float(chulihuansuan['lastvalue']) / 1024
                net_out_query_list.append(chulihuansuan)
            if chulihuansuan['key_'].find('system.cpu.util[,user]') != -1:
                cpu_query_list.append(chulihuansuan)


        print(memory_available_query_list)
        print(memory_total_query_list)
        print(disk_query_list)
        print(net_in_query_list)
        print(net_out_query_list)
        print(cpu_query_list)

        response_queryinfo['available_memory'] = memory_available_query_list
        response_queryinfo['total_memory'] = memory_total_query_list
        response_queryinfo['disk'] = disk_query_list
        response_queryinfo['in_network'] = net_in_query_list
        response_queryinfo['out_network'] = net_out_query_list
        response_queryinfo['cpu'] = cpu_query_list
        response_queryinfo['hostip'] = hostinfo
        db.session.close()
        return response_queryinfo
    except sqlalchemy.exc.OperationalError:
        return {'status':3, 'Oooops': '数据库连接出现错误'}


def zabbix_get_complay_hosts(usertoken, companyid):
    all_host_monitor_value = []
    msg = ""
    status = 0

    #获取zabbix token
    headers_base = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, sdch',
        'Accept-Language': 'en-US,en;q=0.8,zh-CN;q=0.6,zh;q=0.4,zh-TW;q=0.2',
        'Connection': 'keep-alive',
        'User-Agent': 'Chrome/43.0.2357.130 Safari/10000',
        'Content-Type': 'application/json-rpc',
    }

    try:
        user_companyid = companyid
        zabbixinfo_query = Zabbix.query.filter_by(companyid=user_companyid).first()
        zabbixusername = zabbixinfo_query.zabbixuser
        zabbixpassword = zabbixinfo_query.zabbixpassword
        zabbixurl = zabbixinfo_query.zabbixserver
        zabbixtoken = auth(zabbixusername, zabbixpassword, zabbixurl)
    except:

        msg = "未找到与公司匹配的zabbix服务器信息，请联系系统管理员！"
        logger.error(msg, companyid)
        logger.error(sys.exc_info()[0])
        status = -2
        result = {
            "result": all_host_monitor_value,
            "msg": msg,
            "status": status
        }
        return result

    #获取所属公司所有的监控信息
    try:
        zabbixinfo_querys = Monitor.query.filter_by(companyid=user_companyid).all()
        #获取所属公司的zabbix服务器信息
        zabbixitems_list = []
        for zabbixinfo_query in zabbixinfo_querys:
            zabbixitem_host_dict = {}
            zabbixitemid = zabbixinfo_query.zabbixitemid
            zabbixhostid = zabbixinfo_query.zabbixhostid
            zabbixhostip = zabbixinfo_query.zabbixhostip
            zabbixhostname = zabbixinfo_query.zabbixhostname
            zabbixitemid_query_list = eval(zabbixitemid)
            zabbixitem_host_dict['hostid'] = zabbixhostid
            #zabbixitem_host_dict['itemids'] = zabbixitemid_query_list
            zabbixitem_host_dict['host'] = zabbixhostip
            zabbixitem_host_dict['name'] = zabbixhostname
            zabbixitems_list.append(zabbixitem_host_dict)

        #查询zabbix监控
        result_temp = []
        for zabbixitems in zabbixitems_list:
            items_response_info_dict = {}
            data = json.dumps(
                {
                    "jsonrpc": "2.0",
                    "method": "item.get",
                    "params": {
                        "output": ["key_", "lastvalue"],
                        "hostids": zabbixitems['hostid'],
                        # "hostids": ['10254', '10258'],
                    },
                    "auth": zabbixtoken,  # theauth id is what auth script returns, remeber it is string
                    "id": 1,
                })
            items_response = requests.post(zabbixurl + '/zabbix/api_jsonrpc.php', data=data, headers=headers_base)
            items_response_info_dict['host'] = zabbixitems['host']
            items_response_info_dict["item"] = demjson.decode(items_response.content)["result"]
            result_temp.append(items_response_info_dict)

        #整理数据
        #print(result_temp)
        for host_value in result_temp:
            #获取所有主机的监控数据
            temp_raw = {"host": host_value["host"]}
            i = 0
            temp_liebiao = []
            search_keys = ("vfs.fs.size*pfree*", "net.if.in*ens*", "system.cpu.util*idle*",
                           "vm.memory*", "net.if.in*Intel*Network Connection]")
            for item in host_value["item"]:
                #整理每个主机的数据
                item = dict(item)

                # if str(item["key_"]).__contains__("net.if.in"):
                #    print(item["key_"])

                for mykey in search_keys:
                    #过滤需要的key
                    #print(mykey, item["key_"])
                    temp_dict = dict()
                    if fnmatch.fnmatch(item["key_"], mykey):
                        #print(mykey, item["key_"])

                        k = 0
                        if item["key_"].find("system.cpu.util") != -1:
                            temp_dict["key"] = "cpu"
                            temp_dict["available"] = float(item["lastvalue"])
                            temp_dict["total"] = float(100)
                            temp_liebiao.append(temp_dict)
                            break
                        elif fnmatch.fnmatch(item["key_"], "net.if.in*"):
                            
                            temp_dict["key"] = "network"
                            temp_dict["available"] = float(item["lastvalue"])/1024
                            temp_dict["total"] = float(100)
                            
                            temp_liebiao.append(temp_dict)
                            
                            break
                        elif item["key_"].find("net.if.in[Intel(R) PRO/1000 MT Network Connection]") != -1:
                            temp_dict["key"] = "network"
                            temp_dict["available"] = float(item["lastvalue"]) / 1024
                            temp_dict["total"] = float(100)

                            temp_liebiao.append(temp_dict)

                            break
                        elif item["key_"].find("vm.memory.size[available]") != -1:
                            
                            k = 1
                            for j in temp_liebiao:
                                if "memory" in j.values():
                                    
                                    network_value = dict()
                                    network_value.copy(j)
                                    temp_liebiao.remove(j)
                                    # 为已经存在的字典增加一个字段
                                    network_value["available"] = float(item["lastvalue"]) / 1024 / 1024 / 1024

                                    # temp_liebiao[k]["available"] = float(item["lastvalue"])/1024/1024/1024
                                    temp_liebiao.append(network_value)
                                    break

                                if len(temp_liebiao) == k:
                                    # 否则新生成个字典
                                    temp_dict["key"] = "memory"
                                    temp_dict["available"] = float(item["lastvalue"]) / 1024 / 1024 / 1024
                                    temp_liebiao.append(temp_dict)
                                    break
                                k += 1
                        elif item["key_"].find("vm.memory.size[free]") != -1:
                            k = 1
                            for j in temp_liebiao:
                                if "memory" in j.values():
                                    network_value = dict()
                                    network_value.copy(j)
                                    temp_liebiao.remove(j)
                                    # 为已经存在的字典增加一个字段
                                    network_value["available"] = float(item["lastvalue"])/1024/1024/1024
                                    #temp_liebiao[k]["available"] = float(item["lastvalue"])/1024/1024/1024
                                    temp_liebiao.append(network_value)
                                    break

                                if len(temp_liebiao) == k:
                                    #否则新生成个字典
                                    temp_dict["key"] = "memory"
                                    temp_dict["available"] = float(item["lastvalue"])/1024/1024/1024
                                    temp_liebiao.append(temp_dict)
                                    break
                                k += 1

                            #print(temp_dict)

                        elif item["key_"].find("vm.memory.size[total]") != -1:
                            k = 1
                            #print(333)
                            for j in temp_liebiao:
                                if "memory" in j.values():
                                    network_value = j
                                    temp_liebiao.remove(j)
                                    network_value["total"] = float(item["lastvalue"]) / 1024 / 1024 / 1024
                                    temp_liebiao.append(network_value)
                                    break
                                if len(temp_liebiao) == k:
                                    temp_dict["key"] = "memory"
                                    temp_dict["total"] = float(item["lastvalue"]) / 1024 / 1024 / 1024
                                    temp_liebiao.append(temp_dict)
                                    break

                                k += 1


                        elif fnmatch.fnmatch(item["key_"], "vfs.fs.size*pfree]"):
                            temp_dict["key"] = "disk"
                            temp_dict["available"] = float(item["lastvalue"])
                            temp_dict["partition"] = item["key_"].split("[")[1].split(",")[0]
                            temp_dict["total"] = float(100)
                            temp_liebiao.append(temp_dict)
                            break
                        else:
                            pass
                        #temp_liebiao.append(temp_dict)

                i += 1
                temp_raw["item"] = temp_liebiao


            # print(temp_raw)
            all_host_monitor_value.append(temp_raw)
            del temp_raw

        msg = "successful"

    except:

        msg = "get zabbix monitor value error."
        logger.error(msg)
        logger.error(sys.exc_info()[0])
        status = -3
    finally:

        result = {
            "result": all_host_monitor_value,
            "msg": msg,
            "status": status
        }
        #print(demjson.encode(result))
        return result



