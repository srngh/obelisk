# initialize_backend.py
#
# Copyright 2026 simhof
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# SPDX-License-Identifier: GPL-3.0-or-later

from pathlib import Path
from cryptography import fernet
import keyring
import os

from .ob_db_config import ObDBConfig

def get_data_home() -> str:
    """
    Get the Flatpak $XDG_DATA_HOME Path.

    :return: XDG_DATA_HOME
    :rtype: str
    """
    env = os.environ.copy()
    home = None
    if "XDG_DATA_HOME" in env.keys():
        home = env["XDG_DATA_HOME"]

    print(f"Data Home is at {home}")
    return home

def get_master_dek() -> str:
    """
    Retrieve the secrete_key from the system keyring.
    On first startup a new secret_key is created and stored in the system keyring.

    :return: secret_key
    :rtype: str
    """
    secret_key = keyring.get_password("io.github.srngh.obelisk", "master_dek")

    if secret_key is None:
        print("No key found. This might be a first-time application launch.")
        print("Generating new key.")
        key = fernet.Fernet.generate_key()
        print("writing key to keyring")
        keyring.set_password("io.github.srngh.obelisk", "master_dek", key)
        # Check if the key was actually written to the keyring
        secret_key = keyring.get_password("io.github.srngh.obelisk", "master_dek")
        if key.decode() == secret_key:
            print("master_dek was written to the keyring successfully")
            return secret_key
        else:
            print("couldn't find the master_dek in the keyring anymore?!")
    else:
        print("Key securely retrieved from system keyring.")
        return secret_key

def get_config() -> ObDBConfig:
    """
    Check if the users config directory can be accessed to use the sqlite DB.
    Otherwise uses the flatpak $XDG_DATA_HOME to store the DB.

    :return: ObDBConfig
    :rtype: ObDBConfig
    """

    home_dir = Path.home()
    home_config_dir = f"{home_dir}/.config"
    obelisk_config_dir = f"{home_dir}/.config/obelisk"
    
    if Path(home_config_dir).exists() and not Path(obelisk_config_dir).exists() and os.access(home_config_dir, os.W_OK):
        Path.mkdir(obelisk_config_dir)
    else:
        print(f"Could not find {obelisk_config_dir} or create it")


    if Path(obelisk_config_dir).exists() and os.access(f"{obelisk_config_dir}", os.W_OK):
        config = ObDBConfig(
            db_path = f'{obelisk_config_dir}/obelisk.db'
        )
        return config
    else:
        data_dir = get_data_home()
        config = ObDBConfig(
            db_path = f'{data_dir}/obelisk.db'
        )
        print(f"Falling back to placing the db in {data_dir}")
        return config