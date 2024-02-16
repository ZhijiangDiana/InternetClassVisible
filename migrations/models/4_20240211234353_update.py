from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `member` ADD `email` VARCHAR(114)   COMMENT '成员邮箱';
        ALTER TABLE `membercourse` MODIFY COLUMN `finish_datetime` DATETIME(6)   COMMENT '完成时间';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `member` DROP COLUMN `email`;
        ALTER TABLE `membercourse` MODIFY COLUMN `finish_datetime` DATETIME(6) NOT NULL  COMMENT '完成时间';"""
