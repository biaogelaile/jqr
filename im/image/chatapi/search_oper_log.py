#!/usr/bin/env python
#coding=utf-8
from model import *
import sys
from sqlalchemy import desc
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

def search_oper_log(usertoken, companyid):
    status = 0
    #每次查询数量
    #count = 10
    all_page = 1

    result = {
        "result": [],
        "status": status
    }
    temp_result = []
    try:
        #c1 = OperaLog.query.filter_by(companyid=companyid).count()
        #all_page = math.ceil(int(c1)/count)
        # all_company_result = OperaLog.query.filter_by(companyid=companyid).order_by(desc(OperaLog.id)).limit(offset_begin).offset(count).all()

        all_company_result = OperaLog.query.filter_by(companyid=companyid).order_by(desc(OperaLog.id)).all()
        if len(all_company_result) == 0:
            #查询为空
            result["result"] = []
            result["msg"] = "未查找到符合条件的操作日志."
            result["status"] = 1
            return result
        for item in all_company_result:

            sql = """select b.id,b.command_id, b.command, b.command_displayname, b.remark from 
                                    tbl_operacommand  b where b.command like "%{i}%" ;""".format(i=item.exec_com)
            command_search_result = db.session.execute(sql).fetchall()
            if len(command_search_result) > 0:
                command_desc = command_search_result[0]["command_displayname"]
            else:
                command_desc = item.exec_com
            user_image = User.query.filter_by(username=item.username).limit(1).all()
            if len(user_image) == 0:
                image_url = "null"
            else:
                image_url = str(user_image[0].profile)
            msg = " " + item.hostname + "( ip :" + item.ip + ")"
            one_record = {"username": item.username, "user_image": image_url,
                          "exec_time": item.exec_time.strftime("%Y-%m-%d %H:%M:%S"), "operating_command": command_desc,
                          "msg": msg}
            temp_result.append(one_record)

        result["result"] = temp_result
    except:
        result["result"] = []
        result["msg"] = "get operation log was failed ! pls connect admin"
        result["status"] = 1
        logger.error(result["msg"])
        logger.error(sys.exc_info()[0])
    finally:
        result["all_page"] = all_page
        return result


def operation_search_condition(usertoken, companyid, search_command=None, search_user=None):
    msg = "successful"
    status = 0

    result = {
        "result": [],
        "status": status,
        "msg": msg
    }
    if search_command == "0":

        try:
            all_command = OperaCommandGroup.query.all()
            all_groups = {""}
            all_group_result = []

            for item in all_command:
                all_groups.add(item.command_group_id)


                one_group_result = dict()
                one_group_result["groupName"] = item.command_group_displayname
                commands = []
                group_commands = OperaCommand.query.filter_by(command_group_id=item.command_group_id).order_by(desc(OperaCommand.id)).all()
                for com in group_commands:

                    one_recode = dict()
                    one_recode["orderId"] = str(com.command_id)
                    one_recode["name"] = com.command_displayname
                    commands.append(one_recode)
                one_group_result["orders"] = commands
                all_group_result.append(one_group_result)
                #one_group_result.clear()
            result["result"] = all_group_result
        except:
            result["result"] = []
            result["msg"] = "get operation command was failed ! pls connect admin"
            result["status"] = 1
            logger.error(result["msg"])
            logger.error(sys.exc_info()[0])
        finally:
            return result

    elif search_user == "0":
        #查询companyid所有的用户名
        try:
            all_company_result = Opuser.query.filter_by(opcompanyid=companyid).order_by(desc(Opuser.id)).all()
            users = []

            if len(all_company_result) == 0:
                #查询为空
                result["result"] = []
                result["msg"] = "no anything user."
                result["status"] = 1
                return result
            for item in all_company_result:
                one_recode = dict()
                user_image = User.query.filter_by(userid=item.opuserid).limit(1).all()
                if len(user_image) == 0:
                    one_recode["operationImage"] = "null"
                else:
                    one_recode["operationImage"] = str(user_image[0].profile)
                one_recode["operationId"] = item.opuserid
                one_recode["operationName"] = item.opusername
                users.append(one_recode)

            result["result"] = users
        except:
            result["result"] = []
            result["msg"] = "get operation users was failed ! pls connect admin"
            result["status"] = 1
            logger.error(result["msg"])
            logger.error(sys.exc_info()[0])
        finally:
            return result
    else:
        result["result"] = []
        result["msg"] = "未查找到符合条件的操作日志."
        result["status"] = 1


def operation_search_with_condition(usertoken, companyid, search_command_id=None, search_user_id=None, starttime=None, endtime=None):
    status = 0
    all_page = 1

    result = {
        "result": [],
        "status": status
    }
    temp_result = []
    # 开始查询
    try:
        #根据用户userid
        if search_user_id != "":

            result_user = User.query.filter_by(userid=search_user_id).limit(1).all()
            if len(result_user) == 0:
                result["msg"] = "can't find user info."
                result["status"] = 1
                return result
            else:
                username = str(result_user[0].username)
                sql = """select b.id,b.username,b.companyid, b.exec_com, b.ip, b.hostname, b.exec_time from tbl_operalog b
            where username='{u}' order by b.id desc """.format(u=username)
                #all_company_result = OperaLog.query.filter(companyid=companyid).filter(username=username).order_by(desc(OperaLog.id)).all()
                all_company_result = db.session.execute(sql).fetchall()

        elif starttime != "" and endtime != "":
            #根据时间查询
            sql = """select b.id,b.username,b.companyid, b.exec_com, b.ip, b.hostname, b.exec_time from tbl_operalog b
            where companyid='{i}' and exec_time > '{s1} 00:00:01' and exec_time < '{t1} 23:59:59' order by b.id desc""".\
                format(i=companyid,s1=starttime, t1=endtime)
            
            all_company_result = db.session.execute(sql).fetchall()

        elif search_command_id != "":
            sql = """select b.id,b.command_id, b.command, b.command_displayname, b.remark from 
            tbl_operacommand  b where b.command_id={i}""".format(i=int(search_command_id))
            print(sql)
            all_commands = db.session.execute(sql).fetchall()
            sql = """select b.id,b.username,b.companyid, b.exec_com, b.ip, b.hostname, b.exec_time from tbl_operalog b
            where companyid='{i}' and exec_com like "%{j}%" order by b.id desc""".format(i=companyid, j=all_commands[0].command)

            all_company_result = db.session.execute(sql).fetchall()
        else:
            result["result"] = []
            result["msg"] = "未查找到符合条件的操作日志."
            result["status"] = 1


        if len(all_company_result) == 0:
            # 查询为空
            result["result"] = []
            result["msg"] = "未查找到符合条件的操作日志."
            result["status"] = 1
            return result
        for item in all_company_result:

            #后续需要优化，减少查询
            sql = """select b.id,b.command_id, b.command, b.command_displayname, b.remark from 
                        tbl_operacommand  b where b.command like "%{i}%" order by b.id desc;""".format(i=item.exec_com.rstrip())
            command_desc = db.session.execute(sql).fetchall()
            if len(command_desc) == 0:
                cmd_desc = item.exec_com.rstrip()
            else:
                cmd_desc = command_desc[0].command_displayname
            user_image = User.query.filter_by(username=item.username).limit(1).all()
            if len(user_image) == 0:
                image_url = "null"
            else:
                image_url = str(user_image[0].profile)
            msg = " " + item.hostname + "( ip :" + item.ip + ")"
            one_record = {"username": item.username, "user_image": image_url,
                          "exec_time": item.exec_time.strftime("%Y-%m-%d %H:%M:%S"),
                          "operating_command": cmd_desc, "msg": msg}
            temp_result.append(one_record)

        result["result"] = temp_result
    except:
        result["result"] = []
        result["msg"] = "get operation log was failed ! pls connect admin"
        result["status"] = 1
        logger.error(result["msg"])
        logger.error(sys.exc_info()[0])
    finally:
        result["all_page"] = all_page
        return result
