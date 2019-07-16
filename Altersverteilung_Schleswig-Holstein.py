#!/usr/bin/env python3

# Dieses Skript lädt die Daten zur Bevölkerung Schleswig-Holsteins aus dem Open-Data-Portal und erstellt
# daraus einzelne Diagramme zur Altersverteilung. Diese können anschließend mit dem Befehl
# 
# ffmpeg -framerate 1 -i 2%03d.png -r 30 altersverteilung.mp4
# 
# zu einem Film zusammengefügt werden.

import rdflib
from rdflib import Graph, Literal, BNode, Namespace, RDF, URIRef
from rdflib.namespace import DC, FOAF, DCTERMS
import pandas as pd
import re

DCAT_Dataset = rdflib.term.URIRef('http://www.w3.org/ns/dcat#Dataset')
DCAT_Distribution = rdflib.term.URIRef('http://www.w3.org/ns/dcat#Distribution')
DCAT_distribution = rdflib.term.URIRef('http://www.w3.org/ns/dcat#distribution')
DCAT_accessURL = rdflib.term.URIRef('http://www.w3.org/ns/dcat#accessURL')
DC_format = rdflib.term.URIRef('http://purl.org/dc/terms/format')
FileType_XLS = rdflib.term.URIRef('http://publications.europa.eu/resource/authority/file-type/XLS')
FileType_XLSX = rdflib.term.URIRef('http://publications.europa.eu/resource/authority/file-type/XLSX')

# Lädt eine Excel-Datei auf Basis einer URL im Open-Data-Portal
def get_excel_file( uri ):
    g = rdflib.Graph()
    result = g.parse(uri)
    for distribution in g.subjects(RDF.type, DCAT_Distribution):
        f = g.value(distribution, DC_format)
        if( f == FileType_XLS or f == FileType_XLSX ):
            return( g.value(distribution, DCAT_accessURL).toPython())
    return None

datasets = [
    'https://opendata.schleswig-holstein.de/dataset/die-bevolkerung-in-hamburg-und-schleswig-holstein-2004-nach-alter-und-geschlecht.rdf',
    'https://opendata.schleswig-holstein.de/dataset/die-bevolkerung-in-hamburg-und-schleswig-holstein-2005-nach-alter-und-geschlecht.rdf',
    'https://opendata.schleswig-holstein.de/dataset/die-bevolkerung-in-hamburg-und-schleswig-holstein-2006-nach-alter-und-geschlecht.rdf',
    'https://opendata.schleswig-holstein.de/dataset/die-bevolkerung-in-hamburg-und-schleswig-holstein-2007-nach-alter-und-geschlecht.rdf',
    'https://opendata.schleswig-holstein.de/dataset/die-bevolkerung-in-hamburg-und-schleswig-holstein-2008-nach-alter-und-geschlecht.rdf',
    'https://opendata.schleswig-holstein.de/dataset/die-bevolkerung-in-hamburg-und-schleswig-holstein-2009-nach-alter-und-geschlecht.rdf',
    'https://opendata.schleswig-holstein.de/dataset/die-bevolkerung-in-hamburg-und-schleswig-holstein-2010-nach-alter-und-geschlecht.rdf',
    'https://opendata.schleswig-holstein.de/dataset/die-bevolkerung-in-schleswig-holstein-nach-alter-und-geschlecht-2011-endgultige-ergebnisse-2011.rdf',
    'https://opendata.schleswig-holstein.de/dataset/die-bevolkerung-in-schleswig-holstein-nach-alter-und-geschlecht-2012-endgultige-ergebnisse-2011.rdf',
    'https://opendata.schleswig-holstein.de/dataset/die-bevolkerung-in-schleswig-holstein-nach-alter-und-geschlecht-2013-endgultige-ergebnisse-2011.rdf',
    'https://opendata.schleswig-holstein.de/dataset/die-bevolkerung-in-schleswig-holstein-nach-alter-und-geschlecht-2014-endgultige-ergebnisse-2011.rdf',
    'https://opendata.schleswig-holstein.de/dataset/die-bevolkerung-in-schleswig-holstein-nach-alter-und-geschlecht-2015-endgultige-ergebnisse-2011.rdf',
    'https://opendata.schleswig-holstein.de/dataset/die-bevolkerung-in-schleswig-holstein-nach-alter-und-geschlecht-2016-endgultige-ergebnisse-2011.rdf',
    'https://opendata.schleswig-holstein.de/dataset/die-bevolkerung-in-schleswig-holstein-nach-alter-und-geschlecht-2017-endgultige-ergebnisse-2011.rdf',
    'https://opendata.schleswig-holstein.de/dataset/die-bevolkerung-in-schleswig-holstein-nach-alter-und-geschlecht-2018-endgultige-ergebnisse-2011.rdf'
]

def plot_year( year ):
    file_name = get_excel_file(datasets[year-2004])
  
    # dummerweise hat das Statistikamt Nord zwischendurch die Bennennung der Blätter geändert
    try:
        raw_data =  pd.read_excel(file_name,sheet_name='Schleswig-Holstein', skiprows=7)
    except:
        raw_data =  pd.read_excel(file_name,sheet_name='SH-Gesamt_1', skiprows=7)
  
    raw_data.columns = ['alter', 'geburtsjahr','insgesamt','männlich','weiblich']
  
    # Zeilen mit Zusammenfassungen entfernen
    raw_data = raw_data[raw_data.geburtsjahr.isna() == False]
    raw_data = raw_data[raw_data.alter.isna() == False]
  
    raw_data.iloc[0].alter = '0 - 1'
    raw_data.alter=[re.sub( ' .*$','', x) for x in raw_data.alter]
    raw_data.alter=pd.to_numeric(raw_data.alter,errors='coerce')
    raw_data = raw_data[raw_data.alter.isna() == False]

    plot = raw_data.plot(x='alter', y=['männlich','weiblich'], ylim=(0,30000), style='-', figsize=(15,7))
    plot.set_title('Bevölkerung Schleswig-Holstein %d'%year)

    return plot

for year in range(2004, 2019):
    print(year)
    plot_year(year).get_figure().savefig('%d.png' % year)
                    