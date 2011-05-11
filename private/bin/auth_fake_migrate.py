#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
auth_fake_migrate.py

Run this script to create auth tables with fake_migrate=True

Typical usage:

    # Delete all sessions regardless of expiry and exit.
    python web2py.py -S app -M -R path/to/auth_fake_migrate.py
"""
VERSION = 0.1
auth.define_tables(fake_migrate=True)
