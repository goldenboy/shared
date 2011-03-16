#!/usr/bin/python
# -*- coding: utf-8 -*-

"""

Test suite for shared/modules/stickon/tools.py

"""

from applications.shared.modules.local.test_runner import LocalTestSuite, \
    ModuleTestSuite
from applications.shared.modules.stickon.tools import ModelDb, SettingsLoader
from gluon.shell import env
from gluon.storage import Storage
from ConfigParser import NoSectionError
import os
import re
import sys
import unittest

# R0904: Too many public methods
# pylint: disable=C0111,R0904

APPLICATION = __file__.split('/')[-4]


class TestModelDb(unittest.TestCase):

    def test____init__(self):
        # W0212: *Access to a protected member %s of a client class*
        # pylint: disable=W0212

        app_env = env(APPLICATION, import_models=False)
        model_db = ModelDb(app_env)
        self.assertTrue(model_db)  # returns object

        self.assertTrue(model_db.db)  # sets db property
        self.assertEqual(model_db.db._dbname, 'mysql')  # db is mysql db
        self.assertEqual(model_db.db._dbname, 'mysql')  # db is mysql db
        m = \
            re.compile(r"""
                    ^(?P<user>[^:@]+)(\:(?P<passwd>[^@]*))?
                    @(?P<host>[^\:/]+)
                    (\:(?P<port>[0-9]+))?
                    /
                    (?P<db>[^?]+)
                    (\?set_encoding=(?P<charset>\w+))?
                    $""", re.VERBOSE).match(model_db.db._uri[8:])
        # db has correct application
        self.assertTrue(m and m.group('db') == APPLICATION)

        self.assertTrue(model_db.mail)  # sets mail property
        # sender is an email
        email_re = re.compile(r'[a-zA-Z0-9]+@gmail.com')
        self.assertTrue(email_re.match(model_db.mail.settings.sender))

        self.assertTrue(model_db.auth)  # sets auth property
        # admin_email is an email
        self.assertTrue(email_re.match(model_db.auth.settings.admin_email))
        # mailer setting correct
        self.assertEqual(model_db.auth.settings.mailer, model_db.mail)

        self.assertTrue(model_db.crud)  # sets crud property
        # auth setting correct
        self.assertEqual(model_db.crud.settings.auth, model_db.auth)
        # has log_event attr
        self.assertTrue(hasattr(model_db.crud, 'log_event'))

        self.assertTrue(model_db.service)  # sets service property
        # service has xmlrpc
        self.assertTrue(hasattr(model_db.service, 'xmlrpc'))
        return


class TestSettingsLoader(unittest.TestCase):

    def _config_file_from_text(self, filename, text):

        # R0201: *Method could be a function*
        # pylint: disable=R0201

        f = open(filename, 'w')
        f.write(text)
        f.close()
        return

    def test____init__(self):
        settings_loader = SettingsLoader()
        self.assertTrue(settings_loader)  # Creates object
        # No config file, no settings
        self.assertEqual(settings_loader.settings, {})
        return

    def test__get_settings(self):
        settings_loader = SettingsLoader()
        settings_loader.get_settings()
        # No config file, no settings
        self.assertEqual(settings_loader.settings, {})

        tests = [
            {
                'label': 'empty file',
                'expect': {},
                'raise': NoSectionError,
                'text': '',
                },
            {
                'label': 'no web2py section',
                'expect': {},
                'raise': NoSectionError,
                'text': """
[fake_section]
setting = value
""",
                },
            {
                'label': 'web2py section empty',
                'expect': {},
                'raise': None,
                'text': """
[web2py]
""",
                },
            {
                'label': 'web2py one local setting',
                'expect': {'local': {'version': '1.11'}},
                'raise': None,
                'text': """
[web2py]
version = 1.11
""",
                },
            {
                'label': 'web2py two local setting',
                'expect': {'local':
                    {'username': 'jimk', 'version': '1.11'}},
                'raise': None,
                'text': """
[web2py]
username = jimk
version = 1.11
""",
                },
            {
                'label': 'app section',
                'expect': {'local': {'email': 'abc@gmail.com',
                           'username': 'jimk', 'version': '2.22'}},
                'raise': None,
                'text': """
[web2py]
username = jimk
version = 1.11

[app]
version = 2.22
email = abc@gmail.com
""",
                },
            {
                'label': 'app section auth/mail',
                'expect': {
                    'auth': {'username': 'admin', 'version': '5.55'},
                    'mail': {'username': 'mailer', 'version': '6.66'},
                    'local': {'email': 'abc@gmail.com', 'username': 'jimk',
                           'version': '2.22'}},
                'raise': None,
                'text': """
[web2py]
auth.username = admin
auth.version = 3.33
mail.username = mailer
mail.version = 4.44
username = jimk
version = 1.11

[app]
auth.version = 5.55
mail.version = 6.66
version = 2.22
email = abc@gmail.com
""",
                },
            ]

        f_text = '/tmp/settings_loader_config.txt'
        for t in tests:
            settings_loader = SettingsLoader()
            self._config_file_from_text(f_text, t['text'])
            settings_loader.config_file = f_text
            settings_loader.application = 'app'
            if t['raise']:
                self.assertRaises(t['raise'],
                                  settings_loader.get_settings)
            else:
                settings_loader.get_settings()
            self.assertEqual(settings_loader.settings, t['expect'])

        # Test booleans
        tests = [{'label': 'boolean true', 'expect': True,
            'text': """
[web2py]
auth.boolean_setting = 1
"""
        },
        {'label': 'boolean false', 'expect': False,
        'text': """
[web2py]
auth.boolean_setting =
"""}]

        f_text = '/tmp/settings_loader_config.txt'
        for t in tests:
            settings_loader = SettingsLoader()
            self._config_file_from_text(f_text, t['text'])
            settings_loader.config_file = f_text
            settings_loader.application = 'app'
            settings_loader.get_settings()
            if settings_loader.settings['auth']['boolean_setting']:
                self.assertTrue(t['expect'])
            else:
                self.assertFalse(t['expect'])
        os.unlink(f_text)
        return

    def test__import_settings(self):
        settings_loader = SettingsLoader()
        application = 'app'
        group = 'local'
        storage = Storage()
        self.assertEqual(storage.keys(), [])  # Initialized storage is empty
        settings_loader.import_settings(group, storage)
        # No config file, storage unchanged
        self.assertEqual(storage.keys(), [])

        f_text = '/tmp/settings_loader_config.txt'
        text = \
            """
[web2py]
auth.username = admin
auth.version = 3.33
mail.username = mailer
mail.version = 4.44
username = jimk
version = 1.11

[app]
auth.version = 5.55
mail.version = 6.66
version = 2.22
email = abc@gmail.com
"""
        self._config_file_from_text(f_text, text)
        settings_loader.config_file = f_text
        settings_loader.application = application

        settings_loader.get_settings()
        settings_loader.import_settings('zzz', storage)
        # Group has no settings, storage unchanged
        self.assertEqual(storage.keys(), [])
        settings_loader.import_settings(group, storage)
        self.assertEqual(sorted(storage.keys()), ['email', 'username',
                         'version'])

        # Group has settings, storage changed

        self.assertEqual(storage['email'], 'abc@gmail.com')
        self.assertEqual(storage['username'], 'jimk')
        self.assertEqual(storage['version'], '2.22')

        os.unlink(f_text)
        return


def main():
    suite = LocalTestSuite()
    suite.add_tests(ModuleTestSuite(module=sys.modules[__name__]))
    suite.run_tests()


if __name__ == '__main__':
    main()
