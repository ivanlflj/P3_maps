#C:\Anaconda2 python
# -*- coding: utf-8 -*-
# This file has functions to be used in the P3.ipynb
from xml.etree import cElementTree as ET
import sqlite3 as lite
import os
import pandas as pd

def is_street_name(elem):
    '''Verifica se o elemento é um nome de rua'''
    return (elem.attrib['k'] == 'addr:street')

def first_word(street_name):
    '''Pega a primeira palavra da string'''
    return street_name.split()[0]

def audit_1(osm_file, expected_names):
    '''Verifica o início do nome da rua que não era esperado e coloca todas as ocorrências em um dicionário'''
    street_types_unexpected = {}
    for event, elem in ET.iterparse(osm_file, events=("start",)):
        if elem.tag == 'way':
            for tag in elem.iter('tag'):
                if is_street_name(tag):
                    if first_word(tag.attrib['v']) not in expected_names:
                        if first_word(tag.attrib['v']) in street_types_unexpected:
                            street_types_unexpected[first_word(tag.attrib['v'])].append(tag.attrib['v'])
                        else:
                            street_types_unexpected[first_word(tag.attrib['v'])] = [tag.attrib['v']]
    return street_types_unexpected

def print_unexpected(street_types_unexpected):
    '''Apresenta as ruas com nome para ser aprimoradas'''
    counter = 0
    for key, values in street_types_unexpected.iteritems():
        counter += 1
        print(key)
        for value in values:
            print("--- " + value)
        if counter == 5:
            break

def is_amenity(elem):
    '''Verifica se o elemento é um nome de loja'''
    return (elem.attrib['k'] == 'amenity')

def audit_2(osm_file):
    '''Verifica o início do nome da rua que não era esperado e coloca todas as ocorrências em um dicionário'''
    store_types = {}
    for event, elem in ET.iterparse(osm_file, events=("start",)):
        if elem.tag == 'node':
            for tag in elem.iter('tag'):
                if is_amenity(tag):
                    if tag.attrib['v'] in store_types:
                        store_types[tag.attrib['v']] += 1
                    else:
                        store_types[tag.attrib['v']] = 1
    return store_types

def fix_problem1(con):
    '''Resolve o problema 1'''
    words_to_correct = ['Servidão', '15', 'Pça.', 'Praca', 'Bernadino', 'Professor', 'rua', 'Estr.', 'Lourival',
                    'Mário', 'Trav', 'Heráclito', 'Av', 'Alfredo', 'R.', 'Afredo', 'Marquês', 'Dias', 'Presidente']
    # Convertendo todos os dados para unicode, assim pode ser comparado
    words_to_correct = [name.decode('utf-8') for name in words_to_correct]
    cur = con.cursor()
    cur.execute("SELECT * FROM ways_tags WHERE key = 'addr:street'")
    list_to_correct = cur.fetchall()
    for address in list_to_correct:
        if first_word(address[2]) in words_to_correct:
            if (first_word(address[2]) == 'R.'.decode('utf-8') or
                first_word(address[2]) == 'rua'.decode('utf-8')):
                new_part = 'Rua'
                old_part = address[2].split()[1:]
                new_word = new_part + ' ' + ' '.join(old_part)
                cur.execute("UPDATE ways_tags SET value = '" + new_word + "' WHERE id = " + str(address[0]) + " and key = 'addr:street'")
            elif first_word(address[2]) == 'Av'.decode('utf-8'):
                new_part = 'Avenida'
                old_part = address[2].split()[1:]
                new_word = new_part + ' ' + ' '.join(old_part)
                cur.execute("UPDATE ways_tags SET value = '" + new_word + "' WHERE id = " + str(address[0]) + " and key = 'addr:street'")
            elif first_word(address[2]) == 'trav'.decode('utf-8'):
                new_part = 'Travessa'
                old_part = address[2].split()[1:]
                new_word = new_part + ' ' + ' '.join(old_part)
                cur.execute("UPDATE ways_tags SET value = '" + new_word + "' WHERE id = " + str(address[0]) + " and key = 'addr:street'")
            elif first_word(address[2]) == 'Estr.'.decode('utf-8'):
                new_part = 'Estrada'
                old_part = address[2].split()[1:]
                new_word = new_part + ' ' + ' '.join(old_part)
                cur.execute("UPDATE ways_tags SET value = '" + new_word + "' WHERE id = " + str(address[0]) + " and key = 'addr:street'")
            elif (first_word(address[2]) == 'Pça.'.decode('utf-8') or
                first_word(address[2]) == 'Praca'.decode('utf-8')):
                new_part = 'Praça'
                old_part = address[2].split()[1:]
                new_word = new_part.decode('utf-8') + ' ' + ' '.join(old_part)
                cur.execute("UPDATE ways_tags SET value = '" + new_word + "' WHERE id = " + str(address[0]) + " and key = 'addr:street'")
            else:
                new_part = 'Rua'
                old_part = address[2].split()
                new_word = new_part + ' ' + ' '.join(old_part)
                cur.execute("UPDATE ways_tags SET value = '" + new_word + "' WHERE id = " + str(address[0]) + " and key = 'addr:street'")

def create_data_sql(con, file_name):
    '''O objetivo dessa função é colocar o dado na base de dados SQL'''
    cur = con.cursor()
    for event, elem in ET.iterparse(file_name, events=("start",)):
        if elem.tag == 'node':
            cur.execute("INSERT INTO nodes VALUES(" + elem.attrib['id'] + "," + elem.attrib['lat'] + ","
                        + elem.attrib['lon'] + ",'" + elem.attrib['user'] + "'," + elem.attrib['uid'] + ")")
            for tag in elem.iter('tag'):
                cur.execute("INSERT INTO nodes_tags VALUES(" + elem.attrib['id'] + ",'" + tag.attrib['k'] + "','"
                                + tag.attrib['v'].replace("'","") + "')")
        if elem.tag == 'way':
            cur.execute("INSERT INTO ways VALUES(" + elem.attrib['id'] + ",'"
                        + elem.attrib['user'] + "'," + elem.attrib['uid'] + ")")
            for tag in elem.iter('tag'):
                cur.execute("INSERT INTO ways_tags VALUES(" + elem.attrib['id'] + ",'" + tag.attrib['k'] + "','"
                        + tag.attrib['v'].replace("'","") + "')")

def create_tables_sql(con):
    '''O objetivo dessa função é criar a base das tabelas na base de dados SQL'''
    cur = con.cursor()
    cur.execute('''CREATE TABLE nodes (
    id INTEGER PRIMARY KEY NOT NULL,
    lat REAL,
    lon REAL,
    user TEXT,
    uid INTEGER
    );''')
    cur.execute('''CREATE TABLE nodes_tags (
    id INTEGER,
    key TEXT,
    value TEXT,
    FOREIGN KEY (id) REFERENCES nodes(id)
    );''')
    cur.execute('''CREATE TABLE ways (
    id INTEGER PRIMARY KEY NOT NULL,
    user TEXT,
    uid INTEGER
    );''')
    cur.execute('''CREATE TABLE ways_tags (
    id INTEGER NOT NULL,
    key TEXT NOT NULL,
    value TEXT NOT NULL,
    FOREIGN KEY (id) REFERENCES ways(id)
    );''')
