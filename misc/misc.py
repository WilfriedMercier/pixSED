#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
.. codeauthor:: Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>

Miscellaneous, quite general objects used by the SED fitting classes.
"""

import numpy         as     np
from   numpy         import ndarray
from   astropy.units import Unit, Quantity
from   typing        import Any

##############################################
#        Custom errors and exceptions        #
##############################################
      
class ShapeError(Exception):
    r'''
    .. codeauthor:: Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>
    
    Error which is caught when two arrays do not share the same shape.
    
    :param arr1: first array
    :type arr1: `ndarray`_
    :param arr2: second array
    :type arr2: `ndarray`_
    
    :param msg: (**Optional**) message to append at the end
    :type msg: :python:`str`
    '''
    
    def __init__(self, arr1: ndarray, arr2: ndarray, msg: str = '', **kwargs) -> None:
        r'''Init method.'''
        
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
 
##########################
#      Custom class      #
##########################

class NamedColumn:
   r'''
   .. codeauthor:: Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>
   
   A general named column to assicate to an Enum object.
   
   :param name: name of the column when included in a Table
   :type name: :python:`str`
   :param unit: unit of the column
   :type unit: :python:`str`
   
   :param end: (**Optional**) end string to append to the associate enum name
   :type end: :python:`str`
   :param log: (**Optional**) whether this column holds log values. This will trigger a conversion to the power of 10 if True.
   :type log: :python:`bool`
   
   :raises TypeError: if **name**, **unit** and **end** are not of type :python:`str`
   '''
   
   def __init__(self, name: str, unit: str, end: str = '', log=False) -> None:
      r'''Init method.'''
      
      if any((not isinstance(i, str) for i in [name, unit, end])):
         raise TypeError('one of the parameters does not have type str.')
      
      self.name = name
      self.unit = Unit(unit)
      self.end  = end
      self.log  = log
      
      
class PhysicalLogQuantity:
   r'''
   .. codeauthor:: Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>
   
   Implement an Astropy Quantity which can have log of physical values.
   
   :param value: value to pass to the constructor
   
   :param unit: data unit
   :type unit: :python:`str`
   '''
   
   def __init__(self, value: Any, *args, unit: str = '', **kwargs) -> None:
      r'''Init method.'''
      
      # Get unit for data when it is not in log form
      if 'unit' in kwargs:
         kwargs.pop('unit')
         
      if isinstance(value, (list, tuple)):
         value     = np.asarray(value)
   
      self.unit    = unit
      self.value   = value
         
      # Used when printing
      self._args   = args
      self._kwargs = kwargs
      
      
      
   def __str__(self, *args, **kwargs) -> str:
      r'''
      .. codeauthor:: Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>
       
      Slightly modified string representation.
      '''
   
      return f'{Quantity(self.value, *self._args, unit="", **self._kwargs)} [log({self.unit})]'
   
   def toPhysical(self, *args, **kwargs) -> Quantity:
      r'''
      .. codeauthor:: Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>
      
      Go to physical unit by raising to the power of 10 and converting to the right unit.
      '''
      
      return Quantity(10**self.value, unit=self.unit)
      
   
   
   