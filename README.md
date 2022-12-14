# M-FleNS_NLG-Pipeline

## Introduction
This generation pipeline takes predicate-argument structures as input and returns text. It currently covers datasets such as WebNLG (English, Spanish), E2E (English) and Rotowire (English); inputs from these datasets need to be mapped to predicate-argument structures (code for conversions will be released in the near future). The pipeline is made of a series of modules:

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
1. Go to M_FleNS_pipe_release.ipynb and open the project in Colab.
2. Run the first cell to download and unzip the working folder.
3. Run the second cell to install java 8 on the Colab server.
4. Run the third cell.
5. Edit the parameters of the fourth cell (**PARAMETERS FOR GENERATION**) if needed; see Parameters below.
6. Run the fourth cell.
7. Gather the outputs in the */content/FORGe/structures* folder.

In each subfolder of the */content/FORGe/structures* folder, intermediate representations are saved in the native **.str** format (conversion to CoNLL to be released); the output texts can be found in the */content/FORGe/structures/11-SMorphText* subfolders with the **.txt** extension.

## Input specifications
TBD.

Sample input structures are provided in the */content/FORGe/structures/00-PredArg* folder.

## Parameters
There are two types of parameters: (1) system assignment for each module, and (2) grouping or not of modules.

1. **System assignment**: this allows to call different systems for each module; in v0.1, only FORGe can be called, and two modules are not separated yet (PredArg_AggregationMark and RE_Generation).

- PredArg_Normalisation = 'FORGe'
- PredArg_AggregationMark = ''
- PredArg_Aggregation = 'FORGe'
- PredArg_PoSTagging = 'FORGe'
- PredArg_CommStructuring = 'FORGe'
- DSynt_Structuring = 'FORGe'
- SSynt_Structuring = 'FORGe'
- SSynt_Aggregation = 'FORGe'
- RE_Generation = ''
- DMorph_AgreementsLinearisation = 'FORGe'
- SMorph_Processing = 'FORGe'

2. **Module grouping**: 
- group_modules_prm = 'yes', the pipeline will group the consecutive modules of the same system and will save only the output of each system without intermediate representations; this allows for faster generation.
- group_modules_prm = 'no', the pipeline will apply all modules separately whatever system is called and generate all intermediate representations; this makes the generation slower.
