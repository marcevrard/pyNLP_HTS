#!/bin/env python3
#-*- encoding: utf-8 -*-

import os.path
import csv
from collections import namedtuple


def extr_lst_from_dlst(dlst, key, convtype=None):
    """Get a list from a list of dic with all elements corresponding to a given key
    """
    lst = []
    for l_dic in dlst:
        if convtype is not None:
            if convtype == 'float':
                lst.append(float(l_dic[key]))
            if convtype == 'int':
                lst.append(int(l_dic[key]))
            if convtype == 'str':
                lst.append(str(l_dic[key]))
        else:
            lst.append(l_dic[key])

    return lst


def conv_txt_to_lst(fname, path='', sep='', title=None):
    """Read a text file and return a list with the file lines.
    :param fname: name of the text file to process.
    :param path: path of the text file (absolute or relative), default = ''
    :param sep: separation character, if '' => line are taken as is without split, default = ''
    :param title:	if "n" a positive integer is provided => the first "n" lines will be discarded,
                    if "first" or "last" values are provided the corresponding lines are dicarded,
                    if any other string is provided, the first line is discarded.
                    Default = None.
        Note: a line starting with a "#" will always be discarded!
    """
    if path != '':
        abspath = os.path.abspath(path)
        fpath = os.path.join(abspath, fname)
    else:
        fpath = fname

    with open(fpath) as ftxt:
        lines = ftxt.readlines()

    if title is not None:
        title_arg = str(title)
        if title_arg.isdigit():
            for i in range(int(title_arg)):
                lines.pop(0)
        elif 'last' in title_arg.lower():
            lines.pop()
            if 'first' in title_arg.lower():
                lines.pop(0)
        else:
            lines.pop(0)

    for i, row in enumerate(lines):
        if row[0] == '#':
            lines.pop(i)

    if sep != '':
        lines = [l.strip().split(sep) for l in lines]
    else:
        lines = [l.strip() for l in lines]

    return lines


def conv_lst_to_ddic(lst_2d, title_row=None):
    """Get a list of at least 2 column elements and possibly a title row (with n_column - 1 elts),
    return a 2D dict with the field of the first column as first keys and of the first row as second.
    :param lst_2d: 2 dimension list
    :param title_row: if any value is given as "title_row" argument, the first row of the input table will used as keys
    in the sub-dict. If no "title_row" argument is provided the sub-dict will be a simple list.
    """
    lst = lst_2d.copy()

    if title_row is not None:
        l0 = lst.pop(0)
        if len(l0) == len(lst[0]):
            l0.pop(0)
        if len(l0) != len(lst[0])-1:
            l0 = [i for i in range(len(lst[0])-1)]
            # if the length of l0 != length of the list => create num idx

        dic_2d = dict(
            (
                row[0], dict((l0[i], row[i+1]) for i in range(len(l0)))
            ) for row in lst
        )

    else:
        dic_2d = dict(
            (row[0], row[1:]) for row in lst
        )

    return dic_2d


def conv_txt_to_ddic(fname, path='', sep='', title_row=None, title_txt=None):
    """Apply txt_2_lst() and lst_2_2ddic() def in serie:
    Read a text file and return a 2D dict with the field of the first line as first keys and of the 1st row as 2nd.
    :param fname: name of the file to process.
    :param path: path of the file.
    :param sep: separation character to take into account if the line needs to be split.
    :param title_row: (see :param title_row: in :func: lst_2_2ddic())
    :param title_txt: (see :param title: in :func: txt_2_lst())
    """
    lst_2d = conv_txt_to_lst(fname, path, sep, title_txt)

    dic_2d = conv_lst_to_ddic(lst_2d, title_row)

    return dic_2d


def get_2d_dic_items(dic_2d):
    """Get all values and keys from 2D dict and return a dict of lists with the ordered unique values of the keys.
    For example get all values from a parsed xml file.
    """
    lst_out_k = []
    for row_v in dic_2d.values():
        lst_k = list(row_v.keys())
        for k in lst_k:
            if k not in lst_out_k:
                lst_out_k.append(k)

    lst_out_k.sort()

    lst_row_k = list(dic_2d.keys())
    lst_out = []
    for key in lst_out_k:
        lst_out_v = []
        for row_k in lst_row_k:
            if key in dic_2d[row_k].keys():
                v = dic_2d[row_k][key]
                if v not in lst_out_v:
                    lst_out_v.append(v)
        lst_out_v.sort()
        lst_out.append([key, lst_out_v])

    dic_out_ldic = dict(lst_out)

    return dic_out_ldic


# todo: check all and simplify (only 1 fct for all ntpl, simplify previous ones, check names...)
# todo: make a class?
def conv_csv_to_ntpl(csv_fpath, tpl_name='CsvTpl', delimit=',', quote=None):
    """
    Create namedtuple from csv file, with 1st column elements as keys.
    @return: ntpl
    """
    with open(csv_fpath) as csv_f:
        csv_itr = csv.reader(csv_f, delimiter=delimit, quotechar=quote)
        csv_llst = [l for l in csv_itr]                                         # keep a copy of csv info after closing

    fields_lst = [l[0] for l in csv_llst]
    arg_lst = [l[1] for l in csv_llst]

    _CsvTpl = namedtuple(tpl_name, fields_lst)                                   # Create a ntpl struct of rows ntpl
    ntpl = _CsvTpl(* arg_lst)

    return ntpl


def conv_csv_to_nttpl(csv_fpath, tpl_name='CsvTpl', delimit=',', quote=None):
    """
    Create tuple of namedtuple from csv file, with 1st row elements as keys.
    @return: ntpl
    """
    with open(csv_fpath) as csv_f:
        csv_itr = csv.reader(csv_f, delimiter=delimit, quotechar=quote)
        csv_llst = [l for l in csv_itr]                                         # keep a copy of csv info after closing

    fields_lst = csv_llst.pop(0)
    arg_lst = [l[1] for l in csv_llst]

    _CsvTpl = namedtuple(tpl_name, fields_lst)                                   # Create a ntpl struct of rows ntpl
    ntpl_tpl = tuple(_CsvTpl(* arg_lst) for arg_lst in csv_llst)

    return ntpl_tpl


def conv_csv_to_ntdic(csv_fpath, tpl_name='CsvTpl', delimit=',', quote=None):
    """
    Create dic of namedtuple from csv file, with the first row taken as keys.
    @return: ntpl_dic
    """
    with open(csv_fpath) as csv_f:
        csv_itr = csv.reader(csv_f, delimiter=delimit, quotechar=quote)
        csv_llst = [l for l in csv_itr]

    fields_lst = csv_llst.pop(0)

    _CsvTpl = namedtuple(tpl_name, fields_lst)

    ntpl_dic = {_CsvTpl(* args).name: _CsvTpl(* args) for args in csv_llst}

    return ntpl_dic


def conv_csv_to_2d_ntpl(csv_fpath, tpl_name='CsvTpl', delimit=',', quote=None):
    """
    Create 2D namedtuple from csv file, with the first row taken as main keys, and 1st column elements as nested keys.
    @return: ntpl_2d
    """
    with open(csv_fpath) as csv_f:
        csv_itr = csv.reader(csv_f, delimiter=delimit, quotechar=quote)
        csv_llst = [l for l in csv_itr]                                     # keep a copy of csv info after closing

    row_fields_lst = csv_llst.pop(0)

    tpl_name_el = tpl_name + 'El'
    _CsvTplEl = namedtuple(tpl_name_el, row_fields_lst)                     # Create a ntpl structure for all rows

    col_fields_lst = [l[0] for l in csv_llst]
    _CsvTpl = namedtuple(tpl_name, col_fields_lst)                          # Create a ntpl struct of rows ntpl

    ntpl_2d = _CsvTpl(* [_CsvTplEl(* args) for args in csv_llst])

    return ntpl_2d


def conv_csv_to_ldic(csv_fpath, delimit=',', quote=None):
    """
    Convert a csv to a dic of list: values = rows, keys = first column.
    @return: ldic
    """
    with open(csv_fpath) as csv_f:
        csv_itr = csv.reader(csv_f, delimiter=delimit, quotechar=quote)
        csv_lst = [row for row in csv_itr if row[0][0] != '#']              # discard row starting with '#' (comments)

        if len(csv_lst[0]) == 2:
            ldic = dict((row[0], row[1]) for row in csv_lst)
        else:
            ldic = dict((row[0], row[1:]) for row in csv_lst)

        return ldic


def conv_csv_to_ttpl(csv_fpath, delimit=',', quote=None):
    """
    Convert a csv file or a simple list in ttpl or simple tpl.
    @return:
    """
    with open(csv_fpath) as csv_f:
        csv_itr = csv.reader(csv_f, delimiter=delimit, quotechar=quote)
        csv_ttpl = tuple(tuple(el for el in row) for row in csv_itr if row[0] != '#')

        if len(csv_ttpl[0]) == 1:
            csv_ttpl = tuple(row[0] for row in csv_ttpl)

        return csv_ttpl


def transp_dlst_to_ldic(dlst):
    """
    Convert list of dict to dict of list.
    """
    ldic = {}
    for key in dlst[0]:
        ldic[key] = [dic[key] for dic in dlst]

    return ldic


def transp_ldic_to_dlst(ldic, conv_str=None):
    """
    Convert dict of lists to list of dicts.
    """
    dlst = []
    a_key = list(ldic.keys())[0]

    if conv_str is not None:
        for (l_idx, _) in enumerate(ldic[a_key]):
            dic = {key: ldic[key][l_idx] for key in ldic}
            dlst.append(dic)
    else:
        for (l_idx, _) in enumerate(ldic[a_key]):
            dic = {key: str(ldic[key][l_idx]) for key in ldic}
            dlst.append(dic)

    return dlst


def transp_llst(llst):
    """
    Transpose list of lists.
    """
    llst_tild = [
        [row[i] for row in llst]
        for (i, el) in enumerate(llst[0])
    ]

    return llst_tild


def transp_ttpl(ttpl):
    """
    Transpose tuple of tuples.
    """
    ttpl_tild = tuple(
        tuple(row[i] for row in ttpl)
        for (i, el) in enumerate(ttpl[0])
    )

    return ttpl_tild


def conv_obj_ldic(obj, key_lst=None):
    """
    Convert an object into a dictionary according to the key list values if provided.
    """
    if key_lst is None:
        return obj.__dict__

    else:
        ldic = {}
        for key in key_lst:
            ldic[key] = getattr(obj, key)
        return ldic


def conv_llist_to_dlst(llst, fieldnames=None):
    """
    Convert an list of lists (or tuple of tuples) into a list of dicts using the fieldnames.
    """
    dlst = []
    for row in llst:
        dlst.append(dict(zip(fieldnames, row)))

    return dlst
