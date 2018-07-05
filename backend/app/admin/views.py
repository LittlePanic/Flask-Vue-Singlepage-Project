# # coding:utf8
# from . import admin
# from flask import render_template, redirect, url_for, flash, session, request, abort, jsonify
# from app.models import User, Auth, Role, Admin, Adminlog, Card, Userlog, Express, Formids, Userlog
# from functools import wraps
# from app import db, app
# from app.admin.forms import LoginForm, AdminForm, AuthForm, RoleForm, Admin_EditForm, CardForm, GetExpressForm
# import json
# from werkzeug.utils import secure_filename
# from werkzeug.security import generate_password_hash
# import os
# from datetime import datetime
# import uuid
# import requests
# from random import *
#
# UPLOAD_FOLDER = 'app/static/upload'
# ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])
#
# ''' 装饰器部分 '''
#
#
# def admin_login_req(f):  # 登录装饰器
#     @wraps(f)
#     def decorated_function(*args, **kwargs):
#         if "admin" not in session:  # session 没有key可以调用 session.has_key("admin")  会报错
#             return redirect(url_for("admin.admin_login", next=request.url))
#         return f(*args, **kwargs)
#
#     return decorated_function
#
#
# # 权限控制装饰器
# def admin_auth(f):
#     @wraps(f)
#     def decorated_function(*args, **kwargs):
#         admin = Admin.query.join(
#             Role
#         ).filter(
#             Role.id == Admin.role_id,
#             Admin.id == session['admin_id']
#         ).first()
#         if admin.is_super == 0:
#             return f(*args, **kwargs)
#         auths = admin.role.auths
#         auths = list(map(lambda v: int(v), auths.split(",")))
#         auth_list = Auth.query.all()
#         urls = [v.url for v in auth_list for val in auths if val == v.id]
#         rule = request.url_rule
#         print('urls' + str(urls))
#         if str(rule) not in urls:  # 需要将当前的rule转化为字符串，然后再到urls里面遍历
#             abort(404)
#         return f(*args, **kwargs)
#
#     return decorated_function
#
#
# ''' 装饰器部分结束 '''
#
# ''' 首页部分 '''
# @app.route('/api/random')
# def random_number():
#     response = {
#         'randomNumber': randint(1, 100)
#     }
#     return jsonify(response)
#
#
# @app.route('/', defaults={'path': ''})
# @app.route('/<path:path>')
# def catch_all(path):
#     if app.debug:
#         return requests.get('http://localhost:8080/{}'.format(path)).text
#     return render_template("index.html")
#
#
# @admin.route("/", methods=["GET", "POST"])
# @admin_login_req
# def index():
#     return render_template("admin/index.html")
#
#
# ''' 首页部分结束 '''
#
# ''' 登录退出部分 '''
#
#
# # 登录
# @admin.route("/admin/login", methods=["GET", "POST"])
# def admin_login():
#     form = LoginForm()
#     if form.validate_on_submit():  # 这步比较厉害（并且和前面的forms里面定义的validate_account有很大关系，感觉他会调用validate_account来判断是否有用户名），填写表单后执行这句，然后form才会有数据，可以通过form.data查看
#         data = form.data
#         admin = Admin.query.filter_by(name=data["account"]).first()  # 查找第一条满足要求的account字段
#         if not admin.check_pwd(data["pwd"]):  # 通过调用models里面的check_pwd方法，搞定密码校对问题
#             flash("密码错误！", "err")  # 简单的输出报错，到login.html里面的{% for msg in get_flashed_messages() %} 里面
#             return redirect(url_for("admin.admin_login"))  # 错误，自然要重定向到登录页面
#         session["admin"] = data["account"]  # 目前说session就是类似cookie的东西
#         session["admin_id"] = admin.id
#
#         adminlog = Adminlog(
#             admin_id=admin.id,
#             ip=request.remote_addr,
#             log_type='login'
#         )
#         db.session.add(adminlog)
#         db.session.commit()
#
#         return redirect(request.args.get("next") or url_for("admin.index"))  # 成功，自然要返回的后台主要啦
#     return render_template("admin/login.html", form=form)  # 表示用户名都没有，就会返回一些报错，这个form不是一般的form
#
#
# # 退出登录
# @admin.route("/admin/logout", methods=["GET", "POST"])
# @admin_login_req
# def admin_logout():
#     session.pop("admin", None)  # 清空登录信息
#     session.pop("admin_id", None)
#     return redirect(url_for('admin.admin_login'))
#
#
# ''' 登录退出部分结束 '''
#
# ''' 充值卡部分 '''
#
#
# # 充值卡列表
# @admin.route("/admin/all_card_list/<int:page>/", methods=["GET", "POST"])
# @admin_auth
# @admin_login_req
# def all_card_list(page=None):
#     if page is None:
#         page = 1
#     page_data = Card.query.order_by(
#         Card.id
#     ).paginate(page=page, per_page=10000)
#     return render_template("admin/card_list.html", page_data=page_data)
#
#
# # 充值卡列表
# @admin.route("/admin/card_list/<int:page>/", methods=["GET", "POST"])
# @admin_auth
# @admin_login_req
# def card_list(page=None):
#     if page is None:
#         page = 1
#     page_data = Card.query.filter_by(
#         admin_name=session["admin"]
#     ).paginate(page=page, per_page=10000)
#     return render_template("admin/card_list.html", page_data=page_data)
#
#
# # 添加充值卡
# @admin.route("/admin/card_add/", methods=["GET", "POST"])
# @admin_auth
# @admin_login_req
# def card_add():
#     form = CardForm()
#     if form.validate_on_submit():
#         data = form.data
#         card = Card(
#             card_id=data["CardID"],
#             card_pwd=data["CardPWD"],
#             admin_name=session["admin"]
#         )
#         db.session.add(card)
#         db.session.commit()
#
#         adminlog = Adminlog(
#             admin_id=session["admin_id"],
#             ip=request.remote_addr,
#             log_type='card_add'
#         )
#         db.session.add(adminlog)
#         db.session.commit()
#
#         flash("添加充值卡成功", "ok")
#     return render_template("admin/card_add.html", form=form)
#
#
# # 编辑充值卡
# @admin.route("/card/edit/<int:id>/", methods=["GET", "POST"])
# @admin_login_req
# @admin_auth
# def card_edit(id=None):
#     form = CardForm()
#     card = Card.query.filter_by(id=id).first_or_404()  # 到数据库找id，有的话就get到，没有的话就返回404
#     if form.validate_on_submit():  # 接收前端传送过来的数据字段
#         data = form.data
#         card.card_id = data["CardID"]
#         card.card_pwd = data["CardPWD"]
#         db.session.add(card)
#         db.session.commit()
#         flash("修改充值卡成功", "ok")
#
#         adminlog = Adminlog(
#             admin_id=session["admin_id"],
#             ip=request.remote_addr,
#             log_type='card_edit'
#         )
#         db.session.add(adminlog)
#         db.session.commit()
#
#         redirect(url_for("admin.card_edit", id=id))
#     return render_template("admin/card_edit.html", form=form, card=card)
#
#
# # 删除充值卡
# @admin.route("/card/del/<int:id>/", methods=["GET", "POST"])
# @admin_login_req
# @admin_auth
# def card_del(id):
#     card = Card.query.filter_by(id=id).first_or_404()
#     db.session.delete(card)
#     db.session.commit()
#
#     adminlog = Adminlog(
#         admin_id=session["admin_id"],
#         ip=request.remote_addr,
#         log_type='card_del'
#     )
#     db.session.add(adminlog)
#     db.session.commit()
#
#     flash("删除管理员成功！", "ok")
#     return redirect(url_for("admin.card_list", page=1))
#
#
# ''' 充值卡部分结束 '''
#
# ''' 会员部分 '''
#
#
# # 会员列表
# @admin.route("/admin/user_list/<int:page>/", methods=["GET", "POST"])
# @admin_auth
# @admin_login_req
# def admin_user_list(page=None):
#     if page is None:
#         page = 1
#     page_data = User.query.order_by(
#         User.id
#     ).paginate(page=page, per_page=10000)
#     return render_template("admin/user_list.html", page_data=page_data)
#
#
# # 删除会员
# @admin.route("/user/del/<int:id>/", methods=["GET", "POST"])
# @admin_auth
# @admin_login_req
# def user_del(id=None):
#     user = User.query.get_or_404(int(id))
#     db.session.delete(user)  # 删除会员
#     db.session.commit()
#
#     adminlog = Adminlog(
#         admin_id=session["admin_id"],
#         ip=request.remote_addr,
#         log_type='user_del'
#     )
#     db.session.add(adminlog)
#     db.session.commit()
#
#     flash("删除会员成功", "ok")
#     return redirect(url_for('admin.admin_user_list',
#                             page=1))  # 这里需要显示信息，如果仅用admin/user_list.html，page_data数据根本就找不到，所以要使用url_for（），调用其他的方法
#
#
# ''' 会员部分结束 '''
#
# ''' 管理员操作日志部分 '''
#
#
# # 管理员登录列表
# @admin.route("/adminloginlog/list/<int:page>/", methods=["GET", "POST"])
# @admin_login_req
# @admin_auth
# def adminloginlog_list(page=None):
#     if page is None:
#         page = 1
#     page_data = Adminlog.query.join(
#         Admin
#     ).filter(
#         Admin.id == Adminlog.admin_id,  # 关联Oplog表里面你的admin_id字段
#     ).order_by(
#         Adminlog.addtime.desc()
#     ).paginate(page=page, per_page=1000)
#     return render_template("admin/adminloginlog_list.html", page_data=page_data)
#
#
# # 删除日志
# @admin.route("/adminlog/del/<int:id>/", methods=["GET", "POST"])
# @admin_login_req
# @admin_auth
# def adminlog_del(id):
#     adminlog = Adminlog.query.filter_by(id=id).first_or_404()
#     db.session.delete(adminlog)
#     db.session.commit()
#
#     adminlog = Adminlog(
#         admin_id=session["admin_id"],
#         ip=request.remote_addr,
#         log_type='adminlog_del'
#     )
#     db.session.add(adminlog)
#     db.session.commit()
#
#     flash("删除日志成功！", "ok")
#     return redirect(url_for("admin.adminloginlog_list", page=1))
#
#
# ''' 管理员操作日志部分结束 '''
#
# ''' 管理员部分 '''
#
#
# # 管理员列表
# @admin.route("/admin/list/<int:page>/", methods=["GET", "POST"])
# @admin_login_req
# @admin_auth
# def admin_list(page=None):
#     if page is None:
#         page = 1
#     page_data = Admin.query.join(
#         Role
#     ).filter(
#         Role.id == Admin.role_id
#     ).order_by(  # 从Tag里面查询
#         Admin.addtime.desc()  # order_by按时间进行排序
#     ).paginate(page=page, per_page=10)
#     return render_template("admin/admin_list.html", page_data=page_data)
#
#
# # 添加管理员
# @admin.route("/admin/add/", methods=["GET", "POST"])
# @admin_login_req
# @admin_auth
# def admin_add():
#     form = AdminForm()
#     if form.validate_on_submit():
#         data = form.data
#         admin = Admin(
#             name=data["name"],
#             pwd=generate_password_hash(data["pwd"]),
#             role_id=data["role_id"],
#             is_super=1,
#         )
#         db.session.add(admin)
#         db.session.commit()
#
#         adminlog = Adminlog(
#             admin_id=session["admin_id"],
#             ip=request.remote_addr,
#             log_type='admin_add'
#         )
#         db.session.add(adminlog)
#         db.session.commit()
#
#         flash("添加管理员成功", "ok")
#     return render_template("admin/admin_add.html", form=form)
#
#
# # 编辑管理员
# @admin.route("/admin/edit/<int:id>/", methods=["GET", "POST"])
# @admin_login_req
# @admin_auth
# def admin_edit(id=None):
#     form = Admin_EditForm()
#     admin = Admin.query.filter_by(id=id).first_or_404()  # 到数据库找id，有的话就get到，没有的话就返回404
#     if form.validate_on_submit():  # 接收前端传送过来的数据字段
#         data = form.data
#         admin.name = data["name"]
#         admin.role_id = data["role_id"]
#         db.session.add(admin)
#         db.session.commit()
#         flash("修改管理员成功", "ok")
#         print("修改管理员成功")
#
#         adminlog = Adminlog(
#             admin_id=session["admin_id"],
#             ip=request.remote_addr,
#             log_type='admin_edit'
#         )
#         db.session.add(adminlog)
#         db.session.commit()
#
#         redirect(url_for("admin.admin_edit", id=id))
#     return render_template("admin/admin_edit.html", form=form, admin=admin)
#
#
# # 删除管理员
# @admin.route("/admin/del/<int:id>/", methods=["GET", "POST"])
# @admin_login_req
# @admin_auth
# def admin_del(id):
#     admin = Admin.query.filter_by(id=id).first_or_404()
#     db.session.delete(admin)
#     db.session.commit()
#
#     adminlog = Adminlog(
#         admin_id=session["admin_id"],
#         ip=request.remote_addr,
#         log_type='admin_del'
#     )
#     db.session.add(adminlog)
#     db.session.commit()
#
#     flash("删除管理员成功！", "ok")
#     return redirect(url_for("admin.admin_list", page=1))
#
#
# ''' 管理员部分结束 '''
#
# ''' 权限部分（完成）'''
#
#
# # 权限列表
# @admin.route("/auth/list/<int:page>/", methods=["GET", "POST"])
# @admin_login_req
# @admin_auth
# def auth_list(page=None):
#     if page is None:
#         page = 1
#     page_data = Auth.query.order_by(  # 从Tag里面查询
#         Auth.addtime.desc()  # order_by按时间进行排序
#     ).paginate(per_page=50)  # paginate就是进行分页，per_page就是每页显示的数量
#     return render_template("admin/auth_list.html", page_data=page_data)  # 返回到页面
#
#
# # 权限添加
# @admin.route("/auth/add/", methods=["POST", "GET"])
# @admin_login_req
# @admin_auth
# def auth_add():
#     form = AuthForm()
#     if form.validate_on_submit():
#         data = form.data
#         auth = Auth(
#             name=data["name"],
#             url=data["url"]
#         )
#         db.session.add(auth)
#         db.session.commit()
#
#         adminlog = Adminlog(
#             admin_id=session["admin_id"],
#             ip=request.remote_addr,
#             log_type='auth_add'
#         )
#         db.session.add(adminlog)
#         db.session.commit()
#
#         flash("添加权限成功", "ok")
#     return render_template("admin/auth_add.html", form=form)
#
#
# # 编辑权限
# @admin.route("/auth/edit/<int:id>/", methods=["GET", "POST"])
# @admin_login_req
# @admin_auth
# def auth_edit(id=None):
#     form = AuthForm()
#     auth = Auth.query.filter_by(id=id).first_or_404()  # 到数据库找id，有的话就get到，没有的话就返回404
#     if form.validate_on_submit():  # 接收前端传送过来的数据字段
#         data = form.data
#         auth.url = data["url"]
#         auth.name = data["name"]
#         db.session.add(auth)
#         db.session.commit()
#
#         adminlog = Adminlog(
#             admin_id=session["admin_id"],
#             ip=request.remote_addr,
#             log_type='auth_edit'
#         )
#         db.session.add(adminlog)
#         db.session.commit()
#
#         flash("修改标签成功", "ok")
#         redirect(url_for("admin.auth_edit", id=id))
#     return render_template("admin/auth_edit.html", form=form, auth=auth)
#
#
# # 删除权限
# @admin.route("/auth/del/<int:id>/", methods=["GET", "POST"])
# @admin_login_req
# @admin_auth
# def auth_del(id):
#     auth = Auth.query.filter_by(id=id).first_or_404()
#     db.session.delete(auth)
#     db.session.commit()
#
#     adminlog = Adminlog(
#         admin_id=session["admin_id"],
#         ip=request.remote_addr,
#         log_type='auth_del'
#     )
#     db.session.add(adminlog)
#     db.session.commit()
#
#     flash("删除权限成功！", "ok")
#     return redirect(url_for("admin.auth_list", page=1))
#
#
# ''' 权限部分结束 '''
#
# ''' 角色部分(完成) '''
#
#
# # 角色列表
# @admin.route("/role/list/<int:page>/", methods=["GET", "POST"])
# @admin_login_req
# @admin_auth
# def role_list(page=None):
#     if page is None:
#         page = 1
#     page_data = Role.query.order_by(
#         Role.addtime.desc()
#     ).paginate(page=page, per_page=10)
#     return render_template("admin/role_list.html", page_data=page_data)
#
#
# # 角色添加
# @admin.route("/role/add/", methods=["GET", "POST"])
# @admin_login_req
# @admin_auth
# def role_add():
#     form = RoleForm()
#     if form.validate_on_submit():
#         data = form.data
#         role = Role(
#             name=data["name"],
#             auths=",".join(map(lambda v: str(v), data["auths"]))  # 将整形转化为字符串类型，然后才能join链接
#         )
#         db.session.add(role)
#         db.session.commit()
#
#         adminlog = Adminlog(
#             admin_id=session["admin_id"],
#             ip=request.remote_addr,
#             log_type='role_add'
#         )
#         db.session.add(adminlog)
#         db.session.commit()
#
#         flash("添加角色成功", "ok")
#     return render_template("admin/role_add.html", form=form)
#
#
# # 编辑角色
# @admin.route("/role/edit/<int:id>/", methods=["GET", "POST"])
# @admin_login_req
# @admin_auth
# def role_edit(id=None):
#     form = RoleForm()
#     role = Role.query.filter_by(id=id).first_or_404()  # 到数据库找id，有的话就get到，没有的话就返回404
#     if request.method == "GET":
#         auths = role.auths
#         form.auths.data = list(map(lambda v: int(v), auths.split(",")))  # 转化为需要的类型
#     if form.validate_on_submit():  # 接收前端传送过来的数据字段
#         data = form.data
#         print(data["auths"])
#         role.name = data["name"]
#         role.auths = ",".join(map(lambda v: str(v), data["auths"]))
#         db.session.add(role)
#         db.session.commit()
#
#         adminlog = Adminlog(
#             admin_id=session["admin_id"],
#             ip=request.remote_addr,
#             log_type='role_edit'
#         )
#         db.session.add(adminlog)
#         db.session.commit()
#
#         flash("修改成功", "ok")
#     return render_template("admin/role_edit.html", form=form, role=role)
#
#
# # 删除角色
# @admin.route("/role/del/<int:id>/", methods=["GET", "POST"])
# @admin_login_req
# @admin_auth
# def role_del(id):
#     role = Role.query.filter_by(id=id).first_or_404()
#     db.session.delete(role)
#     db.session.commit()
#
#     adminlog = Adminlog(
#         admin_id=session["admin_id"],
#         ip=request.remote_addr,
#         log_type='role_del'
#     )
#     db.session.add(adminlog)
#     db.session.commit()
#
#     flash("删除权限成功！", "ok")
#     return redirect(url_for("admin.role_list", page=1))
#
#
# ''' 角色部分结束 '''
#
# ''' 会员操作日志 '''
#
#
# # 会员操作列表
# @admin.route("/userlog/list/<int:page>/", methods=["GET", "POST"])
# @admin_login_req
# @admin_auth
# def userlog_list(page=None):
#     if page is None:
#         page = 1
#     page_data = Userlog.query.order_by(
#         Userlog.addtime.desc()
#     ).paginate(page=page, per_page=10)
#     return render_template("admin/userlog_list.html", page_data=page_data)
#
#
# # 上传图片的接口
# @admin.route('/upload_file', methods=['GET', 'POST'])
# def upload_file():
#     if request.method == 'POST':
#         file = request.files['file']
#         text = request.form.get("text")
#         if file and allowed_file(file.filename):
#             filename = secure_filename(file.filename)
#             file.save(os.path.join(UPLOAD_FOLDER, filename))
#             return jsonify({"status": 1, "text": text, "file": filename})
#         return jsonify({"status": 0, "errorCode": 130})
#     return jsonify({"status": 0, "errorCode": 101})
#
#
# def allowed_file(filename):
#     return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS
#
#
# # 提交代取信息的接口
# @admin.route('/upload_exmsg', methods=['GET', 'POST'])
# def upload_exmsg():
#     if request.method == 'POST':
#         file = request.files['file']
#         openid = request.form.get("openid")
#         user_name = request.form.get("user_name")
#         phone_number = request.form.get("phone_number")
#         sms_content = request.form.get("sms_content")
#         school_place = request.form.get("school_place")
#         area = request.form.get("area")
#
#         express = Express(
#             openid=str(openid),
#             user_name=user_name,
#             phone_number=str(phone_number),
#             sms_content=sms_content,
#             school_place=school_place,
#             area=area
#         )
#         db.session.add(express)
#         db.session.commit()
#
#         # 保存用户上传的图片
#         if file and allowed_file(file.filename):
#             filename = secure_filename(file.filename)
#             file.save(os.path.join(UPLOAD_FOLDER, filename))
#
#             # 生成标识特殊id
#             express_spid = uuid.uuid5(uuid.NAMESPACE_DNS, str(str(express.id) + str(openid)))
#             print("express_id特殊ID为：" + str(express_spid))
#             print("图片保存地址为：https://wx.xiaodemon.cn/" + 'static/upload' + '/' + filename)
#
#             # 上传数据
#             express.express_spid = express_spid   # 用来对应log
#             express.pic_url = UPLOAD_FOLDER + '/' + filename
#             express.area = area
#
#             db.session.add(express)
#             db.session.commit()
#
#             return jsonify({"status": 1, "express_id": express.id,
#                             'msg_url': 'https://wx.xiaodemon.cn/' + 'static/upload/' + '/' + filename})
#
#         return jsonify(
#             {"status": 0, "errorCode": 130, "msg": None})
#     else:
#         return jsonify({"status": 0, "errorCode": 101, "msg": None})
