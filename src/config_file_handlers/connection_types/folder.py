import yaml


class Folder(yaml.YAMLObject):

    def __init__(self, name, uuid, connections: list):
        self.name = name
        self.uuid = uuid
        self.connections = connections

    def __repr__(self):
        return f'{self.name} - {self.connections}'


def folder_representer(dumper: yaml.SafeDumper, folder: Folder) -> yaml.nodes.MappingNode:
    return dumper.represent_mapping('!Folder', {
        'name': folder.name,
        'uuid': folder.uuid,
        'connections': folder.connections,
    })


def folder_constructor(loader, node):
    values = loader.construct_mapping(node)
    return Folder(**values)

