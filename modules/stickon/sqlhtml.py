#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
stickon/sqlhtml.py

Classes extending functionality of gluon/sqlhtml.py.

"""
from gluon.html import INPUT, OPTION, SELECT
from gluon.sqlhtml import FormWidget, OptionsWidget

# C0103: Invalid name
# pylint: disable=C0103


class InputWidget(FormWidget):
    """Custom input widget."""

    def __init__(self, attributes=None, class_extra=''):
        """Constructor.

        Args:
            attributes: dict, dictionary of custom attributes.
            class_extra: string, value appended to _class value.
        """

        # W0221: Arguments number differs from overridden method
        # W0231: __init__ method from base class FormWidget is not called
        # pylint: disable=W0221,W0231

        self.attributes = attributes if attributes else {}
        self.class_extra = class_extra

    def widget(self, field, value, **attributes):
        """Generate INPUT tag for custom widget.

        See gluon.sqlhtml FormWidget
        """
        # W0221: Arguments number differs from overridden method
        # pylint: disable=W0221

        new_attributes = dict(
            _type='text',
            _value=(value != None and str(value)) or '',
            )
        new_attributes.update(self.attributes)
        attr = self._attributes(field, new_attributes, **attributes)
        if self.class_extra:
            attr['_class'] = ' '.join([attr['_class'], self.class_extra])
        return INPUT(**attr)


class SelectWidget(OptionsWidget):
    """Custom select widget."""

    def __init__(self, attributes=None, class_extra=''):
        """Constructor.

        Args:
            attributes: dict, dictionary of custom attributes.
            class_extra: string, value appended to _class value.
        """

        # W0221: Arguments number differs from overridden method
        # W0231: __init__ method from base class FormWidget is not called
        # pylint: disable=W0221,W0231

        self.attributes = attributes if attributes else {}
        self.class_extra = class_extra

    def widget(self, field, value, **attributes):
        """Generate INPUT tag for custom widget.

        See gluon.sqlhtml FormWidget

        Notes:
            Unlike OptionsWidget, this method permits a select to be created
            without options.
        """
        # W0221: Arguments number differs from overridden method
        # pylint: disable=W0221

        options = {}
        requires = field.requires
        if not isinstance(requires, (list, tuple)):
            requires = [requires]
        if requires:
            if hasattr(requires[0], 'options'):
                options = requires[0].options()
        opts = [OPTION(v, _value=k) for (k, v) in options]

        new_attributes = dict(
            value=value,
            )
        new_attributes.update(self.attributes)
        attr = self._attributes(field, new_attributes, **attributes)
        if self.class_extra:
            attr['_class'] = ' '.join([attr['_class'], self.class_extra])

        return SELECT(*opts, **attr)
