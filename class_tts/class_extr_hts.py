#!/bin/env python3
#-*- encoding: utf-8 -*-

import importlib

#import class_tts.class_tts_extractor as classExtr      # TODO: replace by classTrain() and change global structure
import my_defs.defs_list as Lst
from class_tts import PfsExtractor


#======================================================================================================================#
class PfsExtractorHts(PfsExtractor):
    """
    TTS training based on sps label files, main class.
    """
                    # dirin, dirout non-def. since depend on conv type
    def __init__(self, param_module, utt_total_mix):
        """
        Initializes, gives the absolute path of the files to process and give parameters.
        """
        self.cst = importlib.import_module(param_module)

        super().__init__(param_module, utt_total_mix)
        # super(SpsLabeler, self).__init__(file_in, param_mod)
        # super(SpsFeatExtractor, self).__init__(file_in, param_mod)

        self.hts_lab_gen_prn = []
        self.hts_lab_mono_ttpl = ()
        self.hts_lab_mono_prn = ()
        self.hts_lab_full_prn = ()
        self.proc_fts_dlst = []
        self.fts_code_tpl = ()
        self.hts_utt_qst_tpl = ()
        self.hts_qst_tpl = ()

#== = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =#
    def conv_time_scale(self, conv_keys_lst, scale):
        """
        Apply the scale to time in data_dlst.
        """
        for key in conv_keys_lst:
            self.proc_fts_ldic[key] = tuple(
                '{0:.0f}'.format(float(el) * scale) for el in self.proc_fts_ldic[key]
            )

    def gen_hts_lab_mono(self, data_dlst):
        """
        Generate the mono lab content (hts timed lab) according to HTS standards.
        """
        time_fields_lst = [self.cst.SPS_FIELDS_LST[0], self.cst.SPS_FIELDS_LST[1]]
                                # FIELD: start / end position

        for field in time_fields_lst:
            self.proc_fts_ldic[field] = Lst.extr_lst_from_dlst(data_dlst, field)

        scale = 1E7
        self.conv_time_scale(time_fields_lst, scale)

        chosen_fields_lst = [self.cst.SPS_FIELDS_LST[0], self.cst.SPS_FIELDS_LST[1], 'phone']

        self.hts_lab_mono_ttpl =\
            Lst.transp_ttpl(
                tuple(
                    tuple(self.proc_fts_ldic[field]) for field in chosen_fields_lst
                )
            )
        self.hts_lab_mono_prn = tuple(' '.join(l) for l in self.hts_lab_mono_ttpl)

    def gen_hts_lab_full(self):
        """
        Generate the full lab content (timing + hts gen lab) according to HTS standards.
        """
        hts_lab_time_prn = tuple(' '.join(l[0:2]) for l in self.hts_lab_mono_ttpl)

        self.gen_hts_lab_fts()

        self.hts_lab_full_prn = [' '.join((l_time, l_gen)) for (l_time, l_gen)
                                 in zip(hts_lab_time_prn, self.hts_lab_gen_prn)]

#== = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =#
    def gen_hts_lab_fts(self):
        """
        Generate the generic lab content (pfeats) according to HTS standards.
        """
        proc_fts_dlst = Lst.transp_ldic_to_dlst(self.proc_fts_ldic)

        # TODO: take it from a file with the sorted list of the fts according to hts or mary standard
        ph_fts_tpl = ('prev_prev_phone', 'prev_phone', 'phone', 'next_phone', 'next_next_phone')

        fts_tpl = ph_fts_tpl + self.cst.USED_HMM_FTS_TPL

        self.fts_code_tpl = tuple('f'+str(idx) for (idx, el) in enumerate(self.cst.USED_HMM_FTS_TPL))

        for proc_fts_dic in proc_fts_dlst:
            lab_gen_ph = (
                proc_fts_dic[fts_tpl[0]] + '^' + proc_fts_dic[fts_tpl[1]] + '-' + proc_fts_dic[fts_tpl[2]] + '+' +
                proc_fts_dic[fts_tpl[3]] + '=' + proc_fts_dic[fts_tpl[4]] + '|'
            )
            lab_gen_hmm = '|'
            for idx in range(len(ph_fts_tpl), len(fts_tpl)):
                lab_gen_hmm += self.fts_code_tpl[idx-len(ph_fts_tpl)] + '=' + proc_fts_dic[fts_tpl[idx]] + '|'

            self.hts_lab_gen_prn.append(lab_gen_ph + lab_gen_hmm + '|')
            # self.hts_lab_gen_prn.append(lab_gen_ph + '|')                   # \TEMP DE:

#======================================================================================================================#
# QS "f0=0" 	{*|f0=0|*}
# QS "f0=1" 	{*|f0=1|*}
# QS "f0=2" 	{*|f0=2|*}

    def gen_hts_utt_qst(self):
        """
        Generate the HTS utt question file.
        """
        self.fts_code_tpl = tuple('f'+str(idx) for (idx, el) in enumerate(self.cst.USED_HMM_FTS_TPL))

        for idx, ft in enumerate(self.cst.USED_HMM_FTS_TPL):
            for val in self.fts_used_val_ldic[ft]:
                self.hts_utt_qst_tpl += ('QS "' + self.fts_code_tpl[idx] + '=' + val + '"' + '\t' +
                                         '{*|' + self.fts_code_tpl[idx] + '=' + val + '|*}',)
            self.hts_utt_qst_tpl += ('',)

    def gen_hts_qst_hed(self):
        """
        Generate the HTS question file.
        """
        self.gen_hts_utt_qst()

        for ph in self.fts_used_val_ldic['phone']:
            if ph != '0':
                self.hts_qst_tpl += (
                    'QS "prev_prev_phone=' + ph + '"\t\t{' + ph + '^*}',
                    'QS "prev_phone=' + ph + '"\t\t{*^' + ph + '-*}',
                    'QS "phone=' + ph + '"\t\t\t{*-' + ph + '+*}',
                    'QS "next_phone=' + ph + '"\t\t{*+' + ph + '=*}',
                    'QS "next_next_phone=' + ph + '"\t\t{*=' + ph + '||*}',
                )
                self.hts_qst_tpl += ('',)

        for ft in self.ph_set_fts_val_ldic:
            if 'phone' not in ft:
                for val in self.ph_set_fts_val_ldic[ft]:
                    if val == '0':
                        hts_qst_ph_tpl = tuple(ph for ph in self.ph_set_ddic
                                               if ft not in self.ph_set_ddic[ph])
                    else:
                        hts_qst_ph_tpl = tuple(ph for ph in self.ph_set_ddic
                                               if ft in self.ph_set_ddic[ph] and self.ph_set_ddic[ph][ft] == val)
                    hts_qst_ph_pr_pr = '^*,'.join(hts_qst_ph_tpl)
                    hts_qst_ph_pr = '-*,*^'.join(hts_qst_ph_tpl)
                    hts_qst_ph = '+*,*-'.join(hts_qst_ph_tpl)
                    hts_qst_ph_nx = '=*,*+'.join(hts_qst_ph_tpl)
                    hts_qst_ph_nx_nx = '||*,*='.join(hts_qst_ph_tpl)
                    self.hts_qst_tpl += (
                        'QS "prev_prev_' + ft + '=' + val + '"\t\t{' + hts_qst_ph_pr_pr + '^*}',
                        'QS "prev_' + ft + '=' + val + '"\t\t{*^' + hts_qst_ph_pr + '-*}',
                        'QS "ph_' + ft + '=' + val + '"\t\t{*-' + hts_qst_ph + '+*}',
                        'QS "next_' + ft + '=' + val + '"\t\t{*+' + hts_qst_ph_nx + '=*}',
                        'QS "next_next_' + ft + '=' + val + '"\t\t{*=' + hts_qst_ph_nx_nx + '||*}',
                    )
                    self.hts_qst_tpl += ('',)

        self.hts_qst_tpl += self.hts_utt_qst_tpl

#======================================================================================================================#
# ## TRAINING ACCORDING TO MARY VOICEIMPORT TOOL
#
#     def gen_hts_lab_mono(self):                                 # TODO: replace lab file from SpsConv() by this one
#         """
#         Generate the monophone lab file for HTS.
#         """
#
#     def prepare_voice_data(self):
#         """
#         Prepare voice data, as in HMMVoiceDataPreparation() of MaryTTS.
#         """
#
#     def config_voice_data(self):
#         """
#         Run configure in the main hts folder, as in HMMVoiceConfigure() of MaryTTS.
#
#         ./configure
#          --with-tcl-search-path=/usr/bin
#          --with-sptk-search-path=/home/marc/marytts-master/lib/external/bin
#          --with-hts-search-path=/home/marc/marytts-master/lib/external/bin
#          --with-hts-engine-search-path=/usr/bin
#          --with-sox-search-path=/usr/bin
#          SPEAKER=mgm_20131203
#          DATASET=limsi_fr_mgxx
#          LOWERF0=40
#          UPPERF0=280
#          VER=1
#          QNUM=001
#          FRAMELEN=400
#          FRAMESHIFT=80
#          WINDOWTYPE=1
#          NORMALIZE=1
#          FFTLEN=512
#          FREQWARP=0.42
#          GAMMA=0
#          MGCORDER=34
#          STRORDER=5
#          STRFILTERNAME=filters/mix_excitation_5filters_99taps_16Kz.txt
#          LNGAIN=1
#          SAMPFREQ=16000
#          NSTATE=5
#          NITER=5
#         """
#
#======================================================================================================================#