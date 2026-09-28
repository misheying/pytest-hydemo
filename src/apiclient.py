# -*- coding: utf-8 -*-
"""
API 客户端封装类
================
作用：把「发 HTTP 请求、调接口」这件重复的事情封装成一个类。
测试用例只需要调用这个类的方法（比如 login、add_course），
不用自己拼 URL、设置请求头、管理 cookie。
"""
import requests  # requests 是 Python 最常用的 HTTP 库，用来发 GET / POST 请求


class AIPClient:
    """对被测系统接口的统一封装。"""

    # 被测系统的根地址（base url）：所有接口地址都在它后面拼接
    Base_url = 'https://kdtx-test.itheima.net'

    def __init__(self):
        # 构造方法：每 new 一个 AIPClient 对象时自动执行一次。
        # 1) 创建一个「会话」(Session)：
        #    会话会自动保存 cookie、复用底层连接，比每次新建请求更高效。
        self.session = requests.Session()

        # 2) 公共请求头：告诉服务器「我是浏览器」「我发送的是 JSON」。
        self.headers = {
            "User-Agent": "Mozilla/5.0(windows NT 10.0;Win64;x64) AppleWebKit/537.36",  # 伪装成浏览器
            "Content-type": "application/json",  # 声明请求体是 JSON 格式
        }

        # 3) 登录后拿到的 token 先存成空字符串，登录成功后再填进去
        self.token = ""

    def set_token(self, token):
        """登录成功后，把 token 存起来，并放进请求头。

        后续所有需要登录的接口，请求头都会自动带上：
            Authorization: Bearer <token>
        服务器看到这个头，才知道「你是谁」。
        """
        self.token = token  # 存 token
        self.headers["Authorization"] = f"Bearer {self.token}"  # 放进请求头

    # ==================== 验证码接口 ====================
    def get_captcha(self):
        """获取图片验证码。

        返回：requests 的响应对象 response
        响应体里主要有：
          - uuid：本次验证码的唯一标识（登录时要一起提交）
          - img ：验证码图片（base64 编码，正常要人眼识别出数字）
        """
        url = self.Base_url + '/api/captchaImage'  # 拼出完整接口地址
        response = self.session.get(url, headers=self.headers)  # 发 GET 请求
        return response  # 把响应对象返回给调用者

    # ==================== 登录接口 ====================
    def login(self, username, password, code, uuid):
        """登录。

        参数：
          username : 用户名
          password : 密码
          code     : 验证码答案（图片里的数字；本测试环境固定为 "2"）
          uuid     : 验证码唯一标识（来自 get_captcha）
        返回：
          response : 登录结果，成功时 body 里会带 token
        """
        url = self.Base_url + '/api/login'  # 拼完整地址

        # 要提交给服务器的数据（字典，键名必须和接口文档一致）
        data = {
            "username": username,
            "password": password,
            "uuid": uuid,
            "code": code,
        }

        # 关键：用 json= 发送，requests 会自动把字典转成 JSON 字符串；
        # 如果误用 data=，会被当成表单提交，服务器解析不了（之前报的 JSON parse error 就是这个原因）。
        response = self.session.post(url, json=data, headers=self.headers)
        return response

    # ==================== 课程管理接口 ====================
    def add_course(self, name, subject, price, applicable_person, info=""):
        """新增课程（需先登录）。

        参数：
          name             : 课程名称
          subject          : 学科
          price            : 价格
          applicable_person: 适用人群
          info             : 课程介绍（可选，默认空字符串）
        """
        url = self.Base_url + '/api/clues/course'  # 新增课程的接口地址
        data = {
            "name": name,
            "subject": subject,
            "price": price,
            "applicablePerson": applicable_person,
            "info": info,
        }
        response = self.session.post(url, json=data, headers=self.headers)
        return response

    def get_course_list(self, name="", subject="", price=None, applicable_person="", info=""):
        """查询课程列表（需先登录）。

        所有参数都是可选的：传了就按条件过滤，不传就查全部。
        """
        url = self.Base_url + '/api/clues/course/list'  # 查询列表的接口地址

        # 查询接口用 GET，参数用 params 拼在 URL 后面（而不是像新增那样放 body）
        params = {}
        if name:                       # 传了名字，就按名字过滤
            params["name"] = name
        if subject:
            params["subject"] = subject
        if price is not None:
            params["price"] = price
        if applicable_person:
            params["applicablePerson"] = applicable_person
        if info:
            params["info"] = info

        response = self.session.get(url, params=params, headers=self.headers)
        return response

    def update_course(self, course_id, name="", subject="", price=None, applicable_person="", info=""):
        """修改课程（需先登录）。

        参数：
          course_id        : 课程 id（必填，指定要修改哪门课）
          name             : 新的课程名称
          subject          : 新的课程学科
          price            : 新的课程价格
          applicable_person: 新的适用人群
          info             : 新的课程介绍
        """
        url = self.Base_url + '/api/clues/course'  # 修改课程的接口地址
        data = {
            "id": course_id,
            "name": name,
            "subject": subject,
            "price": price,
            "applicablePerson": applicable_person,
            "info": info,
        }
        # 修改用 PUT 方法，参数放 body（json=）
        response = self.session.put(url, json=data, headers=self.headers)
        return response

    def get_course_by_id(self, course_id):
        """根据课程 id 查询单条课程。"""
        # f-string 把课程 id 拼进地址里，例如 /api/clues/course/123
        url = self.Base_url + f'/api/clues/course/{course_id}'
        response = self.session.get(url, headers=self.headers)
        return response

    def delete_course(self, course_id):
        """删除课程（需先登录）。

        参数：
          course_id : 要删除的课程 id
        """
        url = self.Base_url + f'/api/clues/course/{course_id}'  # 删除课程的接口地址
        response = self.session.delete(url, headers=self.headers)  # 用 DELETE 方法
        return response

    # ==================== 合同管理接口 ====================
    def add_contract(self, contract_no, phone, name, subject, course_id, file_name, channel="", activity_id=None):
        """新增合同（需先登录）。POST /api/contract

        参数：
          contract_no : 合同编号（必填）
          phone       : 手机号（必填）
          name        : 客户姓名（必填）
          subject     : 意向学科（必填）
          course_id   : 课程 id（必填）
          file_name   : 文件名称（必填，合同附件）
          channel     : 渠道来源（可选，0=线上活动 1=推广介绍）
          activity_id : 活动信息（可选）
        """
        url = self.Base_url + '/api/contract'  # 新增合同接口地址
        data = {
            "contractNo": contract_no,
            "phone": phone,
            "name": name,
            "subject": subject,
            "courseId": course_id,
            "fileName": file_name,
            "channel": channel,
            "activityId": activity_id,
        }
        response = self.session.post(url, json=data, headers=self.headers)
        return response

    def get_contract_list(self, name="", phone="", contract_no="", subject="", course_id=None, channel="", activity_id=None, file_name=""):
        """查询合同列表（需先登录）。GET /api/contract/list

        所有参数都可选：传了就按条件过滤，不传就查全部。
        """
        url = self.Base_url + '/api/contract/list'  # 查询合同列表接口地址
        params = {}
        if name:
            params["name"] = name
        if phone:
            params["phone"] = phone
        if contract_no:
            params["contractNo"] = contract_no
        if subject:
            params["subject"] = subject
        if course_id is not None:
            params["courseId"] = course_id
        if channel:
            params["channel"] = channel
        if activity_id is not None:
            params["activityId"] = activity_id
        if file_name:
            params["fileName"] = file_name
        response = self.session.get(url, params=params, headers=self.headers)
        return response

    def upload_file(self, file_path):
        """上传文件（需先登录）。POST /api/common/upload

        参数：
          file_path : 本地文件路径
        返回：
          response : 成功时 body 里带 fileName（上传后的文件地址）
        """
        import os
        url = self.Base_url + '/api/common/upload'  # 文件上传接口地址
        file_name = os.path.basename(file_path)  # 从路径里取出文件名

        # 关键：上传是 multipart/form-data，不能带 "Content-type": application/json，
        # 否则服务器解析不了会报 500。所以单独构造 headers，去掉 Content-type，
        # 让 requests 自动设置成 multipart/form-data; boundary=...
        headers = {
            "Authorization": self.headers["Authorization"],
            "User-Agent": self.headers["User-Agent"],
        }
        with open(file_path, 'rb') as f:
            files = {'file': (file_name, f)}
            response = self.session.post(url, files=files, headers=headers)
        return response

    def close(self):
        """关闭会话，释放连接资源。"""
        self.session.close()
