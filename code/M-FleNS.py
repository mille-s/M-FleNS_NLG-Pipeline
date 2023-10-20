#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import os.path
import subprocess
from subprocess import Popen, PIPE
import sys
from sys import exit
import shutil
from shutil import copyfile
import codecs
import re
import random

language = sys.argv[1]
split = sys.argv[2]

############# Select module grouping #############
# Group consecutive modules for the same system or call each module separately.
# Select 'no' to get all intermediate representations, 'yes' if you're only interested in the output.
group_modules_prm = sys.argv[3]

# Modules to run, with type of processing (FORGe, Model1, SimpleNLG, etc.).
# Only FORGe is supported for this prototype version.
# What if a module spans over several of these?
PredArg_Normalisation = sys.argv[4]
PredArg_AggregationMark = sys.argv[5]
PredArg_Aggregation = sys.argv[6]
PredArg_PoSTagging = sys.argv[7]
PredArg_CommStructuring = sys.argv[8]
DSynt_Structuring = sys.argv[9]
SSynt_Structuring = sys.argv[10]
SSynt_Aggregation = sys.argv[11]
RE_Generation = sys.argv[12]
DMorph_AgreementsLinearisation = sys.argv[13]
SMorph_Processing = sys.argv[14]
# Define all micro modules and several higher level modules that can overlap, the highest level being the one-shot generation.
#Surface_Generation = 'IMS' # That could take DSynt/SSynt as input and return text; to be defined during the query processing

# Paths to FORGe/MATE folders and property files
FORGe_input_folder = sys.argv[15]
path_MATE = sys.argv[16]
path_props_resources_template = sys.argv[17]
path_props_levels = sys.argv[18]
path_props = sys.argv[19]

# Paths to general folders
# The input structure(s) of the correct type should be placed in the folder that corresponds to the first module called in the next cell
str_PredArg_folder = sys.argv[20]
str_PredArgNorm_folder = sys.argv[21]
str_PredArgAggMark_folder = sys.argv[22]
str_PredArgAgg_folder = sys.argv[23]
str_PredArgPoS_folder = sys.argv[24]
str_PredArgComm_folder = sys.argv[25]
str_DSynt_folder = sys.argv[26]
str_SSynt_folder = sys.argv[27]
str_SSyntAgg_folder = sys.argv[28]
str_REG_folder = sys.argv[29]
str_DMorphLin_folder = sys.argv[30]
str_SMorphText_folder = sys.argv[31]

log_folder = sys.argv[32]


# The elements of this list are referenced from several places in the code
# When updating list, update process_input function!
#                 0             1               2                3             4            5            6        7          8        9         10          11
level_names = ['PredArg', 'PredArgNorm', 'PredArgAggMark', 'PredArgAgg', 'PredArgPoS', 'PredArgComm', 'DSynt', 'SSynt', 'SSyntAgg', 'REG', 'DMorphLin', 'SMorphText']

# Static - Description of RGB modules (FORGe)
# Also add dicos here to save some time when loading resources
PredArg0_dict = {'input': ['Init'], 'grammars': []}
PredArg1_Normalisation_dict = {'input': [level_names[0]], 'grammars': ['10_Con_Sem.rl']}
PredArg2_Aggregation_dict = {'input': [level_names[1], level_names[2]], 'grammars': ['11.1_Con_Agg1.rl', '11.2_Con_Agg2.rl', '11.3_Con_Agg3.rl', '11.4_Con_Agg4.rl']}
PredArg3_PoSTagging_dict = {'input': [level_names[1], level_names[3]], 'grammars': ['13_Sem_SemPoS.rl']}
PredArg4_CommStructuring_dict = {'input': [level_names[4]], 'grammars': ['15_SemPoS_SemCommMark.rl', '17_SemCommMark_SemComm.rl']}
DSynt_Structuring_dict = {'input': [level_names[5]], 'grammars': ['20_SemComm_DSynt.rl']}
SSynt_Structuring_dict = {'input': [level_names[6]], 'grammars': ['30_DSynt_SSynt.rl', '35_SSynt_PostProc.rl']}
SSynt_Aggregation_dict = {'input': [level_names[7]], 'grammars': ['37.1_SSynt_Agg1.rl', '37.2_SSynt_Agg2.rl']}
REG_dict = {'input': [level_names[7], level_names[8]], 'grammars': ['38.1_SSynt_REG1.rl', '38.2_SSynt_REG2.rl']}
DMorph_AgreementsLinearisation_dict = {'input': [level_names[7], level_names[8], level_names[9]], 'grammars': ['40_SSynt_DMorph_linearize.rl']}
SMorph_Processing_dict = {'input': [level_names[10]], 'grammars': ['50_DMorph_SMorph.rl', '60_Smorph_Sentence.rl']}

# Static - Description of RGB dicos (FORGe)
dic_common_list = ['EN_control.dic', 'concepticon.dic', 'EN_lexicon_MS.dic', 'project_KRISTINA.dic']
dic_indep_list = ['language_info.dic', 'lexicon.dic', 'semanticon.dic', 'morphologicon.dic']
# If a lexicon.dic, semanticon.dic or morphologicon.dic has something else in the name beyond the language prefix, put in this dictionary
dic_special_name_dico = {'EN_lexicon.dic':'EN_lexicon_SMALL.dic'}


class RGBModule:
  "Class to store information related to the RGB modules"
  def __init__(self, module, system, dico_module, in_folder, out_folder):
    self.module_type = 'RGB'
    self.system = system
    self.output = str(module)
    self.inputs = dico_module.get('input')
    self.grammars = dico_module.get('grammars')
    self.input_folder = in_folder
    self.output_folder = out_folder

def clear_files(folder):
  "Function to clear files from a folder."
  if os.path.exists(folder) and os.path.isdir(folder):
    for filename in os.listdir(folder):
      file_path = os.path.join(folder, filename)
      try:
        if os.path.isfile(file_path) or os.path.islink(file_path):
          os.unlink(file_path)
        elif os.path.isdir(file_path):
          shutil.rmtree(file_path)
      except Exception as e:
        print('Failed to delete %s. Reason: %s' % (file_path, e))

def clear_folder(folder):
  "Function to clear whole folders."
  if os.path.exists(folder) and os.path.isdir(folder):
    for subfolder in os.listdir(folder):
      folder_path = os.path.join(folder, subfolder)
      if os.path.isdir(folder_path):
        try:
          shutil.rmtree(folder_path)
        except Exception as e:
          print('Failed to delete %s. Reason: %s' % (folder, e))

def rename_files(folder, output_type):
  "Function that renames files into more a human-friendly format."
  str_folder_content = os.listdir(folder)
  for filename in str_folder_content:
    filepath_to_change = os.path.join(folder, filename)
    filename_extension = filename.rsplit('.', 1)[1]
    filename_noExt = filename.rsplit('.', 1)[0]
    clean_filename_noExt = filename_noExt.rsplit('__')[0]
    new_filename = clean_filename_noExt+'__'+output_type+'.'+filename_extension
    new_filepath = os.path.join(folder, new_filename)
    os.rename(filepath_to_change, new_filepath)

def copy_files(pathIn, pathOut):
  "Function to copy files into the folder they need to be in to be processed."
  #print(pathIn)
  str_folder_content = os.listdir(pathIn)
  for content in str_folder_content:
    target_path = os.path.join(pathIn, content)
    # If files are found in the folder, copy files to FORGe's input folder
    if os.path.isfile(target_path):
      shutil.copy(target_path, pathOut)
    # If folders are found in the folder, explore them to get to the files
    elif os.path.isdir(target_path):
      str_subfolder_content = os.listdir(target_path)
      for deeper_content in str_subfolder_content:
        new_target_path = os.path.join(target_path, deeper_content)
        if os.path.isfile(new_target_path):
          shutil.copy(new_target_path, pathOut)

def check_pipeline(list_modules):
  "Function that finds the first structure to be processed by the pipeline."
  output_str = []
  input_str = []
  init_str = []
  for module_object in list_modules:
    # Output_str is a string
    output_str.append(module_object.output)
    # Input_str is a list that contains one or more elements
    input_str.append(module_object.inputs)
  for list_input_level in input_str:
    list_seen = []
    # For a given module, check for how many input types we find a corresponding structure to process
    for unique_input_level in list_input_level:
      if unique_input_level in output_str:
        list_seen.append(unique_input_level)
    # If none of the candidate input types is found, the module is the first to apply in the pipeline
    if len(list_seen) == 0:
      init_str.append(list_input_level)
  # If there is only one list of candidate inputs, that's OK, but if there is none or several, it means the pipeline is wrong.
  if len(init_str) == 1:
    print('  -> Initial structure is '+str(init_str[0])+'.')
    return(init_str[0])
  else:
    print('! ERROR! Hole in the pipeline, several possible first modules, or mapping not defined in "process_query" function for a system ('+str(len(init_str))+' initial representations found: '+str(init_str)+').')
    exit()

def define_module_sequence(list_modules):
  "Function that creates all possible module sequences and returns the one that include all modules"
  candidate_output_sequence_list = []
  # Find first module to apply
  for module_object in list_modules:
    # At this point we made sure that only one module expects the initial structure type (see check_pipeline function)
    if module_object.inputs == list_initial_str:
      candidate_output_sequence_list.append([module_object.output])

  # Creates all possible sequences of modules and saves them as lists
  for candidate_output_sequence in candidate_output_sequence_list:
    for module_object in list_modules:
      for input_type in module_object.inputs:
        if input_type == candidate_output_sequence[-1]:
          new_candidate_output_sequence_list = candidate_output_sequence.copy()
          new_candidate_output_sequence_list.append(module_object.output)
          # Update initial list to keep the loop going
          candidate_output_sequence_list.append(new_candidate_output_sequence_list)
  # Look for the longest sequence of modules
  best_candidate_sequence = []
  for candidate_output_sequence in candidate_output_sequence_list:
    if len(candidate_output_sequence) > len(best_candidate_sequence):
      best_candidate_sequence = candidate_output_sequence
  return(best_candidate_sequence)

def group_modules(module_sequence, list_modules):
  "Groups consecutive modules that are run by the same system. module_sequence is a list of strings, list_modules a list of objects of class 'module'"
  # Let's make a list that will contain X lists for X different system sub-pipelines; the system name is the first element of each list, the second element is another list that contains the module object.
  # grouped_modules looks like this: [['SystemName1', [<Module1-Object>, <Module2-Object>]], ['SystemName2', [<Module3-Object>, <Module4-Object>]]]
  grouped_modules = []
  # the elements in module_sequence are in order of execution
  for output_level in module_sequence:
    for module_object in list_modules:
      if output_level == module_object.output:
        # Check that the first element of the last list is not the same as the currently examined object's system
        if len(grouped_modules) > 0:
          if len(grouped_modules[-1]) > 0:
            if grouped_modules[-1][0] == module_object.system:
              # If the last list has the same system name as the current object, add the object to the group
              grouped_modules[-1][1].append(module_object)
            else:
              # Otherwise create the next list for the new system
              grouped_modules.append([module_object.system, [module_object]])
          else:
            grouped_modules.append([module_object.system, [module_object]])
        else:
          grouped_modules.append([module_object.system, [module_object]])
  return(grouped_modules)

def create_grouped_module_objects_FORGe(system_modules):
  "Creates a new object of class RGB module that combines the consecutive modules. system_modules contains at least 2 modules."
  first_module = system_modules[0]
  last_module = system_modules[-1]
  grammars_list = []
  for module in system_modules:
    grammars_list = grammars_list + module.grammars
  grouped_dico = {'input': [first_module.inputs], 'grammars': grammars_list}
  grouped_module = RGBModule(last_module.output, 'FORGe', grouped_dico, first_module.input_folder, last_module.output_folder)
  return(grouped_module)

# def check_pipeline(modules, list_init_str):
# #  "Checks if there are holes in the pipeline (i.e. if an expected input structure is not provided by any other module. Is this one usefule now? CF find_initial_structure."
#   list_outputs = []
#   # build list of all outputs pruduced by the different modules
#   for module in modules:
#     if module.output not in list_outputs:
#       list_outputs.append(module.output)
#   # check that each module takes as input at least one of the outputs of the other modules
#   for module in modules:
#     list_input_seen = []
#     for input in module.inputs:
#       if input in list_outputs or input in list_init_str:
#        list_input_seen.append(input)
#     if len(list_input_seen) == 0:
#      print('ERROR! Incomplete pipeline: there will be no available '+str(input)+' structure (required by '+str(module.output)+' module).')
#      exit()

def process_query(list_modules, PredArg_Normalisation, PredArg_AggregationMark, PredArg_Aggregation, PredArg_PoSTagging, PredArg_CommStructuring, DSynt_Structuring, SSynt_Structuring, SSynt_Aggregation, RE_Generation, DMorph_AgreementsLinearisation, SMorph_Processing):
  "Function to parse the input parameters and prepare the generation pipeline"
  # For each module, create an object with all the relevant class info (module_name, system, dico_module, in_folder, out_folder)
  if PredArg_Normalisation == 'FORGe':
    PredArg_Normalisation_RGB = RGBModule(level_names[1], 'FORGe', PredArg1_Normalisation_dict, str_PredArg_folder, str_PredArgNorm_folder)
    list_modules.append(PredArg_Normalisation_RGB)
  else:
    pass
  if PredArg_AggregationMark == 'FORGe':
    pass
  else:
    pass
  if PredArg_Aggregation == 'FORGe':
    PredArg_Aggregation_RGB = RGBModule(level_names[3], 'FORGe', PredArg2_Aggregation_dict, str_PredArgNorm_folder, str_PredArgAgg_folder)
    list_modules.append(PredArg_Aggregation_RGB)
    if PredArg_PoSTagging == 'FORGe':
      PredArg_PoSTagging_RGB = RGBModule(level_names[4], 'FORGe', PredArg3_PoSTagging_dict, str_PredArgAgg_folder, str_PredArgPoS_folder)
      list_modules.append(PredArg_PoSTagging_RGB)
    elif PredArg_PoSTagging == 'HiddenFORGe':
      PredArg_PoSTagging_RGB = RGBModule(level_names[4], 'HiddenFORGe', PredArg3_PoSTagging_dict, str_PredArgAgg_folder, str_PredArgPoS_folder)
      list_modules.append(PredArg_PoSTagging_RGB)
    else:
      pass
  elif PredArg_PoSTagging == 'FORGe':
    PredArg_PoSTagging_RGB = RGBModule(level_names[4], 'FORGe', PredArg3_PoSTagging_dict, str_PredArgNorm_folder, str_PredArgPoS_folder)
    list_modules.append(PredArg_PoSTagging_RGB)
  else:
    pass
  if PredArg_CommStructuring == 'FORGe':
    PredArg_CommStructuring_RGB = RGBModule(level_names[5], 'FORGe', PredArg4_CommStructuring_dict, str_PredArgPoS_folder, str_PredArgComm_folder)
    list_modules.append(PredArg_CommStructuring_RGB)
  elif PredArg_CommStructuring == 'HiddenFORGe':
    PredArg_CommStructuring_RGB = RGBModule(level_names[5], 'HiddenFORGe', PredArg4_CommStructuring_dict, str_PredArgPoS_folder, str_PredArgComm_folder)
    list_modules.append(PredArg_CommStructuring_RGB)
  else:
    pass
  if DSynt_Structuring == 'FORGe':
    DSynt_Structuring_RGB = RGBModule(level_names[6], 'FORGe', DSynt_Structuring_dict, str_PredArgComm_folder, str_DSynt_folder)
    list_modules.append(DSynt_Structuring_RGB)
  else:
    pass
  if SSynt_Structuring == 'FORGe':
    SSynt_Structuring_RGB = RGBModule(level_names[7], 'FORGe', SSynt_Structuring_dict, str_DSynt_folder, str_SSynt_folder)
    list_modules.append(SSynt_Structuring_RGB)
  else:
    pass
  # Agg + REG + Lin
  if SSynt_Aggregation == 'FORGe':
    SSynt_Aggregation_RGB = RGBModule(level_names[8], 'FORGe', SSynt_Aggregation_dict, str_SSynt_folder, str_SSyntAgg_folder)
    list_modules.append(SSynt_Aggregation_RGB)
    # Agg + REG + Lin
    if RE_Generation == 'FORGe':
      REG_RGB = RGBModule(level_names[9], 'FORGe', REG_dict, str_SSyntAgg_folder, str_REG_folder)
      list_modules.append(REG_RGB)
      # Agg + REG + Lin
      if DMorph_AgreementsLinearisation == 'FORGe':
        DMorph_AgreementsLinearisation_RGB = RGBModule(level_names[10], 'FORGe', DMorph_AgreementsLinearisation_dict, str_REG_folder, str_DMorphLin_folder)
        list_modules.append(DMorph_AgreementsLinearisation_RGB)
      else:
        pass
    # Agg + Lin
    elif DMorph_AgreementsLinearisation == 'FORGe':
      DMorph_AgreementsLinearisation_RGB = RGBModule(level_names[10], 'FORGe', DMorph_AgreementsLinearisation_dict, str_SSyntAgg_folder, str_DMorphLin_folder)
      list_modules.append(DMorph_AgreementsLinearisation_RGB)
    else:
      pass
  # REG + Lin
  elif RE_Generation == 'FORGe':
    REG_RGB = RGBModule(level_names[9], 'FORGe', REG_dict, str_SSynt_folder, str_REG_folder)
    list_modules.append(REG_RGB)
    # REG + Lin
    if DMorph_AgreementsLinearisation == 'FORGe':
      DMorph_AgreementsLinearisation_RGB = RGBModule(level_names[10], 'FORGe', DMorph_AgreementsLinearisation_dict, str_REG_folder, str_DMorphLin_folder)
      list_modules.append(DMorph_AgreementsLinearisation_RGB)
  # Lin
  elif DMorph_AgreementsLinearisation == 'FORGe':
    DMorph_AgreementsLinearisation_RGB = RGBModule(level_names[10], 'FORGe', DMorph_AgreementsLinearisation_dict, str_SSynt_folder, str_DMorphLin_folder)
    list_modules.append(DMorph_AgreementsLinearisation_RGB)
  else:
    pass
  if SMorph_Processing == 'FORGe':
    SMorph_Processing_RGB = RGBModule(level_names[11], 'FORGe', SMorph_Processing_dict, str_DMorphLin_folder, str_SMorphText_folder)
    list_modules.append(SMorph_Processing_RGB)
  else:
    pass

def process_files_FORGe(module_object):
  "Function to call FORGe to process an input of level X and create an output of level Y"
  "The function must be called process_files_SystemName"

  # Erase files from input folder
  # print('  Cleared input folder...')
  clear_files(FORGe_input_folder)

  # Generate mate.properties file, which points to the resources to apply
  # print('  Generated mate.properties file...')
  input_folder_gen = module_object.input_folder
  output_folder_gen = module_object.output_folder
  grammars = module_object.grammars
  # Create list of dictionaries for generation
  dic_resources_list = []
  dic_resources_list.extend(dic_common_list)
  # Lang. info, Lexicon, semanticon, morphologicon
  # We add the language-specific prefix and check if there's a special name for this dico
  for dic_name in dic_indep_list:
    lspec_dic_name = language+'_'+dic_name
    if lspec_dic_name in dic_special_name_dico:
      dic_resources_list.append(dic_special_name_dico.get(lspec_dic_name))
    else:
      dic_resources_list.append(lspec_dic_name)

  # Delete existing property file
  if os.path.exists(path_props):
    os.remove(path_props)

  # Read template to create a new file
  prop_template = open(path_props_resources_template, 'r')
  lines_prop_template = prop_template.readlines()

  # Create a new property file
  with codecs.open(path_props, 'w', 'utf-8') as f:
    for line in lines_prop_template:
      if line.startswith('projectDir='):
        project_dir = FORGe_input_folder.rsplit('/', 1)[0]
        f.write('projectDir='+str(project_dir)+'\n')
      elif line.startswith('resources='):
        f.write('resources=')
        x = 0
        # All but last dico are followed by a comma
        while x < len(dic_resources_list) - 1:
          f.write(dic_resources_list[x])
          f.write(', ')
          x = x + 1
        # Last dico is followed by a linebreak
        if x == len(dic_resources_list) - 1:
          f.write(dic_resources_list[x])
          f.write('\n')
      elif line.startswith('ruleSets='):
        f.write('ruleSets=')
        x = 0
        while x < len(grammars) - 1:
          f.write(grammars[x])
          f.write(', ')
          x = x + 1
        if x == len(grammars) - 1:
          f.write(grammars[x])
          f.write('\n')
      elif line.startswith('outputDir='):
        f.write('outputDir='+output_folder_gen+'\n')
      elif line.startswith('generateText='):
        if output_folder_gen == str_SMorphText_folder:
          f.write('generateText=true'+'\n')
        else:
          f.write('generateText=false'+'\n')
      else:
        f.write(line)
  f.close()

  # Copy files into input folder
  # print('  Copied files to input folder...')
  copy_files(input_folder_gen, FORGe_input_folder)

  # Rename files
  # print('  Renamed files in input folder...')
  rename_files(FORGe_input_folder, module_object.output)

  # Run generator
  print('  Running '+str(module_object.grammars)+' on files in '+str(module_object.input_folder)+'...')
  with open(os.path.join(log_folder, 'log.txt'), 'a') as logfile:
    #proc = subprocess.Popen(['java', '-Xmx1g', '-jar', 'buddy-core-0.1.1-en.jar', os.path.join(surfOutTmp,f), '-o', deepOutTmp], stdout = subprocess.PIPE, universal_newlines=True)
    proc = subprocess.run(['java', '-Xmx1g', '-jar', path_MATE, path_props, path_props_levels], stdout = subprocess.PIPE, universal_newlines=True)
    for line in proc.stdout:
      #sys.stdout.write(line)
      logfile.write(line)

  # Save intermediate log files
  new_logname = 'log_'+str(module_object.output)+'.txt'
  shutil.move(os.path.join(log_folder, 'log.txt'), os.path.join(log_folder, new_logname))

def process_files_HiddenFORGe(module_object):
  "Fake function to test the use of several systems in the pipeline"
  "The function must be called process_files_SystemName"
  process_files_FORGe(module_object)
  
  
# Erase files from output folders
# print('Clearing output folders...')
clear_folder(str_PredArgNorm_folder)
clear_folder(str_PredArgAggMark_folder)
clear_folder(str_PredArgAgg_folder)
clear_folder(str_PredArgPoS_folder)
clear_folder(str_PredArgComm_folder)
clear_folder(str_DSynt_folder)
clear_folder(str_SSynt_folder)
clear_folder(str_SSyntAgg_folder)
clear_folder(str_REG_folder)
clear_folder(str_DMorphLin_folder)
clear_folder(str_SMorphText_folder)
clear_files(log_folder)

# Fill list_modules with module descriptions as objects of a particular Class (e.g. RGB), each of them with associated properties (e.g. input/output types and folders, grammars, etc.)
print('Preparing generation pipeline...')
list_modules = []
process_query(list_modules, PredArg_Normalisation, PredArg_AggregationMark, PredArg_Aggregation, PredArg_PoSTagging, PredArg_CommStructuring, DSynt_Structuring, SSynt_Structuring, SSynt_Aggregation, RE_Generation, DMorph_AgreementsLinearisation, SMorph_Processing)

# Just to make sure the code doesn't depend on the nice order of the list (currently the order established in the process_query function)
random.shuffle(list_modules)

# Find which structure the pipeline starts with, and check for holes in pipeline at the same time
list_initial_str = check_pipeline(list_modules)
print('  -> '+str(len(list_modules))+' modules were selected.')

# Find module sequence that includes all required modules in the right order
module_sequence = define_module_sequence(list_modules)
print('  -> Sequence: '+str(module_sequence))
if len(list_modules) == len(module_sequence):
  print('  -> The pipeline looks good, proceeding...')
else:
  print('! Possible ERROR! There are '+str(len(list_modules))+' modules selected and the longest module sequence found is '+str(len(module_sequence))+'.')

# Break pipeline by system, so we can make one call per system instead of one call per module.
modules_to_process = group_modules(module_sequence, list_modules)

# Run each (sequence of) module(s) with the desired system
# One instance of modules to process looks like that: [['SystemName1', [<Module1-Object>, <Module2-Object>]], ['SystemName2', [<Module3-Object>, <Module4-Object>]], ...]
# globals()[function_name] allow for calling a function using a string
for system_modules in modules_to_process:
  function_name = 'process_files_'+system_modules[0]
  print('--------------------------')
  print('Running '+system_modules[0])
  print('--------------------------')
  if len(system_modules[1]) > 1:
    if group_modules_prm == 'yes':
      grouped_module_object = create_grouped_module_objects_FORGe(system_modules[1])
      globals()[function_name](grouped_module_object)
    else:
      for module_object in system_modules[1]:
        print("Processing module #"+str(system_modules[1].index(module_object)))
        globals()[function_name](module_object)
  else:
    globals()[function_name](system_modules[1][0])

print('=================================================')
print('All done!')
