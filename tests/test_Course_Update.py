# -*- coding: utf-8 -*-
"""
修改课程 测试用例
================
修改课程接口：PUT /api/clues/course
请求体参数：id（必填）、name、subject、price、applicable_person、info

测试流程：先创建一门课 → 修改它 → 查询详情验证修改是否生效
"""
import time

import allure
import pytest

@allure.feature("修改课程")
class TestCourseUpdate:
    """修改课程 测试类。"""

    @allure.story("修改课程")
    @allure.title("修改课程成功")
    @pytest.mark.smoke
    def test_update_course(self, logged_in_client, created_course_id):
        """修改课程：改名称和价格，然后查询验证。"""
        # created_course_id 夹具已经帮我们创建好一门课，直接拿到它的 id
        course_id = created_course_id

        # 1) 准备要改成的新值
        new_name = f"修改后的课程_{int(time.time())}"  # 用时间戳保证名称唯一
        new_price = 999

        print(f" 修改课程 id={course_id}")
        print(f"  新名称={new_name}，新价格={new_price}")

        # 2) 调用修改接口（PUT）
        response = logged_in_client.update_course(
            course_id=course_id,
            name=new_name,
            subject="6",
            price=new_price,
            applicable_person="2",
            info="已修改",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200, f"修改失败：{data.get('msg')}"
        print("    修改成功")

        # 3) 按 id 查询详情，验证修改是否生效
        detail = logged_in_client.get_course_by_id(course_id).json()
        assert detail["code"] == 200
        assert detail["data"]["name"] == new_name, \
            f"名称没改对：{detail['data']['name']} != {new_name}"
        assert detail["data"]["price"] == new_price, \
            f"价格没改对：{detail['data']['price']} != {new_price}"
        print(f"    验证通过：名称={detail['data']['name']}，价格={detail['data']['price']}")
