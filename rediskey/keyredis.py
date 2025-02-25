from typing import Optional, Literal

from aiogram.fsm.storage.base import KeyBuilder, StorageKey


class KeyRedis(KeyBuilder):
    def __init__(
            self,
            *,
            prefix: str = "my_fsm",
            separator: str = ":"
    ) -> None:
        self.prefix = prefix
        self.separator = separator


    def build(
        self,
        key: StorageKey,
        part: Optional[Literal["data", "state", "lock"]] = None,
    ) -> str:
        parts = [self.prefix]
        parts.append(str(key.chat_id))
        if part:
            parts.append(part)
        return self.separator.join(parts)