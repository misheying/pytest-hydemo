# -*- coding: utf-8 -*-
"""
删除课程 测试用例
================
删除课程接口：DELETE /api/clues/course/{id}

本用例：从最早创建时间开始，一次删除 10 条课程。
"""
import pytest


class TestCourseDelete:
    """删除课程 测试类。"""

    @pytest.mark.skip(reason="删除操作不可逆，确认之后再运行")
    def test_delete_earliest_10_courses(self, logged_in_client):
        """从最早创建时间开始，删除 10 条课程。"""
        # 1) 查询所有课程（不传参数 = 查全部）
        list_response = logged_in_client.get_course_list()
        assert list_response.status_code == 200
        list_data = list_response.json()
        all_rows = list_data.get("rows", [])

        # 2) 只保留「有创建时间」的课程，并按创建时间升序排序（最早的在最前面）
        courses = [row for row in all_rows if row.get("createTime")]
        courses.sort(key=lambda r: r.get("createTime", "")) #按创建时间升序排列

        # 3) 只取最早的 10 条
        to_delete = courses[:10]
        print(f"\n 共 {len(courses)} 条有创建时间的课程，本次删除最早的 {len(to_delete)} 条")

        # 4) 逐条删除
        deleted = 0
        for row in to_delete:
            course_id = row["id"]
            resp = logged_in_client.delete_course(course_id)
            assert resp.status_code == 200
            data = resp.json()
            assert data["code"] == 200, f"删除课程 id={course_id} 失败：{data.get('msg')}"
            print(f"   已删除 id={course_id}（创建时间 {row['createTime']}）")
            deleted += 1

        print(f"   成功删除 {deleted} 条课程")
