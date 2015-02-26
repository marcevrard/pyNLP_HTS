#!/usr/bin/env python3
#-*- coding: utf-8 -*-


from class_tts import Utterance, Sentence, Phrase, Word


class WordPh(Word):
    """
    Word class with phoneme input processing.
    """
    def __init__(self, param_mod, word, idx, number):

        self.word = word.strip(' "')
        sylls_lst = [syll for syll in self.word.split(' - ')]

        if '"' in word:
            self.pos = 'content'
        else:
            self.pos = 'function'

        super().__init__(param_mod, sylls_lst, idx, number)


class PhrasePh(Phrase):
    """
    Phrase class with phoneme input processing.
    """
    def __init__(self, param_mod, phrase, phrase_punct, idx, number):

        super().__init__(param_mod, phrase, phrase_punct, idx, number)

        self.words = [WordPh(param_mod, word, idx_wrd, len(self._words_lst))
                      for (idx_wrd, word) in enumerate(self._words_lst)]


class SentencePh(Sentence):
    """
    Sentence class with phoneme input processing.
    """
    def __init__(self, param_mod, token_sentence_lst, sentence_punct, idx, number):

        super().__init__(param_mod, token_sentence_lst, sentence_punct, idx, number)

        self.phrases = [PhrasePh(param_mod, el[0], el[1], idx_phr, len(self._phrases_el_llst))
                        for (idx_phr, el) in enumerate(self._phrases_el_llst)]


class UtterancePh(Utterance):
    """
    Utterance class with phoneme input processing.
    """
    def __init__(self, param_mod, utt, style=''):

        sentences_lst = utt.split('\n')
        sentences_lst_cln = [el for el in sentences_lst if el != '']                                # clean empty trail

        super().__init__(param_mod, sentences_lst_cln, style)

        self.sentences = [SentencePh(param_mod, el[0], el[1], idx_snt, len(self._sentences_el_llst))
                          for (idx_snt, el) in enumerate(self._sentences_el_llst)]
