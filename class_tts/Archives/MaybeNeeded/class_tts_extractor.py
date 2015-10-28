#!/bin/env python3
#-*- encoding: utf-8 -*-

import importlib
import xml.etree.ElementTree as Et
import re
import sys

import my_defs.defs_list as Lst


#======================================================================================================================#
class PfsExtractor:
    """
    TTS Synthesis Class.
    """
    def __init__(self, param_mod, utt_total_mix):

        self.cst = importlib.import_module(param_mod)

        # super().__init__(param_mod)                   # ~= super(TtsSynth, self).__init__() => call __init__ from Tts
        self.utt_total_mix = utt_total_mix

        self.ft_idx_ttpl = ()
        self.proc_fts_ldic = {}
        self.ph_set_ddic = {}
        self.fts_val_inventory_ldic = {}
        self.fts_used_val_ldic = {}
        self.ph_set_fts_val_ldic = {}

        # Try if the utt_total_mix is the proper mix nested element or just transfer the val to the utt_ph_lst
        # this allow to transmit the ph list instead of the nested list (in case of weakly labelled input data e.g. sps)
        try:
            self.utt_ph_lst = [
                ph
                for sentence in self.utt_total_mix                  # list (utt_total_mix)
                for phrase in sentence                              # list (sentence)
                for word in phrase['phrase']                        # dict (phrase)
                for syll in word.word                               # namedtuple (word)
                for ph in syll                                      # tuple (syll)
            ]
        except TypeError:
            self.utt_ph_lst = self.utt_total_mix

    def extract_phone_set_xml(self):
        """
        Read the xml phoneset file and return a 2D dict with the values.
        """
        tree_ph_set = Et.parse(self.cst.PH_SET_FPATH)
        root_ph_set = tree_ph_set.getroot()

        ph_set_dlst = []
        for child_ph_set in root_ph_set:
            ph_set_dlst.append(child_ph_set.attrib)

        # Add key name 'phone'
        for phset_dic in ph_set_dlst:
            phset_dic['phone'] = phset_dic['ph']

        # Remove the 'ph' key from the dic row and create a key with its value to hold the corresponding row (ddic)
        # e.g.: [{'ph': 'dd', 'cvox': '+', ...}] > {'dd': {'cvox': '+', ...}}
        self.ph_set_ddic = dict(
            (row.pop('ph'), row) for row in ph_set_dlst
        )

    def proc_ph_set_fts(self):
        """
        Process the input with the phone set features.
        :rtype : dic of list
        """
        for ft in self.ph_set_fts_val_ldic.keys():					# loop through the ft of the phone set value table

            if ft != 'phone':										# exclude the phone key, not to redo its processing

                proc_ft_lst = ['0'] * len(self.proc_fts_ldic['phone'])  	# pre-assign "proc_ft_lst" with utt length

                for i, ph in enumerate(self.proc_fts_ldic['phone']):  	    # look at one utt phone at a time

                    if ft in self.ph_set_ddic[ph].keys():  # lookup phone set value table fts str in ph_set definit. fts

                        proc_ft_lst[i] = self.ph_set_ddic[ph][ft]  	# when found, return its corresponding value

                self.proc_fts_ldic['ph_'+ft] = proc_ft_lst  # refer the list to the output list in the relevant ft key
                # the 'ph_' has been included to match the MaryTTS name standard for ph_set current fts

    def gen_fts_val_inventory(self):
        """
        Generate the 2D dictionary with all the values possible of all the features parameters.
        Default values (from 0 to 19) for some hmm fts are added here.
        """
        # add the val 0..19 to the fts not present in the manually defined values list (self.cst.ALL_FTS_VAL_LDIC)
        hmm_fts_0_19_val_lst = []
        for ft in self.cst.ALL_HMM_FTS_TPL:
            if ft not in self.cst.ALL_FTS_VAL_LDIC.keys():
                hmm_fts_0_19_val_lst.append([ft, self.cst.ZERO_TO_NINETEEN])		# ZERO_TO_NINETEEN

        hmm_fts_019_val_ldic = dict(hmm_fts_0_19_val_lst)

        self.fts_val_inventory_ldic = dict(list(self.ph_set_fts_val_ldic.items()) +
                                           list(self.cst.ALL_FTS_VAL_LDIC.items()) +
                                           list(hmm_fts_019_val_ldic.items()))
        for key in self.fts_val_inventory_ldic.keys():  # Insert a zero in the val lst 1st position if absent
            if self.fts_val_inventory_ldic[key][0] != '0':
                self.fts_val_inventory_ldic[key].insert(0, '0')

    def gen_used_fts_val(self):
        """
        Generate the all the fts and their corresponding val as an ldic.
        """
        fts_used_val_llst = []
        for ft_used in self.cst.USED_FTS_TPL:						    # take ft_used name from the list

            for ft_class in self.fts_val_inventory_ldic.keys():		# take ft_class from the list of the ft values

                if ft_class in ft_used:  # check if ft_used belongs to ft "class" (ft_class str included in ft_used)
                                                                    # create lst with ft names and val
                    fts_used_val_llst.append([ft_used, self.fts_val_inventory_ldic[ft_class]])

        self.fts_used_val_ldic = dict(fts_used_val_llst)			    # convert into a dic of lists

# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =#
    def process_static_hmm_data(self):
        """
        Prepare the static data used for the extraction.
        """
        self.extract_phone_set_xml()

        self.ph_set_fts_val_ldic = Lst.get_2d_dic_items(self.ph_set_ddic)

        # Get the fts_val_dic out of the 2 dics
        self.gen_fts_val_inventory()

        # Get all used fts
        self.gen_used_fts_val()

#== = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =#
    # TODO: apply to all cases (also to the recalc def)
    def proc_prv_nxt_fts(self, ft, nul_val='0', deg=1, ft_base='', prv='prev_', nxt='next_'):
        """
        Process the prev/next (up to the 2nd degree) of a column in a list of dic or a list of list.
        Return a dic with the processed columns.
        :param ft: key name of the column to process (if str => ldic, if int => llst).
        :param nul_val: value used to fill the outer space in the processed lists.
        :param deg: to how many degree (~=times) the prev/next values need to be process (default = 1).
        :param ft_base: name used to build the key to the output dic for the prev/next values (default = key).
        :param prv: name used to build the key to the output dic for the prev values (default = 'prev_').
        :param nxt: name used to build the key to the output dic for the next values (default = 'next_').
        """
        if ft_base is '':  # default name to use for the output == key
            ft_base = ft

        data = self.proc_fts_ldic[ft]
        data_prv, data_nxt = data.copy(), data.copy()
        data_prv.insert(0, nul_val)
        data_prv.pop()
        data_nxt.pop(0)
        data_nxt.append(nul_val)
        prv_key = prv + ft_base
        nxt_key = nxt + ft_base
        self.proc_fts_ldic[prv_key] = data_prv
        self.proc_fts_ldic[nxt_key] = data_nxt

        if deg == 2:  # TODO improve (reduce code) by using iteration from previous step
            data_prv_prv, data_nxt_nxt = data_prv.copy(), data_nxt.copy()
            data_prv_prv.insert(0, nul_val)
            data_prv_prv.pop()
            data_nxt_nxt.pop(0)
            data_nxt_nxt.append(nul_val)
            prv_prv_key = prv + prv + ft_base
            nxt_nxt_key = nxt + nxt + ft_base
            self.proc_fts_ldic[prv_prv_key] = data_prv_prv
            self.proc_fts_ldic[nxt_nxt_key] = data_nxt_nxt

    def proc_prv_nxt_phset(self):
        """
        Process prev/next phone set fts.
        """
        fts_key_lst = list(self.proc_fts_ldic.keys()).copy()    # to avoid: dictionary changed size during iteration
        for ft in fts_key_lst:
            ft_out = ft										# Defaut value of ft_out is ft
            nul_val = self.cst.PAU								# Value used for outer values in prev/next sets
            if ft != 'phone':
                ft_out = re.sub('^ph_', '', ft)				# remove the starting str 'ft_' from the ph_set features
                nul_val = '0'
            self.proc_prv_nxt_fts(ft, nul_val, 2, ft_out, prv='prev_', nxt='next_')

#== = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =#
    def gen_fts_idx_ldic(self):
        """
        Generate the dict of lists with element indexes.
        """
        ft_idx_tmp = tuple(
            (ph, idx_sll, len(syll), idx_wrd, len(word.word), idx_phr, len(phrase['phrase']), idx_snt, len(sentence))
            for (idx_snt, sentence) in enumerate(self.utt_total_mix)                # utt_mix:  list
            for (idx_phr, phrase) in enumerate(sentence)                            # sentence: list
            for (idx_wrd, word) in enumerate(phrase['phrase'])                      # phrase:   dict
            for (idx_sll, syll) in enumerate(word.word)                             # word:     namedtpl
            for (idx_ph, ph) in enumerate(syll)                                     # syll:     tuple
        )

        self.ft_idx_ttpl = Lst.transp_ttpl(ft_idx_tmp)

    def extract_sentence_numphrases_ft(self, ft):   # QQ: , utt_data_mix): TODO: fct for lst compreh or extr all at once
        """
        Extraction of the number of phrases in the sentence.
        """
        self.proc_fts_ldic[ft] = tuple(el for el in self.ft_idx_ttpl[8])

    def extract_phrase_numwords_ft(self, ft):
        """
        Extraction of the number of words in the phrase.
        """
        self.proc_fts_ldic[ft] = tuple(el-1 for el in self.ft_idx_ttpl[6])          # Remove 1 el for the punctuation

    def extract_sentence_numwords_ft(self, ft):
        """
        Extraction of the number of words in the sentence.
        """
        phrase_idx_bkp = -1
        snt_numb = max(self.ft_idx_ttpl[7]) + 1
        word_cnt = [0] * snt_numb                                           # set a 0 vect of len = number of sentences

        for (ph_idx, _) in enumerate(self.ft_idx_ttpl[0]):

            if self.ft_idx_ttpl[5][ph_idx] != phrase_idx_bkp:

                phrase_idx_bkp = self.ft_idx_ttpl[5][ph_idx]
                sentence_idx = self.ft_idx_ttpl[7][ph_idx]
                word_cnt[sentence_idx] += self.ft_idx_ttpl[6][ph_idx] - 1           # Remove 1 el for the punctuation

        self.proc_fts_ldic[ft] = tuple(word_cnt[snt_idx] for snt_idx in self.ft_idx_ttpl[7])

    # TODO: factorize the code to reuse with the extract_sentence_numwords_ft()
    def extract_phrase_numsyls_ft(self, ft):
        """
        Extraction of the number of syllables in the phrase.
        """
        phrase_idx, phrase_idx_bkp, sentence_idx_bkp, ph_idx_bkp = 0, 0, 0, 0
        # phrase_idx_lst = [0] * len(self.ft_idx_ttpl[0])
        # phrase_tot_numb = sum(set(self.ft_idx_ttpl[8]))
        syll_cnt_per_phrase_tpl = ()  # [-1] * phrase_tot_numb              # set a NULL(-1) vect of len = n of phrases
        syll_cnt_per_phrase_sent_ttpl = ()

        for (ph_idx, _) in enumerate(self.ft_idx_ttpl[0]):

            if (
                    self.ft_idx_ttpl[5][ph_idx] != phrase_idx_bkp
                    or ph_idx == len(self.ft_idx_ttpl[5]) - 1
                    or self.ft_idx_ttpl[7][ph_idx] != sentence_idx_bkp
            ):

                syll_cnt_per_phrase_tpl += (round(sum([1/el for el in self.ft_idx_ttpl[2][ph_idx_bkp:ph_idx]]))-1,)
                phrase_idx_bkp = self.ft_idx_ttpl[5][ph_idx]
                ph_idx_bkp = ph_idx

                if (
                        self.ft_idx_ttpl[7][ph_idx] != sentence_idx_bkp
                        or ph_idx == len(self.ft_idx_ttpl[7]) - 1
                ):

                    syll_cnt_per_phrase_sent_ttpl += (syll_cnt_per_phrase_tpl,)
                    syll_cnt_per_phrase_tpl = ()
                    sentence_idx_bkp = self.ft_idx_ttpl[7][ph_idx]

            # print(
            #     '**DEBUG**',  # self.utt_total_mix,
            #     len(syll_cnt_per_phrase_tpl), phrase_idx, syll_cnt_per_phrase_tpl, self.ft_idx_ttpl[0][ph_idx],ph_idx)
            # print(' '.join(self.ft_idx_ttpl[0]))
            # # print('', '  '.join([str(el) for el in self.ft_idx_ttpl[5]]))
            # for idx, tpl in enumerate(self.ft_idx_ttpl):
            #     if idx > 0:
            #         print('', '  '.join([str(el) for el in tpl]))     # debug

            # phrase_idx_lst[ph_idx] = phrase_idx

        self.proc_fts_ldic[ft] = tuple(syll_cnt_per_phrase_sent_ttpl[sent_idx][phr_idx]
                                       for sent_idx, phr_idx in zip(self.ft_idx_ttpl[7], self.ft_idx_ttpl[5]))

    def format_fts_val(self):
        """
        Set max val to 19 and cast all val to str.
        """
        for ft in self.proc_fts_ldic.keys():
        # Check all element value and set max integer val to 19                       # fixme:**temporary stop 19 conv
            if isinstance(self.proc_fts_ldic[ft][0], int):                            # check if 1st el of lst is int
                self.proc_fts_ldic[ft] = [val if val < 19 else 19
                                          for val in self.proc_fts_ldic[ft]]
            # Cast all ldic elements in str format (TODO: check in process_hmm_fts in the future)

            self.proc_fts_ldic[ft] = tuple(
                str(val) for val in self.proc_fts_ldic[ft]
            )

#== = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =#
    def process_ph_fts_extr(self):
        """
        Process the extraction and store it in a dictionary of lists.
        """
        self.process_static_hmm_data()                          # generate the static hmm data, extraction is based on

        # Fill the proc_fts_ldic with the phoneme list.
        self.proc_fts_ldic = {'phone': self.utt_ph_lst}

        self.proc_ph_set_fts()                                  # Process phone set features

        self.proc_prv_nxt_phset()                               # Process prev/next phone set fts

#== = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =#
    def process_hmm_fts_extr(self, style=''):
        """
        Processing the hmm features listed in the parameter file.
        """
        self.gen_fts_idx_ldic()

        for ft in self.cst.USED_HMM_FTS_TPL:

            if ft == 'sentence_numphrases':     # TODO: change to all hmm fts fct and use if to get dedicated answers
                self.extract_sentence_numphrases_ft(ft)

            elif ft == 'sentence_numwords':
                self.extract_sentence_numwords_ft(ft)

            elif ft == 'phrase_numwords':
                self.extract_phrase_numwords_ft(ft)

            elif ft == 'phrase_numsyls':
                self.extract_phrase_numsyls_ft(ft)

            ## FIXME: TEMP FOR FT CORPUS
            if ft == 'utt_numphrases':     # TODO: change to all hmm fts fct and use if to get dedicated answers
                self.extract_sentence_numphrases_ft(ft)

            elif ft == 'utt_numwords':
                self.extract_sentence_numwords_ft(ft)

            elif ft == 'utt_numsyls':
                self.extract_phrase_numsyls_ft(ft)

            elif ft == 'tobi':
                self.proc_fts_ldic[ft] = tuple(
                    str('L-H%') for val in self.proc_fts_ldic['phone']  # [ft]
                )

            elif ft == 'style':
                self.proc_fts_ldic[ft] = tuple(
                    style for _ in self.proc_fts_ldic['phone']  # [ft]
                )

            else:
                sys.exit("Error! " + "'" + ft + "'" + " feature extraction NOT covered by the PfsExtractor() class")

#======================================================================================================================#
    def process_pfeats_extr(self, style=''):
        """
        Processing ALL the features listed in the parameter file.
        """
        self.process_ph_fts_extr()

        self.process_hmm_fts_extr(style)

        # KEEP AT THE END, LAST FORMATTING STATE!
        self.format_fts_val()                                   # Set max val to 19 and cast all val to str.

#======================================================================================================================#
