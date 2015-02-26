#!/bin/env python3
#-*- encoding: utf-8 -*-


def sample_2_sec(samples, fs):
    """Converts sample to time according to the sample frequency argument.
    """
    samples = float(samples)
    time = samples / fs
    time_rnd = round(time, 3)

    return time_rnd
