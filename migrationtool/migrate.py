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
import util

logging.basicConfig(level=logging.INFO, format="[%(asctime)s][%(levelname)s]%(message)s",
                    datefmt="%d-%m-%Y %I:%M:%S %p")

###########################################################
# Migration methods
###########################################################
# Migrates roundcube user specific configurations like
# signature for example
def transfer_identities(db_from, db_to, where, user_id):
    # Search for identities in database
    identities = [i for i in util.select(db_from, "identities", where)]

    for identity in identities:
        # Update user reference
        identity["user_id"] = user_id

        # Keep track of last id for identity
        prev_identity_id = identity["identity_id"]
        del identity["identity_id"]

        # Insert identity in destination db
        identity["identity_id"] = util.insert(db_to, "identities", identity)

    return identities

# Migrates user contacts
def transfer_contacts(db_from, db_to, where, user_id):
    # Search for contacts in database
    contacts = [c for c in util.select(db_from, "contacts", where)]
    for contact in contacts:
        # Update user reference
        contact["user_id"] = user_id

        # Keep track of last id for contact
        prev_contact_id = contact["contact_id"]
        del contact["contact_id"]

        # Insert contact in destination db
        contact["contact_id"] = util.insert(db_to, "contacts", contact)
        contact["prev_contact_id"] = prev_contact_id

    return contacts

# Migrates user collected contacts, i.e. those ones user
# received mails from or sent mails to but didnt add as
# actual contacts
def transfer_collected_contacts(db_from, db_to, where, user_id):
    # Search for collected_contacts in database
    collected_contacts = [cc for cc in util.select(db_from, "collected_contacts", where)]
    for collected_contact in collected_contacts:
        # Update user reference
        collected_contact["user_id"] = user_id

        # Keep track of last id for collected contact
        prev_contact_id = collected_contact["contact_id"]
        del collected_contact["contact_id"]

        # Insert collected contact in destination db
        collected_contact["contact_id"] = util.insert(db_to, "collected_contacts", collected_contact)
        collected_contact["prev_contact_id"] = prev_contact_id

    return collected_contacts

# Migrates user contact groups like "work" and "family"
# for example
def transfer_contactgroups(db_from, db_to, where, user_id):
    # Search for contactgroups in database
    contactgroups = [cg for cg in util.select(db_from, "contactgroups", where)]
    for contactgroup in contactgroups:
        # Update user reference
        contactgroup["user_id"] = user_id

        # Keep track of last id for contact
        prev_contactgroup_id = contactgroup["contactgroup_id"]
        del contactgroup["contactgroup_id"]

        # Insert contactgroup in destination db
        contactgroup["contactgroup_id"] = util.insert(db_to, "contactgroups", contactgroup)
        contactgroup["prev_contactgroup_id"] = prev_contactgroup_id

    return contactgroups

def get_prev_contact_key(contact_id, contacts):
    for contact in contacts:
        if contact["prev_contact_id"] == contact_id:
            return contact["contact_id"]
    raise Exception("prev_contact_id not found")

def populate_contactgroups(db_from, db_to, contacts, contactgroups):
    members = 0

    for contactgroup in contactgroups:
        where = "contactgroup_id={}".format(contactgroup["prev_contactgroup_id"])

        # Get from db members of an old contact group
        contactgroupmembers = [cgm for cgm in util.select(db_from, "contactgroupmembers", where)]

        # Put users from previous contacts groups into new ones
        for contactgroupmember in contactgroupmembers:
            contactgroupmember["contactgroup_id"] = contactgroup["contactgroup_id"]
            try:
                contactgroupmember["contact_id"] = get_prev_contact_key(contactgroupmember["contact_id"], contacts)
            except Exception, exc:
                logging.exception("Error updating contact group membership of %d in %s",
                                  contactgroupmember["contact_id"], contactgroup["contactgroup_id"])
                raise
            else:
                util.insert(db_to, "contactgroupmembers", contactgroupmember)

        members += len(contactgroupmembers)

    return members
