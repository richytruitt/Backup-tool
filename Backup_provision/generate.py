import os
import sys
from jinja2 import Environment, FileSystemLoader
import subprocess


PATH = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_ENVIRONMENT = Environment(
    autoescape=False,
    loader=FileSystemLoader(os.path.join(PATH, 'templates')),
    trim_blocks=False
)

def render_template(template_filename, context):
    return TEMPLATE_ENVIRONMENT.get_template(template_filename).render(context)

def create_file():
    fname = 'inventory/inventory.ini'
    sshd_config = 'cots/sshd_config'

    username = sys.argv[1]
    password = sys.argv[2]
    ip = sys.argv[3]


    context = {
        'username': username,
        'password': password, 
        'ip': ip
    }

    with open(fname,'w') as f:
        inventory = render_template('inventory_template', context)
        f.write(inventory)
    
    with open(sshd_config, 'w') as f:
        config = render_template('sshd_config_template', context)
        f.write(config)


def main():
    create_file()


if __name__ == '__main__':
    main()
    subprocess.call(['ansible-playbook', '-i', 'inventory/inventory.ini', '-c','paramiko','playbooks/sftp.yml'])