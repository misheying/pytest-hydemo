# -*- coding: utf-8 -*-
"""
============================
调用「查询课程」接口，
  1. 单条件查询：一次只传一个查询条件
  2. 多条件查询：一次同时传多个条件（多个条件之间是「并且」AND 的关系）

查询接口：GET /api/clues/course/list
查询参数（都可选）：name、subject、price、applicable_person、info
"""
import pytest


class TestCourseQuery:
    """查询课程 测试类。"""

    # ==================== 单条件查询 ====================
    # 每个元组是：(用例描述, 查询参数字典)
    SINGLE_QUERY_CASES = [
        ("按课程名称查询", {"name": "自动化测试实战课"}),
        ("按课程学科查询", {"subject": "6"}),
        ("按适用人群查询", {"applicable_person": "2"}),
        ("按课程价格查询", {"price": 900}),
    ]

    # ids 用来给每条用例起个可读的名字，否则 pytest 会显示成 desc0/desc1 这种
    @pytest.mark.parametrize(
        "desc, params",
        SINGLE_QUERY_CASES,
        ids=[case[0] for case in SINGLE_QUERY_CASES],
    )
    def test_query_single_condition(self, logged_in_client, desc, params):
        """单条件查询：一次只传一个查询条件。"""
        print(f"\n {desc}")#打印用例描述

        # **params 把字典「拆开」传参：
        #   比如 params={"name":"xxx"} 等价于 get_course_list(name="xxx")
        response = logged_in_client.get_course_list(**params)

        # ---- 断言 ----
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert data["msg"] == "查询成功"
        # 至少查到 1 条，rows 是课程列表
        assert len(data.get("rows", [])) > 0, f"{desc}：没有查到数据"  #断言失败时才显示的错误消息，告诉你哪条用例挂了
        print(f"   ✅ 查到 {data.get('total')} 条")

    # ==================== 多条件查询 ====================
    MULTI_QUERY_CASES = [
        ("学科+适用人群", {"subject": "6", "applicable_person": "2"}),
        ("学科+价格", {"subject": "6", "price": 900}),
        ("名称+学科", {"name": "自动化测试实战课", "subject": "6"}),
        ("适用人群+价格", {"applicable_person": "2", "price": 900}),
    ]

    @pytest.mark.parametrize(
        "desc, params",
        MULTI_QUERY_CASES,
        ids=[case[0] for case in MULTI_QUERY_CASES],
    )
    def test_query_multi_condition(self, logged_in_client, desc, params):
        """多条件查询：一次同时传多个条件。

        多个条件之间是「并且」（AND）关系：要同时满足所有条件，才会被查出来。
        比如 {"subject":"6", "price":900} 表示「学科是 6 且 价格是 900」。
        """
        print(f"\n {desc}")

        response = logged_in_client.get_course_list(**params)

        # ---- 断言 ----
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert data["msg"] == "查询成功"
        assert len(data.get("rows", [])) > 0, f"{desc}：没有查到数据"
        print(f"   ✅ 查到 {data.get('total')} 条")
