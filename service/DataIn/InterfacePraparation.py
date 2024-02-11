"""
@author David Antilles
@createTime 2023-01-12
@version 0.1.14
"""

import json
import random
import threading

import requests
import re
import smtplib
from email.mime.text import MIMEText
from email.header import Header
import base64
import numpy as np
import pandas as pd
import time


# template: https://qcsh.h5yunban.com/youth-learning/cgi-bin/branch-api/course/statis/v3?nid=N000100110001
# &beginCourse=C1049&endCourse=C1055&accessToken=3614061B-3F20-4C68-8BB9-35DAF7D8BB1F


class MailManager:
    def __init__(self, json_file_path):
        self.parser = DoubtfulJsonReader(json_file_path)
        host = 'smtp.' + re.findall("@(.+)", self.parser.read("email_account"))[0]
        self.distribute = smtplib.SMTP(host)
        user = self.parser.read("email_account")
        pwd = self.parser.read("login_key")
        self.distribute.login(user, pwd)

    def send_mail(self, target_email_account):
        user = self.parser.read("email_account")
        body = MIMEText("看到就赶紧去做青大叭，不用回复", 'html', 'utf-8')
        sender = Header("你的催人做青年大学习的团支书", 'utf-8')
        body["From"] = sender
        body["Subject"] = Header("又有你！！快去做青年大学习！！！", "utf-8")
        self.distribute.sendmail(user, target_email_account, body.as_string())


class Base64ImageParser:
    def __init__(self, ori_code):
        source_code = ori_code.replace("data:image/png;base64,", "")
        self.avatar_bytes = base64.b64decode(source_code)

    def parse(self):
        with open("cap.png", "wb+") as f:
            f.write(self.avatar_bytes)


class DoubtfulJsonReader:
    def __init__(self, json_file_path):
        file = open(json_file_path, "r")
        self.text = file.read()
        file.close()

    def read(self, key):
        value = ""
        while value == "":
            try:
                value = json.loads(self.text)[key]

            except:
                print("傻逼json又报错")

        return value


# 爬虫的单例模式
class YouthBigLearning:
    __instance = None
    __lock = threading.Lock()

    def __new__(cls, json_file_path="service/DataIn/prop.json"):
        with cls.__lock:
            if cls.__instance is None:
                print('new successfully')
                cls.__instance = super().__new__(cls)

                # todo 短时间使用还可以，长时间跑的话需要开一个线程维护登陆信息
                cls.__login(cls.__instance, json_file_path)
        return cls.__instance

    """
        登录调用此函数
    """

    def __login(self, json_file_path):
        # 原__init__中的代码块，用于初始化登陆信息
        statusCode = 404
        login_info = None
        # 生成读取器，读取json配置文件中的信息
        self.reader = DoubtfulJsonReader(json_file_path)
        # 读取访问验证码的生成界面
        tar = self.reader.read("target_captcha_generate_url")
        # 读取访问验证码生产界面的请求头
        headers = self.reader.read("captcha_generate_headers")
        # 获取登录接口
        login_url = self.reader.read("login_interface_url")
        # 获取登录请求头
        post_headers = self.reader.read("login_headers")
        while statusCode != 200:
            # 获取生成验证码的响应
            resp = requests.get(url=tar, headers=headers, timeout=300)
            # 获取验证码的base64信息
            captcha_url = resp.json()["result"]['base64']
            # 获取验证码id信息(用于提交表单)
            captcha_id = resp.json()["result"]["id"]
            # 生成验证码解析器
            parser = Base64ImageParser(captcha_url)
            # 解析验证码，保存到本地"cap.png"
            parser.parse()
            # 获取登录验证表单数据
            data = {"account": self.reader.read("account"),
                    "password": self.reader.read("account_password"),
                    "captchaId": captcha_id,
                    # 不用云打码了，反正这个请求对时间要求也不是很急
                    "captcha": input("请输入同级目录下cap.png中的验证码值>>")
                    }
            # 获取登录响应信息
            # pay_load传参方式，data形参需要传入字符串
            login_info = requests.post(login_url, headers=post_headers, data=json.dumps(data))
            print(login_info.json())
            statusCode = login_info.json()["status"]

            # 提示错误信息
            if login_info.json()["message"] is not None:
                print(login_info.json()["message"])

        # 获取对验证至关重要的accessToken参数，accessToken有效时长1小时
        self.access_token = login_info.json()["result"]["accessToken"]

    """
    更新最近期数
    """

    def renewMostRecentPeriodicalNum(self, json_file_path):
        periodicalNum = self.reader.read("mostRecentPeriodicalNum") + 1
        print(periodicalNum)
        while 1:
            params = {
                "nid": self.reader.read("nid"),
                "beginCourse": "C" + str(periodicalNum),
                "accessToken": self.access_token
            }
            r = requests.get(self.reader.read("final_request_template_query_all"), params=params,
                             headers=self.reader.read("login_headers"))
            # print(r.text)
            score = int(r.json()["result"]["node"]["score"])
            if score > 0:
                print(score)
                break
            else:
                periodicalNum += 1
                time.sleep(1)

        text = json.loads(self.reader.text)
        text["mostRecentPeriodicalNum"] = periodicalNum
        # print(periodicalNum)
        with open(json_file_path, "w+") as f:
            f.write(json.dumps(text))
        self.reader = DoubtfulJsonReader(json_file_path)

    """
    解析整个学院的完成情况
    """

    def parseRecentWholeCollegeInfo(self) -> None:
        course = str(self.reader.read("mostRecentPeriodicalNum"))
        params = {
            "nid": self.reader.read("nid"),
            "beginCourse": "C" + course,
            "accessToken": self.access_token
        }

        wholeCollege = requests.get(self.reader.read("final_request_template_query_all"), params=params,
                                    headers=self.reader.read("login_headers")).json()

        columns = ["团支部名称", "支部人数", "本期学习人数", "本期完成率"]
        index = []
        title = []
        memberCnt = []
        user = []
        score = []
        for item in wholeCollege["result"]["branchs"]:
            index.append(item["id"])
            title.append(item["title"])
            memberCnt.append(item["memberCnt"])
            user.append(item["users"])
            score.append(item["score"])

        data = pd.DataFrame(data=np.array([title, memberCnt, user, score]))
        data = data.T
        data.index = index
        data.columns = columns
        data.sort_values(by=["本期完成率"], ascending=False)
        data.to_excel(f"光电学院本期完成率(C{course}).xlsx")
        print("success")

    """
    单独解析某个支部的完成情况
    """

    def parseCertainClass_bothProvideValuesToRenewNumPeriodicalLink(self, class_nid):
        pNum = str(self.reader.read("mostRecentPeriodicalNum"))
        params = {
            "nid": class_nid,
            "course": "C" + str(pNum),
            "accessToken": self.access_token,
            "pageSize": 140,
            "pageNum": 1,
            "desc": "createTime"
        }

        wholeCollege = requests.get(self.reader.read("final_request_template_query_certain"), params=params,
                                    headers=self.reader.read("login_headers")).json()

        columns = ["填入信息", "学习时间", "支部名称", "本期名称"]
        index = []
        cardNo = []
        createTime = []
        course = []
        className = []
        for item in wholeCollege["result"]["list"]:
            index.append(item["id"])
            cardNo.append(item["cardNo"])
            createTime.append(item["createTime"])
            course.append(item["course"])
            className.append(item["branchs"][-1])

        data = pd.DataFrame(data=np.array([cardNo, createTime, className, course]))
        data = data.T
        data.index = index
        data.columns = columns
        if len(className) != 0:
            data.to_excel(f"{className[0]}{course[0]}完成率.xlsx")
        else:
            data.to_excel(f"{class_nid}本期完成率.xlsx")
        print("success")
        # return {f"{pNum}": [f"C{pNum}", course[0]]}

    """
    找出没完成的人并导出名单、给他们发邮件
    """

    def findBitchesRejectFinishingCourseAndSendMail(self, class_member_list):
        f = open(class_member_list, "r", encoding="utf-8")
        inf = json.loads(f.read())
        f.close()
        class_nid = inf["class_nid"]
        pNum = str(self.reader.read("mostRecentPeriodicalNum"))
        params = {
            "nid": class_nid,
            "course": "C" + str(pNum),
            "accessToken": self.access_token,
            "pageSize": 140,
            "pageNum": 1,
            "desc": "createTime"
        }

        wholeCollege = requests.get(self.reader.read("final_request_template_query_certain"), params=params,
                                    headers=self.reader.read("login_headers")).json()
        did_person = []
        # 姓名和邮箱的映射
        name_email_reflect = {}

        whole_class_name = []
        for k in inf["members"].keys():
            whole_class_name.append(inf["members"][k]["name"])
            name_email_reflect[whole_class_name[-1]] = inf["members"][k]["email_address"]

        whole_class_id = list(inf["members"].keys())

        for item in wholeCollege["result"]["list"]:
            res = re.findall("[0-9]+", item["cardNo"])
            # print(res)
            if len(res) == 0 and whole_class_name.__contains__(item["cardNo"]):
                did_person.append(item["cardNo"])
            elif len(res) != 0 and whole_class_id.__contains__(res[0]):
                did_person.append(inf["members"][res[0]]["name"])

        # mail_manager = MailManager("prop.json")
        # print(did_person)
        # print(whole_class_name)

        for i in (set(whole_class_name) - set(did_person)):
            # mail_manager.send_mail(name_email_reflect[i])
            time.sleep(3)
            print(i, end=" ")
        print("\n")
        print("邮件发送完成")

    def parseCertainClass_periodFinishPersons(self, class_nid):
        n = int(input("请输入你想查询的期数"))
        courses = []
        for i in range(n):
            courses.append(input())
        for i in courses:
            params = {
                "nid": class_nid,
                "course": "C" + i,
                "accessToken": self.access_token,
                "pageSize": 140,
                "pageNum": 1,
                "desc": "createTime"
            }

            wholeCollege = requests.get(self.reader.read("final_request_template_query_certain"), params=params,
                                        headers=self.reader.read("login_headers")).json()

            columns = ["填入信息", "学习时间", "支部名称", "本期名称"]
            index = []
            cardNo = []
            createTime = []
            course = []
            className = []
            for item in wholeCollege["result"]["list"]:
                index.append(item["id"])
                cardNo.append(item["cardNo"])
                createTime.append(item["createTime"])
                course.append(item["course"])
                className.append(item["branchs"][-1])

            data = pd.DataFrame(data=np.array([cardNo, createTime, className, course]))
            data = data.T
            data.index = index
            data.columns = columns
            if len(className) != 0:
                data.to_excel(f"{className[0]}{course[0]}完成率.xlsx")
            else:
                data.to_excel(f"{class_nid}本期完成率.xlsx")
        print("success")

    """
        爬取某人所有的学习记录
    """

    def get_member_record(self, org_id="", mem_name=""):
        params = {
            "nid": org_id,
            "cardNo": mem_name,
            "accessToken": self.access_token,
            "pageNum": 1,
        }

        resp = requests.get(self.reader.read("query_record_by_member"), params=params,
                            headers=self.reader.read("login_headers")).json()
        # print(org_id, mem_name, resp)
        respList = resp["result"]

        time.sleep(random.randrange(1, 3))
        return respList

    """
        爬取所有团员信息
    """

    def getAllMember(self, org_id=""):
        all_member = []
        cnt = 1
        while True:
            params = {
                "pageSize": 300,
                "pageNum": cnt,
                "desc": "createTime",
                "nid": org_id,
                "course": None,
                "accessToken": self.access_token
            }

            resp = requests.get(self.reader.read("query_member"), params=params,
                                headers=self.reader.read("login_headers")).json()

            respList = resp["result"]["list"]
            total_cnt = resp["result"]["pagedInfo"]["total"]
            if respList:
                all_member += respList
            else:
                break
            print(f"\r当前{len(all_member)}  剩余{total_cnt}", end='')
            time.sleep(random.randrange(1, 5))

            cnt += 1
        return all_member

    """
        爬取所有课程信息
    """
    def get_all_courses(self):
        params = {
            "pageSize": 999,
            "pageNum": 1,
            "desc": "startTime",
            "type": "网上主题团课",
            "accessToken": self.access_token
        }
        resp = requests.get(self.reader.read("query_all_courses"), params=params,
                            headers=self.reader.read("login_headers")).json()

        # {
        #     "id": "C1080",
        #     "pid": "C",
        #     "type": "网上主题团课",
        #     "startTime": "2024-01-08 10:04:36",
        #     "endTime": "2024-01-15 12:00:00",
        #     "title": "2024年第1期",
        #     "cover": "https:\/\/st-file.yunbanos.cn\/uploadsoss\/youth-learning\/2024-01-08\/a46b010eac1a0314bcfae59d3623adac.png",
        #     "uriType": "超链接",
        #     "uri": "https:\/\/h5.cyol.com\/special\/daxuexi\/ga1hyw0m8q\/index.html",
        #     "content": null,
        #     "s": "正常",
        #     "creator": "0003417D-0876-4282-8FC5-CA08E0D454E9",
        #     "createTime": "2024-01-08 10:05:02",
        #     "users": "839382",
        #     "clickTimes": "1032008",
        #     "isTop": null,
        #     "score": null
        # }

        return resp["result"]["list"]
