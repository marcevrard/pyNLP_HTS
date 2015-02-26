#!/usr/bin/env python3
#-*- coding: utf-8 -*-

import xml.etree.ElementTree as Et
import importlib

import my_defs.defs_list as lst


class PhoneSet:
    """
    Class providing the Phone Set (articulation characteristics of the phonemes).
    """
    def __init__(self, param_module, ph_set_fpath):
        """
        Read the xml Phone Set file, return a 2D dict with the values and set attributes from this 2D dict.
        """

        self.cst = importlib.import_module(param_module)

        self._ph = ''

        self.vc = []                                            # FIXME:(1) temp solution to remove error in Phone()

        # Read the xml Phone Set file
        tree_ph_set = Et.parse(ph_set_fpath)
        root_ph_set = tree_ph_set.getroot()

        ph_set_dlst = []
        ph_set_param = ()
        for child_ph_set in root_ph_set:
            ph_set_dlst.append(child_ph_set.attrib)
            ph_set_param += tuple(child_ph_set.attrib.keys())

        # Get phone set parameter list
        ph_set_param_dic = set(ph_set_param)
        self._ph_set_param_dic = ph_set_param_dic

        # Add key name 'phone'
        for phset_dic in ph_set_dlst:
            phset_dic['phone'] = phset_dic['ph']

        # Remove the 'ph' key from the dic row and create a key with its value to hold the corresponding row (ddic)
        # e.g.: [{'ph': 'dd', 'cvox': '+', ...}] > {'dd': {'cvox': '+', ...}}
        self._ph_set_ddic = dict(
            (row.pop('ph'), row) for row in ph_set_dlst
        )

        # Set all attributes from parameter keys
        for param in self._ph_set_param_dic:
            if param != 'ph':
                setattr(self, param, self.cst.NULL_VAL)

    def set_current_ph(self, ph):
        """
        Set current phone corresponding attributes for its parameter values
        """
        self._ph = ph

        for param in self._ph_set_ddic[ph]:
            setattr(self, param, self._ph_set_ddic[ph][param])

    def get_ph_set_param_dic(self):
        """
        Get phone set parameter dic.
        """
        return self._ph_set_param_dic

    def get_ph_set_ddic(self):
        """
        Get phone set parameter dic.
        """
        return self._ph_set_ddic

    def get_ph_set_fts_val_ldic(self):
        """
        Get phone set parameter dic.
        """
        return lst.get_2d_dic_items(self._ph_set_ddic)
