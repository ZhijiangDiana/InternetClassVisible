from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `membercourse` DROP COLUMN `nickname`;
        ALTER TABLE `membercourse` DROP COLUMN `avatar`;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `membercourse` ADD `nickname` VARCHAR(114) NOT NULL  COMMENT '完成时的昵称';
        ALTER TABLE `membercourse` ADD `avatar` VARCHAR(1145) NOT NULL  COMMENT '完成时的头像外链';"""
