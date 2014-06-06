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
from google.appengine.api import taskqueue
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
        if len(docs) == 0:
            logging.warning("Zero results.")
            raise Exception("Zero results")

        if len(docs)>=500 and query!="":
            logging.warning("Possible limit reached on '%s'"%query)

        logging.info("Received %d docs for query '%s'"%(len(docs), query))

        put_count = 0
        for doc in docs:
            k = datastore.Comment.build_key("14-28", doc['id'])
            # Skip existing comments
            c = k.get()
            if c:
                # If it doesn't have text, queue it up!
                if not c.DocText:
                    taskqueue.add(queue_name="extract", url="/extract_text?id=%s"%doc['id'], method="GET", target="batch")
                continue
            c = datastore.Comment(key = k)
            c.Link = doc['link']
            c.Author = doc['author']
            c.DocUrl = doc['doc_url']
            c.ReceivedDate = doc['date_received']
            c.PostedDate = doc['date_posted']
            c.AddressLine1 = doc['address']['line1']
            c.AddressLine2 = doc['address']['line2']
            c.AddressCity = doc['address']['city']
            c.AddressState = doc['address']['state']
            c.AddressZip = doc['address']['zip']
            c.put()
            taskqueue.add(queue_name="extract", url="/extract_text?id=%s"%doc['id'], method="GET", target="batch")
            put_count+=1

        logging.info("Put %d docs"%(put_count))

class ExtractText(webapp2.RequestHandler):
    def get(self):
        preceeding = self.request.GET.get('preceeding', '14-28')
        comment_id = self.request.GET.get('id')
        comment = datastore.Comment.build_key(preceeding, comment_id).get()
        if not comment:
            logging.warning("Missing entity: %s/%s"%(preceeding, comment_id))
            raise Exception("Missing entity")
        comment.DocText = fcc_parse.ExtractText(comment.DocUrl)
        comment.put()

app = webapp2.WSGIApplication([
        ('/import', ImportComments),
        ('/extract_text', ExtractText),
    ],debug=True)

