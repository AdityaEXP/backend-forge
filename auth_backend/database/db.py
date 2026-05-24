import asyncpg
from dotenv import load_dotenv
from auth_backend.database.sql import ALL_QUERY
import os, asyncio

load_dotenv()

DATABASE_URL = os.getenv("DB_URL")

class Postgres:
    def __init__(self, database_url: str):
        self.database_url = database_url
        self.pool = None

    async def connect(self):

        for _ in range(10):
            try:
                self.pool = await asyncpg.create_pool(
                    dsn=self.database_url,
                    min_size=5,
                    max_size=20
                )

                print("Database connected")
                return

            except Exception as e:
                print(f"Database connection failed: {e}")
                print("Retrying in 2 seconds...")

                await asyncio.sleep(2)

        raise Exception("Could not connect to database")

    # async def connect(self):
    #     self.pool = await asyncpg.create_pool(
    #         dsn=self.database_url,
    #         min_size=5,
    #         max_size=20
    #     )

    async def disconnect(self):
        if self.pool:
            await self.pool.close()

    async def init_db(self):
        async with self.pool.acquire() as connection:
            for query in ALL_QUERY:
                await connection.execute(query)


database = Postgres(DATABASE_URL)
