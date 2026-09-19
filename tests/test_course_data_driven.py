# -*- coding: utf-8 -*-
"""
课程管理 —— 数据驱动测试
========================
这个文件是「查询/新增课程」的自动化测试用例。

【什么是数据驱动？】
  就是把「测试数据」和「测试逻辑」分开：
    - 测试数据 放在 data/course_data.py（里面是一个列表，每项是一条用例）
    - 测试逻辑 只写一份（就在本文件），pytest 会用 @parametrize 把每条数据自动跑一遍

【好处】
  以后想加一条新用例，只需要去 data/course_data.py 里加一个字典，本文件一行都不用改。
"""
# import 是「导入」：把别处写好的工具拿过来用
import pytest  # 导入测试框架 pytest
from data.course_data import ADD_COURSE_TEST_DATA, QUERY_COURSE_TEST_DATA  # 导入两条测试数据列表


class TestCourseAdd:
    """「新增课程」的测试类。

    class 是「类」，可以理解成一组相关测试用例的集合。
    类名以 Test 开头，pytest 才会把它识别成测试类。
    """

    # @pytest.mark.parametrize 是「参数化」：把 ADD_COURSE_TEST_DATA 列表里的
    # 每一条数据，依次传给下面函数的 test_case 参数，各跑一遍。
    @pytest.mark.parametrize("test_case", ADD_COURSE_TEST_DATA)
    def test_add_course_data_driven(self, logged_in_client, test_case):
        """新增课程用例。

        这个函数有 3 个参数，但调用时我们一个都不用传，pytest 会自动填：
          self             ：代表当前测试类对象（固定写法，不用管）
          logged_in_client ：conftest.py 里定义好的「已登录客户端」夹具
          test_case        ：一条测试数据（一个「字典」，形如 {"id":..., "course":...}）
        """
        # ---- 第 1 步：从测试数据里取出需要的字段 ----
        # test_case 是一个字典(dict)。字典用「键(key)」取值：
        #   test_case["id"] 就是取出 key 为 "id" 的那个值。
        test_id = test_case["id"]               # 用例编号，比如 "TEST_COURSE_ADD_001"
        description = test_case["description"]  # 用例描述
        course = test_case["course"]            # 要添加的课程信息（本身又是一个字典）
        experience = test_case["experience"]    # 期望结果（含 code / msg）
        # .get("check_exists", False) 和 ["check_exists"] 的区别：
        #   get 在 key 不存在时不会报错，而是返回默认值 False，更安全。
        check_exists = test_case.get("check_exists", False)  # 添加后是否要验证它真的存在

        # f-string：字符串前面加 f，就可以在 {} 里直接写变量名，把变量的值嵌进文字里。
        # '\n' 是换行；'=' * 60 表示把 '=' 这个符号重复 60 次，用来当分隔线。
        print(f"\n{'=' * 60}")
        print(f"执行测试用例：{test_id}-{description}")
        print(f"请求参数：{course}")

        # ---- 第 2 步：发送「新增课程」请求 ----
        # 这里用「关键字参数」调用，每个参数前面都写了名字，清楚又不怕顺序错。
        # 注意一个小坑：数据里的字段叫 applicableperson（没下划线），
        #   但接口参数名是 applicable_person（有下划线），这里做了一次映射。
        response = logged_in_client.add_course(
            name=course["name"],                       # 课程名称
            subject=course["subject"],                 # 学科
            price=course["price"],                     # 价格
            applicable_person=course["applicableperson"],  # 适用人群（字段名映射）
            info=course.get("info", ""),               # 课程介绍；info 可选，没有就给空串
        )

        # ---- 第 3 步：验证响应（断言） ----
        # response.status_code 是 HTTP 状态码，200 表示「请求成功」
        assert response.status_code == 200
        # response.json() 把响应体（一段 JSON 字符串）解析成 Python 字典，方便取值
        data = response.json()
        print(f"响应数据：{data}")

        # assert 是「断言」：如果后面条件不成立，测试就失败并抛错。
        # assert 条件, "提示信息"  —— 逗号后面是失败时显示的信息，方便定位问题。
        assert data["code"] == experience["code"], \
            f"用例 {test_id} 失败: 期望 code={experience['code']}，实际 code={data['code']}"
        # 行尾的 \ 表示「这行还没写完，换行继续」，让很长的语句读起来更舒服。
        if "msg" in experience:  # 只有当期望里写了 msg 时，才去校验 msg
            assert data["msg"] == experience["msg"], \
                f"用例 {test_id} 失败: 期望 msg={experience['msg']}，实际 msg={data['msg']}"

        print(f"✅ 断言通过: code={data['code']}, msg={data['msg']}")

        # ---- 第 4 步：如果数据要求「验证课程真的添加成功」，就去查询确认 ----
        # if 是「如果」：只有 check_exists 为 True 且期望成功时，才执行下面这段
        if check_exists and experience["code"] == 200:
            # 用课程名称去查列表，看看能不能查到刚添加的课程
            list_response = logged_in_client.get_course_list(name=course["name"])
            list_data = list_response.json()

            assert list_data["code"] == 200  # 查询接口业务成功
            # 列表接口返回的结构是 {"total": 总数, "rows": [课程1, 课程2, ...]}
            # len(...) 是「求长度」；如果 rows 长度 > 0，说明至少查到了一条
            assert len(list_data.get("rows", [])) > 0, \
                f"课程 '{course['name']}' 未在列表中找到"

            # rows 是一个「列表(list)」，[0] 表示取第一条数据
            found_course = list_data["rows"][0]
            # 校验查到的第一条课程，名称和价格是否和刚添加的一致
            assert found_course["name"] == course["name"], \
                f"课程名称不匹配: {found_course['name']} != {course['name']}"
            assert found_course["price"] == course["price"], \
                f"课程价格不匹配: {found_course['price']} != {course['price']}"

            course_id = found_course["id"]  # 取出这门课的 id
            print(f"✅ 验证通过: 课程已存在，ID={course_id}")
        print(f"✅ 用例 {test_id} 通过!")


class TestCourseDataDriven:
    """「查询课程」的测试类（数据驱动）。"""

    @pytest.mark.parametrize("test_case", QUERY_COURSE_TEST_DATA)
    def test_query_course_data_driven(self, logged_in_client, test_case):
        """查询课程用例。"""
        test_id = test_case["id"]
        description = test_case["description"]
        params = test_case["params"]        # 查询条件（一个字典，比如 {"name": "xxx"}）
        expected = test_case["experience"]  # 期望结果

        print(f"\n{'=' * 60}")
        print(f"执行测试用例{test_id}-{description}")
        print(f"查询参数{params}")

        # ---- 特殊处理：按 ID 查询 ----
        # 说明：当前测试数据里没有 by_id 这个字段，所以这个分支暂时不会执行（属于预留）。
        if params.get("by_id", False):
            import time  # time 模块用来取当前时间
            # 用时间戳拼一个不重名的课程名，避免重复运行冲突
            course_name = f"查询测试_{int(time.time())}"

            # 先创建一个课程，再按 ID 查它
            add_response = logged_in_client.add_course(
                name=course_name,
                subject=params["subject"],
                price=params["price"],
                applicable_person=params["applicable_person"],
                info="用于ID查询测试",
            )
            assert add_response.status_code == 200
            add_data = add_response.json()
            assert add_data["code"] == 200

            # 按名称查到刚创建的课程，拿到它的 ID
            list_response = logged_in_client.get_course_list(name=course_name)
            list_data = list_response.json()
            if list_data.get("rows") and len(list_data.get("rows", [])) > 0:
                course_id = list_data.get("rows")[0].get("id")
                print(f"创建测试课程，ID：{course_id}")

                # 按 ID 查询单条课程
                response = logged_in_client.get_course_by_id(course_id=course_id)
            else:
                pytest.fail("无法创建测试课程")
        else:
            # 普通查询：**params 表示把字典「拆开」传参。
            #   比如 params={"name":"xxx"}，等价于 get_course_list(name="xxx")
            response = logged_in_client.get_course_list(**params)

        # ---- 验证响应 ----
        assert response.status_code == 200
        data = response.json()

        # data.get('total', 0)：取 total 字段；没有就给默认值 0（避免报错）
        print(f"响应数据：（total={data.get('total', 0)}）")

        # 断言业务码和提示信息
        assert data["code"] == expected["code"], \
            f"用例{test_id} 失败：期望 code={expected['code']}，实际 code={data['code']}"
        assert data["msg"] == expected["msg"], \
            f"用例{test_id}失败：期望 msg={expected['msg']},实际 msg={data['msg']}"

        # 验证是否有数据：rows 是课程列表，长度 > 0 说明有数据
        has_data = len(data.get("rows", [])) > 0
        if expected.get("has_data", True):
            if "不存在的" not in description:
                # 普通查询：不强求一定有数据（测试环境里的数据可能变化）
                pass
            else:
                # 预期没有数据（比如查一个不存在的课程名），就断言确实没数据
                assert has_data is False, \
                    f"用例{test_id}失败：预期没有数据，但实际有{len(data.get('rows', []))}条"
            print(f"用例{test_id}通过！")
