"""Write /data/config.yml on first boot and keep the Railway-managed settings in it current.

Railway variables own: password (HOMEHUB_SITE_PASSWORD), instance_name (HOMEHUB_INSTANCE_NAME)
and family_members (HOMEHUB_FAMILY_MEMBERS). Everything else in config.yml is yours to edit
(railway ssh, then vi /data/config.yml); HomeHub picks changes up on the next page load.
The admin password (HOMEHUB_ADMIN_PASSWORD) is stored as a salted hash in the database.
"""
import os
import re
import sys

import yaml

DATA = os.environ.get('HOMEHUB_DATA_DIR', '/data')
CONFIG = os.path.join(DATA, 'config.yml')
EXAMPLE = '/app/config-example.yml'


def die(msg):
    print(f'homehub-railway: {msg}', file=sys.stderr)
    sys.exit(1)


def set_top_level(text, key, value):
    """Replace a top-level YAML key (and its indented block) in place, keeping comments elsewhere."""
    rendered = yaml.safe_dump({key: value}, sort_keys=False, allow_unicode=True, default_flow_style=False).rstrip('\n')
    lines = text.splitlines()
    out, i, done = [], 0, False
    pattern = re.compile(rf'^{re.escape(key)}\s*:')
    while i < len(lines):
        if not done and pattern.match(lines[i]):
            out.append(rendered)
            i += 1
            while i < len(lines) and lines[i][:1] in (' ', '\t', '-'):
                i += 1
            done = True
            continue
        out.append(lines[i])
        i += 1
    if not done:
        out.append(rendered)
    return '\n'.join(out) + '\n'


def main():
    site_pw = os.environ.get('HOMEHUB_SITE_PASSWORD', '')
    admin_pw = os.environ.get('HOMEHUB_ADMIN_PASSWORD', '')
    if len(site_pw) < 12 or len(admin_pw) < 12:
        die('HOMEHUB_SITE_PASSWORD and HOMEHUB_ADMIN_PASSWORD must be 12+ characters')

    first = not os.path.isfile(CONFIG)
    if first:
        with open(EXAMPLE, encoding='utf-8') as f:
            text = f.read()
        # The example's sample names are someone's family; start with neutral ones
        text = set_top_level(text, 'family_members', ['Mom', 'Dad'])
        text = set_top_level(text, 'instance_name', 'Our Home Hub')
    else:
        with open(CONFIG, encoding='utf-8') as f:
            text = f.read()

    name = os.environ.get('HOMEHUB_INSTANCE_NAME', '').strip()
    if name:
        text = set_top_level(text, 'instance_name', name)
    members = [m.strip() for m in os.environ.get('HOMEHUB_FAMILY_MEMBERS', '').split(',') if m.strip()]
    if members:
        # Keep a member's chart colour if config.yml already gives one
        try:
            current = (yaml.safe_load(text) or {}).get('family_members') or []
        except yaml.YAMLError:
            current = []
        colours = {e.get('name'): e for e in current if isinstance(e, dict) and e.get('name')}
        text = set_top_level(text, 'family_members', [colours.get(m, m) for m in members])
    text = set_top_level(text, 'password', site_pw)

    try:
        parsed = yaml.safe_load(text)
    except yaml.YAMLError as e:
        die(f'{CONFIG} is not valid YAML after the update: {e}')
    if not isinstance(parsed, dict) or str(parsed.get('password')) != site_pw:
        die('could not set the site password in config.yml; refusing to start an open HomeHub')

    tmp = CONFIG + '.tmp'
    fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, 'w', encoding='utf-8') as f:
        f.write(text)
    os.replace(tmp, CONFIG)
    print(f'homehub-railway: {"wrote" if first else "updated"} {CONFIG}', flush=True)

    # Admin password: set it only when the stored hash doesn't match, so unlocked sessions survive restarts
    sys.path.insert(0, '/app')
    from werkzeug.security import check_password_hash
    from app import create_app, admin
    app = create_app()
    with app.app_context():
        current = admin.get_admin_password_hash()
        if not current or not check_password_hash(current, admin_pw):
            admin.set_admin_password(admin_pw)
            print('homehub-railway: admin password set from HOMEHUB_ADMIN_PASSWORD', flush=True)
        if not admin.admin_password_enabled():
            die('admin password is not set; refusing to start')


if __name__ == '__main__':
    main()
