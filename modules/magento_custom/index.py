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


class Indexer(API):
    """
    Indexer API
    """
    # W0232: *Class has no __init__ method*
    # pylint: disable=W0232

    def reindex(self, index_codes=None, force=False):
        """
        Reindex an indexer.

        :param index_codes, array of strings
        :param force, if False, the indexer for the code is reindexed only if
            it's status is 'require_reindex'. if True indexer is reindexed
            regardless.
        :return: list of dicts, Eg  [{'code1': 'status1'}, ...]

        If no index_codes are provided, all indexes are checked for reindexing.
        """
        if not index_codes:
            index_codes = []
        return self.call('epps_indexer.reindex', [index_codes, force])

    def status(self, index_codes=None):
        """
        Return the status of indexers.

        :param index_codes, array of strings
        :return: list of dicts, Eg  [{'code1': 'status1'}, ...]

        If no index_codes are provided, the status of all indexes is returned.

        List of codes:
            mysql> select indexer_code from index_process;
            +---------------------------+
            | indexer_code              |
            +---------------------------+
            | cataloginventory_stock    |
            | catalogsearch_fulltext    |
            | catalog_category_flat     |
            | catalog_category_product  |
            | catalog_product_attribute |
            | catalog_product_flat      |
            | catalog_product_price     |
            | catalog_url               |
            | tag_summary               |
            +---------------------------+

        """
        if not index_codes:
            index_codes = []
        return self.call('epps_indexer.status', [index_codes])
