# -*- coding: utf-8 -*-

# 导入第三方库 pytest：测试框架
import pytest
# 导入自己封装的 API 客户端类（负责发 HTTP 请求，封装在 src/apiclient.py）
from src.apiclient import AIPClient
# 导入测试数据：一个列表，里面是一条条字典，每项代表一条用例
from data.login_data import LOGIN_TEST_DATA_JSON

"""
登录接口 —— 数据驱动测试
========================
数据驱动：把「测试数据」和「测试逻辑」拆开。
  - 测试数据：放在 data/login_data.py 的 LOGIN_TEST_DATA_JSON 里（列表，每项是一条用例）
  - 测试逻辑：本文件只写一份，用 pytest 的 @parametrize 把每条数据自动跑一遍

好处：新增一条用例，只需要在数据文件里加一个字典，不用改任何测试代码。
"""


class TestLoginDataDriven:
    """登录测试类 —— 数据驱动方式。

    约定：类名以 Test 开头，pytest 才会把它识别成「测试类」。
    """

    # 测试环境里「图片验证码」的答案固定是 2（俗称万能验证码）。
    # 真实项目里验证码是随机生成的；这里为了教学方便，测试环境固定成 2。
    CORRECT_CAPTCHA = "2"

    # ==================== 夹具（fixture） ====================
    # fixture 用来「准备测试前需要的东西」，测试方法通过参数名来引用它。

    @pytest.fixture(scope="function")
    # scope="function"：每个测试方法执行前，都会重新运行一次这个夹具
    def login_client(self):
        """夹具1：准备一个「登录客户端」对象。

        yield 之前的代码是「测试前准备」，yield 之后是「测试后清理」。
        """
        login_client = AIPClient()  # 准备：创建客户端（内部会自动建立 Session 会话）
        yield login_client          # 把客户端交给测试方法使用
        login_client.close()        # 清理：测试结束后关闭会话，释放连接资源

    @pytest.fixture(scope="function")
    def captcha_client(self, login_client):
        """夹具2：获取一个「新鲜」的验证码 uuid。

        注意：
          1) 依赖 login_client 夹具（见函数参数），pytest 会先把 login_client 准备好再传进来。
          2) 验证码是一次性的，每跑一条用例都要重新获取一个 uuid，所以也是 function 级别。
        """
        response = login_client.get_captcha()   # 调用接口拿验证码
        assert response.status_code == 200      # 先确认接口调用成功（HTTP 状态码 200）
        data = response.json()                  # 把响应体（JSON 字符串）解析成字典
        return {"uuid": data["uuid"]}           # 只把 uuid 返回给用例使用

    # ==================== 数据驱动测试用例 ====================

    # @pytest.mark.parametrize：pytest 的「参数化」装饰器，作用是把多条数据喂给同一个测试函数。
    #   "test_case"          ：参数名，会传入下面测试函数的同名参数
    #   LOGIN_TEST_DATA_JSON ：数据来源（一个列表），列表里有几项，就会生成几条测试用例
    @pytest.mark.parametrize("test_case", LOGIN_TEST_DATA_JSON)
    def test_login_data_driven(self, login_client, captcha_client, test_case):
        """核心用例：一份代码，跑完数据文件里的所有场景。

        参数说明（都由 pytest 自动注入，不需要手动传）：
          login_client  ：夹具1 提供的客户端对象
          captcha_client：夹具2 提供的验证码信息（含 uuid）
          test_case     ：parametrize 注入的「一条测试数据」（一个字典）
        """
        # ---- 第 1 步：从测试数据里取字段 ----
        test_id = test_case["id"]                    # 用例编号，如 TC_LOGIN_001
        description = test_case["description"]       # 用例描述
        username = test_case["username"]             # 用户名
        password = test_case["password"]             # 密码
        code_type = test_case["code_type"]           # 验证码类型："correct" / "wrong"
        expected_code = test_case["expected_code"]   # 期望的业务码：200=成功 / 500=失败
        # expected_msg 用 get() 而不是 []，因为有些用例可能没写这个字段，用 get 不会报错（返回 None）
        expected_msg = test_case.get("expected_msg")
        # check_token 同理用 get()，并给默认值 False（不校验 token）
        check_token = test_case.get("check_token", False)

        # ---- 第 2 步：准备「真实」的请求参数 ----
        # code_type 只是一个标记（"correct"/"wrong"），要转成真正的验证码：
        #   标记为 correct → 用正确验证码 CORRECT_CAPTCHA（即 "2"）
        #   否则（wrong）  → 用错误验证码 "9999"
        code = self.CORRECT_CAPTCHA if code_type == "correct" else "9999"

        # uuid 不在测试数据里，而是来自验证码夹具（每个用例重新获取一个）
        uuid = captcha_client["uuid"]

        # ---- 第 3 步：执行 ----
        print(f"\n执行用例：{test_id} - {description}")  # 打印当前执行哪条用例，方便观察
        # 用「关键字参数」调用 login，好处是名字清晰、参数顺序可以随意调换
        response = login_client.login(
            username=username,
            password=password,
            uuid=uuid,
            code=code,
        )

        # ---- 第 4 步：断言（校验结果是否符合预期）----
        assert response.status_code == 200  # 1) HTTP 状态码必须是 200
        data = response.json()              #    把响应体解析成字典

        # 2) 业务码要和期望一致。
        #    行尾的反斜杠 \ 表示「这行还没写完，换行继续」，让长语句读起来更清楚。
        assert data["code"] == expected_code, \
            f"用例{test_id}失败：期望 code={expected_code}，实际 code={data['code']}"

        # 3) 如果数据里写了期望提示信息，就校验提示信息；没写则跳过（比如有些用例不关心 msg）
        if expected_msg:
            assert data["msg"] == expected_msg, \
                f"用例{test_id}失败：期望 msg={expected_msg}，实际 msg={data['msg']}"

        # 4) 只有成功用例才校验 token（失败用例的返回里根本没有 token）
        if check_token:
            assert "token" in data                          # token 字段必须存在
            assert data["token"] is not None and data["token"] != ""  # token 不能为空
            print(f"token:{data['token'][:30]}...")         # 打印 token 前 30 个字符

        print(f"用例{test_id}通过！")
