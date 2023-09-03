# M-FleNS_NLG-Pipeline

## Introduction
This generation pipeline takes predicate-argument structures as input and returns text. It currently covers datasets such as WebNLG (English, Spanish, Irish), E2E (English) and Rotowire (English); inputs from these datasets need to be mapped to predicate-argument structures (code for conversions will be released in the near future). The pipeline is made of a series of modules:

- **Normalisation of the input**: enriches/corrects the input;
- **Sentence packaging**: aggregates isolated input facts into more complex semantic graphs;
- **Lexicalisation**: chooses words to use in the target language and retrieves PoS tags;
- **Communicative structure marking**: selects what each sentence talks about and what is said about it;
- **Deep sentence structuring**: creates a deep-syntactic structure of each sentence with abstract language-independent syntactic relations that link meaning-bearing words;
- **Surface sentence structuring**: creates a surface-syntactic structure of each sentence with language-specific syntactic relations that link all words (function words are introduced)
- **Syntactic aggregation**: merges sentences based on their syntactic structures (mostly via coordinations);
- **Referring expression Generation**: introduces intra- and inter-sentence pronouns and other referring expressions (currently part of the next module);
- **Linearisation and morphological agreement resolution**: resolves word order and marks nodes for inflection;
- **Inflection and morphological interactions resolution**: retrieves/generates the final form of the words.

## Quick start for running pipeline on Colab
1. Go to M-FleNS-pipe.ipynb and open the project in Colab.
2. Run the first two cells to download and unzip the working folder, and install java 8 on the Colab server.
3. Set parameters: **Edit the parameters** of the third cell if needed (see Parameters below) and run the third cell.
4. Static parameters and functions: Run the fourth cell.
5. Main code: Run the fifth cell.
6. Gather the outputs in the */content/FORGe/structures* folder.
7. (Optional) Check outputs: You can run the sixth cell to check if the number of output texts matches the number of input structures.
8. (Optional) Zip output folder to download: You can run the seventh cell to compress the output folder for easy download.

In each subfolder of the */content/FORGe/structures* folder, intermediate representations are saved in the native **.str** format (conversion to CoNLL to be released); the output texts can be found in the */content/FORGe/structures/11-SMorphText* subfolders with the **.txt** extension.

## Input specifications
TBD.

A sample input file for English is provided: */content/FORGe/201005_dev_4tr_sml_EN.conll*.

## Parameters
There are three types of parameters: (1) language, (2) grouping or not of modules, and (3) system assignment for each module.

1. **Language**: 
- language = *, make sure the language is supported by the current versino of the system and that you have appropriate inputs. 

2. **Module grouping**: 
- group_modules_prm = 'yes', the pipeline will group the consecutive modules of the same system and will save only the output of each system without intermediate representations; this allows for faster generation.
- group_modules_prm = 'no', the pipeline will apply all modules separately whatever system is called and generate all intermediate representations, but this makes the generation slower.
 
3. **System assignment**: this allows to call different systems for each module; in v2.0, only FORGe can be called.

- PredArg_Normalisation = 'FORGe'
- PredArg_AggregationMark = ''
- PredArg_Aggregation = 'FORGe'
- PredArg_PoSTagging = 'FORGe'
- PredArg_CommStructuring = 'FORGe'
- DSynt_Structuring = 'FORGe'
- SSynt_Structuring = 'FORGe'
- SSynt_Aggregation = 'FORGe'
- RE_Generation = FORGe''
- DMorph_AgreementsLinearisation = 'FORGe'
- SMorph_Processing = 'FORGe'

