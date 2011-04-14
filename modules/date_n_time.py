#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
date_n_time.py

Classes and functions related to dates and times.

"""

import datetime


def str_to_date(date_as_str):
    """Convert a string yyyy-mm-dd to a datetime.date() instance"""
    try:
        return datetime.datetime.strptime(date_as_str, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None
