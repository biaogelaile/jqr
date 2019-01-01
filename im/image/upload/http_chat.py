#coding=utf-8
from flask import jsonify, request
from image import *
import os, datetime
from config import *

#聊天上传图片
@app.route('/api/v1/uploads', methods=['POST'])
def upload_file():
    token = request.form.get('token')
    userid = token.split('-')[0]
    usertoken = token.split('-')[1]
    today = str(datetime.date.today())
    print(today)

    if os.path.exists('upload/' + today):       # 判断文件夹是否存在
        pass
    else:
        os.mkdir('upload/' + today)

    file = request.files['image']
    print(file.filename)

    hash_value = generate_random_str(24)

    filename = hash_value + '-' + file.filename
    file.save(os.path.join('upload/' + today,filename))
    file_url = url + '/upload/' + today + '/' + filename

    rs = image_insert(usertoken, userid, file_url)

    return jsonify(rs)



@app.route('/api/v1/headp', methods=['POST'])
def upload_head():
    token = request.form.get('token')
    print(token)
    file = request.files['image']
    print(file.filename)
    userid = token.split('-')[0]
    usertoken = token.split('-')[1]

    today = str(datetime.date.today())
    if os.path.exists('upload/' + today):       # 判断文件夹是否存在
        pass
    else:
        os.mkdir('upload/' + today)
    file = request.files['image']
    hash_value = generate_random_str(24)

    filename = hash_value + '-' + file.filename
    file.save(os.path.join('upload/' + today,filename))
    file_url = url + '/upload/' + today + '/' + filename
    rs = imageurl_update(usertoken, userid, file_url)
    return jsonify(rs)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=6000)