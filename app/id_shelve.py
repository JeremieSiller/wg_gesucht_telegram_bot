import shelve


class MappingIdShelve:
    def __init__(self, file_name: str) -> None:
        self._file_name = file_name

    def store_used_ids(self, chat_id: str, ids: list[str]) -> None:
        with shelve.open(self._file_name) as sh:
            sh[chat_id] = ids

    def read_used_ids(self, chat_id: str) -> list[str]:
        with shelve.open(self._file_name) as sh:
            return sh.get(chat_id, [])

    def get_chat_ids(self) -> list[str]:
        with shelve.open(self._file_name) as sh:
            return list(sh.keys())

    def is_chat_id_already_in_keys(self, chat_id: int) -> bool:
        chat_id_strings = self.get_chat_ids()
        return str(chat_id) in [s.split("|")[-1] for s in chat_id_strings]

    def remove_chat_id(self, chat_id: str) -> None:
        with shelve.open(self._file_name) as sh:
            del sh[chat_id]


class MappingLinkShelve:
    def __init__(self, file_name: str) -> None:
        self._file_name = file_name

    def store_link(self, chat_id: str, link: str) -> None:
        with shelve.open(self._file_name) as sh:
            sh[chat_id] = link

    def read_link(self, chat_id: str) -> str:
        with shelve.open(self._file_name) as sh:
            return sh.get(chat_id, "")

    def remove_chat_id(self, chat_id: str) -> None:
        with shelve.open(self._file_name) as sh:
            del sh[chat_id]
