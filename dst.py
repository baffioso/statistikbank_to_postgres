#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import urllib.request
import json
import subprocess

tables = []

class Table:
    'Informationer om data fra statistikbanken'

    def __init__(self, name, description, variables):
        self.name = name
        self.description = description
        self.variables = variables

    def getTableInfo(self):
        print('Navn: ' + self.name, '\nBeskrivelse: ' + self.description, '\nVariable: ' + ', '.join(self.variables))

    #Variable hentes fra tableinfo api til URL
    def getUrlVariables(self):
        urlVariables = []
        response = urllib.request.urlopen(baseurl + 'tableinfo/' + self.name).read().decode('utf8')
        json_obj = json.loads(response)
        for i in range(len(json_obj['variables'])):
            urlVariables.append(json_obj['variables'][i]['id'])
        return urlVariables

    #Der genereres URL for tabel til CSV download
    def getCsvUrl(self):
        subDataUrl = baseurl + 'data/' + self.name + '/CSV?delimiter=Semicolon&'
        urlVariables = '=*&'.join(self.getUrlVariables())
        csvUrl = subDataUrl + urlVariables + '=*'
        return csvUrl

#Overfør csv til postgres
def csvToPosgres(csvurl):
    pgcreds = 'dbname=postgres host=localhost port=5432 user=postgres password=xxx'
    schema = 'dst'
    ogr2ogr = 'ogr2ogr -f PostgreSQL PG:"' + pgcreds + '" CSV:/vsicurl_streaming/"' + csvurl + '" -nln ' + schema + '.' + table.name + ' -lco FID=gid -lco OVERWRITE=YES'
    subprocess.run(ogr2ogr, shell=True)


baseurl = 'http://api.statbank.dk/v1/'
response = urllib.request.urlopen(baseurl + 'tables').read().decode('utf8')
json_obj = json.loads(response)

#for i in range(len(json_obj)):
for i in range(8,10):
    table = Table(json_obj[i]['id'], json_obj[i]['text'], json_obj[i]['variables'])
    #table.getTableInfo()
    csvToPosgres(table.getCsvUrl())
    table.getTableInfo()
    print('\n')
