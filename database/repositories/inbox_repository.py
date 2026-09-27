import json

from psycopg import Cursor

from database.postgres import Postgres
from database.entities.inbox import Inbox


class InboxRepository:
    def __init__(self, postgres: Postgres) -> None:
        self.postgres = postgres

    def exists(self, cursor: Cursor, event_id: str) -> bool:
        return (
            self.postgres.fetch_one(
                cursor,
                "SELECT 1 FROM inbox_messages WHERE event_id = %s",
                (event_id,),
            )
            is not None
        )

    def create(self, cursor: Cursor, message: Inbox) -> None:
        self.postgres.execute(
            cursor,
            """
            INSERT INTO inbox_messages (
                event_id, event_type, topic, partition, kafka_offset, payload
            )
            VALUES (%s, %s, %s, %s, %s, %s::jsonb)
            """,
            (
                message.event_id,
                message.event_type,
                message.topic,
                message.partition,
                message.offset,
                json.dumps(json.loads(message.payload)),
            ),
        )

    def mark_processed(self, cursor: Cursor, event_id: str) -> None:
        self.postgres.execute(
            cursor,
            "UPDATE inbox_messages SET processed_at = NOW() WHERE event_id = %s",
            (event_id,),
        )
