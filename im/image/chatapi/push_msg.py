# coding=utf-8

from APISender import APISender
from base.APIMessage import *
from APITools import *
from APISubscribe import *
import sys


def push_msg_to_android(userid,usertoken, send_packagename, send_title, send_msg, send_msg_desc, send_pass_through):
    APP_SecKey = r"lsoNVMUZH69YvcsLR6SHNQ=="
    result_code = 0
    try:

        #设置app的包名packageName
        #package_name = "com.domain.operationrobot"
        package_name = send_packagename
        #设置在通知栏展示的通知的标题
        title = send_title.replace("'", '')
        #设置要发送的消息内容, 不允许全是空白字符
        msg = send_msg.replace("'", '')
        #设置在通知栏展示的通知描述
        msg_desc = send_msg_desc.replace("'", '')
        #1表示透传, 0表示通知栏, 默认通知栏
        pass_through = int(send_pass_through)

        # build android message
        message = PushMessage() \
            .restricted_package_name(package_name) \
            .title(title).description(msg_desc) \
            .pass_through(pass_through).payload(msg) \
            .extra({Constants.extra_param_notify_effect: Constants.notify_launcher_activity})

    except:
        print("get parameters value error ! ", sys.exc_info()[0])
        msg = "get parameters value error "
        result = {
            "msg": msg,
            "status": result_code
        }
        return result

    try:
        sender = APISender(APP_SecKey)
        recv = sender.send(message.message_dict(), userid)
        print(recv)
        tools = APITools(APP_SecKey)
        # 查询消息状态
        print(tools.query_message_status('msg_id').data)
        # 验证reg_id是否无效
        print(tools.validate_reg_ids(['reg_id1', 'reg_id2']))
        # 获取无效reg_id
        print(tools.query_invalid_reg_ids())
        # 获取无效alias
        print(tools.query_invalid_aliases())
        # 获取设备订阅topic
        print(tools.query_device_topics('package_name', 'reg_id'))
        print(tools.query_device_presence('package_name', ['reg_id1', 'reg_id2']))
        # 获取设备设置alias
        print(tools.query_device_aliases('package_name', 'reg_id'))
        # 检查定时任务是否存在
        print(tools.check_schedule_job_exist('msg_id'))
    except:
        print("send msg was failed ! ", sys.exc_info()[0])
        result_code = 1
        msg = "send msg was failed "
    finally:
        result = {
            "msg": msg,
            "status": result_code
        }
        return result


def push_msg_to_ios(userid,usertoken, send_packagename, send_title, send_key, send_value, send_msg_desc):
    APP_SecKey = r"XWd6+oOcSmliC4jJJsdrcw=="
    result_code = 0
    try:

        #设置app的包名packageName
        #package_name = "com.domain.operationrobot"
        package_name = send_packagename
        #设置在通知栏展示的通知的标题
        title = send_title.replace("'", '')
        #自定义键值对, 控制客户端行为
        send_key = send_key.replace("'", '')

        #设置在通知栏展示的通知描述
        msg_desc = send_msg_desc.replace("'", '')
    except:
        print("get parameters value error ! ", sys.exc_info()[0])
        result_code = 1
        msg = "get parameters value error "
        result = {
            "msg": msg,
            "status": result_code
        }
        return result

    try:
        sender = APISender(APP_SecKey)
        message_ios = PushMessage() \
            .description(msg_desc) \
            .sound_url("default") \
            .badge(1) \
            .extra({send_key: send_value})
        recv_ios = sender.send(message_ios.message_dict_ios(), userid)
        print(recv_ios)


        tools = APITools(APP_SecKey)
        # 查询消息状态
        print(tools.query_message_status('msg_id').data)
        # 验证reg_id是否无效
        print(tools.validate_reg_ids(['reg_id1', 'reg_id2']))
        # 获取无效reg_id
        print(tools.query_invalid_reg_ids())
        # 获取无效alias
        print(tools.query_invalid_aliases())
        # 获取设备订阅topic
        print(tools.query_device_topics('package_name', 'reg_id'))
        print(tools.query_device_presence('package_name', ['reg_id1', 'reg_id2']))
        # 获取设备设置alias
        print(tools.query_device_aliases('package_name', 'reg_id'))
        # 检查定时任务是否存在
        print(tools.check_schedule_job_exist('msg_id'))
    except:
        print("send msg was failed ! ", sys.exc_info()[0])
        result_code = 1
        msg = "send msg was failed "
    finally:
        result = {
            "msg": msg,
            "status": result_code
        }
        return result

def push_msg_to_ios10(userid,usertoken, send_packagename, send_title, send_key, send_value, send_msg_desc):
    APP_SecKey = r"XWd6+oOcSmliC4jJJsdrcw=="
    result_code = 0
    message_ios10 = PushMessage() \
        .aps_title("title") \
        .aps_subtitle("subtitle") \
        .aps_body("body") \
        .aps_mutable_content("1") \
        .sound_url("default") \
        .badge(1) \
        .category("action") \
        .extra({"key": "value"})
    try:

        #设置app的包名packageName
        #package_name = "com.domain.operationrobot"
        package_name = send_packagename
        #设置在通知栏展示的通知的标题
        title = send_title.replace("'", '')
        #自定义键值对, 控制客户端行为
        send_key = send_key.replace("'", '')

        #设置在通知栏展示的通知描述
        msg_desc = send_msg_desc.replace("'", '')
    except:
        print("get parameters value error ! ", sys.exc_info()[0])
        result_code = 1
        msg = "get parameters value error "
        result = {
            "msg": msg,
            "status": result_code
        }
        return result

    try:
        sender = APISender(APP_SecKey)
        message_ios = PushMessage() \
            .description(msg_desc) \
            .sound_url("default") \
            .badge(1) \
            .extra({send_key: send_value})
        recv_ios = sender.send(message_ios.message_dict_ios(), userid)
        print(recv_ios)


        tools = APITools(APP_SecKey)
        # 查询消息状态
        print(tools.query_message_status('msg_id').data)
        # 验证reg_id是否无效
        print(tools.validate_reg_ids(['reg_id1', 'reg_id2']))
        # 获取无效reg_id
        print(tools.query_invalid_reg_ids())
        # 获取无效alias
        print(tools.query_invalid_aliases())
        # 获取设备订阅topic
        print(tools.query_device_topics('package_name', 'reg_id'))
        print(tools.query_device_presence('package_name', ['reg_id1', 'reg_id2']))
        # 获取设备设置alias
        print(tools.query_device_aliases('package_name', 'reg_id'))
        # 检查定时任务是否存在
        print(tools.check_schedule_job_exist('msg_id'))
    except:
        print("send msg was failed ! ", sys.exc_info()[0])
        result_code = 1
        msg = "send msg was failed "
    finally:
        result = {
            "msg": msg,
            "status": result_code
        }
        return result



