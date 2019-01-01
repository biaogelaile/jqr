from model import *
import sqlalchemy


def usermessage_insert(usertoken, userid, companyid, usernewmessage, usermsgid):
    try:
        if usertoken != '11111':
            return {'status': 1, 'msg': 'Ooooops, token不可用'}

        usernewmessage = str(usernewmessage)

        insert_mobile = Talkmsg(msgid=usermsgid, msguserid=userid, msgcompanyid=companyid, message=usernewmessage)
        db.session.add(insert_mobile)
        db.session.commit()
        db.session.close()
        return {'status':0, 'msg': 'ok'}
    except sqlalchemy.exc.OperationalError:
        return {'Oooops': '数据库连接似乎出了问题'}

def usermessage_query(usertoken, userid, companyid, usermsgid):
    try:
        if usertoken != '11111':
            return {'status': 1, 'msg': 'Ooooops, token不可用'}

        check_user_role_query = User.query.filter_by(userid=userid).first()
        user_role = check_user_role_query.role
        if user_role == '1' or user_role == '2':
            db.session.close()
            return {'status': 2, 'msg': ''}

        if usermsgid:

            message_create_time_query = Talkmsg.query.filter_by(msgid=usermsgid, msgcompanyid=companyid).first()

            print(message_create_time_query)
            message_create_time = message_create_time_query.createtime
            message_database_id = message_create_time_query.id
            user_message_query_page = Talkmsg.query.filter(Talkmsg.createtime >= message_create_time,
                                                           Talkmsg.msgcompanyid==companyid,
                                                           Talkmsg.msgid != usermsgid,
                                                           Talkmsg.id > message_database_id).all()

            user_message_query_page_total = len(user_message_query_page)

            if user_message_query_page_total > 300:

                user_message_query_page = Talkmsg.query.filter(Talkmsg.msgcompanyid == companyid).order_by(
                                        Talkmsg.createtime.desc()).paginate(1, per_page=300, error_out=False)

                rs = user_message_query_page.items
                msg_rs_list = []
                for user_message in rs:
                    if user_message.msgid != usermsgid:
                        return_message = eval(user_message.message)
                        msg_rs_list.append(return_message)
                db.session.close()
                return {'status': 0, 'msg':'查询成功', 'data':msg_rs_list}
            else:
                msg_rs_list = []
                for user_message in user_message_query_page:
                    if user_message.msgid != usermsgid:
                        return_message = eval(user_message.message)
                        msg_rs_list.append(return_message)
                db.session.close()
                return {'status': 0, 'msg':'查询成功', 'data':msg_rs_list}


        else:
            user_message_query_page = Talkmsg.query.filter(Talkmsg.msgcompanyid == companyid).order_by(
                Talkmsg.createtime.desc()).paginate(1, per_page=300, error_out=False)



            rs = user_message_query_page.items

            msg_rs_list = []
            for user_message in rs:
                if user_message.msgid != usermsgid:
                    return_message = eval(user_message.message)
                    msg_rs_list.append(return_message)
            db.session.close()
            return {'status': 0, 'msg': '查询成功', 'data': msg_rs_list}

    except sqlalchemy.exc.OperationalError:
        return {'Oooops': '数据库连接似乎出了问题'}
