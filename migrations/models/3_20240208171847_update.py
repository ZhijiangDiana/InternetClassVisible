from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `organization` ADD `create_time` DATETIME(6) NOT NULL  COMMENT '支部创建时间';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `organization` DROP COLUMN `create_time`;"""
