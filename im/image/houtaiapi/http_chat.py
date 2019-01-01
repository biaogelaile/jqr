#coding=utf-8
from flask import jsonify, request
from user import *
from company import *
from index import *
from setting import *


#后台功能
@app.route('/backstage/index', methods=['GET'])
def BackstageIndex():
    token = request.args.get('token')
    userid = token.split('-')[0]
    usertoken = token.split('-')[1]
    joininfors = backstage(userid, usertoken)
    return jsonify(joininfors)


#公司相关
@app.route('/backstage/companymanages', methods=['GET'])
def BackstageCm():
    token = request.args.get('token')
    userid = token.split('-')[0]
    usertoken = token.split('-')[1]
    if request.args.get('page'):
        page = request.args.get('page')
    else:
        page = 1
    joininfors = backstagecms(userid, usertoken, page)
    return jsonify(joininfors)

@app.route('/backstage/companymanage/<string:companyname>', methods=['GET'])
def BackstageSearch(companyname):
    token = request.args.get('token')
    userid = token.split('-')[0]
    usertoken = token.split('-')[1]
    if request.args.get('page'):
        page = request.args.get('page')
    else:
        page = 1
    joininfors = backstagecm(userid, usertoken, companyname, page)
    return jsonify(joininfors)

@app.route('/backstage/tryouts', methods=['GET'])
def BackstageTryOut():
    token = request.args.get('token')
    userid = token.split('-')[0]
    usertoken = token.split('-')[1]
    if request.args.get('page'):
        page = request.args.get('page')
    else:
        page = 1
    joininfors = backstagetryouts(userid, usertoken, page)
    return jsonify(joininfors)

@app.route('/backstage/expiringcompanys', methods=['GET'])
def BackstageExpireC():
    token = request.args.get('token')
    userid = token.split('-')[0]
    usertoken = token.split('-')[1]
    if request.args.get('page'):
        page = request.args.get('page')
    else:
        page = 1
    joininfors = backstageexpiring(userid, usertoken, page)
    return jsonify(joininfors)


@app.route('/backstage/expiredcompanys', methods=['GET'])
def BackstageExpired():
    token = request.args.get('token')
    userid = token.split('-')[0]
    usertoken = token.split('-')[1]
    if request.args.get('page'):
        page = request.args.get('page')
    else:
        page = 1
    joininfors = backstageexpired(userid, usertoken, page)
    return jsonify(joininfors)

@app.route('/backstage/newcompanys', methods=['GET'])
def BackstageNewCompanys():
    token = request.args.get('token')
    userid = token.split('-')[0]
    usertoken = token.split('-')[1]
    if request.args.get('page'):
        page = request.args.get('page')
    else:
        page = 1
    joininfors = backstagenewcompanytoday(userid, usertoken, page)
    return jsonify(joininfors)


@app.route('/backstage/companymembers', methods=['GET'])
def BackstageCompanyMember():
    token = request.args.get('token')
    userid = token.split('-')[0]
    usertoken = token.split('-')[1]
    if request.args.get('page'):
        page = request.args.get('page')
    else:
        page = 1
    companyname = request.args.get('companyname')
    searchcompanynamers = companymemberinfo(userid, usertoken, page, companyname)
    return jsonify(searchcompanynamers)

@app.route('/backstage/companyhosts', methods=['GET'])
def BackstageCompanyZabbix():
    token = request.args.get('token')
    userid = token.split('-')[0]
    usertoken = token.split('-')[1]
    if request.args.get('page'):
        page = request.args.get('page')
    else:
        page = 1
    companyname = request.args.get('companyname')
    searchcompanynamers = companyhostsinfo(userid, usertoken, page, companyname)
    return jsonify(searchcompanynamers)


@app.route('/backstage/companyexpire', methods=['PATCH'])
def BackstageCompanyExpire():
    request_data = request.get_json()
    token = request_data['token']
    userid = token.split('-')[0]
    usertoken = token.split('-')[1]
    time_chuo = request_data['expiredate']
    companyname = request_data['companyname']
    searchcompanynamers = companyexpire(userid, usertoken,companyname, time_chuo)
    return jsonify(searchcompanynamers)

@app.route('/backstage/companymanager', methods=['PATCH'])
def BackstageCompanyPatch():
    request_data = request.get_json()
    token = request_data['token']
    userid = token.split('-')[0]
    usertoken = token.split('-')[1]
    oldcompanyname = request_data['oldcompanyname']
    newcompanyname = request_data['newcompanyname']
    companyemail = request_data['companyemail']
    mark = request_data['mark']
    disable = request_data['disable']

    searchcompanynamers = companypatch(userid, usertoken,oldcompanyname, newcompanyname,companyemail,mark, disable)
    return jsonify(searchcompanynamers)


@app.route('/backstage/companymanager', methods=['DELETE'])
def BackstageCompanyDelete():
    token = request.args.get('token')
    userid = token.split('-')[0]
    usertoken = token.split('-')[1]
    companyname = request.args.get('companyname')

    searchcompanynamers = companydelete(userid, usertoken,companyname)
    return jsonify(searchcompanynamers)


#============
#用户相关
@app.route('/backstage/users', methods=['GET'])
def BackstageUsers():
    token = request.args.get('token')
    userid = token.split('-')[0]
    usertoken = token.split('-')[1]
    if request.args.get('page'):
        page = request.args.get('page')
    else:
        page = 1
    joininfors = backstageusers(userid, usertoken, page)
    return jsonify(joininfors)

@app.route('/backstage/newusers', methods=['GET'])
def BackstageNewUsers():
    token = request.args.get('token')
    userid = token.split('-')[0]
    usertoken = token.split('-')[1]
    if request.args.get('page'):
        page = request.args.get('page')
    else:
        page = 1
    joininfors = backstagenewusers(userid, usertoken, page)
    return jsonify(joininfors)


@app.route('/backstage/usersearch', methods=['GET'])
def BackstageUserSearch():
    token = request.args.get('token')
    userid = token.split('-')[0]
    usertoken = token.split('-')[1]
    if request.args.get('page'):
        page = request.args.get('page')
    else:
        page = 1
    searchcompanyname = request.args.get('companyname')
    searchmobile = request.args.get('mobile')

    print('lalalalla:',searchcompanyname, searchmobile)
    if searchcompanyname != "" and searchmobile == "":
        companyname = request.args.get('companyname')
        searchcompanynamers = backstagesearchuserscompany(userid, usertoken, page, companyname)
        return jsonify(searchcompanynamers)
    if searchmobile !="" and searchcompanyname == "":
        mobile = request.args.get('mobile')
        joininfors = backstagesearchusersmobile(userid, usertoken, page, mobile)
        return jsonify(joininfors)
    #joininfors = backstagesearchusersmobile(userid, usertoken, page, companyname, mobile)
    if searchmobile != "" and searchcompanyname != "":
        mobile = request.args.get('mobile')
        companyname = request.args.get('companyname')
        searchallrs = backstagesearchusersall(userid, usertoken, page, mobile, companyname)
        return jsonify(searchallrs)
    if searchmobile == "" and searchcompanyname == "":
        print('lalal')
        joininfors = backstageusers(userid, usertoken, page)
        return jsonify(joininfors)


@app.route('/backstage/tourist', methods=['GET'])
def BackstageTouristUsers():
    token = request.args.get('token')
    userid = token.split('-')[0]
    usertoken = token.split('-')[1]
    if request.args.get('page'):
        page = request.args.get('page')
    else:
        page = 1
    joininfors = backstagetourist(userid, usertoken, page)
    return jsonify(joininfors)


@app.route('/backstage/user', methods=['PATCH'])
def BackstagePatchUsers():
    request_data = request.get_json()
    token = request_data['token']
    adminuserid = token.split('-')[0]
    adminusertoken = token.split('-')[1]
    userstatus = request_data['userdisable']
    userid = request_data['userid']
    joininfors = userdisable(adminuserid, adminusertoken, userstatus, userid)
    return jsonify(joininfors)

@app.route('/backstage/user', methods=['DELETE'])
def BackstageDeleteUsers():
    token = request.args.get('token')
    adminuserid = token.split('-')[0]
    adminusertoken = token.split('-')[1]
    userid = request.args.get('userid')
    joininfors = userdelete(adminuserid, adminusertoken, userid)
    return jsonify(joininfors)


#==========
#配置相关
@app.route('/backstage/configs', methods=['GET'])
def BackstageConfigsGet():
    token = request.args.get('token')
    userid = token.split('-')[0]
    usertoken = token.split('-')[1]
    joininfors = configsGet(userid, usertoken)
    return jsonify(joininfors)

@app.route('/backstage/configs', methods=['POST'])
def BackstageConfigsChange():
    request_data = request.get_json()
    token = request_data['token']
    userid = token.split('-')[0]
    usertoken = token.split('-')[1]
    if 'customerservice' in request_data:
        customerservice = request_data['customerservice']
    else:
        customerservice = None
    if 'expire' in request_data:
        expire = request_data['expire']
    else:
        expire = None
    if 'trydate' in request_data:
        trydate = request_data['trydate']
    else:
        trydate = None
    joininfors = configsChange(userid, usertoken, customerservice, expire, trydate)
    return jsonify(joininfors)

#=========
#管理员相关
@app.route('/backstage/login', methods=['POST'])
def AdminLogin():
    request_data = request.get_json()
    print(request_data)
    username = request_data['username']
    password = request_data['password']
    joininfors = AdminInfo(username, password)
    return jsonify(joininfors)

@app.route('/backstage/admin', methods=['PATCH'])
def AdminPatch():
    request_data = request.get_json()
    oldpassword = request_data['oldpassword']
    newpassword = request_data['newpassword']
    token = request_data['token']
    adminuserid = token.split('-')[0]
    admintoken = token.split('-')[1]
    joininfors = adminpatch(adminuserid, admintoken, oldpassword, newpassword)
    return jsonify(joininfors)



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=7000)
