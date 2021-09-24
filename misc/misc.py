#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
.. codeauthor:: Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>

Miscellaneous, quite general objects used by the SED fitting classes.
"""

from numpy import ndarray

##############################################
#        Custom errors and exceptions        #
##############################################
      
class ShapeError(Exception):
    r'''Error which is caught when two arrays do not share the same shape.'''
    
    def __init__(self, arr1: ndarray, arr2: ndarray, msg: str = '', **kwargs) -> None:
        r'''
        .. codeauthor:: Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>
        
        Init method for this exception.
        
        :param ndarray arr1: first array
        :param ndarray arr2: second array
        
        :param str msg: (**Optional**) message to append at the end
        '''
        
        if not isinstance(msg, str):
            msg = ''
        
        super.__init__(f'Array 1 has shape {arr1.shape} but array 2 has shape {arr2.shape}{msg}.')
        

###################################
#        Custom decorators        #
###################################

def check_type(dtype):
    r'''
    .. codeauthor:: Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>
    
    A decorator which check data type of the first mandatory parameter of the function.
    
    :param dtype: type the parameter must have
    
    :raises TypeError: if data has the wrong type.
    :raises ValueError: if there is no data to check the type
    '''
    
    def decorator(func):
        '''
        :param function func: function to be decorated
        '''
    
        def wrap(*args, **kwargs):
            if not len(args) > 1:
                raise ValueError('Cannot check type for data with length 0.')
            
            value = args[1]
            if value != '-1' and not isinstance(value, dtype):
                raise TypeError(f'parameter has type {type(value)} but it must have type {dtype}.')
                
            return func(*args, **kwargs)
        return wrap
    return decorator
        
def check_type_in_list(dtype):
    r'''
    .. codeauthor:: Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>
    
    A decorator which check data type of the first mandatory parameter of the function.
    
    :param dtype: type the parameter must have
    
    :raises TypeError: if data has the wrong type.
    :raises ValueError: if there is no data to check the type
    '''
    
    def decorator(func):
        '''
        :param function func: function to be decorated
        '''
        
        def wrap(*args, **kwargs):
            
            if len(args) < 1 or len(args[1]) < 1:
                raise ValueError('Cannot check type for data with length 0.')
            
            value = args[1]
            if any((not isinstance(i, dtype) for i in value)):
                raise TypeError(f'at least one parameter element does not have type {dtype}.')
                
            return func(*args, **kwargs)
        return wrap
    return decorator