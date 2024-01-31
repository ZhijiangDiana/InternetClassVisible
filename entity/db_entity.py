from tortoise import Model, fields


# {
#     "id": "N0001001100011200",
#     "pid": "N000100110001",
#     "title": "2023级软件工程研究生团支部",
#     "qr_code": "https:\/\/st-file.yunbanos.cn\/uploadsoss\/youth-learning\/2023-10-23\/327748ae7071844cf696e8d82fd4f0bf.jpg"
# }
class Organization(Model):
    id = fields.CharField(max_length=45, pk=True, description="支部nid")
    pid = fields.CharField(max_length=45, description="上级支部nid")
    title = fields.CharField(max_length=114, description="支部名称")
    qr_code = fields.CharField(max_length=1145, description="支部二维码外链地址")


# {
#     "id": "38975",
#     "join_datetime": "2022-09-06 23:17:36",
#     "card_no": "吴琦",
#     "user_type": "团员"
# }
class Member(Model):
    id = fields.IntField(pk=True, description="成员id")
    join_datetime = fields.DatetimeField(description="成员添加时间")
    name = fields.CharField(max_length=114, description="成员姓名")
    user_type = fields.CharField(max_length=45, description="成员类型")

    organization = fields.ForeignKeyField("models.Organization", related_name="Organization")

    finish_task = fields.ManyToManyField("models.Course", through="MemberCourse")


# {
#     "id": "C1003",
#     "type": "网上主题团课",
#     "title": "2022年第2期",
#     "start_datetime": "2022-02-28 09:46:25",
#     "end_datetime": "2022-03-07 12:00:00",
#     "cover": "https:\/\/st-file.yunbanos.cn\/uploadsoss\/youth-learning\/2022-02-28\/85662bb54cbd4b72d8e83e849aac2e90.png",
#     "uri": "http:\/\/h5.cyol.com\/special\/daxuexi\/cq2hkv2t8d\/m.html",
# }
class Course(Model):
    id = fields.CharField(pk=True, max_length=45, description="学习任务id")
    type = fields.CharField(max_length=45, description="学习任务种类")
    title = fields.CharField(max_length=114, description="学习任务标题")
    start_datetime = fields.DatetimeField(description="开始时间")
    end_datetime = fields.DatetimeField(description="结束时间")
    cover = fields.CharField(max_length=1145, description="课程封面外链")
    uri = fields.CharField(max_length=1145, description="课程链接")

    finish_member = fields.ManyToManyField("models.Member", through="MemberCourse")


# {
#     "member_id": "38975",
#     "course_id": "C1080",
#     "finish_datetime": "2024-01-15 11:55:34",
#     "nickname": "sonhyeiio_",
#     "avatar": "https:\/\/thirdwx.qlogo.cn\/mmopen\/vi_32\/fTey0lfI4UYmnORZThr4pdB4m8icJbF2S12R3iccAc13Az21I91Iu7r1riauiaoyfgsjVqgPTa3IL6lBa0xxgo6OCcZBpcPNBNWls5XZNMiaS6yQ\/132"
# }
class MemberCourse(Model):
    member = fields.ForeignKeyField('models.Member', related_name='Course')
    course = fields.ForeignKeyField('models.Course', related_name='Member')

    finish_datetime = fields.DatetimeField(description="完成时间")
    nickname = fields.CharField(max_length=114, description="完成时的昵称")
    avatar = fields.CharField(max_length=1145, description="完成时的头像外链")

    class Meta:
        unique_together = ('member', 'course')

