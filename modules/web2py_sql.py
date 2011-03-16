#!/usr/bin/python
# -*- coding: utf-8 -*-

"""

Classes for handling web2py sql.

"""

import ConfigParser


class FieldPropertyDefaultsSet(object):

    """Class representing a set of FieldPropertyDefaults objects

    A set of field property defaults are stored in a file in ConfigParse
    format. They define field properties it use. For example, a field property
    default for the type 'datetime' is 'requires=IS_DATETIME()' then all
    datetime fields will get that property. If a field property for the name
    'creation_date' is 'requires=IS_NOT_EMPTY' then all field with thename
    'creation_date' will get that property.

    The 'SKIP' property is special. It indicates the field should be skipped
    when printing the field definitions for the table it belongs to.
    """

    def __init__(self, field_property_defaults=None):
        """Constructor.

        Args:
            field_proprerty_defaults: list, List of FieldPropertyDefaults
                object instances.

        """

        self.field_property_defaults = []
        if field_property_defaults:
            self.field_property_defaults = field_property_defaults
        return

    def load(self, filename):
        """Load field property defaults from a file.

        Args:
            filename: string, name of file to read for defaults.
        """

        config = ConfigParser.RawConfigParser()
        config.read(filename)
        # Order section properties low to high precedence.
        section_properties = [
            {'name': 'by_type', 'class': FieldPropertyDefaultsByType,
             'column': 'column_type'},
            {'name': 'by_name', 'class': FieldPropertyDefaultsByName,
             'column': 'column_name'},
             ]

        for section_property in section_properties:
            # Each section is optional
            try:
                items = config.items(section_property['name'])
            except ConfigParser.NoSectionError:
                pass
            else:
                for (name, value) in items:
                    obj = section_property['class']()
                    setattr(obj, section_property['column'], name)
                    obj.defaults = value.split('\n')
                    self.field_property_defaults.append(obj)
        return


class FieldPropertyDefaults(object):

    """Base class representing property defaults defined for a field."""

    def __init__(self, defaults=None):
        """Constructor.

        Args:
            defaults: list, List of field properties. Eg ['required=IS_NOT_EMPTY()', 'writable=False']

        """

        self.defaults = []
        if defaults:
            self.defaults = defaults

    def defaults_for(self, column=None):
        """Return the defaults that apply for the provided column.

        Args:
            column: object instance, Any object instance that has a 'name'
                property that is a string.

        Returns:
            List, a list of defaults if the field property defaults apply to
                the column, otherwise an empty list.

        Intented to be overridden by
        """

        raise NotImplementedError


class FieldPropertyDefaultsByName(FieldPropertyDefaults):

    """Class representing property defaults defined for a field by the field's
    name.

    """

    def __init__(self, defaults=None, column_name=''):
        """Constructor.

        Args:
            defaults: list, List of field properties. Eg ['required=IS_NOT_EMPTY()', 'writable=False']
            column_name: string, Name of the column the field property defaults pertain to.

        """

        super(FieldPropertyDefaultsByName,
              self).__init__(defaults=defaults)
        self.column_name = column_name

    def defaults_for(self, column=None):
        """Return the defaults that apply for the provided column.

        Args:
            column: object instance, Any object instance that has a 'name'
                property that is a string.

        Returns:
            List, a list of defaults if the field property defaults apply to
                the column, otherwise an empty list.

        Raises:
            AttributeError if provided column object instance doesn't have a
            'name' attribute.

        """

        if not column or not self.column_name:
            return []
        try:
            if column.name == self.column_name:
                return self.defaults
        except AttributeError:
            raise AttributeError, \
                "Provided column object does not have a 'name' attribute."
        return []


class FieldPropertyDefaultsByType(FieldPropertyDefaults):

    """Class representing property defaults defined for a field by the field's
    type.

    """

    def __init__(self, defaults=None, column_type=''):
        """Constructor.

        Args:
            defaults: list, List of field properties. Eg ['required=IS_NOT_EMPTY()', 'writable=False']
            column_type: string, Name of the column data type the field property defaults pertain to.

        """

        super(FieldPropertyDefaultsByType,
              self).__init__(defaults=defaults)
        self.column_type = column_type

    def defaults_for(self, column=None):
        """Return the defaults that apply for the provided column.

        Args:
            column: object instance, Any object instance that has a 'type'
                property that is a string.

        Returns:
            List, a list of defaults if the field property defaults apply to
                the column, otherwise an empty list.

        Raises:
            AttributeError if provided column object instance doesn't have a
            'type' attribute.
        """

        if not column or not self.column_type:
            return []
        try:
            if column.data_type == self.column_type:
                return self.defaults
        except AttributeError:
            raise AttributeError, \
                "Provided column object does not have a 'type' attribute."
        return []


