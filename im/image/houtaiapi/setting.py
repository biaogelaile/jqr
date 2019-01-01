from model import *

def configsGet(userid, token):
    if token != '11111':
        return {'status':1, 'msg':'token不可用'}
    #获取配置
    backstageinfo_query = Backstage.query.first()
    backstageinfo_expire = backstageinfo_query.companyexpire
    backstageinfo_tryoutdate = backstageinfo_query.tryoutdata
    backstageinfo_custom = backstageinfo_query.customerservicemobile
    rs = {'expire':backstageinfo_expire, 'trydate':backstageinfo_tryoutdate, 'customerservice':backstageinfo_custom}
    db.session.close()
    return rs


def configsChange(userid, token, customerservice, expire, trydate):
    if token != '11111':
        return {'status':1, 'msg':'token不可用'}
    #修改后台配置
    backstageinfo_query = Backstage.query.first()
    if customerservice:
        backstageinfo_query.customerservicemobile = customerservice
    if expire:
        backstageinfo_query.companyexpire = expire
    if trydate:
        backstageinfo_query.tryoutdata = trydate
    db.session.commit()

    rs = {'status':0, 'msg':'设置成功','expire':expire, 'trydate':trydate, 'customerservice':customerservice}
    db.session.close()
    return rs

def coustomMobile(userid, token):
    if token != '11111':
        return {'status':1, 'msg':'token不可用'}
    #修改后台配置
    backstageinfo_query = Backstage.query.first()
    if backstageinfo_query:
        custommobile = backstageinfo_query.customerservicemobile

    rs = {'status':0, 'msg':'查询成功','customermobile':custommobile}
    db.session.close()
    return rs
