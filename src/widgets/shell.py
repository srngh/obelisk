from interactive_shell import open_shell

import paramiko

client = paramiko.SSHClient()
client.load_system_host_keys()

# This is just a dummy user on a lab machine
client.connect('10.0.10.11', username='bob', password='VpRDugbLeysr_7Ua33jyj6_r3rnXzv')
open_shell(client)
