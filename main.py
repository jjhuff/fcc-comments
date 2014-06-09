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

class Home(BaseHandler):
    def get(self):
        comment = datastore.Comment.getRandom("14-28")
        args = {
            'comment': comment,
            'comment_link': permalinkForComment(comment)
        }
        self.render_response("index.html", **args)

class Comment(BaseHandler):
    def get(self, proceeding, comment_id):
        comment = datastore.Comment.getComment(proceeding, comment_id)
        args = {
            'comment': comment,
            'comment_link': permalinkForComment(comment)
        }
        self.render_response("index.html", **args)

def touch(entity):
    yield op.db.Put(entity)

app = webapp2.WSGIApplication([
        webapp2.Route(r'/', handler=Home, name='home'),
        webapp2.Route(r'/comment/<proceeding>/<comment_id>', handler=Comment, name='comment'),
    ],debug=True)

