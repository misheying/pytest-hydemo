import pytest


class TestCourseFullFlow:
    """课程完整流程测试（新增 → 查询 → 验证）"""

    @pytest.mark.smoke
    def test_add_and_query_full_flow(self, logged_in_client):
        """
        完整流程测试：
        1. 新增课程
        2. 查询列表验证课程存在
        3. 按ID查询验证课程详情
        """
        #导入Python自带的time（时间）模块，导入后就能用它里面和时间有关的函数。
        import time

        print("\n" + "=" * 60)
        print(" 开始课程完整流程测试")
        print("=" * 60)

        # 1. 准备课程数据
        timestamp = int(time.time())#返回当前时间的时间戳
        course_name = f"完整流程测试_{timestamp}"
        course_price = 888

        print(f"\n 步骤1: 新增课程")
        print(f"   课程名: {course_name}")
        print(f"   价格: {course_price}")

        # 2. 新增课程
        add_response = logged_in_client.add_course(
            name=course_name,
            subject="6",
            price=course_price,
            applicable_person="2",
            info="完整流程测试课程"
        )

        add_data = add_response.json()
        assert add_data["code"] == 200
        print(f"   ✅ 新增成功: {add_data}")

        # 3. 查询列表验证
        print(f"\n 步骤2: 查询课程列表，验证新增课程存在")
        list_response = logged_in_client.get_course_list(name=course_name)
        list_data = list_response.json()

        assert list_data["code"] == 200
        assert len(list_data["rows"]) > 0, "新增的课程未在列表中找到"

        course_id = list_data["rows"][0]["id"]
        print(f"   ✅ 找到课程，ID: {course_id}")

        # 验证课程信息
        found_course = list_data["rows"][0]
        assert found_course["name"] == course_name
        assert found_course["price"] == course_price
        print(f"   ✅ 课程信息验证通过")

        # 4. 按ID查询验证
        print(f"\n 步骤3: 按ID查询课程详情")
        detail_response = logged_in_client.get_course_by_id(course_id)
        detail_data = detail_response.json()

        assert detail_data["code"] == 200
        assert detail_data["data"]["id"] == course_id
        assert detail_data["data"]["name"] == course_name
        print(f"   ✅ 课程详情验证通过")

        print("\n" + "=" * 60)
        print("✅ 完整流程测试通过!")
        print("=" * 60)
