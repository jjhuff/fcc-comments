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

class StartPage(webapp2.RequestHandler):
    def get(self):
        self.response.out.write("OK\n")


app = webapp2.WSGIApplication([
        ('/start', StartPage),
    ],debug=True)

