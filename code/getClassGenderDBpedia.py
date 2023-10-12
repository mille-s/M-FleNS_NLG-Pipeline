#!/usr/bin/env python
# -*- coding: utf-8 -*-
# authors: simon mille

from SPARQLWrapper import SPARQLWrapper, JSON
import sys
from xml.dom import minidom
import os
import re
import codecs
import json
import progressbar

bar = ''
def createProgressBar(bar, max):
  bar = progressbar.ProgressBar(max_value=max)
  return(bar)

filepath_subj = sys.argv[1]
filepath_obj = sys.argv[2]

list_subj = []
list_obj = []
with open(filepath_subj) as json_file_s:
  list_subj = json.load(json_file_s)
with open(filepath_obj) as json_file_o:
  list_obj = json.load(json_file_o)

# print(list_subj)
# print(list_obj)

def removeReservedCharsFileName(entityName):
  # reservedChars = ['#', '%', '&', '\{', '\}', '\\', '<', '>', '\*', '\?', '/', ' ', '\$', '!', "'", '"', ':', '@', '\+', '`', '\|', '=']
  newEntityName = str(entityName)
  # for reservedChar in reservedChars:
  while re.search(r'[#%&\{\}\\<>\*\?/ \$!\'":@\+`\|=]', newEntityName):
    newEntityName = re.sub(r'[#%&\{\}\\<>\*\?/ \$!\'":@\+`\|=]', "", newEntityName)
  return(newEntityName)
  
def fillListNeedType(list_entities):
  """ Create a list with all entities that need a type """
  list_need_type = []
  for entity_name in list_entities:
    if not re.search(' ', entity_name) and not entity_name.isnumeric() and entity_name[0].isupper() and entity_name not in list_need_type:
      list_need_type.append(entity_name)
  return(list_need_type)
    
def update_file_class_members(filepath, list_members):
  fd = codecs.open(filepath, 'r', 'utf-8').readlines()
  # We build this list and write it all to be safer (sometimes the all_validated files end with an empty line, sometimes not)
  list_members_to_write = []
  for member_there in fd:
    list_members_to_write.append(member_there.strip())

  for member_to_add in list_members:
    if member_to_add not in list_members_to_write:
      list_members_to_write.append(member_to_add)
    if removeReservedCharsFileName(member_to_add) not in list_members_to_write:
      list_members_to_write.append(removeReservedCharsFileName(member_to_add))

  with codecs.open(filepath, 'w', 'utf-8') as fo:
    for member_to_write in list_members_to_write:
      fo.write(member_to_write)
      fo.write('\n')

def get_types_of_entity(entity_untyped):
  list_types_found = []

  uri = "http://dbpedia.org/resource/"+entity_untyped
  # Define the DBpedia SPARQL endpoint URL
  sparql_endpoint = "https://dbpedia.org/sparql"
  # Compose the SPARQL query
  sparql_query = f"""
  SELECT ?obj
  WHERE {{
    <{uri}> rdf:type ?obj.
  }}
  """
  # Create a SPARQLWrapper object and set the query
  sparql = SPARQLWrapper(sparql_endpoint)
  sparql.setQuery(sparql_query)
  # Set the return format to JSON
  sparql.setReturnFormat(JSON)
  # Execute the query and parse the results
  results = sparql.query().convert()

  # Get types
  for result in results["results"]["bindings"]:
    if re.search('yago/Woman', result["obj"]["value"]) and 'Woman' not in list_types_found:
      list_types_found.append('Woman')
    type_value = result["obj"]["value"].rsplit('/', 1)[1]
    if type_value == 'Person':
      # to filter out entities that are probably not persons (e.g. "Politician")
      if re.search('_', entity_untyped):
        if type_value not in list_types_found:
          list_types_found.append(type_value)
    if type_value == 'Band':
      if type_value not in list_types_found:
        list_types_found.append(type_value)
  return(list_types_found)
  
  # return(results["results"]["bindings"])
  
def createListTypes(entities_that_need_type, bar):
  """ For each of the entities that need a type, get the types"""
  female_list = []
  person_list = []
  band_list = []
  bar = createProgressBar(bar, len(entities_that_need_type)-1)
  for count, entity_untyped in enumerate(entities_that_need_type):
    bar.update(count)
    results_type = get_types_of_entity(entity_untyped)
    entity_clean = entity_untyped.rsplit('_(', 1)[0]
    x = 0
    while x < len(results_type):
      result_type = results_type[x]
      if result_type == 'Woman':
        female_list.append(entity_clean)
      if result_type == 'Person':
        person_list.append(entity_clean)
      if result_type == 'Band':
        band_list.append(entity_clean)
      x += 1
  return(female_list, person_list, band_list)

subj_that_need_type = fillListNeedType(list_subj)
obj_that_need_type = fillListNeedType(list_obj)

female_subj = []
person_subj = []
band_subj = []
female_obj = []
person_obj = []
band_obj = []
if len(subj_that_need_type) > 0:
  female_subj, person_subj, band_subj = createListTypes(subj_that_need_type, bar)
if len(obj_that_need_type) > 0:
  female_obj, person_obj, band_obj = createListTypes(obj_that_need_type, bar)

if len(band_subj) > 0:
  update_file_class_members('/content/triples2predArg/classMembership/band_sub_all_validated.txt', band_subj)
if len(band_obj) > 0:
  update_file_class_members('/content/triples2predArg/classMembership/band_obj_all_validated.txt', band_obj)
if len(female_subj) > 0:
  update_file_class_members('/content/triples2predArg/classMembership/female_sub_all_validated.txt', female_subj)
if len(female_obj) > 0:
  update_file_class_members('/content/triples2predArg/classMembership/female_obj_all_validated.txt', female_obj)
if len(person_subj) > 0:
  update_file_class_members('/content/triples2predArg/classMembership/person_sub_all_validated.txt', person_subj)
if len(person_obj) > 0:
  update_file_class_members('/content/triples2predArg/classMembership/person_obj_all_validated.txt', person_obj)

if len(list_subj) > 0:
  update_file_class_members('/content/triples2predArg/classMembership/all_subValues.txt', list_subj)
if len(list_obj) > 0:
  update_file_class_members('/content/triples2predArg/classMembership/all_objValues.txt', list_obj)

print('\n')
print('Band-sbj: '+str(band_subj))
print('Band-obj: '+str(band_obj))
print('Fem-sbj: '+str(female_subj))
print('Fem-obj: '+str(female_obj))
print('Per-sbj: '+str(person_subj))
print('Per-obj: '+str(person_obj))
