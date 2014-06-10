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
import os

import webapp2


from google.appengine.api import taskqueue
from google.appengine.ext import db
from webapp2_extras import jinja2

from mapreduce import operation as op

import datastore

class BaseHandler(webapp2.RequestHandler):
    @webapp2.cached_property
    def jinja2(self):
        # Returns a Jinja2 renderer cached in the app registry.
        return jinja2.get_jinja2(app=self.app)

    def render_response(self, _template, **context):
        # Renders a template and writes the result to the response.
        rv = self.jinja2.render_template(_template, **context)
        self.response.write(rv)

def permalinkForComment(comment):
    return  webapp2.uri_for("comment", proceeding=comment.key.parent().id(), comment_id=comment.key.id())

class IndexHandler(BaseHandler):
    def get(self, proceeding="14-28", comment_id=None):
        if comment_id:
            self.response.cache_control = 'public'
            self.response.cache_control.max_age = 10*60
            comment = datastore.Comment.getComment(proceeding, comment_id)
            if not comment:
                webapp2.abort(404)
        else:
            comment = datastore.Comment.getRandom(proceeding)

        args = {
            'comment': comment,
            'comment_text': None,
            'comment_link': permalinkForComment(comment)
        }
        if comment.DocText:
            args['comment_text'] =  comment.DocText.replace('\n', '<br>')
        self.render_response("index.html", **args)

def touch(entity):
    yield op.db.Put(entity)

def extract_text(entity):
    taskqueue.add(queue_name="extract", url="/extract_text?proceeding=%s&id=%s"%(entity.key.parent().id(), entity.key.id()), method="GET", target="batch")

app = webapp2.WSGIApplication([
        webapp2.Route(r'/', handler=IndexHandler, name='home'),
        webapp2.Route(r'/comment/<proceeding>/<comment_id>', handler=IndexHandler, name='comment'),
    ],debug=True)

