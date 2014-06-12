#!/usr/bin/python

import feedparser
import re
import logging
import urllib
import cStringIO as StringIO
from datetime import datetime
from time import mktime
import PyPDF2

try:
    from google.appengine.api import urlfetch
    def fetch(url):
        return urlfetch.fetch(url, deadline=2*60).content
except:
    def fetch(url):
        return urllib.urlopen(url).read()

BASE_URL = "http://apps.fcc.gov/ecfs/comment_search/rss?"

ID_REGEX = re.compile(r"http://apps\.fcc\.gov/ecfs/comment/view\?id=(\d+)")
DOC_REGEX = re.compile(r"http://apps\.fcc\.gov/ecfs/document/view\?id=\d+")
DATE_RECEIVED_REGEX = re.compile(r"Date Received:\s*([^\s]*) <br />")
HEADER_REGEX = re.compile(r"\d+\.txt")
PAGE_REGEX = re.compile(r"\n*Page (\d+)")
ADDRESS_REGEX = re.compile(r"(?:(.*) <br />)?\n(.*) <br />\n(.*), (..) ([^\s]+) <br />$")


def extractTextFromPage(page):
    text = ""
    content = page["/Contents"].getObject()
    if not isinstance(content, PyPDF2.pdf.ContentStream):
        content = PyPDF2.pdf.ContentStream(content, page.pdf)
    # Note: we check all strings are TextStringObjects.  ByteStringObjects
    # are strings where the byte->string encoding was unknown, so adding
    # them to the text here would be gibberish.
    for operands, operator in content.operations:
        #print "%s %s"%(operator, repr(operands))
        if operator == "Tj":
            for _text in operands:
                if isinstance(_text, PyPDF2.pdf.TextStringObject):
                    text += _text
                elif isinstance(_text, PyPDF2.pdf.ByteStringObject):
                    text += " "
        elif operator == "T*":
            text += "\n"
        elif operator == "TD":
#            if float(operands[0]) > .5:
#                text += " "
            for x in range(0, -int(operands[1])):
                text += "\n"
        elif operator == "'":
            text += "\n"
            _text = operands[0]
            if isinstance(_text, PyPDF2.pdf.TextStringObject):
                text += operands[0]
        elif operator == '"':
            _text = operands[2]
            if isinstance(_text, PyPDF2.pdf.TextStringObject):
                text += "\n"
                text += _text
        elif operator == "TJ":
            for i in operands[0]:
                if isinstance(i, PyPDF2.pdf.TextStringObject):
                    text += i
    return text

def ExtractText(pdf_url):
    f = fetch(pdf_url)
    pdf = PyPDF2.PdfFileReader(StringIO.StringIO(f))
    pdf_text = ""
    for i in range(0,pdf.numPages):
        page = pdf.getPage(i)
        pdf_text += extractTextFromPage(page)

    pdf_text = re.sub(HEADER_REGEX, "", pdf_text)
    pdf_text = re.sub(PAGE_REGEX, "", pdf_text)
    CHAR_FIXES = {
            u"\u2013": "...",
            u"\ufb01": "\"",
            u"\ufb02": "\"",
            u"\u2122": "'",
    }
    for b,a in CHAR_FIXES.items():
        pdf_text = pdf_text.replace(b, a);

    #logging.info(repr(pdf_text))
    return pdf_text.strip()

def _parse_entry(e):
    address = ADDRESS_REGEX.search(e.description)
    address_parsed = {
            'line1': None,
            'line2': None,
            'city': None,
            'state': None,
            'zip': None,
    }
    if address:
        line1 = address.group(1)
        line2 = address.group(2)
        if line1 == None and line2 != None:
            line1 = line2
            line2 = None
        address_parsed = {
            'line1': line1,
            'line2': line2,
            'city': address.group(3),
            'state': address.group(4),
            'zip': address.group(5),
        }

    doc = {
            'id': ID_REGEX.search(e.link).group(1),
            'link': e.link,
            'author': e.author,
            'doc_url': DOC_REGEX.search(e.description).group(0),
            'doc_text': None,
            'date_received': datetime.strptime(DATE_RECEIVED_REGEX.search(e.description).group(1),"%m/%d/%y"),
            'date_posted':  datetime.fromtimestamp(mktime(e.published_parsed)),
            'address':address_parsed
    }
    #try:
    #    doc['doc_text'] = _extract_text(doc['doc_url'])
    #except Exception, ex:
    #    logging.exception("Failed to extract text from: %s"%doc['doc_url'])

    return doc

# Run and parse:
#   address.zip=98122
#   address.state.stateCd=WA
def RunQuery(query):
    url = BASE_URL + query
    logging.info("Requesting:%s"%url)
    d = feedparser.parse(fetch(url))
    docs = []
    for e in d.entries:
        try:
            doc = _parse_entry(e)
            docs.append(doc)
        except Exception, ex:
            logging.exception("Failed to parse: %s"%e.link)
    return docs

if __name__ == "__main__":
    print RunQuery("address.zip=98122&proceeding=14-28")
    #print RunQuery("")
