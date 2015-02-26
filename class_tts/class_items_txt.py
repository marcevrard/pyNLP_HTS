#!/bin/env python3
#-*- encoding: utf-8 -*-


from class_tts import Utterance, Sentence, Phrase, Word


class WordTxt(Word):
    """
    Word class with grapheme (text) input processing.
    """


class PhraseTxt(Phrase):
    """
    Phrase class with grapheme (text) input processing.
    """


class SentenceTxt(Sentence):
    """
    Utterance class with grapheme (text) input processing.

    """


class UtteranceTxt(Utterance):
    """
    Utterance class with grapheme (text) input processing.
    ** NEED TO CALL A TREETAGGER KIND OF TOKENIZER (TO DIFFERENTIATE ABBREVIATION DOT FROM END OF SENT PERIOD) **
    """

# TODO: to do advanced POS tag use a parallel tokening based on the raw input text, and add the LIMSI word list
