#!/usr/bin/env python
# coding=utf-8

"""
migrationtool: easy migrate roundcube users and configurations

Copyright (c) 2017 João Paulo Bastos <joaopaulosr95@gmail.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License v3 as published by
the Free Software Foundation.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import logging
import MySQLdb

###########################################################
# Database utilities
###########################################################
# Takes a table and returns a query with (or without)
# a where clause
def select(db, table, where=None):
    db_cursor = db.cursor(MySQLdb.cursors.DictCursor)
    query = """SELECT * FROM %s""" % (table)
    if where:
        query += " WHERE %s" % where

    try:
        db_cursor.execute(query)
        for x in db_cursor.fetchall():
            yield x
    except Exception, exc:
        logging.error(exc)
        raise
    finally:
        db_cursor.close()

# Takes a table and a bunch of data to insert on it and
# returns the id of last row inserted
def insert(db, table, toInsert):
    db_cursor = db.cursor(MySQLdb.cursors.DictCursor)

    # Prepare the query taking column names and values to insert
    query = "INSERT into %s (%s) values (%s)" % (table, ",".join(["`%s`" % k for k in toInsert.keys()]),
                                                 ",".join(["%s" for v in toInsert.values()]))

    try:
        db_cursor.executemany(query, [toInsert.values()])
    except Exception, exc:
        logging.error(exc)
        db.rollback()
        raise
    finally:
        last_id = db_cursor.lastrowid
        db_cursor.close()

        # Return id of last row inserted
        return last_id
