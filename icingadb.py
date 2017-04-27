#!/usr/bin/env python
"""
get stuff from IDO DB
"""

import sys
import mysql.connector


class IcingaDb(object):
    def __init__(self):
        self.db = mysql.connector.connect(host='127.0.0.1', user='root', password='icingar0xx', database='icinga')
        self.db.autocommit = True # very important to avoid caching
        try:
            self.c = self.db.cursor()
        except Exception as e:
            print e
            sys.exit(1)

    def dbQuery(self,q):
        try:
            self.c.execute(q)
        except Exception as e:
            print e
            sys.exit(1)
        result = self.c.fetchall()
        return result


    def selectAllIcingaObjects(self):
        return self.dbQuery('SELECT * FROM icinga_objects')

    def queryName1Pattern(self, pattern):
        q = 'SELECT * FROM icinga_objects WHERE name1 LIKE \'%s\'' % pattern	
        return self.dbQuery(q)	

    def queryName1PatternIsActive(self, pattern, is_active):
        q = 'SELECT * FROM icinga_objects WHERE name1 LIKE \'%s\' AND is_active=\'%i\'' % (pattern, is_active)	
        return self.dbQuery(q)	

    def	__exit__(self):
        self.db.close()
