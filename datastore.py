#
# Copyright 2014 Justin Huff <jjhuff@mspin.net>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import datetime
import struct
import os

from google.appengine.ext import ndb

class Proceeding(ndb.Model):
    pass

class Comment(ndb.Model):
    RandomValue = ndb.IntegerProperty()
    Crawled = ndb.DateTimeProperty(auto_now_add=True)
    Link = ndb.StringProperty(default=None)
    Author = ndb.StringProperty(default=None)
    DocUrl = ndb.StringProperty(default=None)
    DocText = ndb.TextProperty(default=None)
    Received = ndb.StringProperty(default=None)
    Posted = ndb.StringProperty(default=None)
    ReceivedDate = ndb.DateProperty(default=None)
    PostedDate = ndb.DateTimeProperty(default=None)
    AddressLine1 = ndb.StringProperty(default=None)
    AddressLine2 = ndb.StringProperty(default=None)
    AddressCity = ndb.StringProperty(default=None)
    AddressState = ndb.StringProperty(default=None)
    AddressZip = ndb.StringProperty(default=None)

    @staticmethod
    def _random():
        return struct.unpack("!l", os.urandom(4))[0]

    def _pre_put_hook(self):
        self.RandomValue = Comment._random();

    @staticmethod
    def build_key(proceeding, comment_id):
        return ndb.Key("Proceeding", proceeding, "Comment", comment_id)

    @staticmethod
    def getRandom(proceeding):
        ancestor_key = ndb.Key("Proceeding", proceeding)
        for x in range(0,100):
            e = Comment.query(ancestor=ancestor_key).filter(Comment.RandomValue >= Comment._random()).order(Comment.RandomValue).get()
            if e.DocText != None:
                return e
        raise Exception("Can't find a valid comment")


