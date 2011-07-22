#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
stickon/validators.py

Classes extending functionality of gluon/validators.py.

"""
from gluon.validators import IS_DECIMAL_IN_RANGE, is_empty

# C0103: Invalid name
# pylint: disable=C0103


class IS_CURRENCY(IS_DECIMAL_IN_RANGE):
    """Class representing a currency validator."""
    def __init__(self, *a, **b):
        IS_DECIMAL_IN_RANGE.__init__(self, *a, **b)
        if not 'error_message' in b:
            self.error_message = self.error_message.replace(' a number ',
                    ' a dollar amount ')

    def __call__(self, value):
        return IS_DECIMAL_IN_RANGE.__call__(self, value)

    def formatter(self, value):
        try:
            return '{val:.2f}'.format(val=float(value))
        except (ValueError, TypeError):
            return value or ''


class IS_NOT_ALL_EMPTY(object):
    """Class representing a validator requiring at least one non-empty field in
    a set.
    """

    def __init__(self, others,
            error_message='Enter a value in at least one field'):
        self.others = others
        self.error_message = error_message

    def __call__(self, value):
        okay = (value, None)
        error = (value, self.error_message)
        # Return okay either the 'value', or one of self.others is not empty.
        values = []
        values.append(value)
        values.extend(self.others)
        empties = []
        for v in values:
            unused_v, empty = is_empty(v)
            empties.append(empty)
        # Example empties == [True, True, False]
        # If one False exists, it's valid
        if reduce(lambda x, y: x and y, empties):
            return error
        return okay


class NOT_EMPTY_IF_OTHER(object):
    """Validator class for "Other" text input.

    If 'Other' is selected from a drop down menu, then the text input must
    include a description value.
    """
    def __init__(self, dropdown_value, error_message='enter a value'):
        self.dropdown_value = dropdown_value
        self.error_message = error_message

    def __call__(self, value):
        if self.dropdown_value == 'Other' and not value:
            return (value, self.error_message)
        else:
            return (value, None)


class NOT_EMPTY_IF_OTHER_BY_ID(object):
    """Validator class for "Other" text input.

    Like NOT_EMPTY_IF_OTHER but used when OPTION tag values are ids not names.

    If 'Other' is selected from a drop down menu, then the text input must
    include a description value.
    """
    def __init__(self, field, selected_id, error_message='enter a value'):
        """Constructor

        Args:
            field: gluon.dal.Field, eg db.table.field, the field that contains
                the value of the selected option
            selected_id: integer, id of the option selected in the drop menu.
            error_message: string
        """
        self.field = field
        self.selected_id = selected_id
        self.error_message = error_message

    def __call__(self, value):
        db = self.field.table._db
        id_field = self.field.table.id

        # Example: self.field = db.type.name
        # selected_value = db(db.type.id == request.vars.type_id).select(
        #       db.type.name)[0].name
        try:
            selected_value = self.field.table._db(
                    self.field.table.id == self.selected_id).select(
                            self.field)[0][self.field.name]
        except IndexError:
            selected_value = ''

        if selected_value == 'Other' and not value:
            return (value, self.error_message)
        else:
            return (value, None)
