from dataclasses import dataclass

@dataclass
class Auth():
    """
    This is an ephemeral dataclass.
    Only used by the ObEditItemDialog structure.
    """
    auth_uuid: str
    username: str = None
    password: str = None
    key_file: str = None

