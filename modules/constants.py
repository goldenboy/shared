#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
constants.py

Useful constants.

"""

# Time
SECONDS_PER_MINUTE = 60
MINUTES_PER_HOUR = 60
HOURS_PER_DAY = 24
MINUTES_PER_DAY = MINUTES_PER_HOUR * HOURS_PER_DAY
SECONDS_PER_HOUR = SECONDS_PER_MINUTE * MINUTES_PER_HOUR
SECONDS_PER_DAY = SECONDS_PER_HOUR * HOURS_PER_DAY

# Length
MM_PER_CM = 10
CM_PER_M = 100
MM_PER_M = MM_PER_CM * CM_PER_M
MM_PER_INCH = 25.4
CM_PER_INCH = MM_PER_INCH / MM_PER_CM
M_PER_INCH = MM_PER_INCH / MM_PER_M
