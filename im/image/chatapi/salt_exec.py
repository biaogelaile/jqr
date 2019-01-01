#!/usr/bin/env python
# _*_ coding:utf-8 _*_

from model import *
import requests
import json
try:
    import cookielib
except:
    import http.cookiejar as cookielib
import ssl
import urllib3
import sys
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import os
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
logger = logging.getLogger("salt_exec")
logger.addHandler(fileshandle)
logger.setLevel(logging.INFO)
context = ssl._create_unverified_context()
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

salt_api = "https://testsaltapi.wintruelife.com/"


class SaltApi:
    """
    定义salt api接口的类
    初始化获得token
    """
    def __init__(self, url):
        self.url = url
        self.username = "saltapi"
        self.password = "Xdhg002539"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36",
            "Content-type": "application/json"
        }
        self.params = {'client': 'local', 'fun': '', 'tgt': ''}
        # self.params = {'client': 'local', 'fun': '', 'tgt': '', 'arg': ''}
        self.login_url = salt_api + "login"
        self.login_params = {'username': self.username, 'password': self.password, 'eauth': 'pam'}
        self.token = self.get_data(self.login_url, self.login_params)['token']
        self.headers['X-Auth-Token'] = self.token

    def get_data(self, url, params):
        send_data = json.dumps(params)
        request = requests.post(url, data=send_data, headers=self.headers, verify=False)
        if request.status_code != 200:
            # result = {
            #     "result": "salt服务" + salt_api + "连接失败。 http code： " + str(request.status_code),
            #     "status": 1
            # }
            logger.error("salt服务" + salt_api + "连接失败。 http code： " + str(request.status_code))
            print("salt服务" + salt_api + "连接失败。 http code： " + str(request.status_code))
            #return result
        assert request.status_code == 200


        response = request.json()
        result = dict(response)
        return result['return'][0]

    def salt_command(self, tgt, method, arg=None):
        """远程执行命令，相当于salt 'client1' cmd.run 'free -m'"""
        if arg:
            params = {'client': 'local', 'fun': method, 'tgt': tgt, 'arg': arg}
        else:
            params = {'client': 'local', 'fun': method, 'tgt': tgt}
        result = self.get_data(self.url, params)
        return result

def main(username,  usertoken, clientip, command, companyid, hostname):

    status = 0
    msg = ""
    result = dict()
    salt = SaltApi(salt_api)
    #salt_client = '10.0.60.187'
    salt_client = clientip
    salt_test = 'test.ping'
    salt_method = 'cmd.run'
    salt_params = command

    try:

        result_test = salt.salt_command(salt_client, salt_test)
        # for i in result_test.keys():
        #     print(i, ': ', result_test[i])

        if not bool(result_test[salt_client]):
            msg = "can not connect desc server."
            logger.error(msg)
            status = 1
            result = {
                "result": msg,
                "status": status
            }
            return json.dumps(result)
    except:
        msg = "can not connect desc server."
        logger.error(msg)
        logger.error(sys.exc_info()[0])
        status = 1
        result = {
            "result": msg,
            "status": status
        }
        return json.dumps(result)

    #执行输入的命令
    try:
        with ThreadPoolExecutor(2) as executor:
            cmd_result = executor.submit(salt.salt_command, salt_client, salt_method, salt_params)
            result2 = cmd_result.result()
        #result2 = salt.salt_command(salt_client, salt_method, salt_params)
            for i in result2.keys():
                cur_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                #print(username, clientip, command, cur_time, companyid)
                insert_log = OperaLog(username=str(username), ip=str(clientip), hostname=hostname, exec_com=str(command),
                                      exec_time=cur_time, companyid=str(companyid))

                db.session.add(insert_log)
                db.session.commit()
                msg = result2[i]
                status = 0
            # msg = result2[i]
    except:
        msg = "the " + clientip + " exec command '" + command + "' has failed."
        logger.error(msg)
        logger.error(sys.exc_info()[0])
        status = 1
    finally:
        db.session.close()
        result = {
            'result': msg,
            'status': status
        }
        return result


def exec_passport(username,  usertoken, clientip, commandid, companyid):
    status = 0
    msg = "successful"
    result = dict()
    salt = SaltApi(salt_api)
    #salt_client = '10.0.60.187'
    salt_client = clientip
    salt_test = 'test.ping'
    salt_method = 'cmd.run'
    try:
        monitor_host = Monitor.query.filter_by(zabbixhostip=clientip).first()

        if not monitor_host:
            status = 1
            result = {
                "result": [],
                "msg": "没找到服务器，请重新输入.",
                "status": status
            }
            return result

    except:
        status = 1
        result = {
            "result": [],
            "msg": "没找到服务器，请重新输入.",
            "status": status
        }
        logger.error("没找到服务器，请重新输入.")
        logger.error(sys.exc_info()[0])
        return result


    salt_params = OperaCommand.query.filter_by(command_id=commandid).limit(1).all()
    try:

        result_test = salt.salt_command(salt_client, salt_test)
        if not bool(result_test[salt_client]):
            print("can not connect desc server.")
            msg = "can not connect desc server."
            status = 1
            result = {
                "result": [],
                "msg": msg,
                "status": status
            }
            return result
    except:
        msg = "can not connect desc server."
        print(msg, sys.exc_info()[0])
        status = 1
        result = {
            "result": [],
            "msg": msg,
            "status": status
        }
        return result

    #执行输入的命令
    try:
        with ThreadPoolExecutor(2) as executor:
            cmd_result = executor.submit(salt.salt_command, salt_client, salt_method, salt_params)
            result2 = cmd_result.result()
        #result2 = salt.salt_command(salt_client, salt_method, salt_params[0].command)
            for i in result2.keys():
                command_result = dict()
                command_result_list = []

                cur_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                #print(username, clientip, command, cur_time, companyid)
                insert_log = OperaLog(username=str(username), ip=str(clientip), hostname=monitor_host.zabbixhostname,
                                      exec_com=str(salt_params[0].command), exec_time=cur_time, companyid=str(companyid))

                db.session.add(insert_log)
                db.session.commit()
                command_result["name"] = monitor_host.zabbixhostname
                command_result["host"] = monitor_host.zabbixhostip
                for item1 in result2[i].split("\n"):
                    if item1.find("Blk_read") > 0:
                        continue
                    item_result = dict()
                    temp_list = item1.split(" ")

                    item_result["Device"] = temp_list[0]
                    item_result["Blk_read"] = temp_list[1]
                    item_result["Blk_wrtn"] = temp_list[2]

                    command_result_list.append(item_result)

                command_result["command_result"] = command_result_list
                result['result'] = command_result
                msg = "当前 " + monitor_host.zabbixhostname + " (ip:"+clientip + ") 磁盘IO"
                status = 0
            # msg = result2[i]
    except:
        msg = "the " + clientip + " exec command '" + salt_params + "' has failed."
        logger.error(msg)
        logger.error(sys.exc_info()[0])
        status = 1
    finally:
        db.session.close()
        result['msg'] = msg
        result['status'] = status

        return result