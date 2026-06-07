from dataclasses import dataclass

@dataclass
class Node():
    """
    This is an ephemeral dataclass.
    Only used by the ObEditItemDialog structure.
    """
    uuid: str
    name: str = None
    is_folder: bool = False
    parent_uuid: str = None
    address: str = None
    port: int = None
    auth_uuid: str = None
    use_parent_auth: bool = None
    is_jumphost: bool = None
    use_jumphost: str = None
    use_parent_jumphost: bool = None

