#!/bin/env python3
#-*- encoding: utf-8 -*-

from .class_tts_gp import Gp
from class_tts.Archives.MaybeNeeded.class_tts_extractor import PfsExtractor

from .class_ph_set import PhoneSet
from .class_items import Item, Utterance, Sentence, Phrase, Word, Syllable, Phone
from .class_items_ph import UtterancePh, SentencePh, PhrasePh, WordPh
from .class_items_txt import UtteranceTxt, SentenceTxt, PhraseTxt, WordTxt
from .class_sequence import Sequence
from .class_text_features import TextFeatures
from .class_text_features_import import TextFeaturesImport
from .class_qst import Question
# from .class_tts import Tts


# from .class_tts_synth import TtsSynthesizer
# from .class_tts_trainer import TtsTrainer

# Class import order depends on heritage hierarchy!!