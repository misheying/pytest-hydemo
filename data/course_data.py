# -*- coding: utf-8 -*-
"""
课程管理 —— 数据驱动测试数据
============================
数据驱动：把「测试数据」和「测试逻辑」分开。
本文件只放数据，测试逻辑在 tests/test_course_data_driven.py 里。

字段说明（以新增课程为例）：
  id          : 用例编号
  description : 用例描述
  course      : 要添加的课程信息（一个字典）
  experience  : 期望结果（code 业务码 / msg 提示信息）
  check_exists: 添加后是否再去查询验证它真的存在
"""

# ==================== 新增课程测试数据 ====================
ADD_COURSE_TEST_DATA = [
    {
        "id": "TEST_COURSE_ADD_001",
        "description": "正常添加课程--成功",
        # 要添加的课程信息。
        # 注意字段名：applicableperson 是本地数据的键名，接口实际参数是 applicablePerson
        "course": {
            "name": "自动化测试实战课",   # 课程名称
            "subject": "6",              # 课程学科
            "price": 900,                # 课程价格
            "applicableperson": "2",     # 适用人群
            "info": "从零开始学习自动化测试",  # 课程介绍
        },
        # 期望结果：接口返回 code=200、msg=操作成功
        "experience": {
            "code": 200,
            "msg": "操作成功",
        },
        "check_exists": True,  # 添加后再去查询验证课程是否存在
    }
]

