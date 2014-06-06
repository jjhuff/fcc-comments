#!/usr/bin/env python
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
#
import datetime
import logging

import webapp2
from google.appengine.ext import db

import datastore
import fcc_parse

class ImportComments(webapp2.RequestHandler):
    def get(self):
        zipcode = self.request.GET.get('zip')
        if zipcode:
            query = "address.zip=%s"%zipcode
        else:
            query = ""

        docs = fcc_parse.RunQuery(query)
        logging.info("Received %d docs for query '%s'"%(len(docs), query))
        if len(docs)>=500 and query!="":
            logging.warning("Possible limit reached on '%s'"%query)

        put_count = 0
        for doc in docs:
            k = datastore.Comment.build_key("14-28", doc['id'])
            # Skip existing comments
            if k.get():
                continue
            c = datastore.Comment(key = k)
            c.Link = doc['link']
            c.Author = doc['author']
            c.DocUrl = doc['doc_url']
            c.DocText = doc['doc_text']
            c.ReceivedDate = doc['date_received']
            c.PostedDate = doc['date_posted']
            c.AddressLine1 = doc['address']['line1']
            c.AddressLine2 = doc['address']['line2']
            c.AddressCity = doc['address']['city']
            c.AddressState = doc['address']['state']
            c.AddressZip = doc['address']['zip']
            c.put()
            put_count+=1

        logging.info("Put %d docs"%(put_count))


app = webapp2.WSGIApplication([
        ('/import', ImportComments),
    ],debug=True)

