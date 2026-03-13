#!/usr/bin/env python
# -*- coding: utf-8 -*-

import glob
import sys
import os
import codecs
import re

language = sys.argv[1]
output_folder = sys.argv[2]

#encodings: cp1252, utf-8, utf-16BE ...

#get path of input folder
containing_path = output_folder.rsplit('\\', 1)[0].replace('\\', '/')
# language = 'GA'
with_underscores = 'no'
without_underscores = 'yes'
#folder_name = path.rsplit('\\', 1)[1]

#filename = os.path.join(containing_path, str(x)+'_report.txt')

#create output file
#fo = codecs.open(filename, 'a', 'utf-8')

#read filepaths
#list_filepaths = glob.glob(os.path.join(path, '*.conll'))
list_filepaths = glob.glob(os.path.join(output_folder, '*.txt'))

def uppercase(match):
  return(match.group(1).upper())

def uppercaseDot(match):
  return('. '+match.group(1).upper())

def clean_outputs (text, count, underscores):
  # Irish things
  if language == 'GA':
    # Reestablish punctuations removed for morph processing
    text = re.subn(r"_APSTR_", r"'", text)[0]
    text = re.subn(r"_OBRKT_", r"(", text)[0]
    text = re.subn(r"_CBRKT_", r")", text)[0]
    text = re.subn(r"_AMPRS_", r"&", text)[0]
    text = re.subn(r"_SEMICOL_", r";", text)[0]
    text = re.subn(r"_DOLLSIGN_", r"$", text)[0]
    # The next line was not activated for the WebNLG submission
    # text = re.subn(r"_PLUSSIGN_", r"+", text)[0]
    text = re.subn(r"_DBLQUOT_", r'\"', text)[0]
    # Process prefixes (either after a space or at the beginning of a line)
    text = re.subn(r" d- ", r" d'", text)[0]
    text = re.subn(r"^d- ", r"d'", text)[0]
    text = re.subn(r' h- ', r' h', text)[0]
    text = re.subn(r'^h- ', r'h', text)[0]
    text = re.subn(r' t- ', r' t-', text)[0]
    text = re.subn(r'^t- ', r't-', text)[0]
    # The hyphens left should all be from prefixed adjectives
    text = re.subn(r'- - ', '', text)[0]
    text = re.subn(r' - ', '', text)[0]
    text = re.subn(r'- ', '', text)[0]
    # Bring together a + tá in relative clauses
    text = re.subn(r' a tá ', r' atá ', text)[0]
    # contract "de" in front of "fh" and vowels, i, etc.
    text = re.subn(r' de [aA]n ', r' den ', text)[0]
    text = re.subn(r' de [aA]n_', r' den ', text)[0]
    text = re.subn(r' do [aA]n ', r' don ', text)[0]
    text = re.subn(r' do [aA]n_', r' don ', text)[0]
    text = re.subn(r' faoi [aA]n ', r' faoin ', text)[0]
    text = re.subn(r' faoi [aA]n_', r' faoin ', text)[0]
    text = re.subn(r' ó [aA]n ', r' ón ', text)[0]
    text = re.subn(r' ó [aA]n_', r' ón ', text)[0]
    text = re.subn(r' sa [aA]n ', r' san ', text)[0]
    text = re.subn(r' sa [aA]n_', r' san ', text)[0]
    text = re.subn(r" d[eo] ([fF])h", r" d'\g<1>h", text)[0]
    text = re.subn(r" de ([aeiouAEIOUáéíóúÁÉÍÓÚ])", r" d'\g<1>", text)[0]
    text = re.subn(r' i Éire ', r' in Éirinn ', text)[0]
    text = re.subn(r' i An ', r' ins An ', text)[0]
    text = re.subn(r' i An_', r' ins An ', text)[0]
    text = re.subn(r' i ([aeiouáéíóúAEIOUÁÉÍÓÚ])', r' in \g<1>', text)[0]
    text = re.subn(r' i [Nn]a ', r' sna ', text)[0]
    text = re.subn(r' le [Nn]a ', r'leis na ', text)[0]
    # Remove det when the next NP is probably genitive (restricting to uppercase words to target nouns more safely, but we may be missing some cases this way ).
    # le+an - leis an (FORGe correctly produces that), but if we remove the "an" here, we need to revert "leis" to "le".
    text = re.subn(r' leis an ([A-Z][^\s]+) (an|na) ([A-Z][^\s]+)', r' le \g<1> \g<2> \g<3>', text)[0]
    text = re.subn(r' leis an ([A-Z][^\s]+)_(an|na)_([A-Z][^\s]+)', r' le \g<1>_\g<2>_\g<3>', text)[0]
    # Same for sa
    text = re.subn(r' san* ([A-Z][^\s]+) (an|na) ([A-Z][^\s]+)', r' i \g<1> \g<2> \g<3>', text)[0]
    text = re.subn(r' san* ([A-Z][^\s]+)_(an|na)_([A-Z][^\s]+)', r' i \g<1>_\g<2>_\g<3>', text)[0]
    text = re.subn(r' an ([A-Z][^\s]+) (an|na) ([A-Z][^\s]+)', r' \g<1> \g<2> \g<3>', text)[0]
    text = re.subn(r' an ([A-Z][^\s]+)_(an|na)_([A-Z][^\s]+)', r' \g<1>_\g<2>_\g<3>', text)[0]
    # Repeat the 2 lines below because now we introduced a "i" and "le" again with the rules above
    text = re.subn(r' i ([aeiouáéíóúAEIOUÁÉÍÓÚ])', r' in \g<1>', text)[0]
    text = re.subn(r' le [Nn]a ', r'leis na ', text)[0]
    # Lenition f (+ contraction)
    text = re.subn(r' d[eo] ([fF])([^h])', r" d'\g<1>h\g<2>", text)[0]
    text = re.subn(r" (ar|de|do|faoi|mar|ó|roimh|trí|um|céad) ([bcdfgmptBCDFGMPT])([^hH])", r" \g<1> \g<2>h\g<3>", text)[0]
    text = re.subn(r" (ar|de|do|faoi|mar|ó|roimh|trí|um|céad) ([sS])([^hcfmptvHCFMPTV])", r" \g<1> \g<2>h\g<3>", text)[0]
    # Eclipsis
    text = re.subn(r' (i|leis an) ([bB][^pP])', r' \g<1> m\g<2>', text)[0]
    text = re.subn(r' (i|leis an) ([cC])', r' \g<1> g\g<2>', text)[0]
    text = re.subn(r' i ([dD][^tT])', r' i n\g<1>', text)[0]
    text = re.subn(r' (i|leis an) ([fF])', r' \g<1> bh\g<2>', text)[0]
    text = re.subn(r' (i|leis an) ([gG][^cC])', r' \g<1> n\g<2>', text)[0]
    text = re.subn(r' (i|leis an) ([pP])', r' \g<1> b\g<2>', text)[0]
    text = re.subn(r' i ([tT])', r' i d\g<1>', text)[0]
    # text = re.subn(r' i ([aeiouáéíóú])', r' i n-\g<1>', text)[0]
    # text = re.subn(r' i ([AEIOUÁÉÍÓÚ])', r' i n\g<1>', text)[0]
    # Ugly patches
    text = re.subn(r' ar bhí ', r' a bhí ', text)[0]
    text = re.subn(r' an ann ', r' air ', text)[0]
    text = re.subn(r' an sé ', r' an é ', text)[0]
    text = re.subn(r' an ([aA])n([\s_])', r' \g<1>n\g<2>', text)[0]
    text = re.subn(r'^An ([aA])n([\s_])', r' An\g<2>', text)[0]
    text = re.subn(r'([0-9]+\s*)meters', r'\g<1>méadar', text)[0]
    text = re.subn(r'([0-9]+_)meters', r'\g<1>méadar', text)[0]
    text = re.subn(r'([0-9]+\s*)minutes', r'\g<1>nóiméad', text)[0]
    text = re.subn(r'([0-9]+_)minutes', r'\g<1>nóiméad', text)[0]
  # Erroneous "type = parenthetical" fix
  if re.search(r'\) \(', text):
    print('!!! Failed parenthesis generation in input '+str(count)+' (fixed)')
    text = re.subn(r'\) \(', r' ', text)[0]
  # clean quotes that MATE can’t take care of
  text = re.subn(r'\\\\"([^\\\\]+)\\\\', r'"\g<1>"', text)[0]
  # uppercase words when at the beginning of a sentence or after a final dot (dots preceded by a space)
  text = re.subn(r' \. ([a-z])', uppercaseDot, text)[0]
  text = re.subn(r'^([a-z])', uppercase, text)[0]
  # replace "a" by "an" before vowels (should restrict to English)
  if language == 'EN':
    text = re.subn(r' a ([aeioAEIO])', r' an \g<1>', text)[0]
    text = re.subn(r" 's ", r"'s ", text)[0]
  # French post-processing
  if language == 'FR':
    # Conjunctions/Prepositions (+determiner)
    text = re.subn(r' de ([haeiouHAEIOU])', r" d'\g<1>", text)[0]
    text = re.subn(r' du ([haeiouHAEIOU])', r" de l'\g<1>", text)[0]
    text = re.subn(r' que ([haeiouHAEIOU])', r" qu'\g<1>", text)[0]
    text = re.subn(r' jusque ([aeiouAEIOU])', r" jusqu'\g<1>", text)[0]
    # Determiners/pronouns
    text = re.subn(r' l[ae] ([aeiouAEIOU])', r" l'\g<1>", text)[0]
    text = re.subn(r'L[ae] ([aeiouAEIOU])', r"L'\g<1>", text)[0]
    text = re.subn(r' ça était', r" c'était", text)[0]
    text = re.subn(r' ça est', r" c'est", text)[0]
    # Pronouns
    text = re.subn(r' ce ([aeiouAEIOU])', r' cet \g<1>', text)[0]
    text = re.subn(r' je ([aeiouyAEIOUY])', r" j'\g<1>", text)[0]
    text = re.subn(r' me ([aeiouyAEIOUY])', r" m'\g<1>", text)[0]
    text = re.subn(r' te ([aeiouyAEIOUY])', r" t'\g<1>", text)[0]
    text = re.subn(r' se ([aeiouyAEIOUY])', r" s'\g<1>", text)[0]
    # Others
    text = re.subn(r' ne ([aeiouyAEIOUY])', r" n'\g<1>", text)[0]
    # Patches units
    text = re.subn(r'_meters', r'_mètres', text)[0]
    text = re.subn(r' meters', r' mètres', text)[0]
    text = re.subn(r'_kilometers', r'kilomètres', text)[0]
    text = re.subn(r' kilometers', r'kilomètres', text)[0]
    # Added after generating FR v0.1
    text = re.subn(r'_metres', r'_mètres', text)[0]
    text = re.subn(r' metres', r' mètres', text)[0]
    text = re.subn(r'_kilometres', r'kilomètres', text)[0]
    text = re.subn(r' kilometres', r'kilomètres', text)[0]
    text = re.subn(r'_per_second', r'_par_seconde', text)[0]
    text = re.subn(r' per second', r' par seconde', text)[0]
    text = re.subn(r'_per_hour', r'_heure', text)[0]
    text = re.subn(r' per hour', r' heure', text)[0]
    text = re.subn(r'_degrees', r'_degrés', text)[0]
    text = re.subn(r' degrees', r' degrés', text)[0]
    text = re.subn(r'_inhabitants', r'_habitants', text)[0]
    text = re.subn(r' inhabitants', r' habitants', text)[0]
    text = re.subn(r'_square', r'_carrés', text)[0]
    text = re.subn(r' square', r' carrés', text)[0]
    
  # find generation fails (we introduce [..] or [...] or [......] when a sentence cannot be generated
  if re.search(r'\[\.\.', text):
    print('!!! Failed sentence generation in input '+str(count))
  # replace underscores by spaces
  if underscores == 'yes':
    pass
  else:
    text = re.subn(r'_', r' ', text)[0]
  # remove space before commas,  dots, etc.
  text = re.subn(r' ,', r',', text)[0]
  text = re.subn(r' \.', r'.', text)[0]
  text = re.subn(r' \)', r')', text)[0]
  text = re.subn(r'\( ', r'(', text)[0]
  text = re.subn(r' ([0-9]+)\.0 kilogram', r' \g<1>kg', text)[0]
  # replace double dots by single ones
  while re.search(r'\.\.', text):
    text = re.subn(r'\.\.', '.', text)[0]
  text = re.subn(r'% %', r'%', text)[0]
  # Clean remnants of non-generated sentences
  text = re.subn(r'Sentence \[\.\]\.', '', text)[0]
  # Remove initial spaces
  while re.search(r'^ ', text):
    text = re.subn(r'^ ', '', text)[0]
  # New 2023: replace double spaces by single ones
  while re.search(r'  ', text):
    text = re.subn(r'  ', r' ', text)[0]
  # reformat date/time
  text = re.subn(r'([0-9]+)-([0-9]+)-([0-9]+)T([0-9]+:[0-9]+:[0-9]+)Z', r'\g<1>/\g<2>/\g<3> at \g<4>', text)[0]
  return(text)

count_strs_all_postproc = []
for filepath in sorted(list_filepaths):
  count_strs_all = 0
  # filename = filepath.split('\\')[-1].split('.')[0]
  head, tail = os.path.split(filepath)
  filename = tail.rsplit('.')[0]
  fd = codecs.open(filepath, 'r', 'utf-8')
  print('Processing '+filename)
  filename_out_noUnderscores = filename+'_postproc''.txt'
  filename_out_Underscores = filename+'_postproc_underscores''.txt'
  if without_underscores == 'yes':
    fo1 = codecs.open(os.path.join(output_folder, filename_out_noUnderscores), 'w', 'utf-8')
  if with_underscores == 'yes':
    fo2 = codecs.open(os.path.join(output_folder, filename_out_Underscores), 'w', 'utf-8')
  lines = fd.readlines()
  x = 0
  for line in lines:
    # To filter out final linebreak in each file
    if not line == '\n':
      if without_underscores == 'yes':
        new_line = clean_outputs(line, x, 'no')
        fo1.write(new_line)
      if with_underscores == 'yes':
        new_line = clean_outputs(line, x, 'yes')
        fo2.write(new_line)
      count_strs_all += 1
    x += 1
  if without_underscores == 'yes':
    fo1.close()
  if with_underscores == 'yes':
    fo2.close()
  count_strs_all_postproc.append(count_strs_all)

