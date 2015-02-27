#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Usage:  python3 /Volumes/Python/python_tts/run_tts_synth_hts.py -n limsi_fr_tat_10 -v
    Usage:  python3 /Volumes/Python/python_tts/run_tts_synth_hts.py -n limsi_fr_tat_10 -r
                    [~/Documents/at_LIMSI_BIG/CORPUS/VOCALLY/limsi_fr_jlc_2/txt_testing_corpus] (default: pwd)
"""

import sys
import importlib
import os.path
import glob
import argparse
import shutil
import readline
import subprocess

import my_defs.defs_misc as misc
import my_defs.class_history_completer as hist

from class_tts import Gp
from class_tts import TextFeatures

PARAM_BASE_LST = ['param_dir.', '.tts_const']                               # Because modules cannot be called by path
THIS_PATH = os.path.dirname(__file__)                                       # Path of the current script

HTS_PROD_PATH = os.path.expanduser('~/Desktop/DEMO_VOICE/HTS_PROD')

if sys.platform.startswith('linux'):
    WAV_PLAY = 'aplay'
else:
    WAV_PLAY = 'afplay'

HTS_PATH = '/usr/local/HTS-2.3alpha/bin/'
PROJECT_PATH = '~/Documents/at_LIMSI_BIG/STRAIGHT/HTS_DEMOs/HTS-demo_STRAIGHT_TAT8'


#   ====================================================================================================================
def debug_print(hts_lab_gen_lst, command_txt, base_fpath):
    """
    Print the HTS label file and the commands, instead of executing them.
    """
    print('\n')
    for l in hts_lab_gen_lst:
        print(l)
    print('')
    print(command_txt, '\n')

    print(WAV_PLAY + ' ' + base_fpath + '.wav', '\n')


def run_hts_eng_synth(hts_lab_gen_prn, base_fpath):
    """
    Run the hts_engine and read the output wav files.
    """
    with open(utt_gen_lab_fpath, 'w') as utt_gen_f:                         # Print utt_gen to file
        for l in hts_lab_gen_prn:
            print(l, file=utt_gen_f)

    if args.verbose:
        hts_eng_command = (
            'hts_engine -m ' + voice_fpath
            + ' -or ' + base_fpath + '.raw' + ' -ow ' + base_fpath+'.wav' + ' -ot ' + base_fpath + '.trace'
            + ' -od ' + base_fpath + '.dur' + ' -om ' + base_fpath + '.spec' + ' -of ' + base_fpath + '.lf0'
            + ' ' + utt_gen_lab_fpath + ' -r '+str(args.speed_rate)
        )
        shutil.copyfile(utt_gen_lab_fpath, base_fpath+'.lab')

    else:
        hts_eng_command = (
            'hts_engine -m '+voice_fpath + ' -ow '+base_fpath+'.wav'
            + ' ' + utt_gen_lab_fpath + ' -r '+str(args.speed_rate)
        )

    if args.debug:
        debug_print(hts_lab_gen_prn, hts_eng_command, base_fpath)

    else:
        subprocess.call(hts_eng_command, shell=True)                            # call the hts_engine API

        if not args.process_path:                                               # avoid playing if recursive synthesis

            subprocess.call(WAV_PLAY + ' ' + base_fpath + '.wav', shell=True)   # play the wav output


def run_hts_htk_synth(hts_lab_gen_prn, base_fpath):
    """
    Run the HTS and read the output wav files.
    """
    with open(utt_gen_lab_fpath, 'w') as utt_gen_f:                         # Print utt_gen to file
        for l in hts_lab_gen_prn:
            print(l, file=utt_gen_f)

    mix = '1mix'
    hts_2mix_make_unseen_mod_command = (
        os.path.join(HTS_PATH, 'HHEd') + ' -A -B -C ' +
        os.path.join(PROJECT_PATH, 'configs/qst001/ver1/trn.cnf') + ' -D -T 1 -p -i -H ' +
        os.path.join(PROJECT_PATH, 'models/qst001/ver1/cmp/re_clustered.mmf.'+mix) + ' -w ' +
        os.path.join(PROJECT_PATH, 'models/qst001/ver1/cmp/re_clustered_all.mmf.'+mix) + ' ' +
        os.path.join(PROJECT_PATH, 'edfiles/qst001/ver1/cmp/mku.hed') + ' ' +
        os.path.join(PROJECT_PATH, 'data/lists/full.list')
    )
    shutil.copyfile(utt_gen_lab_fpath, base_fpath+'.lab')

    # if args.debug:
    #     debug_print(hts_lab_gen_prn, hts_htk_command, base_fpath)
    #
    # else:
    #     os.system(hts_htk_command)                                          # call the hts_engine API
    #
    #     if not args.process_path:                                           # avoid playing if recursive synthesis
    #
    #         os.system(WAV_PLAY + ' ' + base_fpath + '.wav')             # play the wav output


def process_utt_synth(_utt, _txt_fpath):
    """
    Process the synthesis of a single utterance.
    """
    with open(_txt_fpath, 'w') as utt_f:
        print(_utt, file=utt_f)

    # **FROM ClassTts**
    # tts_obj = Tts(param_module, ph_dic='lia')                 # launch the complete TTS synthesis process FIXME
    # tts_obj.process_synthesize_hts(txt_fpath, args.style)

    utt_gp_obj = Gp(param_module, _txt_fpath, gp_opt='lia')
    utt_gp_obj.phonetize_txt_utt()
    utt_ph = utt_gp_obj.utt_ph

    # **FROM RUN_COMPO**
    utt_pfs_obj = TextFeatures(param_module, utt_ph)
    utt_pfs_obj.process_pfeats()
    utt_pfs_obj.process_lab_prn()
    # FROM RUN_COMPO

    return utt_pfs_obj


def process_interactive_synth():
    """
    Process the speech synthesis.
    Loop input prompt, write it to a file and record the input history, until a quit command is given.
    Run from the 'python_tts' main directory, e.g. /Volumes/Python/python_tts in the current system.
    """
    # utt_fpath = os.path.join(THIS_PATH, 'utt.txt')                                # TODO: delete!
    hist_fpath = os.path.join(THIS_PATH, '.completer.hist')
    quit_com = '.'

    # Register our completer function
    readline.set_completer(hist.HistoryCompleter().complete)
    # Use the tab key for completion
    readline.parse_and_bind('tab: complete')

    if os.path.exists(hist_fpath):
        readline.read_history_file(hist_fpath)

    try:
        while True:

            readline.write_history_file(hist_fpath)

            prompt_utt = input('Enter new utterance to synthesize (enter "'
                               + quit_com + '" to quit and "-cls" to clear all history): ')

            if prompt_utt == quit_com:
                readline.remove_history_item(readline.get_current_history_length()-1)
                break
            elif prompt_utt == '':
                pass

            elif prompt_utt == '-cls':
                for _ in range(readline.get_current_history_length()):                          # Remove all items
                    readline.remove_history_item(0)
            else:
                txt_fpath = cst.TXT_FPATH

                if prompt_utt[-1] not in cst.PUNCT_END:
                    prompt_utt += '.'                                       # add a '.' if end mark missing

                print("\nThe utterance:", '"' + prompt_utt.strip('\n') + '"', "is being synthesized...\n")

                utt_pfs_obj = process_utt_synth(prompt_utt, txt_fpath)

                try:
                    os.mkdir(base_gen_path)
                except FileExistsError:
                    pass

                idx = 0
                base_fpath = base_gen_fpath + '_{:04d}'.format(idx)
                while os.path.isfile(base_fpath + '.wav'):                  # iterate file names to keep history
                    idx += 1
                    base_fpath = base_gen_fpath + '_{:04d}'.format(idx)

                if args.verbose:                                            # if verbose mode on > print utt_txt to file
                    with open(base_fpath+'.txt', 'w') as f_txt:
                        print(prompt_utt, file=f_txt)

                run_hts_eng_synth(utt_pfs_obj.hts_lab_gen_prn, base_fpath)  # run synthesis

    except KeyboardInterrupt:
        print("\nExit: KeyboardInterrupt detected!")

    except EOFError:
        print("\nExit: EOF detected!")

    finally:
        readline.write_history_file(hist_fpath)
        print('')


def process_recursive_synth(proc_path):
    """
    Recursively process the file lines in the given path.
    """
    i_proc = 0
    path_in = os.path.abspath(proc_path)
    # prod_path = cst.HTS_PROD_PATH + args.style

    try:
        with open(path_in) as file_in:
            process_utt_lst = [utt for utt in file_in.readlines()]
    except IsADirectoryError:       # case path is a directory of individual files.
        process_utt_lst = []
        process_file_lst = [fname for fname in os.listdir(path_in) if '.txt' in fname]
        for fname_in in process_file_lst:
            fpath_in = os.path.join(path_in, fname_in)
            with open(fpath_in) as file_in:
                process_utt_lst.append(file_in.readline())

    print(len(process_utt_lst))

    try:
        os.mkdir(base_gen_path)
    except FileExistsError:
        pass

    for utt in process_utt_lst:
        misc.progress_bar(i_proc, len(process_utt_lst))

        if args.style != '':
            base_fpath = base_gen_fpath + '_' + args.style + '_{:04d}'.format(i_proc)
        else:
            base_fpath = base_gen_fpath + '_{:04d}'.format(i_proc)
        txt_fpath = base_fpath + '.txt'

        utt_pfs_obj = process_utt_synth(utt, txt_fpath)

        run_hts_eng_synth(utt_pfs_obj.hts_lab_gen_prn, base_fpath)

        i_proc += 1

    print('\n')                                                         # add a \n after the progress_bar


def main():

    if args.delete:
        files_lst = glob.glob(base_gen_fpath + '*')
        for f in files_lst:
            ext = os.path.splitext(f)
            if (
                ('.lab' in ext) or ('.raw' in ext) or ('.trace' in ext) or ('.txt' in ext) or ('.wav' in ext)
                or ('.dur' in ext) or ('.spec' in ext) or ('.lf0' in ext)
            ):
                try:
                    os.remove(f)
                except PermissionError:
                    print("\nWarning: "'"'+os.path.basename(f)+'"' +
                          " may be a directory and thus hasn't been deleted.")

    if args.process_path:
        process_recursive_synth(args.process_path)

    else:
        process_interactive_synth()


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='"python3 run_tts_synth_hts.py -n limsi_fr_guy -s calme -v -x"'
                                                 " Synthesize the given utterance.")

    #   -db DATABASE -u USERNAME -p PASSWORD -size 20000
    parser.add_argument('-n', '--voice_name', required=True,
                        help="Set the parameter name of the current voice.")
    parser.add_argument('-s', '--style', default='', help="Set the utterance style to synthesize.")
    parser.add_argument('-c', '--speed_rate', default='1.0', help="Set speech rate.")
    parser.add_argument('-r', '--recursive', nargs='?', const=os.getcwd(), dest='process_path',
                        help="Recursively process lines from corpus text file, given as file path.")
    parser.add_argument('-d', '--debug', action='store_true', help="Set the debug mode: print commands to screen only.")
    parser.add_argument('-v', '--verbose', action='store_true', help="Set the verbose mode to hts_engine.")
    parser.add_argument('-x', '--delete', action='store_true', help="Delete previous synthesis recordings.")
    #   parser.add_argument('-l', '--onlylab', action='store_true', help="Output only lab files, no sound.")

    args = parser.parse_args()

    voice_name_lst = args.voice_name.split('_')                         # Parse voice name with '_'
    param_name = '_'.join(voice_name_lst[0:3])                          # Param name is the root voice name

    param_module = PARAM_BASE_LST[0] + param_name + PARAM_BASE_LST[1]
    # print(param_module)     # debug
    cst = importlib.import_module(param_module)

    voice_fname = param_name + '.htsvoice'                              # Voice filename is based on the root voice name
    voice_dir = args.voice_name + '_voice'
    voice_relpath = os.path.join(voice_dir, 'qst001/ver1')

    voice_fpath = os.path.join(HTS_PROD_PATH, voice_relpath, voice_fname)
    base_gen_fname = args.voice_name + '_gen'
    gen_dir = args.voice_name + '_prod'
    base_gen_path = os.path.join(HTS_PROD_PATH, gen_dir)
    base_gen_fpath = os.path.join(base_gen_path, base_gen_fname)

    utt_gen_lab_fname = '.' + base_gen_fname + '_tmp.lab'
    utt_gen_lab_fpath = os.path.join(HTS_PROD_PATH, utt_gen_lab_fname)

    print("\nThe style {} is chosen for synthesis.\n".format(args.style))

    main()


# note: INSTALL HTS_ENGINE FOR 64bit OS: ./configure --prefix=<path_to>/hts_engine_API-1.07 CFLAGS="-m32 -g -O2 -Wall"
#   ====================================================================================================================
