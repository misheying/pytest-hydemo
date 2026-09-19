# -*- coding: utf-8 -*-
"""
conftest.py —— pytest 的「共享夹具」文件
========================================
什么是 conftest.py？
  - 放在测试目录下，pytest 会自动加载它。
  - 里面定义的 fixture（夹具）可以被同目录下所有测试文件直接使用，不需要 import。

什么是 fixture（夹具）？
  - 就是「测试前的准备工作」：准备客户端、登录、造数据等等。
  - 测试方法只要在参数里写上 fixture 的名字，pytest 就会自动把它的返回值传进来。
"""
import pytest  # 导入测试框架
from src.apiclient import AIPClient  # 导入我们封装的 API 客户端类


# ==================== 夹具1：客户端 ====================
@pytest.fixture(scope="function")
# @pytest.fixture：告诉 pytest「下面这个函数是一个夹具」
# scope="function"：每个测试方法执行前，都会重新运行一次这个夹具
#                  （这样每个用例都拿到一个独立、干净的客户端）
def client():
    """准备一个 API 客户端对象。"""
    client = AIPClient()  # 测试前准备：创建客户端（内部自动建立 Session）
    yield client          # yield 把客户端交给测试方法；测试跑完后，再回来执行下面一行
    client.close()        # 测试后清理：关闭会话、释放连接资源


# ==================== 夹具2：验证码 ====================
@pytest.fixture(scope="function")
def captcha_info(client):
    """获取验证码信息（uuid + 验证码答案）。"""
    # 注意：参数 client 依赖「夹具1」，pytest 会先把 client 准备好，再传进来
    response = client.get_captcha()    # 调用「获取验证码」接口
    assert response.status_code == 200  # 先确认接口调用成功（HTTP 200）
    data = response.json()             # 把响应体（JSON 字符串）解析成字典

    # 返回验证码信息：
    #   code : 验证码答案，测试环境固定是 "2"
    #   uuid : 验证码唯一标识（登录时要一起提交）
    # 注意：接口返回的 data["code"] 是「业务状态码」200，不是验证码答案，别混用。
    return {
        "code": "2",
        "uuid": data["uuid"],
    }


# ==================== 夹具3：已登录的客户端 ====================
@pytest.fixture(scope="function")
def logged_in_client(client, captcha_info):
    """自动完成「拿验证码 → 登录」，返回一个已经登录好的客户端。"""
    code = captcha_info["code"]  # 验证码答案
    uuid = captcha_info["uuid"]  # 验证码唯一标识

    # 登录（用系统内置的 admin 账号）
    response = client.login("admin", "HM_2023_test", code, uuid)
    assert response.status_code == 200  # 1) HTTP 层成功
    data = response.json()
    # 2) 业务层成功；失败时断言会报错，并显示服务器返回的原因
    assert data["code"] == 200, f"登陆失败：{data.get('msg')}"

    # 把登录返回的 token 存到客户端，后续请求会自动带上登录态
    client.set_token(data["token"])
    print(f"\n自动登陆成功，token:{client.token[:30]}...")  # 打印 token 前 30 个字符

    return client  # 返回已登录的客户端


# ==================== 夹具4：创建课程并返回 ID ====================
@pytest.fixture(scope="function")
def created_course_id(logged_in_client):
    """创建一个测试课程，返回它的 ID，供「查询/修改/删除」等用例使用。"""
    import time  # 用时间戳来生成不重名的课程名
    course_name = f"测试课程_{int(time.time())}"

    # 1) 新增课程
    response = logged_in_client.add_course(
        name=course_name,
        subject="6",                  # 学科编号
        price=888,                    # 价格
        applicable_person="2",        # 适用人群
        info="由fixture创建的测试课程"  # 课程介绍
    )
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200, f"创建课程失败{data.get('msg')}"

    # 2) 按名称查询课程，拿到刚创建课程的 ID
    list_response = logged_in_client.get_course_list(name=course_name)
    list_data = list_response.json()

    # 列表接口返回结构：{"total": N, "rows": [ {...}, {...} ]}
    if list_data.get("rows") and len(list_data["rows"]) > 0:
        course_id = list_data["rows"][0]["id"]  # 取第一条课程的 id
        print(f"\n创建测试课程成功，ID：{course_id}")
        return course_id
    else:
        # 查不到就主动让用例失败，并给出明确提示
        pytest.fail("无法获取创建课程ID")
