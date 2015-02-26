#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import importlib
# from collections import namedtuple

import my_defs.defs_list as lst

from class_tts import Sequence


#   ====================================================================================================================
class TextFeatures:
    """
    Class providing the extraction parameters.
    """
    def __init__(self, param_module, utt, time_nttpl=None, style=''):

        # FIXME: set phone set reference data outside of init, and allow for initialisation without utt input

        self.param_module = param_module

        self.cst = importlib.import_module(param_module)

        self.style_val = style

        self.utt_seq_obj = Sequence(self.param_module, utt, style)
        if time_nttpl is not None:
            self.utt_seq_obj.set_ph_time(time_nttpl)                        # Add time and apply eHMM lab sequence

        # Set the _PH_SET_PARAM_TPL reference tuple
        def set_ph_set_param_tpl(ft_prefix=''):
            return tuple(ft_prefix+ft_base for ft_base in self.utt_seq_obj.phones[0].ph_set_obj.get_ph_set_param_dic()
                         if ft_base != 'ph')

        self._PH_SET_BASE_PARAM_TPL = set_ph_set_param_tpl()
        self._PH_SET_ALL_PARAM_TPL = self._PH_SET_BASE_PARAM_TPL

        if self.cst.NUMBER_PHONES > 1:
            self._PH_SET_ALL_PARAM_TPL += set_ph_set_param_tpl('prev_')
            self._PH_SET_ALL_PARAM_TPL += set_ph_set_param_tpl('next_')
            if self.cst.NUMBER_PHONES > 3:
                self._PH_SET_ALL_PARAM_TPL += set_ph_set_param_tpl('prev_prev_')
                self._PH_SET_ALL_PARAM_TPL += set_ph_set_param_tpl('next_next_')

        # Initiate all phone feature attributes
        for ft in self._PH_SET_ALL_PARAM_TPL:
            setattr(self, ft, 0)

        for ft in self.cst.ALL_HMM_FTS_TPL:
            setattr(self, ft, 0)

        self._ALL_PFEATS_TPL = self._PH_SET_ALL_PARAM_TPL + self.cst.ALL_HMM_FTS_TPL
        self._USED_PFEATS_TPL = self._PH_SET_ALL_PARAM_TPL + self.cst.USED_HMM_FTS_TPL

        self.hts_lab_gen_prn = ()
        self._proc_ldic = {}
        self._hts_lab_mono_ttpl = ()
        self.hts_lab_mono_prn = ()
        self.hts_lab_full_prn = ()

    def __str__(self):
        """
        Get all Phone Features as a ...?
        """
        tpl = ()
        for ft in self._USED_PFEATS_TPL:
            try:                                                                    # debug print
                tpl += (ft, ' '.join([str(el) for el in getattr(self, ft)]))
            except AttributeError:
                print("\nError: the "+"'"+ft+"'"+" phone feature is not present in the standard phone feature list!\n")
            except TypeError:
                print("\nError: the "+"'"+ft+"'"+" phone feature has not been processed yet!\n")

        return '\n'.join(tpl)

#   ====================================================================================================================
    def proc_prev_ph_tpl(self, ft, nul_val):    # TODO change to phoneme!!
        """
        Return the current phone tuple attribute without the last element and append the default value to the first el.
        """
        return (nul_val,) + getattr(self, ft)[:-1]

    def proc_next_ph_tpl(self, ft, nul_val):    # TODO change to phoneme!!
        """
        Return the current phone tuple attribute without the first element and append the default value to the last el.
        """
        return getattr(self, ft)[1:] + (nul_val,)

    def proc_ph_set_fts(self, nul_val, prv_nxt=''):
        """
        Process all phone set features.
        """
        for ft in self._PH_SET_BASE_PARAM_TPL:
            if ft != 'ph':
                if prv_nxt == 'prev_':
                    setattr(self, prv_nxt+ft, (nul_val,) + tuple(getattr(phone.ph_set_obj, ft) for phone
                                                                 in self.utt_seq_obj.phones[:-1]))
                elif prv_nxt == 'next_':
                    setattr(self, prv_nxt+ft, tuple(getattr(phone.ph_set_obj, ft) for phone
                                                    in self.utt_seq_obj.phones[1:]) + (nul_val,))
                elif prv_nxt == 'prev_prev_':
                    setattr(self, prv_nxt+ft, (nul_val, nul_val) + tuple(getattr(phone.ph_set_obj, ft) for phone
                                                                         in self.utt_seq_obj.phones[:-2]))
                elif prv_nxt == 'next_next_':
                    setattr(self, prv_nxt+ft, tuple(getattr(phone.ph_set_obj, ft) for phone
                                                    in self.utt_seq_obj.phones[2:]) + (nul_val, nul_val))
                else:
                    setattr(self, prv_nxt+ft, tuple(getattr(phone.ph_set_obj, ft) for phone
                                                    in self.utt_seq_obj.phones))

    # def process_pfeats(self, style=''):     # 2014-05-08
    def process_pfeats(self):      # FIXME process time_nttpl in this class?
        """
        Process all used hmm phone features.
        """
        # **PHONE HORIZON FTS: PROCESS CURRENT 'PHONE' (A)**
        setattr(self, 'phone', tuple(ph.ph for ph in self.utt_seq_obj.phones))

        # Process current phone set features
        self.proc_ph_set_fts(self.cst.NULL_VAL)

        # Time stamp processing from lab files.
        setattr(self, 'start', tuple(ph.start_time for ph in self.utt_seq_obj.phones))
        setattr(self, 'stop', tuple(ph.stop_time for ph in self.utt_seq_obj.phones))

        # **PHONE HORIZON FTS: (B, C)**

        if self.cst.NUMBER_PHONES > 1:

            setattr(self, 'prev_phone', self.proc_prev_ph_tpl('phone', self.cst.NULL_VAL))
            setattr(self, 'next_phone', self.proc_next_ph_tpl('phone', self.cst.NULL_VAL))
            self.proc_ph_set_fts(self.cst.NULL_VAL, 'prev_')
            self.proc_ph_set_fts(self.cst.NULL_VAL, 'next_')

            if self.cst.NUMBER_PHONES > 3:

                setattr(self, 'prev_prev_phone', self.proc_prev_ph_tpl('prev_phone', self.cst.NULL_VAL))
                setattr(self, 'next_next_phone', self.proc_next_ph_tpl('next_phone', self.cst.NULL_VAL))
                self.proc_ph_set_fts(self.cst.NULL_VAL, 'prev_prev_')
                self.proc_ph_set_fts(self.cst.NULL_VAL, 'next_next_')

        if (
                'phone_from_syl_start' in self.cst.USED_HMM_FTS_TPL and
                'phone_from_syl_end' in self.cst.USED_HMM_FTS_TPL
        ):
            setattr(self, 'phone_from_syl_start', tuple(self.utt_seq_obj.get_rel_position('phones', 'sylls')))
            setattr(self, 'phone_from_syl_end', tuple(self.utt_seq_obj.get_rel_position_bckwd('phones', 'sylls')))
            # TODO: change 'phones' or 'phs' or 'ph' for coherent standard!!

        if (
                'phone_from_word_start' in self.cst.USED_HMM_FTS_TPL and
                'phone_from_word_end' in self.cst.USED_HMM_FTS_TPL
        ):
            setattr(self, 'phone_from_word_start', tuple(self.utt_seq_obj.get_rel_position('phones', 'words')))
            setattr(self, 'phone_from_word_end', tuple(self.utt_seq_obj.get_rel_position_bckwd('phones', 'words')))

        # **SYLLABLE HORIZON FTS**: (D)

        if 'syl_numphones' in self.cst.USED_HMM_FTS_TPL:
            setattr(self, 'syl_numphones', tuple(self.utt_seq_obj.get_rel_number('phones', 'sylls')))

        if (
                'prev_syl_numphones' in self.cst.USED_HMM_FTS_TPL and
                'next_syl_numphones' in self.cst.USED_HMM_FTS_TPL
        ):
            setattr(self, 'prev_syl_numphones', getattr(self, 'syl_numphones'))
            setattr(self, 'next_syl_numphones', getattr(self, 'syl_numphones'))
            # FIXME unfinished

        if (
                'syl_from_word_start' in self.cst.USED_HMM_FTS_TPL and
                'syl_from_word_end' in self.cst.USED_HMM_FTS_TPL
        ):
            setattr(self, 'syl_from_word_start', tuple(self.utt_seq_obj.get_rel_position('sylls', 'words')))
            setattr(self, 'syl_from_word_end', tuple(self.utt_seq_obj.get_rel_position_bckwd('sylls', 'words')))

            # print('')                                               # debug
            # print(*self.utt_seq_obj.item_trigger_ldic['phones'])    # debug
            # print(*self.utt_seq_obj.item_trigger_ldic['sylls'])     # debug
            # print(*self.utt_seq_obj.item_trigger_ldic['words'])     # debug
            # print(*self.utt_seq_obj.item_trigger_ldic['phrases'])     # debug
            # print(*self.utt_seq_obj.item_trigger_ldic['sentences'])     # debug
            # print(*self.utt_seq_obj.item_trigger_ldic['utterance'])     # debug

        if (
                'syl_from_phrase_start' in self.cst.USED_HMM_FTS_TPL and
                'syl_from_phrase_end' in self.cst.USED_HMM_FTS_TPL
        ):
            setattr(self, 'syl_from_phrase_start', tuple(self.utt_seq_obj.get_rel_position('sylls', 'phrases')))
            setattr(self, 'syl_from_phrase_end', tuple(self.utt_seq_obj.get_rel_position_bckwd('sylls', 'phrases')))

        if 'syl_vowel' in self.cst.USED_HMM_FTS_TPL:
            # print('')     # debug??
            setattr(self, 'syl_vowel', tuple(syll.vowels[0] if len(syll.vowels) > 0 else 0  # case pauses
                                             for syll in self.utt_seq_obj.sylls))

        # **WORD HORIZON FTS**:

        if 'word_numphones' in self.cst.USED_HMM_FTS_TPL:
            setattr(self, 'word_numphones', tuple(self.utt_seq_obj.get_rel_number('phones', 'words')))

        if 'word_numsyls' in self.cst.USED_HMM_FTS_TPL:
            setattr(self, 'word_numsyls', tuple(self.utt_seq_obj.get_rel_number('sylls', 'words')))

        if 'word_gpos' in self.cst.USED_HMM_FTS_TPL:
            setattr(self, 'word_gpos', tuple(word.pos for word in self.utt_seq_obj.words))

        # **PHRASE HORIZON FTS**:

        if 'phrase_endtone' in self.cst.USED_HMM_FTS_TPL:
            setattr(self, 'phrase_endtone', tuple(phrase.tobi for phrase in self.utt_seq_obj.phrases))

        # **UTT HORIZON FTS**:

        # fixme: plaster to fix the problem in "class_seq()" (get_rel_number doesn't work for UTT HORIZON FTS anymore!
        if 'utt_numsyls' in self.cst.USED_HMM_FTS_TPL:
            setattr(self, 'utt_numsyls', tuple(self.utt_seq_obj.get_utt_numb_of('sylls')))

        if 'utt_numwords' in self.cst.USED_HMM_FTS_TPL:
            setattr(self, 'utt_numwords', tuple(self.utt_seq_obj.get_utt_numb_of('words')))

        if 'utt_numphrases' in self.cst.USED_HMM_FTS_TPL:
            setattr(self, 'utt_numphrases', tuple(self.utt_seq_obj.get_utt_numb_of('phrases')))

        # if 'utt_numsyls' in self.cst.USED_HMM_FTS_TPL:
        #     setattr(self, 'utt_numsyls', tuple(self.utt_seq_obj.get_rel_number('sylls', 'utterance')))
        #
        # if 'utt_numwords' in self.cst.USED_HMM_FTS_TPL:
        #     setattr(self, 'utt_numwords', tuple(self.utt_seq_obj.get_rel_number('words', 'utterance')))
        #
        # if 'utt_numphrases' in self.cst.USED_HMM_FTS_TPL:
        #     setattr(self, 'utt_numphrases', tuple(self.utt_seq_obj.get_rel_number('phrases', 'utterance')))

        if (
                #   'style' in style and    # self.cst.USED_HMM_FTS_TPL    # 2014-05-08
                self.style_val != ''
        ):
            setattr(self, 'style', tuple(utt.style for utt in self.utt_seq_obj.utterances))

        # TODO: create "packages" with 'level' of fts cf Le Maguer
        # TODO: check if attributes haven't been created with a wrong name (attribute list still consistent)

#   ====================================================================================================================
    def gen_hts_lab_fts(self):
        """
        Generate the generic lab content (pfeats) according to HTS standards.
        """
        if self.cst.NUMBER_PHONES > 1:
            ph_fts_tpl = ('prev_phone', 'phone', 'next_phone')
            if self.cst.NUMBER_PHONES > 3:
                ph_fts_tpl = ('prev_prev_phone', 'prev_phone', 'phone', 'next_phone', 'next_next_phone')
        else:
            ph_fts_tpl = ('phone',)
        fts_tpl = ph_fts_tpl + self.cst.USED_HMM_FTS_TPL

        self._proc_ldic = lst.conv_obj_ldic(self, fts_tpl + ('start', 'stop'))      # FIXME-20140309 ('start', 'stop')
        # print("DEBUG**:", [(key, len(self._proc_ldic[key])) for key in self._proc_ldic])
        # print('utt_numphrases:', self._proc_ldic['utt_numphrases'], '\n', 'phone:', self._proc_ldic['phone'])
        proc_fts_dlst = lst.transp_ldic_to_dlst(self._proc_ldic, conv_str=True)             # FIXME conv el to string

        # for el in proc_fts_dlst:   # debug
        #     for key in el:
        #         print(key, el[key])
        # for el in proc_fts_dlst:   # debug
        #     print(el)

        # POSTPROD: PUT A 'x' FOR THE REQUIRED FTS WHEN THE CORRESPONDING PH IS: 'pau' or 'ssil'
        for idx, _ in enumerate(proc_fts_dlst):
            if proc_fts_dlst[idx]['phone'] == self.cst.PAU or proc_fts_dlst[idx]['phone'] == self.cst.SSIL:
                if 'phone_from_syl_start' in self.cst.USED_HMM_FTS_TPL:
                    proc_fts_dlst[idx]['phone_from_syl_start'] = self.cst.NULL_VAL
                if 'phone_from_syl_end' in self.cst.USED_HMM_FTS_TPL:
                    proc_fts_dlst[idx]['phone_from_syl_end'] = self.cst.NULL_VAL
                if 'phone_from_word_start' in self.cst.USED_HMM_FTS_TPL:
                    proc_fts_dlst[idx]['phone_from_word_start'] = self.cst.NULL_VAL
                if 'phone_from_word_end' in self.cst.USED_HMM_FTS_TPL:
                    proc_fts_dlst[idx]['phone_from_word_end'] = self.cst.NULL_VAL
                if 'syl_numphones' in self.cst.USED_HMM_FTS_TPL:
                    proc_fts_dlst[idx]['syl_numphones'] = self.cst.NULL_VAL
                if 'prev_syl_numphones' in self.cst.USED_HMM_FTS_TPL:
                    proc_fts_dlst[idx]['prev_syl_numphones'] = self.cst.NULL_VAL
                if 'syl_from_word_start' in self.cst.USED_HMM_FTS_TPL:
                    proc_fts_dlst[idx]['syl_from_word_start'] = self.cst.NULL_VAL
                if 'syl_from_word_end' in self.cst.USED_HMM_FTS_TPL:
                    proc_fts_dlst[idx]['syl_from_word_end'] = self.cst.NULL_VAL
                if 'syl_from_phrase_start' in self.cst.USED_HMM_FTS_TPL:
                    proc_fts_dlst[idx]['syl_from_phrase_start'] = self.cst.NULL_VAL
                if 'syl_from_phrase_end' in self.cst.USED_HMM_FTS_TPL:
                    proc_fts_dlst[idx]['syl_from_phrase_end'] = self.cst.NULL_VAL
                if 'syl_vowel' in self.cst.USED_HMM_FTS_TPL:
                    proc_fts_dlst[idx]['syl_vowel'] = self.cst.NULL_VAL
                if 'word_numphones' in self.cst.USED_HMM_FTS_TPL:
                    proc_fts_dlst[idx]['word_numphones'] = self.cst.NULL_VAL
                if 'word_numsyls' in self.cst.USED_HMM_FTS_TPL:
                    proc_fts_dlst[idx]['word_numsyls'] = self.cst.NULL_VAL
                if 'word_gpos' in self.cst.USED_HMM_FTS_TPL:
                    proc_fts_dlst[idx]['word_gpos'] = self.cst.NULL_VAL

                # NO 'x' FOR PHRASE HORIZON FTS
                # NO 'x' FOR UTT HORIZON FTS

        # TODO: take it from a file with the sorted list of the fts according to hts or mary standard

        fts_code_tpl = tuple('f'+str(idx) for (idx, _) in enumerate(self.cst.USED_HMM_FTS_TPL))

        self.hts_lab_gen_prn = ()

        for proc_fts_dic in proc_fts_dlst:
            if self.cst.NUMBER_PHONES > 1:
                lab_gen_ph = (
                    proc_fts_dic[fts_tpl[0]] + '-' + proc_fts_dic[fts_tpl[1]] + '+'
                    + proc_fts_dic[fts_tpl[2]] + '|'
                )
                if self.cst.NUMBER_PHONES > 3:
                    lab_gen_ph = (
                        proc_fts_dic[fts_tpl[0]] + '^' + proc_fts_dic[fts_tpl[1]] + '-' + proc_fts_dic[fts_tpl[2]] + '+'
                        + proc_fts_dic[fts_tpl[3]] + '=' + proc_fts_dic[fts_tpl[4]] + '|'
                    )
            else:
                lab_gen_ph = (
                    proc_fts_dic[fts_tpl[0]] + '|'
                )

            lab_gen_hmm = '|'
            for idx in range(len(ph_fts_tpl), len(fts_tpl)):
                #   print(fts_code_tpl, proc_fts_dic)    # debug
                lab_gen_hmm += str(fts_code_tpl[idx-len(ph_fts_tpl)]) + '=' + str(proc_fts_dic[fts_tpl[idx]]) + '|'

            self.hts_lab_gen_prn += (lab_gen_ph + lab_gen_hmm + '|',)

    def gen_hts_lab_mono(self):
        """
        Generate the mono lab content (hts timed lab) according to HTS standards.
        """
        chosen_fields_lst = ['start', 'stop', 'phone']

        self._hts_lab_mono_ttpl = \
            lst.transp_ttpl(
                tuple(
                    tuple(self._proc_ldic[field]) for field in chosen_fields_lst
                )
            )

        self._hts_lab_mono_ttpl = tuple(tuple(["{:>10}".format(row[0]), "{:>10}".format(row[1]), row[2]])
                                        for row in self._hts_lab_mono_ttpl)

        self.hts_lab_mono_prn = tuple(' '.join(l) for l in self._hts_lab_mono_ttpl)

    def gen_hts_lab_full(self):
        """
        Generate the full lab content (timing + hts gen lab) according to HTS standards.
        """
        self.gen_hts_lab_mono()

        hts_lab_time_prn = tuple(' '.join(l[0:2]) for l in self._hts_lab_mono_ttpl)

        self.hts_lab_full_prn = tuple(' '.join((l_time, l_gen)) for (l_time, l_gen)
                                      in zip(hts_lab_time_prn, self.hts_lab_gen_prn))

    def process_lab_prn(self):
        """
        Complete process of the label file generation.
        hts_lab_mono_prn
        hts_lab_gen_prn
        hts_lab_full_prn
        """
        self.gen_hts_lab_fts()
        self.gen_hts_lab_full()
