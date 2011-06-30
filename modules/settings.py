#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
settings.py

Classes related to settings.

"""
from applications.shared.modules.database import DbObject

# E0602: *Undefined variable %r*
# pylint: disable=E0602


class Setting(DbObject):
    """Class representing a setting record."""
    def __init__(self, tbl_, **kwargs):
        """Constructor."""
        DbObject.__init__(self, tbl_, **kwargs)

    def formatted_value(self):
        """Return the setting value formatted."""
        if self.type == 'boolean':
            value = True if self.value == 'True' else False
        else:
            value = self.value
        return value

    @classmethod
    def get(cls, dbset, name):
        """Convenience method for accessing a setting value by name.

        value = Setting.get(name)

        Args:
            dbset, gluon.dal.DAL instance
            name, string, setting name whose value is returned

        Returns:
            string, value of setting.

        Raises:
            ValueError, if setting name is not found.

        """
        query = (dbset.setting.name == name)
        setting = cls(dbset.setting).set_.get(query=query).first()
        if not setting:
            raise ValueError(
                    'Cannot access setting "{name}": No such setting.'.format(
                        name=name))
        return setting.formatted_value()

    @classmethod
    def match(cls, dbset, wildcard, as_dict=False):
        """Get all settings matching provided wildcard.

        Args:
            dbset, gluon.dal.DAL instance
            wildcard, string, eg '%_abc_%', settings with matching names are
                returned.
            as_dict, if True, return a dictionary of name/value pairs.

        Returns:
            list, list of Setting instances
            dict, if as_dict=True, dictionary of name/value pairs
        """
        query = (dbset.setting.name.like(wildcard))
        settings = cls(dbset.setting).set_.get(query=query)
        if as_dict:
            settings_dict = {}
            for setting in settings:
                settings_dict[setting.name] = setting.formatted_value()
            return settings_dict
        else:
            return settings
