#!/usr/bin/python

"""

Classes for useful for debugging.

"""

import os
import sys


class LocalEnvironment(object):
    """Class for exposing local environment.

    WARNING: This class exposes sensitive data. Use with caution.

    Example usage

    Controller:

        @auth.requires_membership('admin')
        def environment():
            from applications.shared.modules.local.environment import LocalEnvironment
            local_env = LocalEnvironment(request=request, session=session,
                                         auth=auth, beauty=BEAUTIFY, db=db)

            env_vars = DIV(TABLE(TR(TH('Variable'), TH('Value')), [TR(TD(k,
                       _class='env_table_cell'), TD(v, _class='env_table_cell'
                       )) for (k, v) in sorted(local_env.vars.items())],
                       _class='env_table', _id='env_table'))

            return dict(vars=env_vars)
    View:

        {{extend 'layout.html'}}
        <style>
            .env_table {
                padding: 0px;
                width: 700px;
            }
            .env_table_cell {
                padding: 3px;
                border-left: 0px;
                border-right: 0px;
                border-top: 0px;
                border-bottom: dotted 1px;
            }
        </style>
        {{=vars}}
    """

    def __init__(self, request=None, session=None, auth=None, beauty=None,
            db=None):
        self.request = request
        self.session = session
        self.auth = auth
        self.beauty = beauty
        self.db = db
        self.vars = {}

        os_env = dict(vars=self.beauty(os.environ))
        for k, v in os_env.items():
            key = "os.env.%(k)s" % locals()
            self.vars[key] = v

        sys_path = dict(path=self.beauty(sys.path))
        for k, v in sys_path.items():
            key = "sys.%(k)s" % locals()
            self.vars[key] = v

        session_vars = dict(vars=self.beauty(session))
        for k, v in session_vars.items():
            key = "session.%(k)s" % locals()
            self.vars[key] = v

        auth_vars = dict(vars=self.beauty(self.auth.settings))
        for k, v in auth_vars.items():
            key = "auth.settings.%(k)s" % locals()
            self.vars[key] = v

        request_vars = dict(vars=self.beauty(self.request))
        for k, v in request_vars.items():
            key = "request.%(k)s" % locals()
            self.vars[key] = v

        database_stuff = {
                'uri': self.db._uri,
                'pool_size': self.db._pool_size,
                }

        for var in self.db.executesql('SHOW variables'):
            name = "mysql.%s" % var[0]
            database_stuff[name] = var[1]

        db_stuff = dict(vars=self.beauty(database_stuff))
        for k, v in db_stuff.items():
            key = "mysql.%(k)s" % locals()
            self.vars[key] = v

    def __repr__(self):
        return str(self.__dict__)

def main():

    local_env = LocalEnvironment()
    print local_env

if __name__ == '__main__':
    main()
