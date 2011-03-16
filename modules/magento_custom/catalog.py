#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
    magento.catalog

    Product Catalog API for magento

    :copyright: (c) 2010 by Sharoon Thomas.
    :copyright: (c) 2010 by Openlabs Technologies & Consulting (P) LTD
    :license: AGPLv3, see LICENSE for more details
'''
# E1101: *%s %r has no %r member*
# F0401: *Unable to import %r*
# pylint: disable=E1101,F0401

from magento.api import API


class ProductAttribute(API):
    """
    Product Attribute API
    """
    # W0232: *Class has no __init__ method*
    # pylint: disable=W0232

    def create(self, product_attribute_code, data):
        """
        Create a product attribute.

        :param product_attribute_code
            Eg 'firearm_action',
        :param data, Example:
            data = {
                'is_global': 1,         # 0=Store View, 1=Global, 2=Website
                'frontend_input': 'select', # See list below
                'default_value_text': '',
                'default_value_yesno': 0,
                'default_value_date': '',
                'default_value_textarea': '',
                'is_unique': False,
                'is_required': False,
                'is_configurable': False,
                'is_searchable': False,
                'is_visible_in_advanced_search': False,
                'is_comparable': False,
                'is_filterable': 0,     # 0=No, 1=with results, 2=no results
                'is_filterable_in_search': True,
                'is_used_for_promo_rules': False,
                'position': 99,
                'is_html_allowed_on_front': True,
                'is_visible_on_front': True,
                'used_in_product_listing': True,
                'used_for_sort_by': True,
                'frontend_label': {
                        '0': 'Admin Label',
                        '1': 'Default Store Label',
                    },
                }

            Valid frontend_input values.
                +----------------+
                | frontend_input |
                +----------------+
                |                |
                | boolean        |
                | date           |
                | gallery        |
                | hidden         |
                | image          |
                | media_image    |
                | multiline      |
                | multiselect    |
                | price          |
                | select         |
                | text           |
                | textarea       |
                +----------------+

        :return:  integer, id of the new product attribute
        """
        args = [product_attribute_code, data]
        return int(self.call('epps_product_attribute.create', args))

    def update(self, attribute, data, id_type=None):
        """
        Update a product attribute.
        :param attribute: attribute id or code
        :param data, see create for more attribute property examples.
        :param id_type, string, determines what 'attribute' parameter is,
            one of 'id' or 'code'. If None, the type is guessed: if attribute
            is all digits, then id_type = 'id', else 'code'.
        :return: boolean

        Notes:
            The update method can be used for attribute options CRUD:

            To *create* an option use a 'option_N' value key, where N starts at
            0 and increments for each option.

                custom_prod_attr_api.update(
                    attribute_code,
                    {'option': {
                        'value': {
                            'option_0': {
                                '0': 'Zero Label admin',
                                '1': 'Zero Label store',
                                },
                            'option_1': {
                                '0': 'One Label admin',
                                '1': 'One Label store',
                                },
                            },
                        'order': {
                            'option_0': 1,
                            'option_1': 2,
                            }
                         }
                    },
                    )

            To *update* options, use the option id as the value key. Get the
            option ids using the magento.catalog.ProductAttribute options()
            method.

                custom_prod_attr_api.update(
                    attribute_code,
                    {'option': {
                        'value': {
                            '130': {
                                '0': 'Zero Label Admin',
                                '1': 'Zero Label Store',
                                },
                            '131': {
                                '0': 'One Label Admin',
                                '1': 'One Label Store',
                                },
                            },
                        'order': {
                            '130': 2,
                            '131': 1,
                            }
                         }
                    },
                    )

            To *delete* options, set the delete key to True.

                custom_prod_attr_api.update(
                    attribute_code,
                    {'option': {
                        'value': {
                            '130': {},
                            },
                        'delete': {
                            '130': True,
                            }
                         }
                    },
                    )

            Any number of options can be updated.

            Options can be added and while others are updated with one call.

            To update an option, whether to modify labels, change the order or
            delete it, the 'value' of the option must be indicated.

            Any existing options not keyed in the 'value' dict are not
            affected.

            If the 'order' value is not indicated it is set to 0.

            The 'order' of an option will not be modified if the 'value' is not
            included. To change only the 'order', provide the 'value'
            unchanged.

            The 'order' can be changed on any number of options. No sequencing
            is done. The 'order' values are saved as is, allowing duplicates
            and values out of sequence.

            To add an option to the end of the list of options, set the 'order'
            to a value higher than any existing.

            To delete an option, both the 'value' and 'delete' values of the
            option must be provided but the 'order' value is not necessary. It
            will be ignored if provided.

            An attribute can be created with no options. The options can be
            updated with a second call.
        """
        if not id_type:
            if str(attribute).isdigit():
                id_type = 'id'
            else:
                id_type = 'code'

        args = [attribute, data, id_type]
        return bool(self.call('epps_product_attribute.update', args))

    def delete(self, attribute, id_type=None):
        """
        Delete a product attribute.

        :param attribute: attribute id or code
        :param id_type, string, determines what 'attribute' parameter is,
            one of 'id' or 'code'. If None, the type is guessed: if attribute
            is all digits, then id_type = 'id', else 'code'.
        :return: boolean
        """
        if not id_type:
            if str(attribute).isdigit():
                id_type = 'id'
            else:
                id_type = 'code'

        args = [attribute, id_type]
        return bool(self.call('epps_product_attribute.delete', args))


class ProductAttributeSet(API):
    """
    Product Attribute Set API
    """
    # W0232: *Class has no __init__ method*
    # pylint: disable=W0232

    def insert(self, attribute_set, attribute_group, attribute, position=0):
        """
        Insert an attribute into an attribute list.

        :param attribute_set, attribute set Id or name
        :param attribute_group, attribute group Id or name
        :param attribute, attribute Id or code
        :param position, integer, insert position. If position = 0, attributed
            is added to end of set.
        :return: boolean

        For the attribute_set, attribute_group and attribute, if they are
        numeric the API assumes an id, else assumes name/code.

        """
        args = [attribute_set, attribute_group, attribute, position]
        return bool(self.call('epps_product_attribute_set.insert', args))

    def remove(self, attribute_set, attribute):
        """
        Insert an attribute into an attribute list.

        :param attribute_set, attribute set Id or name
        :param attribute, attribute Id or code
        :return: boolean

        For the attribute_set, attribute_group and attribute, if they are
        numeric the API assumes an id, else assumes name/code.

        """
        args = [attribute_set, attribute]
        return bool(self.call('epps_product_attribute_set.remove', args))
