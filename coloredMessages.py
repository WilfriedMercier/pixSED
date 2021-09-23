#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
.. codeauthor:: Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>

General functions to format io output using ANSII sequences using colorama.
"""

import colorama as col

def errorMessage(text):
    '''
    .. codeauthor:: Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>
    
    Colorise text in red and emphasise it for error messages.
    
    :param str text: text
    
    :returns: colorised text
    :rtype: str
    '''
    
    return col.Fore.RED + col.Style.BRIGHT + text + col.Style.RESET_ALL

def okMessage(text):
    '''
    .. codeauthor:: Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>
    
    Dim green text for validation messages.
    
    :param str text: text
    
    :returns: colorised text
    :rtype: str
    '''
    
    return col.Fore.GREEN + col.Style.DIM + text + col.Style.RESET_ALL

def brightMessage(text):
    '''
    .. codeauthor:: Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>
    
    Emphasize a text by brightening it.
    
    :param str text: text
    
    :returns: brightened text
    :rtype: str
    '''
    
    return col.Style.BRIGHT + text + col.Style.RESET_ALL

def dimMessage(text):
    '''
    .. codeauthor:: Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>
    
    Dim a text.

    :param str text: text
    
    :returns: dimmed text
    :rtype: str
    '''
    
    return col.Style.DIM + text + col.Style.RESET_ALL

def warningMessage(text):
    '''
    .. codeauthor:: Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>
    
    Same as error message but using yellow instead of red.

    :param str text: text
    
    :returns: colorised text
    :rtype: str
    '''
    
    return col.Style.BRIGHT + col.Fore.YELLOW + text + col.Style.RESET_ALL
    
