#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
.. codeauthor:: Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>

Enumerations used in other parts of the code.
"""

from enum import Enum

class CleanMethod(Enum):
    r'''An enumeration for the cleaning method used by the filters.'''
     
    ZERO = 'zero'
    MIN  = 'min'
    
class MagType(Enum):
    r'''An enumeration for valid magnitude types for LePhare.'''
    
    AB   = 'AB'
    VEGA = 'VEGA'

class SEDcode(Enum):
    r'''An enumeration for the SED fitting codes available.'''
    
    LEPHARE = 'lephare'
    CIGALE  = 'cigale'
    
class TableFormat(Enum):
    r'''An enumerator for valid table format for LePhare.'''
    
    MEME = 'MEME'
    MMEE = 'MMEE'
    
class TableType(Enum):
    r'''An enumerator for valid table data type for LePhare.'''
    
    LONG  = 'LONG'
    SHORT = 'SHORT'
    
class TableUnit(Enum):
    r'''An enumeration for valid values for table units for LePhare.'''
    
    MAG  = 'M'
    FLUX = 'F'
    
class YESNO(Enum):
    r'''An enumeration with YES or NO options for LePhare.'''
    
    YES = 'YES'
    NO  = 'NO'
    
class ANDOR(Enum):
    r'''An enumeration with AND or OR options for LePhare.'''
    
    AND = 'AND'
    OR  = 'OR'