from dataclasses import dataclass

@dataclass
class Node():
    """
    This is an ephemeral dataclass.
    Only used by the ObEditItemDialog to structure.
    """
    uuid: str
    name: str = None
    is_folder: bool = False
    parent_uuid: str = None
    address: str = None
    port: int = None
    username: str = None
    password: str = None

