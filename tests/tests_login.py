# -*- coding: utf-8 -*-
"""
登录接口的自动化测试用例
=========================
本文件用 pytest 框架，对「登录」接口做正向 + 反向测试。

测试思路（等价类 / 边界）：
  正向：正确的用户名 + 正确的密码 + 正确的验证码  → 登录成功
  反向：密码错 / 用户名错 / 验证码错 / 缺用户名 / 缺密码 → 登录失败
"""
import pytest
from src.apiclient import AIPClient


class TestLogin:
    """登录接口测试类。

    注意：类名以 Test 开头，pytest 才会把它识别成测试类。
    """

    # 测试用到的「正确」账号密码（放成类属性，方便统一维护）
    VALID_USERNAME = 'admin'
    VALID_PASSWORD = 'HM_2023_test'

    # ==================== 夹具（fixture） ====================
    # fixture 用来「准备测试前需要的东西」，测试方法通过参数名来引用它。

    @pytest.fixture(scope='function')  # scope='function'：每个测试方法执行前都会重新运行一次
    def client(self):
        """夹具1：准备一个 AIPClient 客户端对象。

        yield 之前是「测试前的准备」，yield 之后是「测试后的清理」。
        """
        client = AIPClient()  # 准备：创建客户端（内部会自动建立 Session）
        yield client          # 把 client 交给测试方法使用
        client.close()        # 清理：测试结束后关闭会话

    @pytest.fixture(scope='function')
    def captcha_info(self, client):
        """夹具2：获取一个「新鲜」的验证码 uuid。

        依赖 client 夹具（见参数），pytest 会先把 client 准备好再传进来。
        注意：验证码是一次性的，所以每个用例都要重新获取一个 uuid。
        """
        response = client.get_captcha()    # 调接口拿验证码
        assert response.status_code == 200  # 先确认接口调用成功
        data = response.json()              # 把响应体解析成字典
        return {"uuid": data["uuid"]}       # 只把 uuid 返回给用例

    # ==================== 测试用例 ====================
    # 约定：方法名以 test_ 开头，pytest 才会把它当成一条测试用例执行。

    def test_login_success(self, client: AIPClient, captcha_info: dict):
        """用例1（正向）：正确用户名 + 正确密码 + 正确验证码 → 登录成功。"""
        username = 'admin'
        password = 'HM_2023_test'
        uuid = captcha_info["uuid"]  # 从夹具拿到验证码唯一标识
        # 第 3 个参数 "2" 是验证码：当前测试环境的图片验证码固定为 2
        response = client.login(username, password, "2", uuid)

        # ---- 开始断言：检查结果是否符合预期 ----
        assert response.status_code == 200  # 1) HTTP 状态码是 200
        data = response.json()              #    把响应体解析成字典
        assert data["code"] == 200          # 2) 业务码是 200（业务成功）
        assert data["msg"] == "操作成功"     # 3) 提示信息是「操作成功」
        assert "token" in data              # 4) 返回里包含 token 字段
        assert data["token"] is not None and data["token"] != ""  # 5) token 不为空

        # 打印 token 前 20 个字符，方便肉眼确认
        print(f"登录成功，token:{data['token'][:20]}..")

    def test_login_fail(self, client: AIPClient, captcha_info: dict):
        """用例2（反向）：正确用户名 + 错误密码 → 登录失败。"""
        username = "admin"
        password = "wrong_info"  # 故意用错密码

        uuid = captcha_info["uuid"]
        response = client.login(username, password, "2", uuid)

        assert response.status_code == 200           # HTTP 层面仍返回 200
        data = response.json()
        assert data["code"] == 500                   # 但业务码是 500（业务失败）
        assert data["msg"] == "用户不存在/密码错误"   # 提示「用户不存在/密码错误」
        print("密码错误测试通过")

    def test_login_fail2(self, client: AIPClient, captcha_info: dict):
        """用例3（反向）：错误用户名 + 正确密码 → 登录失败。"""
        username = "wrong_username"  # 故意用错用户名
        password = "HM_2023_test"

        uuid = captcha_info["uuid"]
        response = client.login(username, password, "2", uuid)

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 500
        assert data["msg"] == "用户不存在/密码错误"
        print("用户名错误测试通过")

    def test_login_fail3(self, client: AIPClient, captcha_info: dict):
        """用例4（反向）：正确用户名 + 正确密码 + 错误验证码 → 登录失败。"""
        username = "admin"
        password = "HM_2023_test"
        code = "9999"  # 故意用错验证码

        uuid = captcha_info["uuid"]
        response = client.login(username, password, code, uuid)

        assert response.status_code == 200   # 注意：业务失败时 HTTP 仍是 200，错误信息在 body 里
        data = response.json()
        assert data["code"] == 500           # 业务码 500 表示失败
        assert data["msg"] == "验证码错误"
        print("验证码错误测试通过")

    def test_login_fail4(self, client: AIPClient, captcha_info: dict):
        """用例5（反向）：缺少用户名（空字符串）→ 登录失败。"""
        username = ""  # 用户名为空
        password = "HM_2023_test"

        uuid = captcha_info["uuid"]
        response = client.login(username, password, "2", uuid)

        assert response.status_code == 200
        data = response.json()
        assert data["code"] != 200  # 这里不关心具体错误码，只要「不是成功」即可
        print(f"缺少用户名测试通过：{data}")

    def test_login_fail5(self, client: AIPClient, captcha_info: dict):
        """用例6（反向）：缺少密码（空字符串）→ 登录失败。"""
        username = "admin"
        password = ""  # 密码为空

        uuid = captcha_info["uuid"]
        response = client.login(username, password, "2", uuid)

        assert response.status_code == 200
        data = response.json()
        assert data["code"] != 200
        print(f"缺少密码测试通过：{data}")
