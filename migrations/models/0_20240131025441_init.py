from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS `course` (
    `id` VARCHAR(45) NOT NULL  PRIMARY KEY COMMENT '学习任务id',
    `type` VARCHAR(45) NOT NULL  COMMENT '学习任务种类',
    `title` VARCHAR(114) NOT NULL  COMMENT '学习任务标题',
    `start_datetime` DATETIME(6) NOT NULL  COMMENT '开始时间',
    `end_datetime` DATETIME(6) NOT NULL  COMMENT '结束时间',
    `cover` VARCHAR(1145) NOT NULL  COMMENT '课程封面外链',
    `uri` VARCHAR(1145) NOT NULL  COMMENT '课程链接'
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `organization` (
    `id` VARCHAR(45) NOT NULL  PRIMARY KEY COMMENT '支部nid',
    `pid` VARCHAR(45) NOT NULL  COMMENT '上级支部nid',
    `title` VARCHAR(114) NOT NULL  COMMENT '支部名称',
    `qr_code` VARCHAR(1145) NOT NULL  COMMENT '支部二维码外链地址'
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `member` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT COMMENT '成员id',
    `join_datetime` DATETIME(6) NOT NULL  COMMENT '成员添加时间',
    `name` VARCHAR(114) NOT NULL  COMMENT '成员姓名',
    `user_type` VARCHAR(45) NOT NULL  COMMENT '成员类型',
    `organization_id` VARCHAR(45) NOT NULL,
    CONSTRAINT `fk_member_organiza_5399c2e9` FOREIGN KEY (`organization_id`) REFERENCES `organization` (`id`) ON DELETE CASCADE
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `membercourse` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `finish_datetime` DATETIME(6) NOT NULL  COMMENT '完成时间',
    `nickname` VARCHAR(114) NOT NULL  COMMENT '完成时的昵称',
    `avatar` VARCHAR(1145) NOT NULL  COMMENT '完成时的头像外链',
    `course_id` VARCHAR(45) NOT NULL,
    `member_id` INT NOT NULL,
    UNIQUE KEY `uid_membercours_member__9af12c` (`member_id`, `course_id`),
    CONSTRAINT `fk_memberco_course_d18c6aa7` FOREIGN KEY (`course_id`) REFERENCES `course` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_memberco_member_47f5fffd` FOREIGN KEY (`member_id`) REFERENCES `member` (`id`) ON DELETE CASCADE
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `aerich` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `version` VARCHAR(255) NOT NULL,
    `app` VARCHAR(100) NOT NULL,
    `content` JSON NOT NULL
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `MemberCourse` (
    `course_id` VARCHAR(45) NOT NULL,
    `member_id` INT NOT NULL,
    FOREIGN KEY (`course_id`) REFERENCES `course` (`id`) ON DELETE CASCADE,
    FOREIGN KEY (`member_id`) REFERENCES `member` (`id`) ON DELETE CASCADE
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `MemberCourse` (
    `member_id` INT NOT NULL,
    `course_id` VARCHAR(45) NOT NULL,
    FOREIGN KEY (`member_id`) REFERENCES `member` (`id`) ON DELETE CASCADE,
    FOREIGN KEY (`course_id`) REFERENCES `course` (`id`) ON DELETE CASCADE
) CHARACTER SET utf8mb4;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """
