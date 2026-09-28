import json
from urllib import response

import pytest
from src.apiclient import AIPClient
from data.login_test import login_test_data
from tests.tset003 import uuid


class testlogindatadriven:
    correct_captcha ="2"

    @pytest.fixture(scope="function")
    def login_client(self):
        login_client = AIPClient()
        yield login_client
        login_client.close()

    @pytest.fixture(scope="function")
    def captcha_client(self,login_client):
        response=login_client.get_captcha()
        assert response.status_code == 200
        data=json.loads(response.json())
        return {"uuid":data["uuid"]}

    @pytest.mark.parametrize("test_case", login_test_data)
    def login_test(self,login_client,captcha_client,test_case):

        test_id = test_case["id"]
        descrption = test_case["descrption"]
        username = test_case["username"]
        password = test_case["password"]
        code_type = test_case["code_type"]
        expected_code = test_case["expected_code"]
        expected_msg = test_case.get("expected_msg")
        check_token =test_case.get("check_token",False)

        code = self.correct_captcha if code_type=="correct" else "8888"
        uuid =captcha_client["uuid"]

        print(f'\nzhixingyongli')

        response=login_client.login(
            username=username,
            password=password,
            uuid=uuid,
            code=code,
        )
        assert response.status_code == 200
        data=response.json()
        assert data["code"] == expected_code,\
            f"yongli{test_id}shibai:qiwang code={expected_code},shiji code={data['code']}"

        if expected_msg:
            assert  data['msg']== expected_msg,\
                 f"yongli{test_id}shibai msg={expected_msg},shiji msg={data['msg']}"
            if check_token:
                assert "token" in data
                assert data["token"] == check_token
                print(f"token:{check_token}")

            print(f"yongli{test_id}success")

