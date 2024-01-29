import shelve


class IdShelve:
    def __init__(self, file_name: str) -> None:
        self._file_name = file_name

    def store_used_ids(self, ids: list[str]) -> None:
        with shelve.open(self._file_name) as sh:
            sh["ids"] = ids

    def read_used_ids(self) -> list[str]:
        with shelve.open(self._file_name) as sh:
            return sh.get("ids", [])


class MappingIdShelve:
    def __init__(self, file_name: str) -> None:
        self._file_name = file_name

    def store_used_ids(self, chat_id: int, ids: list[str]) -> None:
        with shelve.open(self._file_name) as sh:
            sh[str(chat_id)] = ids

    def read_used_ids(self, chat_id: int) -> list[str]:
        with shelve.open(self._file_name) as sh:
            return sh.get(str(chat_id), [])

    def get_chat_ids(self) -> list[str]:
        with shelve.open(self._file_name) as sh:
            return list(sh.keys())

    def is_chat_id_already_in_keys(self, chat_id: int) -> bool:
        with shelve.open(self._file_name) as sh:
            return str(chat_id) in sh.keys()
