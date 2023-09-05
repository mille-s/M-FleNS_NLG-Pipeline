#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os.path
import sys
from sys import exit
import shutil
import codecs
import re

input_folder = sys.argv[1]
output_folder = sys.argv[2]
log_folder = sys.argv[3]

str_count_perLevel = []
txt_count_perLevel = []
error_count_perLevel = []

def count_conll(filePath):
  """ counts how many conll structures are in a file """
  counter = 0
  fd = codecs.open(filePath, 'r', 'utf-8')
  lines = fd.readlines()
  for line in lines:
    if re.search('^0\t_', line):
      counter += 1
  return(counter)

def count_txt(filePath):
  """ counts how many texts are in a file """
  fd = codecs.open(filePath, 'r', 'utf-8')
  lines = fd.readlines()
  return(len(lines))

def examine_files(path, count_perLevel):
  folder_content = os.listdir(path)
  # Sorting the files so they remain aligned with the outputs
  for file in sorted(folder_content):
    file_path = os.path.join(path, file)
    # If files are found in the folder, process them
    # Get number of input structures
    if os.path.isfile(file_path):
      if re.search('\.conll', file_path):
        count = count_conll(file_path)
        count_perLevel.append(count)
    # If folders are found in the folder, go deeper
    elif os.path.isdir(file_path):
      str_subfolder_content = os.listdir(file_path)
      # Sorting the folders so they remain aligned with the inputs
      for deeper_content in sorted(str_subfolder_content):
        new_file_path = os.path.join(file_path, deeper_content)
        # Get number of texts
        if os.path.isfile(new_file_path):
          if re.search('\.txt', new_file_path):
            count = count_txt(new_file_path)
            count_perLevel.append(count)

def examine_logs(path, count_perLevel):
  folder_content = os.listdir(path)
  dico_log_errors = {}
  for filepath in sorted(folder_content):
    if re.search('log_', os.path.basename(filepath)):
      level_name = os.path.basename(filepath).split('.')[0].split('log_')[1]
      dico_log_errors[level_name] = {}
      fd = codecs.open(os.path.join(path, filepath), 'r', 'utf-8')
      lines = fd.readlines()
      # Look for errors in log files and store how many of them in dico
      # E.G. 'DMorphLin': {'train_1triple_ga_utf8_0000-0449': 2, 'train_1triple_ga_utf8_0900-1349': 1, 'train_1triple_ga_utf8_0450-0899': 0}
      for line in lines:
        if line.startswith('Processing file '):
          input_id = 0
          input_name = line.split('Processing file ')[1].split('__')[0]
          dico_log_errors[level_name][input_name] = []
        if re.search('[Ee]rror', line):
          dico_log_errors[level_name][input_name].append(input_id)
        if  line.startswith('Processing graph output'):
          input_id += 1
        else:
          pass
  # print(dico_log_errors)
  # Make alist with all errors
  # E.g. ['2 errors found in DMorphLin train_1triple_ga_utf8_0000-0449', '1 errors found in DMorphLin train_1triple_ga_utf8_0900-1349']
  for level_key, level_values in dico_log_errors.items():
    for input_key, input_values in dico_log_errors[level_key].items():
      if len(dico_log_errors[level_key][input_key]) > 0:
        error = 'Error(s) found in '+str(level_key)+' '+str(input_key)+': '+str(dico_log_errors[level_key][input_key])
        count_perLevel.append(error)

examine_logs(log_folder, error_count_perLevel)
examine_files(input_folder, str_count_perLevel)
examine_files(output_folder, txt_count_perLevel)

fo = codecs.open(os.path.join(log_folder, 'summary.txt'), 'w', 'utf-8')

if len(error_count_perLevel) == 0:
  print('Log files OK!\n----')
  fo.write('Log files OK!\n----\n')
else:
  print('Error(s) found in log files!\n----')
  fo.write('Error(s) found in log files!\n----\n')
  print(error_count_perLevel)
  fo.write(str(error_count_perLevel)+'\n')

print('\n')
fo.write('\n')

if str_count_perLevel == txt_count_perLevel:
  print('Number of texts OK!\n----')
  fo.write('Number of texts OK!\n----\n')
else:
  print('Problem with number of texts!\n----')
  fo.write('Problem with number of texts!\n----\n')
  print(error_count_perLevel)
  fo.write(str(error_count_perLevel)+'\n')

print('Inputs:  ' + str(sum(str_count_perLevel)))
fo.write('Inputs:  ' + str(sum(str_count_perLevel))+'\n')
print('Outputs: ' + str(sum(txt_count_perLevel)))
fo.write('Outputs: ' + str(sum(txt_count_perLevel))+'\n')

print('Inputs per file:  ' + str(str_count_perLevel))
fo.write('Inputs per file:  ' + str(str_count_perLevel)+'\n')
print('Outputs per file: ' + str(txt_count_perLevel))
fo.write('Outputs per file: ' + str(txt_count_perLevel)+'\n')

fo.close()
