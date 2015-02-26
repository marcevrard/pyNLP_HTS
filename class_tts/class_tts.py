#!/bin/env python3
#-*- encoding: utf-8 -*-

import importlib
# import os.path
# from collections import namedtuple

#import tts_const as cst                                # Module call integrated into the class __init__ for portability

from class_tts import Phonetizer
from class_tts import PfsExtractorHts
from class_tts import TextFeatures


#======================================================================================================================#
class Tts:
    """
    TTS base Class.
    """
    def __init__(self, param_module, ph_dic='lia'):
        """
        Initializes, gives the absolute path of the files to process and give parameters.
        """
        self.cst = importlib.import_module(param_module)
        # TODO: change cst to global and remove all the 'self._' version in the init? Also replace 'self._' > 'cst.'

        # self.fpath_out = None
        # self.utt_txt = ''

        self.param_module = param_module
        self.ph_dic = ph_dic

        self.utt_total_mix = None

        self.phonetizer_obj = None

# self.utt_total_mix = self.phonetizer_obj.utt_total_mix  # QQ: means PfsExtr() connected to Phonem()? Better way?

        # self.pfs_xtr_obj = None         # PfsExtractor(utt_total_mix, param_module)
        # self.pfs_xtr_mary_obj = None    # PfsExtrMary(utt_total_mix, param_module)
        self.pfs_xtr_hts_obj = None     # PfsExtrHts(utt_total_mix, param_module)

        self.hts_lab_gen_prn = []

# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =#

    def process_phonetize(self, txt_fpath):
        """
        Launch the complete TTS synthesis process.
        """
        # Input text loaded with self.load_input_text() from the main() in the run file.

        self.phonetizer_obj = Phonetizer(self.param_module, txt_fpath, self.ph_dic)    # phonetizer_obj INITIALIZATION

        self.phonetizer_obj.phonetize_txt_utt()                 # generate list with phonetized elmts (1 token / elmt)
        self.phonetizer_obj.tag_pos_utt()                       # tag phonetic tokens pos

        self.phonetizer_obj.tokenize_el_utt()                   # tokenize ph and syll from phonetized tokens
        self.phonetizer_obj.tokenize_phrases()                  # tokenize utt in sentences in phrases
        self.phonetizer_obj.label_prosody_utt()                 # label the phrase according to syntax

        # convert nested total mixed into flat list
        # self.pfs_xtr_mary_obj.conv_totalmix_flat_lst(self.phonetizer_obj.utt_total_mix) TODO > in __init__?

    def process_phonetize_hts(self, txt_fpath, style=''):
        """
        Launch the complete TTS synthesis process through the HTS interface.
        """
        self.process_phonetize(txt_fpath)
        self.utt_total_mix = self.phonetizer_obj.utt_total_mix

        self.pfs_xtr_hts_obj = PfsExtractorHts(self.param_module, self.utt_total_mix)

        self.pfs_xtr_hts_obj.process_pfeats_extr(style)

        self.pfs_xtr_hts_obj.gen_hts_lab_fts()
        self.hts_lab_gen_prn = self.pfs_xtr_hts_obj.hts_lab_gen_prn

    def process_synthesize_hts(self, txt_fpath, style=''):
        """
        Launch the complete TTS synthesis process through the HTS interface.
        """
        self.process_phonetize(txt_fpath)

        # self.pfs_xtr_hts_obj = PfsExtractorHts(self.param_module, self.utt_total_mix)

        # self.pfs_xtr_hts_obj.process_pfeats_extr(style)

        utt_pfs_obj = TextFeatures(self.param_module, self.phonetizer_obj.utt_ph)

        utt_pfs_obj.process_pfeats(style)

        utt_pfs_obj.process_lab_prn_gen()

        self.hts_lab_gen_prn = utt_pfs_obj.hts_lab_gen_prn

        # self.pfs_xtr_hts_obj.gen_hts_lab_fts()
        # self.hts_lab_gen_prn = self.pfs_xtr_hts_obj.hts_lab_gen_prn

#======================================================================================================================#
