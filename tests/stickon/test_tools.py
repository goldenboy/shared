#!/usr/bin/python
# -*- coding: utf-8 -*-

"""

Test suite for shared/modules/stickon/tools.py

"""

from applications.shared.modules.test_runner import LocalTestSuite, \
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

        #
        # Test with default config file.
        #
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
        # has log_event attr
        self.assertTrue(hasattr(model_db.crud, 'log_event'))

        self.assertTrue(model_db.service)  # sets service property
        # service has xmlrpc
        self.assertTrue(hasattr(model_db.service, 'xmlrpc'))

        #
        # Test with custom config file.
        #
        config_text = """
[web2py]
mail.server = smtp.mymailserver.com:587
mail.sender = myusername@example.com
mail.login = myusername:fakepassword
auth.registration_requires_verification = True
auth.registration_requires_approval = False
auth.admin_email = myadmin@example.com

[shared]
auth.registration_requires_verification = False
auth.registration_requires_approval = True
database = shared
hmac_key = 226bca51c2121b
magento_api_username = api_user
magento_api_password = fake_api_password
mysql_user = shared
mysql_password = {mysql_pw}
version = '0.1'
""".format(mysql_pw=model_db.local_settings.mysql_password)

        f_text = '/tmp/TestModelDb_test__init__.txt'
        _config_file_from_text(f_text, config_text)

        model_db = ModelDb(app_env, config_file=f_text)
        self.assertTrue(model_db)

        self.assertEqual(model_db.mail.settings.server,
                'smtp.mymailserver.com:587')
        self.assertEqual(model_db.mail.settings.sender,
                'myusername@example.com')
        self.assertEqual(
                model_db.auth.settings.registration_requires_verification,
                False)
        self.assertEqual(model_db.auth.settings.registration_requires_approval,
                True)

        os.unlink(f_text)
        return


class TestSettingsLoader(unittest.TestCase):

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
version = '1.11'
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
version = '1.11'
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
version = '1.11'

[app]
version = '2.22'
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
auth.version = '3.33'
mail.username = mailer
mail.version = '4.44'
username = jimk
version = '1.11'

[app]
auth.version = '5.55'
mail.version = '6.66'
version = '2.22'
email = abc@gmail.com
""",
                },
            ]

        f_text = '/tmp/settings_loader_config.txt'
        for t in tests:
            settings_loader = SettingsLoader()
            _config_file_from_text(f_text, t['text'])
            settings_loader.config_file = f_text
            settings_loader.application = 'app'
            if t['raise']:
                self.assertRaises(t['raise'],
                                  settings_loader.get_settings)
            else:
                settings_loader.get_settings()
            self.assertEqual(settings_loader.settings, t['expect'])

        # Test datatype handling.
        text = \
            """
[web2py]
s01_true = True
s02_false = False
s03_int = 123
s04_float = 123.45
s05_str1 = my setting
s06_str2 = 'my setting'
s07_str_true = 'True'
s08_str_int = '123'
s09_str_float = '123.45'

[app]
"""
        settings_loader = SettingsLoader()
        _config_file_from_text(f_text, text)
        settings_loader.config_file = f_text
        settings_loader.application = 'app'
        settings_loader.get_settings()

        self.assertEqual(sorted(settings_loader.settings['local'].keys()),
            [
                's01_true',
                's02_false',
                's03_int',
                's04_float',
                's05_str1',
                's06_str2',
                's07_str_true',
                's08_str_int',
                's09_str_float',
            ])

        slocal = settings_loader.settings['local']
        self.assertEqual(slocal['s01_true'], True)
        self.assertEqual(slocal['s02_false'], False)
        self.assertEqual(slocal['s03_int'], 123)
        self.assertEqual(slocal['s04_float'], 123.45)
        self.assertEqual(slocal['s05_str1'], 'my setting')
        self.assertEqual(slocal['s06_str2'], "'my setting'")
        self.assertEqual(slocal['s07_str_true'], 'True')
        self.assertEqual(slocal['s08_str_int'], '123')
        self.assertEqual(slocal['s09_str_float'], '123.45')

        os.unlink(f_text)

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

        # Test defaults and section overrides
        text = \
            """
[web2py]
auth.username = admin
auth.version = '3.33'
mail.username = mailer
mail.version = '4.44'
username = jimk
version = '1.11'

[app]
auth.version = '5.55'
mail.version = '6.66'
version = '2.22'
email = abc@gmail.com
"""
        _config_file_from_text(f_text, text)
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


def _config_file_from_text(filename, text):

    # R0201: *Method could be a function*
    # pylint: disable=R0201

    f = open(filename, 'w')
    f.write(text)
    f.close()
    return


def main():
    suite = LocalTestSuite()
    suite.add_tests(ModuleTestSuite(module=sys.modules[__name__]))
    suite.run_tests()


if __name__ == '__main__':
    main()
