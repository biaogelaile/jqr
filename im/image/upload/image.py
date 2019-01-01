from model import *
import sqlalchemy
import random
import string


def generate_random_str(randomlength=16):
    """
    生成一个指定长度的随机字符串，其中
    string.digits=0123456789
    string.ascii_letters=abcdefghigklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ
    """
    str_list = [random.choice(string.digits + string.ascii_letters) for i in range(randomlength)]
    random_str = ''.join(str_list)
    return random_str


def imageurl_update(usertoken, userid, imageurl):
    try:
        if usertoken != '11111':
            return {'status': 1, 'msg': 'token 不可用'}

        user_image_query = User.query.filter_by(userid=userid).first()
        user_image_query.profile = imageurl
        db.session.commit()

        print(user_image_query.mobile)
        username = user_image_query.username

        mobile = user_image_query.mobile
        role = user_image_query.role
        db.session.close()
        return {'status': 0, 'msg': '修改头像成功', 'mobile': mobile, 'username':username,
                    'userid': userid, 'role':role, 'imageUrl': imageurl}
    except sqlalchemy.exc.OperationalError:
        return {'Oooops': 'There is a problem with the database'}

def image_insert(usertoken, userid, imageurl):
    try:

        if usertoken != '11111':
            return {'status': 1, 'msg': 'token不可用'}

        insert_image = Upload(userid=userid, imageurl=imageurl)
        db.session.add(insert_image)
        db.session.commit()
        user_image_query = User.query.filter_by(userid=userid).first()
        username = user_image_query.username
        mobile = user_image_query.mobile
        role = user_image_query.role
        db.session.close()

        return {'status': 0, 'msg': '上传成功', 'mobile': mobile, 'username': username,
                'userid': userid, 'role': role, 'uploadUrl': imageurl}

    except sqlalchemy.exc.OperationalError:
        return {'Oooops': 'There is a problem with the database'}