#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#   Usage:  python3 /Volumes/Python/python_tts/run_compos_class.py -n limsi_fr_tat -e -l -s colere
#   From:   /Users/mev/Documents/_LIMSI_MEDIA/CORPUS/TATIANA
#


import os
import argparse
import random

import my_defs.defs_list as lst
import my_defs.defs_misc as misc

from class_tts import TextFeatures
from class_tts import Gp
from class_tts import Question


# LAB_RAW_DIR = 'LAB_EHMM/lab_auto_2'
LAB_RAW_DIR = 'ehmm/lab'
# LAB_RAW_DIR = 'LAB_EHMM/lab_gp_modified/lab_tat_schwa_less'
# LAB_DIR = 'LAB/lab_auto_2'
LAB_DIR = 'LAB/lab'

# Note: manual labelling => we used a phonetized bases to apply the GP only for conversion ('syll_lia')
# TXT_DIR = 'TXT/txt'
# TXT_DIR = 'PHONE/ph_gp_bin_schwa_less'
TXT_DIR = 'txt'
PH_DIR = 'ph'
GP_LIA = 'lia'
GP_SYL = 'syll_lia'

DATA_DIR = 'DATA_HTS'
LABELS_DIR = 'labels'
GEN_DIR = 'gen'
FULL_DIR = 'full'
MONO_DIR = 'mono'
QST_DIR = 'questions'

PARAM_BASE_LST = ['param_dir.', '.tts_const']                                 # Because module cannot be called by path

PICK_NUM = 100


def process_ehmm_lab(_lab_fname):     # TODO: put the function in a class of the project.
    """
    Convert eHMM lab file to the HTS required format: 'ph', 'start', 'stop'.
    """
    lab_raw_fpath = os.path.join(LAB_RAW_DIR, _lab_fname)
    lab_out_fpath = os.path.join(LAB_DIR, _lab_fname)

    with open(lab_raw_fpath) as lab_raw_f:
        lab_ttpl = tuple(tuple(l.strip('\n').split(' ')) for l in lab_raw_f if '#' not in l)

    lab_ttpl_tild = lst.transp_ttpl(lab_ttpl)
    start_time_tpl = ('0',) + lab_ttpl_tild[0][:-1]

    # phone_tpl = tuple(ph if ph != 'ssil' else 'pau' for ph in lab_ttpl_tild[2])     # convert ssil to pau
    phone_tpl = tuple(ph for ph in lab_ttpl_tild[2])                                # no ssil conversion
    start_time_tpl = tuple(str(int(float(el)*1e7)) for el in start_time_tpl)
    stop_time_tpl = tuple(str(int(float(el)*1e7)) for el in lab_ttpl_tild[0])

    lab_out_ttpl_tild = (phone_tpl, start_time_tpl, stop_time_tpl)
    lab_out_ttpl = lst.transp_ttpl(lab_out_ttpl_tild)

    misc.write_lst_to_file(lab_out_ttpl, lab_out_fpath, title='phone start stop', unpack_prn=True)


def process_hts_lab(_lab_fname, _gen_on, style):
    """
    Process to obtain the hts lab files.
    """
    fbase = os.path.splitext(_lab_fname)[0]
    if style != '':
        fbase_split = fbase.split('_')
        # noinspection PyTypeChecker
        fbase_style = '_'.join(fbase_split[0:3]) + '_' + style + '_' + '_'.join(fbase_split[3:])
    else:
        fbase_style = fbase
    lab_fpath = os.path.join(LAB_DIR, _lab_fname)
    mono_fpath = os.path.join(DATA_DIR, LABELS_DIR, MONO_DIR, fbase_style+'.lab')
    gen_fpath = os.path.join(DATA_DIR, LABELS_DIR, GEN_DIR, fbase_style+'.lab')
    full_fpath = os.path.join(DATA_DIR, LABELS_DIR, FULL_DIR, fbase_style+'.lab')

    time_nttpl = lst.conv_csv_to_nttpl(lab_fpath, 'LabTpl', delimit=' ')

    txt_fpath = os.path.join(TXT_IN_DIR, fbase+'.txt')

    utt_gp_obj = Gp(param_module, txt_fpath, gp_opt=GP_OPT)
    utt_gp_obj.phonetize_txt_utt()
    utt_ph = utt_gp_obj.utt_ph

    utt_pfs_obj = TextFeatures(param_module, utt_ph, time_nttpl, style)
    utt_pfs_obj.process_pfeats()
    utt_pfs_obj.process_lab_prn()

    misc.write_lst_to_file(utt_pfs_obj.hts_lab_mono_prn, mono_fpath)
    misc.write_lst_to_file(utt_pfs_obj.hts_lab_full_prn, full_fpath)
    if _gen_on:
        misc.write_lst_to_file(utt_pfs_obj.hts_lab_gen_prn, gen_fpath)


def process_qst(_lab_fname, style):    # TODO: very similar fct to process_hts_lab(_lab_fname) => rewrite Question(obj)
    """
    Process to obtain the hts lab files.
    """
    lab_fbase = os.path.splitext(_lab_fname)[0]
    lab_fpath = os.path.join(LAB_DIR, _lab_fname)

    time_nttpl = lst.conv_csv_to_nttpl(lab_fpath, 'LabTpl', delimit=' ')

    txt_fpath = os.path.join(TXT_IN_DIR, lab_fbase+'.txt')

    utt_gp_obj = Gp(param_module, txt_fpath, gp_opt=GP_OPT)
    utt_gp_obj.phonetize_txt_utt()
    utt_ph = utt_gp_obj.utt_ph

    utt_pfs_obj2 = TextFeatures(param_module, utt_ph, time_nttpl, style)
    utt_pfs_obj2.process_pfeats()
    utt_pfs_obj2.process_lab_prn()

    qst_obj = Question(param_module, utt_pfs_obj2)   # FIXME: wrong solution to pass obj this way?
    qst_obj.process_qst_data()

    misc.write_lst_to_file(qst_obj.hts_qst_utt_tpl, os.path.join(DATA_DIR, QST_DIR, 'questions_utt_qst001.hed'))
    misc.write_lst_to_file(qst_obj.hts_qst_tpl, os.path.join(DATA_DIR, QST_DIR, 'questions_qst001.hed'))


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='"python3 run_compos_class.py -n limsi_fr_tat"'
                                                 " Produce the hts lab files and the qst files.")
    parser.add_argument('-n', '--param_name', required=True,
                        help="Set the parameter name of the current voice.")
    parser.add_argument('-e', '--lab_ehmm', action='store_true', help="If -e: convert the ehmm lab to required format.")
    parser.add_argument('-l', '--lab_hts', action='store_true', help="If -l: process to obtain hts lab and qst files.")
    parser.add_argument('-p', '--ph_in', action='store_true', help="If -p: use manuel phonetized input instead of txt.")
    parser.add_argument('-s', '--style', default='', help="Set the style value, default Null.")
    args = parser.parse_args()

    param_name = args.param_name
    param_module = PARAM_BASE_LST[0] + param_name + PARAM_BASE_LST[1]

    # ph_set_obj = PhoneSet(Cst.PH_SET_FPATH)

    # By default use text input and fully phonetize it.
    TXT_IN_DIR = TXT_DIR
    GP_OPT = GP_LIA

    # Use already phonetized text (e.g. case of manual labeling).
    if args.ph_in:
        TXT_IN_DIR = PH_DIR
        GP_OPT = GP_SYL

    # **CONVERT EHMM LAB FILES**
    if args.lab_ehmm:
        process_lab_lst = [fname for fname in os.listdir(LAB_RAW_DIR) if '.lab' in fname]
        for lab_fname in process_lab_lst:
            process_ehmm_lab(lab_fname)

    # **CREATE LAB FILES**
    if args.lab_hts:

        fname_filter = ''
        # fname_filter = 'limsi_fr_tat_0001'

        # 2014-05-08
        # process_lab_lst = [fname for fname in os.listdir(LAB_RAW_DIR) if '.lab' in fname and fname_filter in fname]
        process_lab_lst = [fname for fname in os.listdir(LAB_DIR) if '.lab' in fname and fname_filter in fname]

        # Select randomly some sentence from the corpus to be used as synth test.
        process_gen_lst = random.sample(process_lab_lst, PICK_NUM)
        process_gen_lst.sort()

        if args.style != '':
            DATA_DIR = DATA_DIR + '_' + args.style

        try:
            with open(os.path.join(DATA_DIR, 'gen.scp')) as gen_f:
                gen_lst = [fpath.strip('\n') for fpath in gen_f]
                process_gen_lst = [os.path.split(fpath)[1] for fpath in gen_lst]
        except FileNotFoundError:
            os.mkdir(DATA_DIR)
            with open(os.path.join(DATA_DIR, 'gen.scp'), 'w') as gen_w_f:
                for fname in process_gen_lst:
                    print(fname, file=gen_w_f)

        i_proc = 0

        for lab_fname in process_lab_lst:

            misc.progress_bar(i_proc, len(process_lab_lst))
            i_proc += 1

            # Process all mono and full lab files, and the selected gen lab files
            try:
                gen_on = False
                if lab_fname in process_gen_lst:
                    gen_on = True
                process_hts_lab(lab_fname, gen_on, args.style)
            except AttributeError:
                print(lab_fname)

        # **CREATE QST FILES**
        process_qst(process_lab_lst[0], args.style)

        print('')
        misc.print_process_time()
