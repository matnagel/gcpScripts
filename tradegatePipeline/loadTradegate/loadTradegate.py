import apache_beam as beam
from apache_beam.io import fileio
#from google.cloud import storage

import concurrent.futures
import requests as rq

from datetime import date, datetime
import time

from bs4 import BeautifulSoup
from zipfile import ZipFile, ZIP_DEFLATED
from gcp.SqlSources import Stock, Price, StdSource

class Webpage:
    def __init__(self, isin, scrapeDate, content):
        self.isin = isin
        self.scrapeDate = scrapeDate
        self.content = content
    def __str__(self):
        return f"Webpage of {self.isin} on {self.scrapeDate}"
    @staticmethod
    def recoverFromFile(filename, content):
        filename = filename.replace('_', '.')
        parts = filename.split('.')
        isin = parts[1]
        dateString = parts[0]
        scrapeDate = datetime.strptime(dateString, "%y%m%d")
        return Webpage(isin, scrapeDate, content)

def filesToProcess(bucketName):
    return fileio.MatchFiles(f"{bucketName}/*") | fileio.ReadMatches()

def unzipFiles(zipHandle):
    with zipHandle.open() as zipMemory, ZipFile(zipMemory, 'r', ZIP_DEFLATED) as zipFile:
        for name in zipFile.namelist():
            cont = zipFile.read(name)
            yield (name, cont)

def convertToWebpage(t):
    return Webpage.recoverFromFile(t[0], t[1])

class saveToDB(beam.DoFn):
    def setup(self):
        self.source = StdSource()
    def teardown(self):
        self.source.tearDown()
    def process(self, element):
        self.source.addRow(element)
        self.source.commit()
        yield f"Committed {element}"

def runBeam():
    bucketName = 'localBucket'
    with beam.Pipeline() as p:
        print("Starting pipeline")
        p | filesToProcess(bucketName) | LoadFile(bucketName)

def extractId(soup, css):
    #setlocale(LC_NUMERIC, 'de_DE.UTF-8')
    html = soup.select(css)[0]
    txt = html.text.replace(' ', '')
    txt = txt.replace(',', '.')
    return float(txt)
    #return atof(txt)

def toPrice(webpage):
    rawPage = webpage.content
    soupPage = BeautifulSoup(rawPage, 'html.parser')
    try:
        last = extractId(soupPage, '#last')
        high = extractId(soupPage, '#high')
        low = extractId(soupPage, '#low')
    except ValueError:
        print(f"Malformed page returned for {isin}")
    return Price(isin=webpage.isin, date=webpage.scrapeDate, last=last, high=high, low=low)

# def verifyPreconditions(source):
#     stocks = source.query(Stock)
#     if len(list(stocks)) >= 25:
#         raise ValueError('There are more than 25 stocks to update')
#     lastUpdate = source.query(Price.date).order_by(Price.date.desc()).first()
#     today = date.today()
#     if lastUpdate.date >= today:
#         raise RuntimeError(f'Already have entries with date {lastUpdate.date}, which is today {today} or later. Only updates once a day.')

if __name__ == '__main__':
    runBeam()
