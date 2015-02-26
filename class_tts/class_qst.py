#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import importlib

import my_defs.defs_list as lst

from class_tts import PhoneSet


class Question:
    def __init__(self, param_module, pfs_obj):

        self.cst = importlib.import_module(param_module)

        ph_set_obj = PhoneSet(param_module, self.cst.PH_SET_FPATH)
        self._ph_set_ddic = ph_set_obj.get_ph_set_ddic()

        self._PH_SET_FTS_VAL_INVENTORY_LDIC = lst.get_2d_dic_items(self._ph_set_ddic)
        self.pfs_obj = pfs_obj

        self._fts_val_inventory_ldic = {}
        self._fts_used_val_ldic = {}
        self._hts_lab_mono_ttpl = ()
        self._hts_qst_hmm_tpl = ()
        self.hts_qst_tpl = ()
        self.hts_qst_utt_tpl = ()

    def gen_fts_val_inventory(self):
        """
        Generate the 2D dictionary with all the values possible of all the features parameters.
        Default values (from 0 to 50) for some hmm fts are added here.
        """
        # add the val 0..50 to the fts not present in the manually defined values list (self.cst.ALL_FTS_VAL_LDIC)
        hmm_fts_0_50_val_lst = []
        for ft in self.cst.USED_HMM_FTS_TPL:
            if (
                    ft not in self.cst.HMM_FTS_VAL_INVENTORY_LDIC.keys() and
                    ft != 'phone' and 'prev_phone' not in ft and 'next_phone' not in ft and 'vowel' not in ft
            ):
                hmm_fts_0_50_val_lst.append([ft, self.cst.ZERO_TO_FIFTY])

            # 'phone' related keys are covered by _PH_SET_FTS_VAL_INVENTORY_LDIC,
            # BUT not the 'vowel' related one (add all the phonemes for simplicity)
            elif 'vowel' in ft:
                hmm_fts_0_50_val_lst.append([ft, self._PH_SET_FTS_VAL_INVENTORY_LDIC['phone']])

        hmm_fts_050_val_ldic = dict(hmm_fts_0_50_val_lst)

        # Concatenate dictionaries
        self._fts_val_inventory_ldic = dict(list(self._PH_SET_FTS_VAL_INVENTORY_LDIC.items())
                                            + list(self.cst.HMM_FTS_VAL_INVENTORY_LDIC.items())
                                            + list(hmm_fts_050_val_ldic.items()))
        # Insert a null value in the val lst 1st position if absent
        for key in self._fts_val_inventory_ldic.keys():
            if self._fts_val_inventory_ldic[key][0] != self.cst.NULL_VAL:
                self._fts_val_inventory_ldic[key].insert(0, self.cst.NULL_VAL)

    def gen_used_fts_val(self):
        """
        Generate the all the fts and their corresponding val as an ldic.
        """
        fts_used_val_llst = []
        for ft_used in self.cst.USED_FTS_TPL:						    # take ft_used name from the list

            for ft_class in self._fts_val_inventory_ldic.keys():		# take ft_class from the list of the ft values
                if ft_class == ft_used.lstrip('prev_') or ft_class == ft_used.lstrip('next_'):
                    # check if ft_used belongs to ft "class" (ft_class str included in ft_used)
                                                                    # create lst with ft names and val
                    fts_used_val_llst.append([ft_used, self._fts_val_inventory_ldic[ft_class]])

        self._fts_used_val_ldic = dict(fts_used_val_llst)			    # convert into a dic of lists

    def format_fts_val(self):
        """
        Set max val to 19 and cast all val to str.
        """
        # noinspection PyProtectedMember
        for ft in self.pfs_obj._USED_PFEATS_TPL:                    # self.pfs_obj._ALL_PFEATS_TPL
            # Check all element value and set max integer val to 50
            val_tpl = ()
            for val in getattr(self.pfs_obj, ft):
                if isinstance(val, int):                            # check if ft val is int
                    val = str(val) if val < 50 else '50'
                val_tpl += (val,)
                # Cast all ldic elements in str format (TODO: check in process_hmm_fts in the future)

            setattr(self.pfs_obj, ft, tuple(val for val in val_tpl))

    def gen_hts_ph_qst(self):
        """
        Generate the HTS question file.
        """
        self.hts_qst_tpl = ()
        for ph in self._fts_used_val_ldic['phone']:
            if ph != self.cst.NULL_VAL:
                self.hts_qst_tpl += (
                    'QS "prev_prev_phone=' + ph + '"\t\t{' + ph + '^*}',
                    'QS "prev_phone=' + ph + '"\t\t{*^' + ph + '-*}',
                    'QS "phone=' + ph + '"\t\t\t{*-' + ph + '+*}',
                    'QS "next_phone=' + ph + '"\t\t{*+' + ph + '=*}',
                    'QS "next_next_phone=' + ph + '"\t\t{*=' + ph + '||*}',
                )
                self.hts_qst_tpl += ('',)

        for ft in self._PH_SET_FTS_VAL_INVENTORY_LDIC:
            if 'phone' not in ft:
                for val in self._PH_SET_FTS_VAL_INVENTORY_LDIC[ft]:
                    if val == self.cst.NULL_VAL:
                        hts_qst_ph_tpl = tuple(ph for ph in self._ph_set_ddic
                                               if ft not in self._ph_set_ddic[ph])
                    else:
                        hts_qst_ph_tpl = tuple(ph for ph in self._ph_set_ddic
                                               if ft in self._ph_set_ddic[ph] and self._ph_set_ddic[ph][ft] == val)
                    hts_qst_ph_prv_prv = '^*,'.join(hts_qst_ph_tpl)
                    hts_qst_ph_prv = '-*,*^'.join(hts_qst_ph_tpl)
                    hts_qst_ph = '+*,*-'.join(hts_qst_ph_tpl)
                    hts_qst_ph_nxt = '=*,*+'.join(hts_qst_ph_tpl)
                    hts_qst_ph_nxt_nxt = '||*,*='.join(hts_qst_ph_tpl)
                    self.hts_qst_tpl += (
                        'QS "prev_prev_' + ft + '=' + val + '"\t\t{' + hts_qst_ph_prv_prv + '^*}',
                        'QS "prev_' + ft + '=' + val + '"\t\t{*^' + hts_qst_ph_prv + '-*}',
                        'QS "ph_' + ft + '=' + val + '"\t\t{*-' + hts_qst_ph + '+*}',
                        'QS "next_' + ft + '=' + val + '"\t\t{*+' + hts_qst_ph_nxt + '=*}',
                        'QS "next_next_' + ft + '=' + val + '"\t\t{*=' + hts_qst_ph_nxt_nxt + '||*}',
                    )
                    self.hts_qst_tpl += ('',)

    def gen_hts_hmm_qst(self):
        """
        Generate the HTS question file (for hmm fts).
        """
        self._hts_qst_hmm_tpl, self.hts_qst_utt_tpl = (), ()

        fts_code_tpl = tuple('f'+str(idx) for (idx, _) in enumerate(self.cst.USED_HMM_FTS_TPL))

        for (idx, ft) in enumerate(self.cst.USED_HMM_FTS_TPL):
            for val in self._fts_used_val_ldic[ft]:
                self._hts_qst_hmm_tpl += ('QS "' + fts_code_tpl[idx] + '=' + val + '"' + '\t'
                                          + '{*|' + fts_code_tpl[idx] + '=' + val + '|*}',)
            self._hts_qst_hmm_tpl += ('',)

            if ft in self.cst.UTT_HMM_FTS_TPL:                  # Check if ft belongs to utt qst file and insert it
                for val in self._fts_used_val_ldic[ft]:
                    self.hts_qst_utt_tpl += ('QS "' + fts_code_tpl[idx] + '=' + val + '"' + '\t'
                                             + '{*|' + fts_code_tpl[idx] + '=' + val + '|*}',)
                self.hts_qst_utt_tpl += ('',)

    def process_qst_data(self):
        """
        Complete process of qst data creation.
        """
        self.gen_fts_val_inventory()
        # for key in self._fts_val_inventory_ldic:
        #     print(key, self._fts_val_inventory_ldic[key])   # debug
        self.gen_used_fts_val()
        self.format_fts_val()
        self.gen_hts_hmm_qst()
        self.gen_hts_ph_qst()
        self.hts_qst_tpl += self._hts_qst_hmm_tpl
