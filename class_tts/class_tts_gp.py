#!/bin/env python3
#-*- encoding: utf-8 -*-

import importlib
import subprocess as subp


#======================================================================================================================#
class Gp:
    """
    TTS GP class.
    """
    def __init__(self, param_module, txt_fpath, gp_opt='syll_lia'):

        self.cst = importlib.import_module(param_module)

        if gp_opt == 'syll_lia':                        # TODO: manage the conversion within python (instead of seltts)
            self._GP_OPTION = self.cst.GP_OPT_SYLL_LIA  # TODO... control also version of allophone.fr.xml
        else:
            self._GP_OPTION = self.cst.GP_OPTION_LIA

        self.utt_ph_tpl = ()                            # QQ: if attr init here, its val erased if sub-class called?

        self.txt_fpath = txt_fpath
        self.utt_ph = ''

    def phonetize_txt_utt(self):
        """
        Call the phonetizer to tokenize and transcribe the utt from text to phonemes.
        The text utt to convert is always stored in a file for convenience (see get_text(self) method).
        txt_fpath: path to the text utt to convert.
        @return self.utt_ph_tpl and print to file=self.UTT_FPATH
        """
        ph_command = self.cst.GP_F_PATH + ' ' + self._GP_OPTION + ' ' + self.txt_fpath

        with subp.Popen(ph_command, shell=True, stdout=subp.PIPE) as proc:
            self.utt_ph = proc.stdout.read()						# get the phonetized lines
        self.utt_ph = bytes(self.utt_ph).decode('utf-8')			# conv. B into str (bytes() added to solve warning)

        with open(self.cst.UTT_FPATH, 'w') as utt_fpath:            # to keep a written copy of the raw phonetization
            print(self.utt_ph, file=utt_fpath)
