#!/bin/env python3
#-*- encoding: utf-8 -*-


import os.path
from time import process_time


def get_var_names(obj, namespace=globals()):
    """Get the variable name.
    :param obj: variable (object)
    :param namespace: default = globals()
    """
    return [name for name in namespace
            if namespace[name] is obj]


def debug_prn(stuff):
    """Print stuff for debug purposes. The name of the variable is included as header in the
    :param stuff: stuff to print
    """
    print('\n', '*DEBUG PRINT* Variable/Object name(s): ', get_var_names(stuff), '\n', stuff, '\n', sep='')


def progress_bar(item_count, total_count):
    """Show text progress bar in the console.
    """
    item_count += 2  # usually counter starts at 0 and is updated after the this call => add 2 to all item_count
    progress = int(item_count / total_count * 100)
    if progress > 100:
        progress = 100  # to ensure the counter stops at 100%
        # \r to rewind cursor
    print('\r{0}%\t[{1}{2}]'.format(progress, '#'*(progress//2), ' '*(50-(progress//2))), sep=' ', end='')


def process_status_msg(i_process, ext_in, ext_out):
    """Show text with a summary of the process if required files were found, and a error message if not.
    """
    if i_process == 0:
        print('\n\nAttention, no', '"'+ext_in+'"', 'file to process were found!\n')
    else:
        print('\n\n"'+ext_in+'"', 'file conversion done:', i_process, '"'+ext_out+'"', 'files were created.\n')


def prompt_file_exist():
    """Prompt an answer whether the existing file should be overwritten or not.
    """
    answ = input("The file already exist in the provided destination location, do you want to overwrite it?\n"
                 "Enter 'Y': yes all, 'y': yes this time, 'N': none, 'n': not this time.  Default: [N] ")
    if answ == '' or answ == 'N':
        action = 'no_to_all'
    elif answ == 'n':
        action = 'no'
    elif answ == 'y':
        action = 'yes'
    elif answ == 'Y':
        action = 'yes_to_all'
    else:
        action = 'no_to_all'

    return action


def is_int(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


def write_lst_to_file(lst, fpath, title=None, unpack_prn=False):
    """
    Write the given list to the given file, and create dir(s) if necessary.
    """
    if not os.path.exists(os.path.dirname(fpath)):
        os.makedirs(os.path.dirname(fpath))

    with open(fpath, 'w') as f:
        if title is not None:
            print(title, file=f)
        if unpack_prn is True:
            for el in lst:
                print(*el, file=f)
        else:
            for el in lst:
                print(el, file=f)


def print_process_time():
    """
    Print process time in s.
    """
    print('Processing time:', round(process_time(), 2), 's')


def boxplot_df(df, title='', out='view', fig_idx=None):
    """
    Boxplot features
    :param df: features to boxplot
    :param title: Title of the figure (default='')
    :return: bp
    """
    import matplotlib.pyplot as plt
    import os

    plt.figure(fig_idx)
    ax = df.boxplot(return_type='axes', sym='', notch=True)  # , bootstrap=100)
                        # hide outlier (symbol = '')
    plt.title(title)
    if out == 'view':
        plt.show()
    if out == 'save':
        try:
            os.mkdir('PyPlot')
        except FileExistsError:
            pass
        plt.savefig(os.path.join('PyPlot', title+'.pdf'), format='pdf')
        plt.close('all')

    return ax


def zero_pad_np(array_np, ref_np, val=None):
    """
    Pad array with zeros according to the shape of another array given as reference
    :param array_np: array to pad (1 or 2D)
    :param ref_np: reference (1 or 2D)
    """
    import numpy as np

    if val:
        padded_np = np.ones(ref_np.shape) * val
    else:
        padded_np = np.zeros(ref_np.shape)

    # To put the array_np in the center of the padded array
    init_idx = tuple(np.round((np.array(ref_np.shape) - np.array(array_np.shape)) / 2))

    if len(ref_np.shape) > 1:
        padded_np[init_idx[0]:array_np.shape[0]+init_idx[0], init_idx[1]:array_np.shape[1]+init_idx[1]] = array_np
    else:
        padded_np[init_idx[0]:array_np.shape[0]+init_idx[0]] = array_np

    return padded_np
