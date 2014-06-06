#!/usr/bin/python

import feedparser
import re
#import PyPDF2
import urllib
import logging
import cStringIO as StringIO
from datetime import datetime
from time import mktime

BASE_URL = "http://apps.fcc.gov/ecfs/comment_search/rss?proceeding=14-28"

ID_REGEX = re.compile(r"http://apps\.fcc\.gov/ecfs/comment/view\?id=(\d+)")
DOC_REGEX = re.compile(r"http://apps\.fcc\.gov/ecfs/document/view\?id=\d+")
DATE_RECEIVED_REGEX = re.compile(r"Date Received:\s*([^\s]*) <br />")
DATE_POSTED_REGEX = re.compile(r"Date Posted:\s*([^\s]* [^\s]* [^\s]*) <br />")
HEADER_REGEX = re.compile(r"\d+\.txt")
ADDRESS_REGEX = re.compile(r"(?:(.*) <br />)?\n(.*) <br />\n(.*), (..) ([^\s]+) <br />$")



def _extract_text(pdf_url):
    f = urllib.urlopen(pdf_url)
    pdf = PyPDF2.PdfFileReader(StringIO.StringIO(f.read()))
    pdf_text = ""
    for i in range(0,pdf.numPages):
        page = pdf.getPage(i)
        pdf_text += page.extractText()

    pdf_text = re.sub(HEADER_REGEX, "", pdf_text)
    return pdf_text

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
    #    print "Failed to extract text from: %s"%doc['doc_url']
    #    print ex

    return doc

# Run and parse:
#   address.zip=98122
#   address.state.stateCd=WA
def RunQuery(query):
    url = BASE_URL
    if query:
        url += "&"+query
    logging.info("Requesting:%s"%url)
    d = feedparser.parse(url)
    docs = []
    for e in d.entries:
        try:
            doc = _parse_entry(e)
            docs.append(doc)
        except Exception, ex:
            logging.exception("Failed to parse: %s"%e.link)
    return docs

if __name__ == "__main__":
    print RunQuery("address.zip=98122")
    #print RunQuery("")
