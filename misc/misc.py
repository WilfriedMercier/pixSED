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
 
##########################
#      Custom class      #
##########################

class NamedColumn:
   r'''A general named column to assicate to an Enum object.'''
   
   def __init__(self, name: str, unit: Unit, end: str = '', log=False) -> None:
      r'''
      .. codeauthor:: Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>
      
      Init named column.
      
      :param str name: name of the column when included in a Table
      :param Unit unit: unit of the column
      
      :param str end: (**Optional**) end string to append to the associate enum name
      :param bool log: (**Optional**) whether this column holds log values. This will trigger a conversion to the power of 10 if True.
      
      :raises TypeError: 
         
         * if **name** is not of type str
         * if **unit** is not of type Astropy Unit
         * if **end** is not of type str
      '''
      
      if any((not isinstance(i, str) for i in [name, unit, end])):
         raise TypeError('one of the parameters does not have type str.')
      
      self.name = name
      self.unit = Unit(unit)
      self.end  = end
      self.log  = log
      
      
class PhysicalLogQuantity:
   r'''Implement an Astropy Quantity which can have log of physical values.'''
   
   def __init__(self, value: Any, *args, unit: str = '', **kwargs) -> None:
      r'''
      .. codeauthor:: Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>
      
      Init the physical log quantity object.
      
      :param value: value to pass to the constructor
      '''
      
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
      
   
   
   