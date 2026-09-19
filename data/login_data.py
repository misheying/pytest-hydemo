# -*- coding: utf-8 -*-
"""
登录接口 - 数据驱动测试数据
===========================
每条字典就是一条测试用例的数据。
字段说明：
  id           : 用例编号
  description  : 用例描述
  username     : 用户名
  password     : 密码
  code_type    : 验证码类型，"correct"=正确验证码 / "wrong"=错误验证码
  expected_code: 期望的业务码（200=成功，500=失败）
  expected_msg : 期望的提示信息（可选）
  check_token  : 是否校验 token（只有成功用例才需要）
"""
LOGIN_TEST_DATA_JSON = [
    {
        "id": "TC_LOGIN_001",
        "description": "正确用户名+正确密码+正确验证码 → 登录成功",
        "username": "admin",
        "password": "HM_2023_test",
        "code_type": "correct",  # 使用正确验证码
        "expected_code": 200,
        "expected_msg": "操作成功",
        "check_token": True,
    },
    {
        "id": "TC_LOGIN_002",
        "description": "正确用户名+错误密码+正确验证码 → 登录失败",
        "username": "admin",
        "password": "wrong_password",
        "code_type": "correct",
        "expected_code": 500,
        "expected_msg": "用户不存在/密码错误",
        "check_token": False,
    },
    {
        "id": "TC_LOGIN_003",
        "description": "错误用户名+正确密码+正确验证码 → 登录失败",
        "username": "wrong_user",
        "password": "HM_2023_test",
        "code_type": "correct",
        "expected_code": 500,
        "expected_msg": "用户不存在/密码错误",
        "check_token": False,
    },
    {
        "id": "TC_LOGIN_004",
        "description": "正确用户名+正确密码+错误验证码 → 登录失败",
        "username": "admin",
        "password": "HM_2023_test",
        "code_type": "wrong",  # 使用错误验证码
        "expected_code": 500,
        "expected_msg": "验证码错误",
        "check_token": False,
    },
    {
        "id": "TC_LOGIN_005",
        "description": "空用户名+正确密码+正确验证码 → 登录失败",
        "username": "",
        "password": "HM_2023_test",
        "code_type": "correct",
        "expected_code": 500,
        "expected_msg": "用户不存在/密码错误",
        "check_token": False,
    },
    {
        "id": "TC_LOGIN_006",
        "description": "正确用户名+空密码+正确验证码 → 登录失败",
        "username": "admin",
        "password": "",
        "code_type": "correct",
        "expected_code": 500,
        "expected_msg": "用户不存在/密码错误",
        "check_token": False,
    },
]
