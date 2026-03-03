import yaml


class Item(yaml.YAMLObject):

    def __init__(
        self,
        name: str,
        uuid: str,
        username: str,
        ip4_address: str,
        description: str,
        protocol: str,
        port: int,
        auth: str
    ):
        self.name = name
        self.uuid = uuid
        self.username: str = username
        self.ip4_address: str = ip4_address
        self.description: str = description
        self.protocol: str = protocol
        self.port: int = port
        self.auth: str = auth

    def __repr__(self):
        return f'{self.name}-{self.uuid}-{self.username}-{self.ip4_address}-{self.description}-{self.protocol}-{self.port}-{self.auth}'


def item_representer(dumper: yaml.SafeDumper, item: Item) -> yaml.nodes.MappingNode:
    return dumper.represent_mapping('!Item', {
        'name': item.name,
        'uuid': item.uuid,
        'username': item.username,
        'ip4_address': item.ip4_address,
        'description': item.description,
        'protocol': item.protocol,
        'port': item.port,
        'auth': item.auth
    })


def item_constructor(loader, node):
    values = loader.construct_mapping(node)
    return Item(**values)
