#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os.path
import sys
import shutil
import codecs
import re
import glob

out_folder = sys.argv[1]
clean_out_str_folder = sys.argv[2]
split = sys.argv[3]

def write_file(filename, list_to_concatenate):
  with codecs.open(filename, 'w', 'utf-8') as outfile:
    # Files need to be sorted to be concatenated in the right order
    for fname in sorted(list_to_concatenate):
      print('Processing '+fname)
      with open(fname) as infile:
        outfile.write(infile.read())

def collect_files(path):
  folder_content = os.listdir(path)
  list_str_same_level = []
  list_txt = []
  # Sorting the files so they remain aligned with the outputs
  for folder in sorted(folder_content):
    folder_path = os.path.join(path, folder)
    # If folders are found in the folder (should be this way), go deeper
    if os.path.isdir(folder_path):
      str_subfolder_content = os.listdir(folder_path)
      # Sorting the folders so they remain aligned with the inputs
      for deeper_content in sorted(str_subfolder_content):
        new_file_path = os.path.join(folder_path, deeper_content)
        # Collect paths
        if os.path.isfile(new_file_path):
          if re.search('\.txt', new_file_path):
            list_txt.append(new_file_path)
          else:
            list_str_same_level.append(new_file_path)
  return(list_str_same_level, list_txt)

str_to_concatenate, txt_to_concatenate = collect_files(out_folder)

split_path = os.path.join(clean_out_str_folder, split)
if not os.path.exists(split_path):
  os.makedirs(split_path)

filename_str = os.path.join(split_path, os.path.split(out_folder)[-1]+'.str')
filename_txt = os.path.join(split_path, '00-Text.txt')

write_file(filename_str, str_to_concatenate)
if re.search('SMorphText', out_folder):
  write_file(filename_txt, txt_to_concatenate)