from tortoise import Model, fields


class Organization(Model):
    id = fields.CharField(max_length=45, pk=True, description="支部nid")
    pid = fields.CharField(max_length=45, description="上级支部nid")
    title = fields.CharField(max_length=114, description="支部名称", unique=True)
    qr_code = fields.CharField(max_length=1145, description="支部二维码外链地址")
    create_time = fields.DatetimeField(description="支部创建时间")


class Member(Model):
    id = fields.IntField(pk=True, description="成员id")
    join_datetime = fields.DatetimeField(description="成员添加时间")
    name = fields.CharField(max_length=114, description="成员姓名")
    user_type = fields.CharField(max_length=45, description="成员类型")
    email = fields.CharField(max_length=114, null=True, description="成员邮箱")
    password = fields.CharField(max_length=114, null=True, description="成员密码", default="114514")
    permission = fields.IntField(description="成员权限", default=1)

    organization = fields.ForeignKeyField("models.Organization", related_name="Organization")

    finish_task = fields.ManyToManyField("models.Course", through="MemberCourse")


class Course(Model):
    id = fields.CharField(pk=True, max_length=45, description="学习任务id")
    type = fields.CharField(max_length=45, description="学习任务种类")
    title = fields.CharField(max_length=114, description="学习任务标题")
    start_datetime = fields.DatetimeField(description="开始时间")
    end_datetime = fields.DatetimeField(description="结束时间")
    cover = fields.CharField(max_length=1145, description="课程封面外链")
    uri = fields.CharField(max_length=1145, description="课程链接")

    finish_member = fields.ManyToManyField("models.Member", through="MemberCourse")


class MemberCourse(Model):
    member = fields.ForeignKeyField('models.Member', related_name='Member')
    course = fields.ForeignKeyField('models.Course', related_name='Course')

    finish_datetime = fields.DatetimeField(null=True, description="完成时间")

    class Meta:
        unique_together = ('member', 'course')

