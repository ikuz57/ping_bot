from dataclasses import dataclass


@dataclass
class Devices():
    id: int
    name: str
    ip: str
    id_object: int


@dataclass
class Objects():
    id: int
    name: str


@dataclass
class Favorites():
    id: int
    id_chat: str
    id_object: int
