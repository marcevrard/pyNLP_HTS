#!/usr/bin/env python3
#-*- coding: utf-8 -*-

import importlib

import my_defs.defs_list as lst

from class_tts import UtterancePh, Phone


class Sequence:
    """
    Class presenting the utterance in a sequential fashion.
    """
    def __init__(self, param_module, utt, style=''):

        self.param_mod = param_module
        self.cst = importlib.import_module(param_module)

        self.rel_posit_lst, self.rel_numb_lst, self.rel_posit_bckwd_lst = [], [], []

        self.utt_obj = UtterancePh(param_module, utt, style)

        self.item_tpl = ('phones', 'sylls', 'words', 'phrases', 'sentences')
        # self.item_val = [ph.posit_from_start, syll.posit_from_start, word.posit_from_start,
        #                  phrase.posit_from_start, sentence.posit_from_start]

        self.item_idx_ldic = {}
        self.item_trigger_ldic = {}

        self.phones = []
        self.sylls = []
        self.words = []
        self.phrases = []
        self.sentences = []
        self.utterances = []

        self.num_pau_begin = 0

        for sentence in self.utt_obj.sentences:
            for phrase in sentence.phrases:
                for word in phrase.words:
                    for syll in word.sylls:
                        for ph in syll.phs:

                            self.phones.append(ph)
                            self.sylls.append(syll)
                            self.words.append(word)
                            self.phrases.append(phrase)
                            self.sentences.append(sentence)
                            self.utterances.append(self.utt_obj)

    def set_ph_time(self, time_nttpl):
        """
        Set time stamp from lab files.
        """
        ph_tpl = tuple(ph.ph for ph in self.phones)

        # Identify the number of pauses present at the beginning/end of the utt in the eHMM lab (time_nttpl).
        non_pau_idx_lab_lst = [idx for (idx, el) in enumerate(time_nttpl) if el.phone != self.cst.PAU]
        non_pau_idx_ph_lst = [idx for (idx, phone) in enumerate(self.phones) if phone.ph != self.cst.PAU]

        self.num_pau_begin = non_pau_idx_lab_lst[0]
        num_pau_end = len(time_nttpl) - (non_pau_idx_lab_lst[-1] + 1) - (len(ph_tpl) - (non_pau_idx_ph_lst[-1] + 1))

        self.phones = []
        self.sylls = []
        self.words = []
        self.phrases = []
        self.sentences = []

        # Insert "manually" pauses at beginning/end of the first/last syll objects resp.
        # fixme: create a problem for "proc_item_trigger_ldic(self)" since the first syllable doesn't start at 0.
        for _ in range(self.num_pau_begin):
            self.utt_obj.sentences[0].phrases[0].words[0].sylls[0].phs.\
                insert(0, Phone(self.param_mod, self.cst.PAU, 0, 0))

        for _ in range(num_pau_end):
            self.utt_obj.sentences[-1].phrases[-1].words[-1].sylls[-1].phs.\
                append(Phone(self.param_mod, self.cst.PAU, 0, 0))

        # for idx_st, sentence in enumerate(self.utt_obj.sentences):
        #     for idx_phr, phrase in enumerate(self.utt_obj.sentences[idx_st].phrases):
        #         for idx_wd, word in enumerate(self.utt_obj.sentences[idx_st].phrases[idx_phr].words):
        #         for idx_syl, syll in enumerate(self.utt_obj.sentences[idx_st].phrases[idx_phr].words[idx_wd].sylls):
        #                 for idx_ph, ph in enumerate(
        #                         self.utt_obj.sentences[idx_st].phrases[idx_phr].words[idx_wd].sylls[idx_syl].phs
        #                 ):

        # Recompose the Sequence objects with the pauses added.
        idx_time = 0
        for sentence in self.utt_obj.sentences:
            for phrase in sentence.phrases:
                for word in phrase.words:
                    for syll in word.sylls:
                        for idx_ph, ph in enumerate(syll.phs):

                            if ph.ph == time_nttpl[idx_time].phone:
                                # Only assign the value with the pauses present in the eHMM lab file
                                idx_time += 1
                                self.phones.append(ph)
                                self.sylls.append(syll)
                                self.words.append(word)
                                self.phrases.append(phrase)
                                self.sentences.append(sentence)
                                self.utterances.append(self.utt_obj)                # ADDED 2014-05-08
                            else:
                                # Delete the pauses deleted during the eHMM alignment
                                del(syll.phs[idx_ph])

        # Assign the time info to the ph object.
        for (ph, time_ntpl) in zip(self.phones, time_nttpl):
            ph.set_time(time_ntpl.start, time_ntpl.stop)

    def get_ph_lst(self):
        """
        Return phone sequence as a list.
        """
        return [ph.ph for ph in self.phones]

    def proc_item_idx_ldic(self):
        """
        Compose a dict with the item index list.
        """
        dlst = [
            {'phones': ph.posit_from_start, 'sylls': syll.posit_from_start, 'words': word.posit_from_start,
             'phrases': phrase.posit_from_start, 'sentences': sentence.posit_from_start}
            for sentence in self.utt_obj.sentences
            for phrase in sentence.phrases
            for word in phrase.words
            for syll in word.sylls
            for ph in syll.phs
        ]

        self.item_idx_ldic = lst.transp_dlst_to_ldic(dlst)                # return ldic transposed version of the dlst

    def proc_item_trigger_ldic(self):
        """
        Compose a dict of lists holding the item start positions.
        """
        item_trigger_dlst = [                                                       # trigger action: 'pause' (!= 'pau')
            {'test_DEBUG': idx_ph,
             'phones': 'start' if ph.ph != self.cst.PAU and ph.ph != self.cst.SSIL else 'pause',
             'sylls': 'start' if (idx_ph == 0 and ph.ph != self.cst.PAU and ph.ph != self.cst.SSIL)
             or (idx_syl == 0 and idx_wrd == 0 and idx_phr == 0 and idx_snt == 0 and idx_ph == self.num_pau_begin)
             else 0,
             # fixme:^ plaster on wooden leg (see above)
             'words': 'start' if (idx_ph == 0 and idx_syl == 0 and ph.ph != self.cst.PAU and ph.ph != self.cst.SSIL)
             or (idx_syl == 0 and idx_wrd == 0 and idx_phr == 0 and idx_snt == 0 and idx_ph == self.num_pau_begin)
             else 0,
             # fixme:^ plaster on wooden leg (see above)
             'phrases': 'start' if idx_ph == 0 and idx_syl == 0 and idx_wrd == 0 else 0,
             'sentences': 'start' if idx_ph == 0 and idx_syl == 0 and idx_wrd == 0 and idx_phr == 0 else 0,
             'utterance': 'start' if idx_ph == 0 and idx_syl == 0 and idx_wrd == 0 and idx_phr == 0 and idx_snt == 0
             else 0}
            for (idx_snt, sentence) in enumerate(self.utt_obj.sentences)
            for (idx_phr, phrase) in enumerate(sentence.phrases)
            for (idx_wrd, word) in enumerate(phrase.words)
            for (idx_syl, syll) in enumerate(word.sylls)
            for (idx_ph, ph) in enumerate(syll.phs)
        ]
        # for l in item_trigger_dlst:     # debug
        #     print(l['test_DEBUG'], end=' ')

        self.item_trigger_ldic = lst.transp_dlst_to_ldic(item_trigger_dlst)   # return ldic transp. version of the dlst

    def get_rel_position(self, item, ref_item):
        """
        Get the position of the current linguistic item in relation to another given as argument.
        """
        self.proc_item_trigger_ldic()

        idx_bkp, calc_el = 0, 0
        rel_posit_tpl = []

        for idx, _ in enumerate(self.item_trigger_ldic['phones']):
            if self.item_trigger_ldic[item][idx] == 'start':
                calc_el += 1

            if self.item_trigger_ldic[ref_item][idx] == 'start':
                calc_el = 1

            if (
                    self.item_trigger_ldic['phones'][idx] == 'pause'
                and item != 'phrases' and item != 'sentences'           # Silence does not restart counting in these ...
                and ref_item != 'sentences' and ref_item != 'utterance'     # ... 4 cases.
            ):
                calc_el = 0

            rel_posit_tpl += (calc_el,)

        return rel_posit_tpl

    def get_rel_number(self, item, ref_item):
        """
        Get the number of the current linguistic item in relation to another given as argument.
        """
        rel_posit_tpl = self.get_rel_position(item, ref_item)
        rel_numb_lst = [0] * len(rel_posit_tpl)

        idx_bkp, calc_sum = 0, 0
        for (idx, el) in enumerate(rel_posit_tpl):
            if idx > 0:
                if (
                        self.item_trigger_ldic[ref_item][idx] == 'start'
                    or (
                        self.item_trigger_ldic['phones'][idx] == 'pause'
                        and item != 'phrases' and item != 'sentences'
                        and ref_item != 'sentences' and ref_item != 'utterance'
                    )
                    or idx == len(rel_posit_tpl) - 1                            # when the end of the list is reached
                ):
                    calc_sum = rel_posit_tpl[idx-1]
                    if idx == len(rel_posit_tpl) - 1:
                        if self.item_trigger_ldic[item][idx] == 'start':
                            calc_sum += 1
                        idx += 1

                    rel_numb_lst[idx_bkp:idx] = [calc_sum] * (idx - idx_bkp)

                    if (
                            self.item_trigger_ldic['phones'][-1] == 'pause'
                        and item != 'phrases' and item != 'sentences'
                        and ref_item != 'sentences' and ref_item != 'utterance'
                    ):
                        rel_numb_lst[-1] = 0

                    idx_bkp = idx

        return tuple(rel_numb_lst)

    # fixme: plaster to fix the above problem (get_rel_number doesn't work for UTT HORIZON FTS anymore!
    def get_utt_numb_of(self, item):
        """
        Get the number of the current linguistic item in the utt.
        """
        num = self.item_trigger_ldic[item].count('start')

        return (num,) * len(self.item_trigger_ldic[item])

    def get_rel_position_bckwd(self, item, ref_item):
        """
        Get the position of the current linguistic item in relation to another given as argument in backward order.
        """
        rel_posit_tpl = self.get_rel_position(item, ref_item)
        rel_numb_tpl = self.get_rel_number(item, ref_item)

        return tuple(el_num - el_pos + 1 if el_num != 0 else 0
                     for (el_num, el_pos) in zip(rel_numb_tpl, rel_posit_tpl))