from flask import Flask
from config import *

from flask_sqlalchemy import SQLAlchemy as SQLAlchemyBase
from sqlalchemy.pool import NullPool

class SQLAlchemy(SQLAlchemyBase):
  def apply_driver_hacks(self, app, info, options):
    super(SQLAlchemy, self).apply_driver_hacks(app, info, options)
    options['poolclass'] = NullPool
    options.pop('pool_size', None)

'''配置数据库'''
app = Flask(__name__)
app.config['SECRET_KEY'] ='hard to guess'
app.config['SQLALCHEMY_DATABASE_URI'] = localdatabase

#设置这一项是每次请求结束后都会自动提交数据库中的变动
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN']=True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
#实例化
db = SQLAlchemy(app)

class User(db.Model):
    # 定义表名
    __tablename__ = 'tbl_users'
    # 定义列对象
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(128), nullable=True, comment='用户名')
    userid = db.Column(db.String(128), nullable=True,unique=True, comment='用户名')
    role = db.Column(db.String(128), nullable=True, comment='用户状态')
    #password_hash = db.Column(db.String(64))
    password = db.Column(db.String(128), nullable=False, comment='用户密码')
    mobile = db.Column(db.String(128), nullable=False,unique=True, comment='用户手机号码')
    #1为游客，2为申请待同意用户，3为普通公司用户，4为公司管理员
    profile = db.Column(db.String(128), nullable=False, server_default='http://139.196.107.14:6001/upload/2018-11-12/qMWML0jLCnhs2o1Nv6a5ajpr-defaultUser@3x.png', comment='profile picture')
    logintime = db.Column(db.TIMESTAMP(True), nullable=False, comment='登录时间')
    createtime = db.Column(db.TIMESTAMP(True), nullable=False,comment='创建时间')
    updatetime = db.Column(db.TIMESTAMP(True), nullable=False, comment='更新时间')


class Upload(db.Model):
    # 定义表名
    __tablename__ = 'tbl_uploads'
    # 定义列对象
    id = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.String(128), nullable=True,comment='用户名')
    imageurl = db.Column(db.String(128), nullable=False, comment='upload image picture')
    createtime = db.Column(db.TIMESTAMP(True), nullable=False,comment='创建时间')
    updatetime = db.Column(db.TIMESTAMP(True), nullable=False, comment='更新时间')
db.create_all()