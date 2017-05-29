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

import argparse
import logging
import MySQLdb
from .context import migrate
from .context import util

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("db1host", help="source database host")
    parser.add_argument("--db1port", help="source database port (default=3306)", metavar="PORT",
                        default="3306", type=int)
    parser.add_argument("db1user", help="source database username")
    parser.add_argument("db1passwd", help="source database password")
    parser.add_argument("--db1name", help="source database name (default=\"roundcubemail\")", metavar="DB",
                        default="roundcubemail")
    parser.add_argument("db2host", help="destination database host")
    parser.add_argument("--db2port", help="destination database port (default=3306)", metavar="PORT",
                        default="3306", type=int)
    parser.add_argument("db2user", help="destination database username")
    parser.add_argument("db2passwd", help="destination database password")
    parser.add_argument("--db2name", help="destination database name (default=\"roundcubemail\")",
                        metavar="DB", default="roundcubemail")
    parser.add_argument("--domain",
                        help="Performs a full migration of users from a specified domain, i.e. example.com")
    parser.add_argument("--skip-contacts",
                        help="Skips users contacts, contactgroups and collected contacts (default=False)",
                        action='store_true')
    args = parser.parse_args()

    # establish connection with host_from
    try:
        db_from = MySQLdb.connect(host=args.db1host, port=args.db1port, user=args.db1user, passwd=args.db1passwd,
                                  db=args.db1name)
        logging.info("Successfully connected to %s:%d", args.db1host, args.db1port)
    except Exception, exc:
        logging.exception(exc)
        exit(2)

    # establish connection with host_to
    try:
        db_to = MySQLdb.connect(host=args.db2host, port=args.db2port, user=args.db2user, passwd=args.db2passwd,
                                db=args.db2name)
        logging.info("Successfully connected to %s:%d", args.db2host, args.db2port)
    except Exception, exc:
        logging.exception(exc)
        exit(2)

    # start migration from host_from to host_to
    try:
        if args.domain:
            logging.info("Starting migration for domain %s", args.domain)

        for user in util.select(db_from, "users",
                                where="""username like '%%@%s'""" % args.domain if args.domain else None):

            logging.info("[USERNAME: %s] starting migration", user["username"])
            where = "user_id={}".format(user["user_id"])

            # Update mail host reference for the new host
            user["mail_host"] = args.db2host

            if len(user["mail_host"]) == 0:
                raise Exception("Did you fill user['mail_host']?")

            # remove old user_id and insert him in new db
            del user["user_id"]
            user["user_id"] = util.insert(db_to, "users", user)
            if user["user_id"] != None:
                identities = migrate.transfer_identities(db_from, db_to, where, user["user_id"])
                logging.info("[USERNAME: %s] %d identities moved", user["username"], len(identities))

                if not args.skip_contacts:
                    contacts = migrate.transfer_contacts(db_from, db_to, where, user["user_id"])
                    logging.info("[USERNAME: %s] %d contacts moved", user["username"], len(contacts))

                    collected_contacts = migrate.transfer_collected_contacts(db_from, db_to, where,
                                                                             user["user_id"])
                    logging.info("[USERNAME: %s] %d collected contacts moved", user["username"],
                                 len(collected_contacts))

                    contactgroups = migrate.transfer_contactgroups(db_from, db_to, where, user["user_id"])
                    logging.info("[USERNAME: %s] %d contact groups moved", user["username"], len(contactgroups))

                    try:
                        count_contactgroupmembers = migrate.populate_contactgroups(db_from, db_to,
                                                                                   contacts,
                                                                                   contactgroups)
                        logging.info("[USERNAME: %s] %d contactgroup members trasfered from %d contact groups",
                                     user["username"], count_contactgroupmembers, len(contactgroups))
                    except Exception, exc:
                        raise

                logging.info("[USERNAME: %s] OK!", user["username"])
    except Exception, exc:
        print exc
        db_to.rollback()

    # if everything goes well, commit
    else:
        db_to.commit()
    finally:
        db_to.close()
        db_from.close()
