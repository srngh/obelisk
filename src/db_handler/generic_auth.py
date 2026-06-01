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
    priv_key_file: str = None
    pref_method: str = None
    ignost_host_key: bool = None
    
