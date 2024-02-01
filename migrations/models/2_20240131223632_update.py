from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `organization` ADD UNIQUE INDEX `uid_organizatio_title_841a2f` (`title`);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `organization` DROP INDEX `idx_organizatio_title_841a2f`;"""
