import scraperwiki
import lxml.html
import urllib
import urllib2
import re
from datetime import datetime

url = "http://www.bacnet.org/Interpretations/index.html"

base, page = url.rsplit('/', 1)
print base

root = lxml.html.parse(url).getroot()
tables = root.cssselect("table")

#print tables
irTable = tables[1]
trs = irTable.cssselect('tr')
#print trs
irTr = trs[3]

tds = irTr.cssselect('td')
#print tds
#print lxml.html.tostring(tds[0])
paras = tds[0].cssselect('p')

try:
    for id, para in enumerate(paras):
        irLinks = para.cssselect('a')
        if len(irLinks) != 1:
            continue
        irLink = irLinks[0]
        irTitle = irLink.text
    #    data['title'] = irTitle
        print irTitle
        titleMatch = re.match('Interpretation (?P<id>[\d-.]+) - (?P<date>.+)$', irTitle)
        if titleMatch is not None:
            id = titleMatch.group('id')
            print id
            data = {'id' : id}
            dateStr = titleMatch.group('date')
            publishDate = datetime.strptime(dateStr, '%B %d, %Y')
            print publishDate
            data['publish_date'] = publishDate
        else:
            raise Exception('Could not match')

        relDocUrl = urllib.quote(irLink.attrib.get('href'))
        absDocUrl = ('/'.join((base, relDocUrl)))
        print absDocUrl
        data['doc_url'] = absDocUrl
        
        pdfData = urllib2.urlopen(absDocUrl).read()
        xmldata = scraperwiki.pdftoxml(pdfData)
        #print xmldata

        italics = para.cssselect('i')
        summary = italics[0].text
        data['summary'] = summary

        scraperwiki.sqlite.save(unique_keys=['id'], data=data)
except Exception as ex:
    print "Error: " + str(ex)
    exit(2)
