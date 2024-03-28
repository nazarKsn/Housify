#!/usr/bin/env python3
"""Populate MongoDB database with sample data"""
import csv
import json
from samples.images import images
from src.mongo import DBClient

csv_file = './samples/samples.csv'
ind = 0
client = DBClient('LordsProperties')

with open(csv_file) as cfile:
    reader = csv.DictReader(cfile)
    for row in reader:
        row['bedrooms'] = int(row['bedrooms'])
        row['bathrooms'] = int(row['bathrooms'])
        row['square_feet'] = int(row['square_feet'])
        row['images'] = [images[ind], images[ind+1]]

        ind += 2

        client.insert_one('properties', row)
