#!/bin/env python3
#-*- encoding: utf-8 -*-

import importlib
from collections import namedtuple
import re
import os.path

import my_defs.defs_list as Lst
from class_tts import PhoneSet


#======================================================================================================================#
class TextFeaturesImport:
    """
    Class providing the extraction parameters.
    """
    def __init__(self, param_module, style=''):

        self.param_module = param_module

        self.cst = importlib.import_module(param_module)

        self.style = style

        self._ImportedFtsNTpl = namedtuple('ImportedFtsNTpl', self.cst.IMPORT_LAB_FIELDS)
        self.imported_fts_ntpl = None

        self._PH_SET_BASE_PARAM_TPL = ()
        self._PH_SET_ALL_PARAM_TPL = ()
        self._ALL_PFEATS_TPL = ()
        self._USED_PFEATS_TPL = ()

        self.ph_set_obj_tpl = ()
        self._proc_ldic = {}
        self._hts_lab_mono_ttpl = ()
        self.hts_lab_gen_prn = ()
        self.hts_lab_mono_prn = ()
        self.hts_lab_full_prn = ()

    def __str__(self):
        """
        Get all Phone Features as a ...?
        """
        tpl = ()
        for ft in self._USED_PFEATS_TPL:
            try:                                                                    # debug print
                tpl += (ft, ' '.join([str(el) for el in getattr(self, ft)]))
            except AttributeError:
                print("\nError: the "+"'"+ft+"'"+" phone feature is not present in the standard phone feature list!\n")
            except TypeError:
                print("\nError: the "+"'"+ft+"'"+" phone feature has not been processed yet!\n")

        return '\n'.join(tpl)

# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =#
    def get_imported_fts_from_hts_lab(self, lab_fpath):
        """
        Parse and import features from a HTS label file.
        """
        time = '([0-9]{1,9})'                                           # Start and stop time fields
        ph = '([a-zA-Z0-9_]{1,3})'                                      # Phones: letters or numbers or '_' from 1 to 3
        # vowel = '([a-zA-Z0-9]{1,10})'                                   # Current syllable vowel "novowel"
        n1 = '([0-9x])'                                                 # Numbers: small values (only 1 digit) or 'x'
        n2 = '([0-9x]{1,2})'                                            # Numbers: big values (up to 2 digits) or 'x'
        pos = '(content|0|x|darC|ppeCNC|ppeC|prpCNC|conCNC|dpoC|preC|prpAL|pdeC|ddeC|dintC|prpAL|autreAL)'
        # pos = '([a-zA-Zx0]{1,11})'
        tobi = '([LH%0\-]{1,4})'                                        # ToBI

        parser = re.compile(
            time + '[ ]' + time + '[ ]' +
            ph + '\^' + ph + '-' + ph + '\+' + ph + '=' + ph + '@' + n1 + '_' + n1
            + '/A:' + n1 + '_' + n1 + '_' + n1
            + '/B:' + n1 + '-' + n1 + '-' + n1 + '@' + n2 + '-' + n2 + '&' + n2 + '-' + n2 + '\$' + n2 + '-' + n2
            + '!' + n2 + '-' + n2 + ';' + n2 + '-' + n2 + '\|' + ph  # vowel
            + '/C:' + n1 + '\+' + n1 + '\+' + n1
            + '/D:' + pos + '_' + n1
            + '/E:' + pos + '\+' + n1 + '@' + n2 + '\+' + n2 + '&' + n2 + '\+' + n2 + '#' + n2 + '\+' + n2
            + '/F:' + pos + '_' + n1
            + '/G:' + n2 + '_' + n2
            + '/H:' + n2 + '=' + n2 + '\^' + n1 + '=' + n1 + '\|' + tobi
            + '/I:' + n2 + '=' + n2
            + '/J:' + n2 + '\+' + n2 + '-' + n1
            + '\n'
        )

        imported_fts_ttpl = ()
        with open(lab_fpath) as lab_f:
            idx = 0
            for line in lab_f.readlines():
                idx += 1
                match_obj = parser.match(line)
                # print(match_obj.groups())   # debug

                try:
                    imported_fts_ttpl += (match_obj.groups(),)
                except AttributeError:
                    print('AttributeError in', os.path.basename(lab_fpath), 'file, line', idx, '!')

            self.imported_fts_ntpl = self._ImportedFtsNTpl(*Lst.transp_ttpl(imported_fts_ttpl))

    def set_imported_fts_to_attr(self):
        """
        Set object attributes with imported feature values if present in the used list.
        """
        # noinspection PyProtectedMember
        imported_fts_fields = self.imported_fts_ntpl._fields
        for ft_out in self.cst.USED_HMM_FTS_TPL:
            for ft_in in imported_fts_fields:
                if ft_out == ft_in.lstrip('abcdefghijkp0123456789').lstrip('_'):                # remove leading code
                    setattr(self, ft_out, getattr(self.imported_fts_ntpl, ft_in))

        for ft in ['start', 'end']:                                                             # add time data
            setattr(self, ft, getattr(self.imported_fts_ntpl, 'p0_'+ft))

    def conv_pos_ft_val(self):
        """
        Convert pos values different from 'content' (or nul_val) to 'function'.
        """
        for ft in self.cst.USED_HMM_FTS_TPL:
            if 'gpos' in ft:
                setattr(self, ft,
                        tuple(el if el in ['content', 'x', '0'] else 'function' for el in getattr(self, ft)))

    def set_ph_to_seq_attr(self):     # FIXME: hack
        """
        Temporary trick to use TextFeatures as is.
        """
        self.ph_set_obj_tpl = ()
        for phone in self.imported_fts_ntpl.p3_phone:
            self.ph_set_obj_tpl += (PhoneSet(self.param_module, self.cst.PH_SET_FPATH, phone),)

        # Set the _PH_SET_PARAM_TPL reference tuple
        def set_ph_set_param_tpl(ft_prefix=''):
            return tuple(ft_prefix+ft_base for ft_base in self.ph_set_obj_tpl[0].get_ph_set_param_dic()
                         if ft_base != 'ph')

        self._PH_SET_BASE_PARAM_TPL = set_ph_set_param_tpl()
        self._PH_SET_ALL_PARAM_TPL = self._PH_SET_BASE_PARAM_TPL

        if self.cst.NUMBER_PHONES > 1:
            self._PH_SET_ALL_PARAM_TPL += set_ph_set_param_tpl('prev_')
            self._PH_SET_ALL_PARAM_TPL += set_ph_set_param_tpl('next_')
            if self.cst.NUMBER_PHONES > 3:
                self._PH_SET_ALL_PARAM_TPL += set_ph_set_param_tpl('prev_prev_')
                self._PH_SET_ALL_PARAM_TPL += set_ph_set_param_tpl('next_next_')

        self._ALL_PFEATS_TPL = self._PH_SET_ALL_PARAM_TPL + self.cst.ALL_HMM_FTS_TPL
        self._USED_PFEATS_TPL = self._PH_SET_ALL_PARAM_TPL + self.cst.USED_HMM_FTS_TPL + tuple(['start', 'end'])

    def proc_prev_ph_tpl(self, ft, nul_val):      # TODO change to phoneme!!
        """
        Return the previous phone.
        """
        return (nul_val,) + getattr(self, ft)[:-1]

    def proc_next_ph_tpl(self, ft, nul_val):        # TODO change to phoneme!!
        """
        Return the previous phone.
        """
        return getattr(self, ft)[1:] + (nul_val,)

    def proc_ph_set_fts(self, nul_val, prv_nxt=''):
        """
        Process all phone set features.
        """
        for ft in self._PH_SET_BASE_PARAM_TPL:
            if ft != 'ph':
                if prv_nxt == 'prev_':
                    setattr(self, prv_nxt+ft,
                            (nul_val,) + tuple(getattr(ph_set_obj, ft)
                                               for ph_set_obj in self.ph_set_obj_tpl[:-1]))
                elif prv_nxt == 'next_':
                    setattr(self, prv_nxt+ft,
                            tuple(getattr(ph_set_obj, ft)
                                  for ph_set_obj in self.ph_set_obj_tpl[1:]) + (nul_val,))
                elif prv_nxt == 'prev_prev_':
                    setattr(self, prv_nxt+ft,
                            (nul_val, nul_val) + tuple(getattr(ph_set_obj, ft)
                                                       for ph_set_obj in self.ph_set_obj_tpl[:-2]))
                elif prv_nxt == 'next_next_':
                    setattr(self, prv_nxt+ft,
                            tuple(getattr(ph_set_obj, ft)
                                  for ph_set_obj in self.ph_set_obj_tpl[2:]) + (nul_val, nul_val))
                else:
                    setattr(self, prv_nxt+ft,
                            tuple(getattr(ph_set_obj, ft) for ph_set_obj in self.ph_set_obj_tpl))

    def process_import_hts_fts(self, lab_fpath):
        """
        Complete process of importing the fts from HTS lab files.
        """
        self.get_imported_fts_from_hts_lab(lab_fpath)
        self.set_imported_fts_to_attr()
        self.conv_pos_ft_val()
        self.set_ph_to_seq_attr()

# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =#
    def process_pfeats(self):
        """
        Process all used hmm phone features.
        """
        ## PHONE HORIZON FTS: PROCESS CURRENT 'PHONE' (A)
        setattr(self, 'phone', tuple(ph for ph in self.imported_fts_ntpl.p3_phone))

        # Process current phone set features
        self.proc_ph_set_fts(self.cst.NULL_VAL)

        ## PHONE HORIZON FTS: (B, C)

        if self.cst.NUMBER_PHONES > 1:

            setattr(self, 'prev_phone', self.proc_prev_ph_tpl('phone', self.cst.PAU))
            setattr(self, 'next_phone', self.proc_next_ph_tpl('phone', self.cst.PAU))
            self.proc_ph_set_fts(self.cst.NULL_VAL, 'prev_')
            self.proc_ph_set_fts(self.cst.NULL_VAL, 'next_')

            if self.cst.NUMBER_PHONES > 3:

                setattr(self, 'prev_prev_phone', self.proc_prev_ph_tpl('prev_phone', self.cst.PAU))
                setattr(self, 'next_next_phone', self.proc_next_ph_tpl('next_phone', self.cst.PAU))
                self.proc_ph_set_fts(self.cst.NULL_VAL, 'prev_prev_')
                self.proc_ph_set_fts(self.cst.NULL_VAL, 'next_next_')

# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =#
    def gen_hts_lab_fts(self):
        """
        Generate the generic lab content (pfeats) according to HTS standards.
        """
        if self.cst.NUMBER_PHONES > 1:
            ph_fts_tpl = ('prev_phone', 'phone', 'next_phone')
            if self.cst.NUMBER_PHONES > 3:
                ph_fts_tpl = ('prev_prev_phone', 'prev_phone', 'phone', 'next_phone', 'next_next_phone')
        else:
            ph_fts_tpl = ('phone',)
        fts_tpl = ph_fts_tpl + self.cst.USED_HMM_FTS_TPL

        self._proc_ldic = Lst.conv_obj_ldic(self, fts_tpl + tuple(['start', 'end']))   # FIXME +(['start', 'end']) messy
        proc_fts_dlst = Lst.transp_ldic_to_dlst(self._proc_ldic, conv_str=True)        # FIXME conv el to string

        # for el in proc_fts_dlst:   # debug
        #     for key in el:
        #         print(key, el[key])
        # for el in proc_fts_dlst:   # debug
        #     print(el)

        # TODO: take it from a file with the sorted list of the fts according to hts or mary standard

        fts_code_tpl = tuple('f'+str(idx) for (idx, _) in enumerate(self.cst.USED_HMM_FTS_TPL))

        self.hts_lab_gen_prn = ()

        for proc_fts_dic in proc_fts_dlst:
            if self.cst.NUMBER_PHONES > 1:
                lab_gen_ph = (
                    proc_fts_dic[fts_tpl[0]] + '-' + proc_fts_dic[fts_tpl[1]] + '+'
                    + proc_fts_dic[fts_tpl[2]] + '|'
                )
                if self.cst.NUMBER_PHONES > 3:
                    lab_gen_ph = (
                        proc_fts_dic[fts_tpl[0]] + '^' + proc_fts_dic[fts_tpl[1]] + '-' + proc_fts_dic[fts_tpl[2]] + '+'
                        + proc_fts_dic[fts_tpl[3]] + '=' + proc_fts_dic[fts_tpl[4]] + '|'
                    )
            else:
                lab_gen_ph = (
                    proc_fts_dic[fts_tpl[0]] + '|'
                )

            lab_gen_hmm = '|'
            for idx in range(len(ph_fts_tpl), len(fts_tpl)):
            # print(fts_code_tpl, proc_fts_dic)    # debug
                lab_gen_hmm += str(fts_code_tpl[idx-len(ph_fts_tpl)]) + '=' + str(proc_fts_dic[fts_tpl[idx]]) + '|'

            self.hts_lab_gen_prn += (lab_gen_ph + lab_gen_hmm + '|',)

    def gen_hts_lab_mono(self):
        """
        Generate the mono lab content (hts timed lab) according to HTS standards.
        """
        chosen_fields_lst = ['start', 'end', 'phone']

        self._hts_lab_mono_ttpl = \
            Lst.transp_ttpl(
                tuple(
                    tuple(self._proc_ldic[field]) for field in chosen_fields_lst
                )
            )

        self.hts_lab_mono_prn = tuple(' '.join(l) for l in self._hts_lab_mono_ttpl)

    def gen_hts_lab_full(self):
        """
        Generate the full lab content (timing + hts gen lab) according to HTS standards.
        """
        self.gen_hts_lab_mono()

        hts_lab_time_prn = tuple(' '.join(l[0:2]) for l in self._hts_lab_mono_ttpl)

        self.hts_lab_full_prn = tuple(' '.join((l_time, l_gen)) for (l_time, l_gen)
                                      in zip(hts_lab_time_prn, self.hts_lab_gen_prn))

    def process_lab_prn(self):
        """
        Complete process of the label file generation.
        """
        self.gen_hts_lab_fts()
        self.gen_hts_lab_mono()
        self.gen_hts_lab_full()

#======================================================================================================================#
