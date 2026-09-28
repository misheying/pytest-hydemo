# -*- coding: utf-8 -*-
"""
合同管理 测试用例
================
文件上传接口：POST /api/common/upload（multipart/form-data）
新增合同接口：POST /api/contract
查询合同接口：GET /api/contract/list

流程：建课程拿 courseId → 上传合同文件拿 fileName → 新增合同 → 按手机号查询验证。
"""
import time
import os
import base64
import tempfile
import pytest


class TestContract:
    """合同管理 测试类。"""

    @pytest.mark.smoke
    def test_add_and_query_contract(self, logged_in_client, created_course_id):
        """上传文件 + 新增合同 + 查询验证。"""
        # created_course_id 夹具已创建好一门课，拿它的 id（合同必须挂在一门课上）
        course_id = created_course_id

        # 1) 生成一个临时图片文件用于上传（1x1 PNG）
        png = base64.b64decode(
            'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII='
        )
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            f.write(png)
            temp_file = f.name

        # 2) 上传文件，拿到 fileName（上传返回的真实文件地址）
        upload_response = logged_in_client.upload_file(temp_file)
        assert upload_response.status_code == 200
        upload_data = upload_response.json()
        assert upload_data["code"] == 200, f"上传失败：{upload_data.get('msg')}"
        file_name = upload_data["fileName"]  # 如 /profile/upload/2026/09/28/xxx.png
        print(f"\n 上传成功，fileName={file_name}")

        # 3) 准备合同数据（合同编号、手机号用时间戳保证唯一）
        contract_no = f"HT{int(time.time())}"
        phone = f"138{str(int(time.time()))[-8:]}"  # 拼成 11 位手机号

        # 4) 新增合同（fileName 用上传返回的真实地址，不再是写死的占位）
        response = logged_in_client.add_contract(
            contract_no=contract_no,
            phone=phone,
            name="测试客户",
            subject="6",            # 意向学科
            course_id=course_id,    # 课程 id（必填）
            file_name=file_name,    # 文件名称（上传返回的真实地址）
            channel="0",            # 渠道来源：0=线上活动
        )
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200, f"新增合同失败：{data.get('msg')}"
        print("   新增合同成功")

        # 5) 按手机号查询，验证合同真的新增成功
        list_response = logged_in_client.get_contract_list(phone=phone)
        assert list_response.status_code == 200
        list_data = list_response.json()
        assert list_data["code"] == 200
        assert list_data.get("total", 0) >= 1, "新增的合同没查到"
        found = list_data["rows"][0]
        assert found["contractNo"] == contract_no, f"合同编号不对：{found['contractNo']} != {contract_no}"
        print(f"   查询到合同：合同编号={found['contractNo']}，客户={found['name']}")

        # 6) 清理临时文件
        os.remove(temp_file)
