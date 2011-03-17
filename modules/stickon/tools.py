#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
stickon/tools.py

Classes extending functionality of gluon/tools.py.

"""
from applications.shared.modules.mysql import LocalMySQL
from gluon.storage import Settings
from gluon.tools import Auth, Crud, Mail, Service
import os
import ConfigParser

# C0103: *Invalid name "%s" (should match %s)*
# Some variable names are adapted from web2py.
# pylint: disable=C0103


class ModelDb(object):

    """Class representing the db.py model"""

    def __init__(self, environment):
        self.environment = environment
        self.DAL = self.environment['DAL']

        self.local_settings = Settings()
        self.settings_loader = self._settings_loader()

        # The order of these is intentional. Some depend on each other.

        self.db = self._db()
        self.mail = self._mail()
        self.auth = self._auth()
        self.crud = self._crud()
        self.service = self._service()
        return

    def _auth(self):
        """Create a auth instance

        """

        auth = Auth(self.environment, self.db)  # authentication/authorization
        auth.settings.hmac_key = self.local_settings.hmac_key
        auth.define_tables(fake_migrate=True)  # creates all needed tables
        self.settings_loader.import_settings(group='auth',
                storage=auth.settings)
        auth.settings.mailer = self.mail
        auth.settings.verify_email_onaccept = self.verify_email_onaccept
        host = 'www.igeejo.com'
        request = self.environment['request']
        if 'wsgi' in request.keys():
            if 'environ' in request['wsgi'].keys():
                host = request['wsgi']['environ']['HTTP_HOST']

        auth.messages.verify_email = 'Click on the link http://' + host \
            + '/' + request.application \
            + '/default/user/verify_email/%(key)s to verify your email'
        # registration_requires_approval is False by default but for some
        # reason it doesn't stick. See if explicitly setting it works.
        auth.settings.registration_requires_approval = False
        return auth

    def _crud(self):
        """Create a Crud instance
        """

        # for CRUD helpers using auth

        crud = Crud(self.environment, self.db)
        crud.settings.auth = self.auth  # enforces authorization on crud
        return crud

    def _db(self):
        """Create a database handle

        """

        request = self.environment['request']
        response = self.environment['response']
        session = self.environment['session']
        if request.env.web2py_runtime_gae:

            # if running on Google App Engine connect to Google BigTable and
            # store sessions and tickets there.

            db = self.DAL('gae')
            session.connect(request, response, db=db)
        else:

            # or use the following lines to store sessions in Memcache
            #   from gluon.contrib.memdb import MEMDB
            #   from google.appengine.api.memcache import Client
            #   session.connect(request, response, db=MEMDB(Client())

            # else use a normal relational database

            local_mysql = LocalMySQL(request=request,
                    database=self.local_settings.database,
                    user=self.local_settings.mysql_user,
                    password=self.local_settings.mysql_password)
            db = self.DAL(local_mysql.sqldb, check_reserved=['mysql'])
        return db

    def _mail(self):
        """Create a mailer object instance

        """

        mail = Mail()  # mailer
        self.settings_loader.import_settings(group='mail',
                storage=mail.settings)
        return mail

    def _service(self):
        """Create a service object instance

        Service object is used for json, xml, jsonrpc, xmlrpc, amfrpc.
        """

        service = Service(self.environment)
        return service

    def _settings_loader(self):
        """Create a settings loader object instance

        """

        request = self.environment['request']
        etc_conf_file = os.path.join(request.folder, 'private', 'etc',
                '%s.conf' % os.environ.get('WEB2PY_SERVER_MODE', 'live'
                ))
        settings_loader = SettingsLoader(config_file=etc_conf_file,
                application=request.application)
        settings_loader.import_settings(group='local',
                storage=self.local_settings)
        return settings_loader

    def verify_email_onaccept(self, user):
        """
        This is run after the registration email is verified. The
        auth.setting.verify_email_onaccept in model/db.py points here.
        """

        # Create an admin group if not already done.

        admin = 'admin'
        if not self.auth.id_group(admin):
            self.auth.add_group(admin,
                                description='Administration group')

        # Add user to admin group if email matches admin_email.

        if user.email == self.auth.settings.admin_email:
            if not self.auth.has_membership(self.auth.id_group(admin),
                    user.id):
                self.auth.add_membership(self.auth.id_group(admin),
                        user.id)


class SettingsLoader(object):

    """Class representing a settings loader.

    Object instances permit loading settings from a config file and importing
    them into web2py storage objects.
    """

    def __init__(self, config_file=None, application=''):
        """Constructor.

        Args:
            config_file: string, name of file containing configuration settings
            application: string, name of web2py application

        """

        self.config_file = config_file
        self.application = application

        # settings = {'grp1': {set1:val1, set2:val2}, 'grp2': {...}

        self.settings = {}
        self.get_settings()
        return

    def __repr__(self):
        return str(self.__dict__)

    def get_settings(self):
        """Read settings from config file."""

        if not self.config_file:
            return
        config = ConfigParser.RawConfigParser()
        config.read(self.config_file)
        settings = {}

        # The web2py section is required, if not found an exception is raised.

        for (name, value) in config.items('web2py'):
            settings[name] = value
        if self.application:

            # The application section is optional, if not found the web2py
            # values are used.

            try:
                for (name, value) in config.items(self.application):
                    settings[name] = value
            except ConfigParser.NoSectionError:
                pass
        for key in settings.keys():
            parts = key.split('.', 1)
            if len(parts) == 1:
                parts.insert(0, 'local')
            (group, setting) = parts[0:2]
            if not group in self.settings:
                self.settings[group] = {}
            self.settings[group][setting] = settings[key]
        return

    def import_settings(self, group, storage):
        """Import a group of settings into a storage.

        Args:
            group: string, The name of the group of settings to import,
                eg 'auth'
            storage: gluon.storage Storage object instance.

        """

        if group == 'auth':
            storage.lock_keys = False  # Required to permit custom settings
        if not group in self.settings:

            # nothing to import

            return
        for setting in self.settings[group].keys():
            storage[setting] = self.settings[group][setting]
        return
