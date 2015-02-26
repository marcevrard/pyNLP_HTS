#!/usr/bin/env python3
#-*- coding: utf-8 -*-

import importlib

from class_tts import PhoneSet


class Item:
    """
    Abstract class for all text units: Phonemes, Syllables, Words, Phrases, Sentences and Utterances.
    """
    def __init__(self, param_module, idx, number):

        self.cst = importlib.import_module(param_module)

        self.number = number
        self.posit_from_start = idx + 1
        self.posit_from_end = self.number - idx

        # self.trigger = 0

        if idx == 0:
            self.trigger = 'start'


class Phone(Item):
    """
    Phoneme class (smallest unit).
    """
    def __init__(self, param_module, ph, idx, number):

        super().__init__(param_module, idx, number)

        self.ph = ph
        self.idx_ph = idx
        self.number_ph = number

        self.start_time = '0'
        self.stop_time = '0'

        self.ph_set_obj = PhoneSet(param_module, self.cst.PH_SET_FPATH)
        self.ph_set_obj.set_current_ph(ph)

        # self.ph_set_obj = ph_set_obj(self.ph)       # TODO: Manage the problem of object transmission (aggregation)
                                                    # TODO... maybe structure to improve (Phone part of PhoneSet?)

        # self._ph_pfs = {}
    # def set_ph_pfs(self):     # QQ: Should I process the ph_set here and include the class_tts_extr here (aggreg.)?
                                # QQ: or should I include the Phoneme class in the class_tts_extr (aggr. the other way)

    def set_time(self, start_time, stop_time):
        """
        Set time stamp from lab files.
        """
        self.start_time = start_time
        self.stop_time = stop_time


class Syllable(Item):
    """
    Syllable class (based on phonemes).
    """
    def __init__(self, param_module, syll, idx, number):

        super().__init__(param_module, idx, number)

        _ph_lst = str(syll).split(' ')

        # _phs_lst = [ph if ph not in self.cst.PUNCT_ALL else self.cst.PAU        # Transform punct marks in pauses
        _phs_lst = [ph if ph not in self.cst.PUNCT_ALL else                     # Transform punct marks in pau and ssil
                    self.cst.PAU if ph in self.cst.PUNCT_END else
                    self.cst.SSIL for ph in _ph_lst]

        self.phs = [Phone(param_module, ph, idx_ph, len(_phs_lst)) for (idx_ph, ph) in enumerate(_phs_lst)]
                                                                                    # punct marks > pauses

        self.vowels = [ph.ph for ph in self.phs if ph.ph_set_obj.vc == '+']         # TODO: warning see (1)


class Word(Item):
    """
    Word class (graphemes and phonemes).
    """
    def __init__(self, param_module, word, idx, number):

        super().__init__(param_module, idx, number-1)                   # -1 to remove the punct counting as word here

        self._sylls_lst = [syll for syll in word]

        self.sylls = [Syllable(param_module, syll, idx_syl, len(self._sylls_lst))
                      for (idx_syl, syll) in enumerate(self._sylls_lst)]


class Phrase(Item):
    """
    Phrase class (graphemes and phonemes).
    """
    def __init__(self, param_module, phrase, phrase_punct, idx, number):
        # self._punct = phrase.pop()
        super().__init__(param_module, idx, number)

        self._punct = phrase_punct

        # Punctuation normalization TODO: do normalization in Utterance(), check "punct in a raw" and "punt to del"
        if self._punct in self.cst.PUNCT:
            self._punct_normalized = self._punct
        elif self._punct in self.cst.PUNCT_CONV_PERIOD:
            self._punct_normalized = '.'
        elif self._punct in self.cst.PUNCT_CONV_COMA:
            self._punct_normalized = ','

        self.tobi = self.cst.PROSO_LABEL[self._punct_normalized]
        self._words_lst = [word for word in phrase]
        # self.words = [Word(word, idx_wrd, len(self._words_lst)) for (idx_wrd, word) in enumerate(self._words_lst)]


class Sentence(Item):
    """
    Sentence class (graphemes and phonemes).
    """
    def __init__(self, param_module, token_sentence_lst, sentence_punct, idx, number):

        super().__init__(param_module, idx, number)

        self._punct = sentence_punct
        self._phrases_el_llst = []
        idx_bkp = 0
        for idx, token in enumerate(token_sentence_lst):
            if token in self.cst.PUNCT_PHRASE:
                self._phrases_el_llst.append([token_sentence_lst[idx_bkp:idx+1], token])
                # self._phrase_punct = token
                idx_bkp = idx + 1
            elif idx == len(token_sentence_lst) - 1:        # if last token of phrase (punct used for sentence_punct)
                self._phrases_el_llst.append([token_sentence_lst[idx_bkp:idx+1], sentence_punct])

        # self.phrases = [Phrase(el[0], el[1], idx_phr, len(self._phrases_el_llst))
        #                 for (idx_phr, el) in enumerate(self._phrases_el_llst)]


class Utterance:
    """
    Utterance class (graphemes and phonemes).
    """
    def __init__(self, param_module, sentences_lst_cln, style=''):

        self.cst = importlib.import_module(param_module)

        self.sentences = []

        self.style = style

        self._sentences_el_llst = []                                 # el_llst since the punct_mkr is nested in the lst
        idx_bkp = 0
        for idx, token in enumerate(sentences_lst_cln):
            if token in self.cst.PUNCT_END:
                self._sentences_el_llst.append([sentences_lst_cln[idx_bkp:idx+1], token])
                # self._sent_punct = token
                idx_bkp = idx + 1

            elif idx == len(sentences_lst_cln) - 1:                 # if ended by char other than end of sentence punct
                if token in self.cst.PUNCT_PHRASE:
                    self._sentences_el_llst.append([sentences_lst_cln[idx_bkp:idx], token])
                else:
                    self._sentences_el_llst.append([sentences_lst_cln[idx_bkp:idx+1], self.cst.PAU])

        # # Why using a separated list comprehension to build obj, instead of using directly previous appended lists?
        # # because we need to transfer the number of el in the list to the composite objects
        # self.sentences = [Sentence(el[0], el[1], idx_snt, len(self._sentences_el_llst))
        #                   for (idx_snt, el) in enumerate(self._sentences_el_llst)]
