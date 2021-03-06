# -*- coding: utf-8 -*-
##
## This file is part of Invenio.
## Copyright (C) 2013 CERN.
##
## Invenio is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License as
## published by the Free Software Foundation; either version 2 of the
## License, or (at your option) any later version.
##
## Invenio is distributed in the hope that it will be useful, but
## WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
## General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with Invenio; if not, write to the Free Software Foundation, Inc.,
## 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.


import sys
from invenio.config import CFG_SITE_SECRET_KEY
from invenio.scriptutils import Manager, change_command_name, \
    generate_secret_key, register_manager
from invenio.sqlalchemyutils import db
from invenio.webinterface_handler_flask import create_invenio_flask_app


# Fixes problems with empty secret key in config manager.
if 'config' in sys.argv and \
        (not CFG_SITE_SECRET_KEY or CFG_SITE_SECRET_KEY == ''):
    create_invenio_flask_app = create_invenio_flask_app(
        SECRET_KEY=generate_secret_key())


manager = Manager(create_invenio_flask_app, with_default_commands=False)
register_manager(manager)


@manager.shell
def make_shell_context():
    """Extend shell context."""
    from flask import current_app
    return dict(current_app=current_app, db=db)


@manager.command
def version():
    """ Get running version of Invenio """
    from invenio.config import CFG_VERSION
    return CFG_VERSION


@manager.command
@change_command_name
def check_for_software_updates():
    from flask import get_flashed_messages
    from invenio.scriptutils import check_for_software_updates
    print ">>> Going to check software updates ..."
    result = check_for_software_updates()
    messages = list(get_flashed_messages(with_categories=True))
    if len(messages) > 0:
        print '\n'.join(map(lambda t, msg: '[%s]: %s' % (t.upper(), msg),
                            messages))
    print '>>> ' + ('Invenio is up to date.' if result else
        'Please consider updating your Invenio installation.')

@manager.command
@change_command_name
def detect_system_details():
    """
    Detect and print system details such as Apache/Python/MySQL
    versions etc. (useful for debugging problems on various OS)
    """
    import sys
    import socket
    print ">>> Going to detect system details..."
    print "* Hostname: " + socket.gethostname()
    print "* Invenio version: " + version()
    print "* Python version: " + sys.version.replace("\n", " ")

    try:
        from invenio.apache_manager import version as detect_apache_version
        print "* Apache version: " + detect_apache_version(
            separator=";\n                  ")
    except ImportError:
        print >> sys.stderr, '* Apache manager could not be imported.'

    try:
        from invenio.database_manager import \
            mysql_info, \
            version as detect_database_driver_version, \
            driver as detect_database_driver_name

        print "* " + detect_database_driver_name() + " version: " + \
            detect_database_driver_version()
        try:
            out = mysql_info(separator="\n", line_format="    - %s: %s")
            print "* MySQL version:\n", out
        except Exception, e:
            print >> sys.stderr, "* Error:", e
    except ImportError:
        print >> sys.stderr, '* Database manager could not be imported.'

    print ">>> System details detected successfully."


def main():
    manager.run()

if __name__ == "__main__":
    main()
