from dataclasses import dataclass


@dataclass
class Node:
    """
    Only really used by the ObEditItemDialog to shuffle data to the database.
    This class is not used by any UI parts.
    """

    uuid: str
    protocol: str = "ssh"
    name: str = None
    is_folder: bool = False
    parent_uuid: str = None
    address: str = None
    port: int = None
    auth_uuid: str = None
    use_parent_auth: bool = None
    is_jumphost: bool = None
    jumphost_uuid: str = None
    use_parent_jumphost: bool = None
