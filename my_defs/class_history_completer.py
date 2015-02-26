#!/bin/env python3
#-*- encoding: utf-8 -*-


import readline
# import os.path


class HistoryCompleter(object):
    """
    History recorder and tab completer.
    """
    def __init__(self):
        self.matches = []
        # return

    def complete(self, text, state):
        # response = None
        if state == 0:
            # noinspection PyArgumentList
            history_values = [
                readline.get_history_item(idx)
                for idx in range(1, readline.get_current_history_length() + 1)
            ]
            if text:
                self.matches = sorted(h 
                                      for h in history_values 
                                      if h and h.startswith(text))
            else:
                self.matches = []
        try:
            response = self.matches[state]
        except IndexError:
            response = None

        return response


# def input_loop(prompt_fpath='prompt.txt', hist_fpath='.completer.hist', quit_com='.'):
#     """
#     Create a loop that write the result to a file and record the input history, until a quit command is prompt.
#     """
#     # Register our completer function
#     readline.set_completer(HistoryCompleter().complete)
#     # Use the tab key for completion
#     readline.parse_and_bind('tab: complete')
#
#     if os.path.exists(hist_fpath):
#         readline.read_history_file(hist_fpath)
#
#     try:
#         while True:
#             prompt = input('Prompt "' + quit_com + '" to quit (and "-cls" to clear all history): ')
#             if prompt == quit_com:
#                 readline.remove_history_item(readline.get_current_history_length()-1)
#                 break
#             elif prompt == '-cls':
#                 for _ in range(readline.get_current_history_length()):                          # Remove all items
#                     readline.remove_history_item(0)
#             else:
#                 readline.write_history_file(hist_fpath)
#
#                 with open(prompt_fpath, 'w') as prompt_f:
#                     print(prompt, file=prompt_f)
#
#     finally:
#         readline.write_history_file(hist_fpath)
