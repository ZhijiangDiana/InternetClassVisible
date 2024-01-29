from InterfacePraparation import YouthBigLearning

a = YouthBigLearning("prop.json")
# 新的一周开始记得把下面这行代码解开跑一下
# a.renewMostRecentPeriodicalNum("prop.json")
a.parseRecentWholeCollegeInfo()
while 1:
    print("程序功能如下：\n1.查看本学院完成率情况\n2.查询某一支部完成率情况\n3.给没做的同学发邮件\n4.查询某支部一段时期内完成情况\n输入-1退出程序")
    cmd = input("输入命令>>")
    if cmd == '1':
        a.parseRecentWholeCollegeInfo()
    elif cmd == '2':
        a.parseCertainClass_bothProvideValuesToRenewNumPeriodicalLink(input("输入支部的nid数据"))
    elif cmd == '3':
        a.findBitchesRejectFinishingCourseAndSendMail(input("输入存放该班级信息的json文件全称"))
    elif cmd == '4':
        a.parseCertainClass_periodFinishPersons(input("输入支部的nid数据"))
    elif cmd == '-1':
        exit(0)
    else:
        print("非法输入！")
