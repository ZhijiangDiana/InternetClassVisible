import numpy as np
import pandas as pd
import json
import time
import datetime
from InterfacePraparation import MailManager

# def parseRecentWholeCollegeInfo():
#     wholeCollege0 = open("光电学院支部信息.json", "r", encoding="utf-8")
#
#     text = wholeCollege0.read()
#     wholeCollege = json.loads(text)
#
#     columns = ["团支部名称", "支部人数", "本期学习人数", "本期完成率"]
#     index = []
#     title = []
#     memberCnt = []
#     user = []
#     score = []
#     for item in wholeCollege["result"]["branchs"]:
#         index.append(item["id"])
#         title.append(item["title"])
#         memberCnt.append(item["memberCnt"])
#         user.append(item["users"])
#         score.append(item["score"])
#
#     data = pd.DataFrame(data=np.array([title, memberCnt, user, score]))
#     data = data.T
#     data.index = index
#     data.columns = columns
#     data.sort_values(by=["本期完成率"], ascending=False)
#     data.to_excel("本期完成率1032.xlsx")
#     print("success")

# def parseRecentWholeCollegeInfo():
#     wholeCollege0 = open("某班具体完成响应.json", "r", encoding="utf-8")
#
#     text = wholeCollege0.read()
#     wholeCollege = json.loads(text)
#
#     columns = ["填入信息", "学习时间", "支部名称", "本期名称"]
#     index = []
#     cardNo = []
#     createTime = []
#     course = []
#     className = []
#     for item in wholeCollege["result"]["list"]:
#         index.append(item["id"])
#         cardNo.append(item["cardNo"])
#         createTime.append(item["createTime"])
#         course.append(item["course"])
#         className.append(item["branchs"][-1])
#
#     data = pd.DataFrame(data=np.array([cardNo, createTime, course, className]))
#     data = data.T
#     data.index = index
#     data.columns = columns
#     data.to_excel(f"{className[0]}本期完成率1032.xlsx")
#     print("success")


if __name__ == '__main__':
    # file = open("prop.json", "r")
    # text = file.read()
    # dic = json.loads(text)
    # dic["mostRecentPeriodicalNum"] = 12
    # file.close()
    # file = open("prop.json", "w")
    # file.write(json.dumps(dic))
    # file.close()


    # file = open("21CS1.json", "r", encoding="utf-8")
    # t = file.read()
    # file.close()
    # dic = json.loads(t)
    # for k in dic["members"].keys():
    #     print("\""+k+"\":{\"name\":\""+dic["members"][k]+"\",\"email_address\":"+"\"@qq.com\"},")

    print(datetime.datetime.now())
    mail = MailManager("prop.json")
    mail.send_mail("1179948527@qq.com")

