#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import urllib.request
import json
import subprocess

############################
########## CONFIG ##########
############################

# statistikbank URL
baseurl = 'http://api.statbank.dk/v1/'
# postgres
pg_connect = 'dbname=postgres host=localhost port=5432 user=postgres password=xxx'
pg_schema = 'dst'

############################

class Table:
    'Informationer om data fra statistikbanken'

    def __init__(self, name, description, variables):
        self.name = name
        self.description = description
        self.variables = variables

    def getTableInfo(self):
        print('Navn: ' + self.name, '\nBeskrivelse: ' + self.description, '\nVariable: ' + ', '.join(self.variables))

    def getUrlVariables(self):
        """Variable hentes fra tableinfo api til URL"""
        urlVariables = []
        json_obj = getjson(baseurl + 'tableinfo/' + self.name)
        for i in range(len(json_obj['variables'])):
            urlVariables.append(json_obj['variables'][i]['id'])
        return urlVariables

    def getCsvUrl(self):
        """Der genereres URL for tabel til CSV download"""
        subDataUrl = baseurl + 'data/' + self.name + '/CSV?delimiter=Semicolon&'
        urlVariables = '=*&'.join(self.getUrlVariables())
        csvUrl = subDataUrl + urlVariables + '=*'
        return csvUrl

def getjson(url):
    response = urllib \
        .request \
        .urlopen(url) \
        .read() \
        .decode('utf8')
    return json.loads(response)

#####################################
########## DST -> Postgres ##########
#####################################

def csvToPosgres(csvurl):
    """Overfør csv til postgres vha. GDAL/ogr2ogr"""
    ogr2ogr = 'ogr2ogr -f PostgreSQL PG:"' + pg_connect + '" CSV:/vsicurl_streaming/"' + csvurl + '" -nln ' + pg_schema + '.' + table.name + ' -lco FID=gid -lco OVERWRITE=YES'
    subprocess.run(ogr2ogr, shell=True)


###########################
########## EMNER ##########
###########################

def getmainsubjects():
    """hent alle hovedemner"""
    json_obj = getjson(baseurl + 'subjects')
    for i in range(len(json_obj)):
        print(json_obj[i]['id'], json_obj[i]['description'])

def getsubjects(subject_id):
    """hent underemner for et emne"""
    json_obj = getjson(baseurl + 'subjects/' + subject_id)
    if json_obj[0]['hasSubjects'] == True:
        for i in range(len(json_obj[0]['subjects'])):
            print(json_obj[0]['subjects'][i]['id'], json_obj[0]['subjects'][i]['description'])
    else:
        print('Har ingen underemner')


##########################
########## TEST ##########
##########################

#getmainsubjects()
#getsubjects('02')


tablelist = ['FT', 'MUS', ]

for i in tablelist:
    json_obj = getjson(baseurl + 'tableinfo/' + i)
    table = Table(json_obj['id'], json_obj['text'], json_obj['variables'])
    csvToPosgres(table.getCsvUrl())

'''
# for i in range(len(json_obj)):
for i in range(7, 10):
    table = Table(json_obj[i]['id'], json_obj[i]['text'], json_obj[i]['variables'])
    csvToPosgres(table.getCsvUrl())
    table.getTableInfo()
'''
