#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
magento_api.py

Classes related to magento API.


Rationale:

The magento/*.py modules are a copy of the open source modules developed by
Sharoon Thomas. They need to remain unchanged.

The magento_custom/*.py includes modules for custom Igeejo/Epps magento api
calls.

This module attempts to create a single, simple interface that hides which
modules and methods are used.

* Simplify calling interface.
    Example
        api = API(url=URL, api_user=API_USER, api_password=API_PASSWORD)
        print api.category.info(1)
* Hide away API connecting and disconnecting.
* Hide away caching of API client objects.
* Subclass classes found in both magento/*.py and magento_custom/*.py so a
    single class can be used to get all methods.
* Standardize importing. The magento/*.py and magento_custom/*.py require
    the path be added to the sys.path. See below.
"""

import os
import sys

sys.path.append(os.path.join(os.getcwd(), 'applications/shared/modules'))

# F0401: *Unable to import %r*
# pylint: disable=F0401

import magento
import magento_custom


class API(object):
    """Class representing a magento api."""
    def __init__(self, url, api_user, api_password):
        """Constructor.

        Args:
            url: string, magento api url.
            api_user: string, magento api login username.
            api_password: string, magento api login password.

        """
        self.url = url
        self.api_user = api_user
        self.api_password = api_password
        self.api_classes = {}           # Cache of api classes
        self.api = magento.API(self.url, self.api_user, self.api_password,
                protocol='xmlrpc')
        try:
            self.api.__enter__()
        except IOError:
            self.api = None

    def __del__(self):
        if self.api:
            self.api.__exit__(None, None, None)

    def api_for_class(self, api_class):
        """Create an API instance for a specific class.

        This can be used to save creating multiple sessions when several
        classes are needed.

        Example:
            api = API(url=URL, api_user=API_USER, api_password=API_PASSWORD)
            product_api = api.api_for_class(magento.catalog.Product)
            products = product_api.product().list()

        Args:
            api: magento.api.API instance

        Returns:
            magento.api subclass instance.
        """
        name = '{mod}.{name}'.format(mod=api_class.__module__,
                name=api_class.__name__)
        if not name in self.api_classes:
            self.api_classes[name] = api_class(self.api.url, self.api_user,
                    self.api_password)
            self.api_classes[name].session = self.api.session
            self.api_classes[name].client = self.api.client
            self.api_classes[name].protocol = self.api.protocol
        return self.api_classes[name]

    @property
    def category(self):
        """Category class api."""
        return self.api_for_class(magento.catalog.Category)

    @property
    def category_attribute(self):
        """CategoryAttribute class api."""
        return self.api_for_class(magento.catalog.CategoryAttribute)

    @property
    def country(self):
        """Country class api."""
        return self.api_for_class(magento.directory.Country)

    @property
    def customer(self):
        """Customer class api."""
        return self.api_for_class(magento.customer.Customer)

    @property
    def customer_group(self):
        """CustomerGroup class api."""
        return self.api_for_class(magento.customer.CustomerGroup)

    @property
    def customer_address(self):
        """CustomerAddress class api."""
        return self.api_for_class(magento.customer.CustomerAddress)

    @property
    def indexer(self):
        """Indexer class api."""
        return self.api_for_class(magento_custom.index.Indexer)

    @property
    def inventory(self):
        """Inventory class api."""
        return self.api_for_class(magento.catalog.Inventory)

    @property
    def product(self):
        """Product class api."""
        return self.api_for_class(magento.catalog.Product)

    @property
    def product_attribute(self):
        """ProductAttribute class api."""
        return self.api_for_class(ProductAttribute)

    @property
    def product_attribute_set(self):
        """ProductAttributeSet class api."""
        return self.api_for_class(ProductAttributeSet)

    @property
    def product_types(self):
        """ProductTypes class api."""
        return self.api_for_class(magento.catalog.ProductTypes)

    @property
    def product_images(self):
        """ProductImages class api."""
        return self.api_for_class(magento.catalog.ProductImages)

    @property
    def product_tier_price(self):
        """ProductTierPrice class api."""
        return self.api_for_class(magento.catalog.ProductTierPrice)

    @property
    def product_links(self):
        """ProductLinks class api."""
        return self.api_for_class(magento.catalog.ProductLinks)

    @property
    def region(self):
        """Region class api."""
        return self.api_for_class(magento.directory.Region)


# W0232: *Class has no __init__ method*
# pylint: disable=W0232
class ProductAttribute(magento.catalog.ProductAttribute,
        magento_custom.catalog.ProductAttribute):
    """Class inheriting methods from magento.catalog.ProductAttribute and
    magento_custom.catalog.ProductAttribute so all methods can be called with
    one class.
    """


# W0232: *Class has no __init__ method*
# pylint: disable=W0232
class ProductAttributeSet(magento.catalog.ProductAttributeSet,
        magento_custom.catalog.ProductAttributeSet):
    """Class inheriting methods from magento.catalog.ProductAttributeSet and
    magento_custom.catalog.ProductAttributeSet so all methods can be called
    with one class.
    """
