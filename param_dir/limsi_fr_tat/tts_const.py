#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os.path

import my_defs.defs_list as lst


#   ====================================================================================================================
# TTS constants

PARAM_PATH = os.path.dirname(os.path.realpath(__file__))
PYTTS_PATH = os.path.join(PARAM_PATH, os.pardir, os.pardir)
CONF_PATH = os.path.join(PARAM_PATH, 'conf_files')
_HTS_BKP_FILES_DIR = 'hts_bkp_files/'

_GP_FNAME = 'seltts'
GP_OPTION_LIA = '-s abcdefhj -f'
GP_OPT_SYLL_LIA = '-s hj -f'
GP_OPTION_SAMPA = '-s abcdefhk -f'
GP_OPT_SYLL_SAMPA = '-s hk -f'
_POS_FPATH = os.path.join(CONF_PATH, 'pos_labels.txt')
POS_LABELS = lst.conv_csv_to_ntpl(_POS_FPATH, 'PosLabelsTpl', delimit='\t')
PUNCT = ',.!?'                                                          # All punctuations
PUNCT_END = '.!?...'                                                    # End of sentence punctuations
PUNCT_PHRASE = ',)(;:'                                                  # End of phrase punctuations
PUNCT_TO_DEL = ')'                                                      # Punctuation not to take into account (to del)
PUNCT_CONV_COMA = ')(;:'                                                # Punctuation to convert to a coma
PUNCT_CONV_PERIOD = '...'                                               # Punctuation to convert to a point
PUNCT_ALL = PUNCT + PUNCT_TO_DEL + PUNCT_CONV_COMA + PUNCT_CONV_PERIOD
# TODO: clarify punctuation categories for normalization

FS = 16000
PHONE = 'phone'
PAU = 'pau'                                                     # Phonetic marker for pause, note: change also in ph_set
SSIL = 'ssil'                                                   # Phonetic marker for short silence, note: idem
NULL_VAL = 'x'                                                  # Usually '0'
NUMBER_PHONES = 5                                               # 1: current, 3: current + next/prev, 5...

PH_SET_FPATH = os.path.join(CONF_PATH, 'allophones.fr.xml')
_HMM_FTS_VAL_INVENTORY_FPATH = os.path.join(CONF_PATH, 'hmm_fts_val_inventory.txt')
_PH_FTS_FPATH = os.path.join(CONF_PATH, 'ph_features.txt')
_USED_HMM_FTS_FPATH = os.path.join(CONF_PATH, 'used_hmm_features.txt')
_ALL_HMM_FTS_FPATH = os.path.join(CONF_PATH, 'all_hmm_features.txt')
_UTT_HMM_FTS_FPATH = os.path.join(CONF_PATH, 'utt_hmm_features.txt')

PH_FTS_TPL = lst.conv_csv_to_ttpl(_PH_FTS_FPATH)
USED_HMM_FTS_TPL = lst.conv_csv_to_ttpl(_USED_HMM_FTS_FPATH)
UTT_HMM_FTS_TPL = lst.conv_csv_to_ttpl(_UTT_HMM_FTS_FPATH)

# Put phone on top of USED_FTS_TPL
USED_FTS_TPL = (PHONE,) + tuple([name for name in sorted(PH_FTS_TPL + USED_HMM_FTS_TPL)
                                 if name != PHONE])

HMM_FTS_VAL_INVENTORY_LDIC = lst.conv_csv_to_ldic(_HMM_FTS_VAL_INVENTORY_FPATH, delimit='\t')
ALL_HMM_FTS_TPL = tuple(lst.conv_csv_to_ttpl(_ALL_HMM_FTS_FPATH))

ZERO_TO_FIFTY = [str(i) for i in range(51)]					        # Default hmm fts values 0..19

_IPA_CONV_FPATH = os.path.join(CONF_PATH, 't_LPA_LIA.txt')
IPA_CONV_DIC = lst.conv_csv_to_ldic(_IPA_CONV_FPATH, delimit='\t')

if sys.platform.startswith('darwin'):
    _GP_PATH = '/Volumes/Projet/TTS/gp_bin/src/'							# MAC OS X 10.7 mev
elif sys.platform.startswith('linux'):
    _GP_PATH = os.path.expanduser('~/GP/gp_bin/src/')			# Ubuntu LST 12.04 mev
else:
    _GP_PATH = os.getcwd()

GP_F_PATH = os.path.join(_GP_PATH, _GP_FNAME)

_PROSO_LABEL_FPATH = os.path.join(CONF_PATH, 'tobi_fr.txt')
PROSO_LABEL = lst.conv_csv_to_ldic(_PROSO_LABEL_FPATH, '\t')


#   ====================================================================================================================
# TTS Training constants

#   MAIN_PATH = os.path.expanduser('~/Documents/_LIMSI_MEDIA/CORPUS/Corpus_FT/guy_triste')
# TODO: put in main
_IMPORT_LAB_FPATH = os.path.join(CONF_PATH, 'import_lab_fields.txt')
IMPORT_LAB_FIELDS = lst.conv_csv_to_ttpl(_IMPORT_LAB_FPATH)


#   ====================================================================================================================
# TTS Synthesis constants

TXT_FPATH = os.path.join(PYTTS_PATH, 'utt.txt')                         # Raw text to synthezise file path
UTT_FPATH = os.path.join(PYTTS_PATH, 'utt_ph.txt')                      # Phonetized text file path


#   ====================================================================================================================
# TTS MARY Synthesis constants

_MARY_PATH = os.path.expanduser('~/marytts-clone/')
_MARY_EX_PATH = os.path.join(_MARY_PATH, 'user-examples/example-embedded/')
_MARY_EX_FNAME = 'example-embedded-5.1-SNAPSHOT.jar'
MARY_EX_F_PATH = os.path.join(_MARY_EX_PATH, 'target/', _MARY_EX_FNAME)
UTT_XML_F_PATH = os.path.join(_MARY_EX_PATH, 'utt_ph.xml')

XML_START = '<?xml version="1.0" encoding="UTF-8"?>\n' \
            '<maryxml xmlns="http://mary.dfki.de/2002/MaryXML" ' \
            'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="0.5" xml:lang="fr">\n' \
            '<p>\n' \
            '<s>\n'
XML_END = '\n</p>\n</maryxml>'
XML_SEP_S = '\n</s>\n<s>'												# XML maker between phonetized sentences

XML_PRE_WORD = '<t g2p_method="lexicon" ph="'
XML_PRE_PUNCT = '<t pos="$PUNCT">'
XML_POST_PUNCT = '</t>'
XML_CONT_PH = '" pos="content"/>'
XML_FUNC_PH = '" pos="function"/>'


#   ====================================================================================================================
# eHMM

EHMM_PATH = os.path.join(PARAM_PATH, 'ehmm_files')
EHMM_CONF_FPATH = os.path.join(EHMM_PATH, 'ehmm.featSettings')
ALIGN_FNAME = 'ehmm.align'


#   ====================================================================================================================
# SPS file converter

_SPS_FIELDS_FPATH = os.path.join(CONF_PATH, 'fields_sps.txt')
SPS_FIELDS_LST = lst.conv_txt_to_lst(_SPS_FIELDS_FPATH)
