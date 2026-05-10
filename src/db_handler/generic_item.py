from uuid import uuid4


class Item():

    def __init__(
        self,
        name: str,
        is_folder: bool,
        uuid: str,
        username: str,
        address: str,
        description: str,
        protocol: str,
        port: int,
        auth: str
    ):
        self.name = name
        self.is_folder = is_folder,
        self.uuid = str(uuid4())
        self.username: str = username
        self.address: str = address
        self.description: str = description
        self.protocol: str = protocol
        self.port: int = port
        self.auth: str = auth

    def __repr__(self):
        return f'{self.name}-{self.uuid}-{self.username}-{self.address}-{self.description}-{self.protocol}-{self.port}-{self.auth}'


