#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
.. codeauthor:: Hugo Plombat - LUPM <hugo.plombat@umontpellier.fr> & Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>

Miscellaneous, quite general objects used by the SED fitting classes.
"""

from   abc     import ABC, abstractmethod
from   typing  import Any, Union, Callable, List, Optional
from   numpy   import ndarray
from   enum    import Enum
import os.path as     opath


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
        
##############################
#        Enumerations        #
##############################

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
    FLUX = ''
    
class YESNO(Enum):
    r'''An enumeration with YES or NO options for LePhare.'''
    
    YES = 'YES'
    NO  = 'NO'
    
class ANDOR(Enum):
    r'''An enumeration with AND or OR options for LePhare.'''
    
    AND = 'AND'
    OR  = 'OR'
    

########################################
#           Property objects           #
########################################
        
class Property(ABC):
    r'''
    Abstract class which defines a property object used by SED objects to store SED parameters.
    
    You must subclass it with __str__ and set methods or used a default subclass in order to use it.
    '''
    
    def __init__(self, default: Any,
                 minBound: Optional[Any] = None, 
                 maxBound: Optional[Any] = None, 
                 testFunc: Callable[[Any], bool] = lambda value: False, 
                 testMsg: str ='', **kwargs) -> None:
        r'''
        .. codeauthor:: Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>
        
        Init the property object.

        :param default: default value used at init

        :param minBound: (**Optional**) minimum value for the property. If None, it is ignored.
        :param maxBound: (**Optional**) maximum value for the property. If None, it is ignored.
        :param testFunc: (**Optional**) a test function with the value to test as argument which must not be passed in order to set a value. This can be used to add additional checks which are not taken into account by default.
        :param testMsg: (**Optional**) a test message used to throw an error if testFunc returns False
        
        :raises TypeError: if **testFunc** is not callable or **testMsg** is not of type str
        :raises ValueError: if **minBound** is larger than **maxBound** and both are not None
        '''
        
        if not callable(testFunc) or not isinstance(testMsg, str):
            raise TypeError('test function and test message must be a callable object and of type str respectively.')
        
        if maxBound is not None and minBound is not None and maxBound < minBound:
            raise ValueError('maximum bound must be larger than minimum bound.')
        
        self.min       = minBound
        self.max       = maxBound
        self._testFunc = testFunc
        self._testMsg  = testMsg
        self.default   = default
        
    ##################################
    #        Built-in methods        #
    ##################################
    
    @abstractmethod
    def __str__(self, *args, **kwargs) -> str:
        r'''
        .. codeauthor:: Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>
        
        Implement a string representation of the class.
        '''
        
        return
        
    ###############################
    #        Miscellaneous        #
    ###############################
    
    @staticmethod
    def check_bounds(value: Any, mini: Any, maxi: Any, func: Callable, msg: str) -> None:
        r'''
        .. codeauthor:: Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>
        
        :param value: value to check
        :param mini: minimum value
        :param maxi: maximum value
        :param function func: test function with the value to test as argument which must not be passed in order to set a value. This can be used to add additional checks which are not taken into account by default.
        :param str msg: test message used to throw an error if testFunc returns False
        
        :raises ValueError:
            
            * if the **value** is below the minimum bound
            * if the **value** is above the maximum bound
            * if the test function is not passed
        '''
        
        if mini is not None and value < mini:
            raise ValueError('value is {value} but minimum acceptable bound is {mini}.')
        
        if maxi is not None and value > maxi:
            raise ValueError('value is {value} but maximum acceptable bound is {maxi}.')
            
        if func(value):
            raise ValueError(msg)
            
        return
    
    @abstractmethod
    def set(self, value: Any, *args, **kwargs) -> None:
        r'''
        .. codeauthor:: Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>
        
        Set the current value.

        :param value: new value
        '''
        
        return
    
class IntProperty(Property):
    r'''Define a property object which stores a single integer.'''
    
    def __init__(self, default: int,
                 minBound: int = None, 
                 maxBound: int = None, 
                 testFunc: Callable[[int], bool] = lambda value: False, 
                 testMsg: str ='', **kwargs) -> None:
        
        r'''
        .. codeauthor:: Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>
        
        Init the int property object.

        :param int default: default value used at init

        :param int minBound: (**Optional**) minimum value for the property. If None, it is ignored.
        :param int maxBound: (**Optional**) maximum value for the property. If None, it is ignored.
        :param testFunc: (**Optional**) a test function with the value to test as argument which must not be passed in order to set a value. This can be used to add additional checks which are not taken into account by default.
        :param testMsg: (**Optional**) a test message used to throw an error if testFunc returns False
        '''
        
        super().__init__(default, minBound=minBound, maxBound=maxBound, testFunc=testFunc, testMsg=testMsg)
        
        # Set the value to check data type (default property has already been set)
        self.set(default)
        
    def __str__(self, *args, **kwargs) -> str:
        r'''
        .. codeauthor:: Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>
        
        Implement a string representation of the class.
        '''
        
        return f'{self.value}'
    
    @check_type(int)
    def set(self, value: int, *args, **kwargs) -> None:
        r'''.. codeauthor:: Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>
        
        Set the current value.

        :param int value: new value. Must be within bounds.
        '''
        
        self.check_bounds(value, self.min, self.max, self._testFunc, self._testMsg)
        self.value = value
        return
    
class FloatProperty(Property):
    r'''Define a property object which stores a single float.'''
    
    def __init__(self, default: float,
                 minBound: float = None, 
                 maxBound: float = None, 
                 testFunc: Callable[[float], bool] = lambda value: False, 
                 testMsg: str ='', **kwargs) -> None:
        
        r'''
        .. codeauthor:: Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>
        
        Init the float property object.

        :param float default: default value used at init

        :param float minBound: (**Optional**) minimum value for the property. If None, it is ignored.
        :param float maxBound: (**Optional**) maximum value for the property. If None, it is ignored.
        :param testFunc: (**Optional**) a test function with the value to test as argument which must not be passed in order to set a value. This can be used to add additional checks which are not taken into account by default.
        :param testMsg: (**Optional**) a test message used to throw an error if testFunc returns False
        '''
        
        super().__init__(default, minBound=minBound, maxBound=maxBound, testFunc=testFunc, testMsg=testMsg)
        
        # Set the value to check data type (default property has already been set)
        self.set(default)
        
    def __str__(self, *args, **kwargs) -> str:
        r'''
        .. codeauthor:: Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>
        
        Implement a string representation of the class.
        '''
        
        # -1 is the value which indicates no value in LePhare
        if self.value == '-1':
            return self.value
        elif self.value == 0 or (self.value > 1e-3 and self.value < 1e3):
            return f'{self.value:.3f}'
        else:
            return f'{self.value:.3e}'
    
    @check_type(float)
    def set(self, value: float, *args, **kwargs) -> None:
        r'''.. codeauthor:: Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>
        
        Set the current value.

        :param float value: new value. Must be within bounds.
        '''
        
        if value != '-1':
            self.check_bounds(value, self.min, self.max, self._testFunc, self._testMsg)
            
        self.value = value
        return
    
class StrProperty(Property):
    r'''Define a property which stores a single str object.'''
    
    def __init__(self, default: str,
                 testFunc: Callable[[str], bool] = lambda value: False, 
                 testMsg: str ='', **kwargs) -> None:
        
        r'''
        .. codeauthor:: Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>
        
        Init the string property object.

        :param str default: default value used at init

        :param testFunc: (**Optional**) a test function with the value to test as argument which must not be passed in order to set a value. This can be used to add additional checks which are not taken into account by default.
        :param testMsg: (**Optional**) a test message used to throw an error if testFunc returns False
        '''
        
        super().__init__(default, minBound=None, maxBound=None, testFunc=testFunc, testMsg=testMsg)
        
        # Set the value to check data type (default property has already been set)
        self.set(default)
        
    def __str__(self, *args, **kwargs) -> str:
        r'''
        .. codeauthor:: Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>
        
        Implement a string representation of the class.
        '''
        
        return self.value
    
    @check_type(str)
    def set(self, value: str, *args, **kwargs) -> None:
        r'''
        .. codeauthor:: Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>
        
        Set the current value.

        :param str value: new value. Must be within bounds.
        
        :raises ValueError: if the test function does not pass
        '''
        
        if self._testFunc(value):
            raise ValueError(self._testMsg)
            
        self.value = value
        return
    
#############################################
#           List property objects           #
#############################################
    
class ListProperty(Property):
    r'''
    An abstract class which defines a property which stores a list object.
    
    You must subclass it with __str__ and set methods or use a default subclass in order to use it.
    '''
        
    def __init__(self, default: List[Any],
                 minBound: Any = None, 
                 maxBound: Any = None, 
                 testFunc: Callable[[List[Any]], bool] = lambda value: False, 
                 testMsg: str ='', **kwargs) -> None:
        
        r'''
        .. codeauthor:: Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>
        
        Init the list property object.

        :param default: default value used at init

        :param minBound: (**Optional**) minimum value for the property. If None, it is ignored.
        :param maxBound: (**Optional**) maximum value for the property. If None, it is ignored.
        :param testFunc: (**Optional**) a test function with the value to test as argument which must not be passed in order to set a value. This can be used to add additional checks which are not taken into account by default.
        :param testMsg: (**Optional**) a test message used to throw an error if testFunc returns False
        '''
        
        super().__init__(default, minBound=minBound, maxBound=maxBound, testFunc=testFunc, testMsg=testMsg)
        
    ###############################
    #        Miscellaneous        #
    ###############################
    
    @staticmethod
    def check_bounds(value: List[Any], mini: Any, maxi: Any, func: Callable, msg: str) -> None:
        r'''
        .. codeauthor:: Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>
        
        :param list value: value to check
        :param mini: minimum value
        :param maxi: maximum value
        :param function func: test function with the value to test as argument which must not be passed in order to set a value. This can be used to add additional checks which are not taken into account by default.
        :param str msg: test message used to throw an error if testFunc returns False
        
        :raises ValueError:
            
            * if one of the values in **value** is below the minimum bound
            * if one of the values in **value** is above the maximum bound
            * if the test function is not passed
        '''
        
        if mini is not None and any((i < mini for i in value)):
            raise ValueError('value is {value} but minimum acceptable bound is {mini}.')
        
        if maxi is not None and any((i > maxi for i in value)):
            raise ValueError('value is {value} but maximum acceptable bound is {maxi}.')
            
        if func(value):
            raise ValueError(msg)
            
        return
    
    @abstractmethod
    def set(self, value: List[Any], *args, **kwargs) -> None:
        r'''
        .. codeauthor:: Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>
        
        Set the current value.

        :param list value: new value. Must be of correct type, and within bounds.
        '''
        
        return
    
class ListIntProperty(ListProperty):
    r'''Define a property which stores an int list object.'''
    
    def __init__(self, default: List[int],
                 minBound: int = None, 
                 maxBound: int = None, 
                 testFunc: Callable[[List[int]], bool] = lambda value: False, 
                 testMsg: str ='', **kwargs) -> None:
        
        r'''
        .. codeauthor:: Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>
        
        Init the int list property object.

        :param list[int] default: default value used at init

        :param int minBound: (**Optional**) minimum value for the property. If None, it is ignored.
        :param int maxBound: (**Optional**) maximum value for the property. If None, it is ignored.
        :param testFunc: (**Optional**) a test function with the value to test as argument which must not be passed in order to set a value. This can be used to add additional checks which are not taken into account by default.
        :param testMsg: (**Optional**) a test message used to throw an error if testFunc returns False
        '''
        
        super().__init__(default, minBound=minBound, maxBound=maxBound, testFunc=testFunc, testMsg=testMsg)
        
        # Set the value to check data type (default property has already been set)
        self.set(default)
        
    def __str__(self, *args, **kwargs) -> str:
        r'''
        .. codeauthor:: Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>
        
        Implement a string representation of the class.
        '''
        
        return ','.join([f'{i}' for i in self.value])
        
    @check_type(list)
    @check_type_in_list(int)
    def set(self, value: List[int], *args, **kwargs) -> None:
        r'''
        .. codeauthor:: Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>
        
        Set the current value.

        :param list[int] value: new value. Must be of correct type, and within bounds.
        '''
        
        self.check_bounds(value, self.min, self.max, self._testFunc, self._testMsg)
        self.value = value
        return
    
class ListFloatProperty(ListProperty):
    r'''Define a property which stores an int list object.'''
    
    def __init__(self, default: List[float],
                 minBound: float = None, 
                 maxBound: float = None, 
                 testFunc: Callable[[List[float]], bool] = lambda value: False, 
                 testMsg: str ='', **kwargs) -> None:
        
        r'''
        .. codeauthor:: Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>
        
        Init the float list property object.

        :param list[float] default: default value used at init

        :param float minBound: (**Optional**) minimum value for the property. If None, it is ignored.
        :param float maxBound: (**Optional**) maximum value for the property. If None, it is ignored.
        :param testFunc: (**Optional**) a test function with the value to test as argument which must not be passed in order to set a value. This can be used to add additional checks which are not taken into account by default.
        :param testMsg: (**Optional**) a test message used to throw an error if testFunc returns False
        '''
        
        super().__init__(default, minBound=minBound, maxBound=maxBound, testFunc=testFunc, testMsg=testMsg)
        
        # Set the value to check data type (default property has already been set)
        self.set(default)
        
    def __str__(self, *args, **kwargs) -> str:
        r'''
        .. codeauthor:: Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>
        
        Implement a string representation of the class.
        '''
        
        return ','.join([f'{i:.3f}' if i == 0 or (i > 1e-3 and i < 1e3) else f'{i:.3e}' for i in self.value])
        
    @check_type(list)
    @check_type_in_list(float)
    def set(self, value: List[float], *args, **kwargs) -> None:
        r'''
        .. codeauthor:: Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>
        
        Set the current value.

        :param list[float] value: new value. Must be of correct type, and within bounds.
        '''
        
        self.check_bounds(value, self.min, self.max, self._testFunc, self._testMsg)
        self.value = value
        return

class ListStrProperty(ListProperty):
    r'''Define a property which stores an int list object.'''
    
    def __init__(self, default: List[str],
                 testFunc: Callable[[List[str]], bool] = lambda value: False, 
                 testMsg: str ='', **kwargs) -> None:
        
        r'''
        .. codeauthor:: Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>
        
        Init the str list property object.

        :param list[str] default: default value used at init

        :param testFunc: (**Optional**) a test function with the value to test as argument which must not be passed in order to set a value. This can be used to add additional checks which are not taken into account by default.
        :param testMsg: (**Optional**) a test message used to throw an error if testFunc returns False
        '''
        
        super().__init__(default, minBound=None, maxBound=None, testFunc=testFunc, testMsg=testMsg)
        
        # Set the value to check data type (default property has already been set)
        self.set(default)
        
    def __str__(self, *args, **kwargs) -> str:
        r'''
        .. codeauthor:: Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>
        
        Implement a string representation of the class.
        '''
        
        return ','.join(self.value)
        
    @check_type(list)
    @check_type_in_list(str)
    def set(self, value: List[str], *args, **kwargs) -> None:
        r'''
        .. codeauthor:: Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>
        
        Set the current value.

        :param list[str] value: new value. Must be of correct type, and within bounds.
        
        :raises ValueError: if the test function does not pass
        '''
        
        if self._testFunc(value):
            raise ValueError(self._testMsg)
        
        self.value = value
        return


#############################################
#           List property objects           #
#############################################

class PathProperty(Property):
    r'''Define a property which stores a str object which includes additional checks for paths.'''

    def __init__(self, default: str,
                 testFunc: Callable[[str], bool] = lambda value: False, 
                 testMsg: str ='', 
                 path: str = '', 
                 ext: str = '', **kwargs) -> None:
        
        r'''
        .. codeauthor:: Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>
        
        Init the path property object.

        :param str default: default value used at init

        :param testFunc: (**Optional**) a test function with the value to test as argument which must not be passed in order to set a value. This can be used to add additional checks which are not taken into account by default.
        :param testMsg: (**Optional**) a test message used to throw an error if testFunc returns False
        :param str path: (**Optional**) path to append each time to the new value
        :param str ext: (**Optionall**) extension to append at the end of the file name when checking the path
        
        :raises TypeError: if neither **path** nor **ext** are str
        '''
        
        if not isinstance(path, str):
            raise TypeError(f'path has type {type(path)} but it must have type str.')
            
        if not isinstance(ext, str):
            raise TypeError(f'extension has type {type(ext)} but it must have type str.')
        
        super().__init__(default, testFunc=testFunc, testMsg=testMsg)
        
        # Extension to append when checking path
        self.ext     = ext
        
        # Set path to append at the beginning of a check
        self.path    = path
        
        # Set the value to check data type (default property has already been set)
        self.set(default)
        
    def __str__(self, *args, **kwargs) -> str:
        r'''
        .. codeauthor:: Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>
        
        Implement a string representation of the class.
        '''
        
        return self.value
    
    @check_type(str)
    def set(self, value: str, *args, **kwargs) -> None:
        r'''
        .. codeauthor:: Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>
        
        Set the current value.

        :param str value: new value. Must be within bounds.
        
        :raises OSError: if the path does not exist
        :raises ValueError: if the test function does not pass
        '''
        
        path       = opath.join(self.path, value) + self.ext
        epath      = opath.expandvars(path)
        if value.upper() != 'NONE' and not opath.exists(epath) and not opath.isfile(epath):
            raise OSError(f'path {path} (expanded as {epath}) does not exist.')
        
        if self._testFunc(value):
            raise ValueError(self._testMsg)
        
        self.value = value
        return

class ListPathProperty(ListProperty):
    r'''Define a property which stores a str list object which includes additional checks for paths.'''

    def __init__(self, default: List[str],
                 testFunc: Callable[[List[str]], bool] = lambda value: False, 
                 testMsg: str ='', 
                 path: str = '', 
                 ext: str = '', **kwargs) -> None:
        
        r'''
        .. codeauthor:: Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>
        
        Init the path list property object.

        :param list[str] default: default value used at init

        :param testFunc: (**Optional**) a test function with the value to test as argument which must not be passed in order to set a value. This can be used to add additional checks which are not taken into account by default.
        :param testMsg: (**Optional**) a test message used to throw an error if testFunc returns False
        :param str path: (**Optional**) path to append each time to the new value
        :param str ext: (**Optionall**) extension to append at the end of the file name when checking the path
        
        :raises TypeError: if neither **path** nor **ext** are str
        '''
        
        if not isinstance(path, str):
            raise TypeError(f'path has type {type(path)} but it must have type str.')
            
        if not isinstance(ext, str):
            raise TypeError(f'extension has type {type(ext)} but it must have type str.')
        
        super().__init__(default, minBound=None, maxBound=None, testFunc=testFunc, testMsg=testMsg)
        
        # Extension to append when checking path
        self.ext     = ext
        
        # Set path to append at the beginning of a check
        self.path    = path
        
        # Set the value to check data type (default property has already been set)
        self.set(default)
        
    def __str__(self, *args, **kwargs) -> str:
        r'''
        .. codeauthor:: Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>
        
        Implement a string representation of the class.
        '''
        
        return ','.join(self.value)
        
    @check_type(list)
    @check_type_in_list(str)
    def set(self, value: List[str], *args, **kwargs) -> None:
        r'''
        .. codeauthor:: Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>
        
        Set the current value.

        :param list[str] value: new value. Must be of correct type, and within bounds.
        
        :raises OSError: if at least one path does not exist
        :raises ValueError: if the test function does not pass
        '''
        
        for p in value:  
            
            path  = opath.join(self.path, p) + self.ext
            epath = opath.expandvars(path)
                
            if p.upper() != 'NONE' and not opath.exists(epath) and not opath.isfile(epath):
                raise OSError(f'path {path} (expanded as {epath}) does not exist.')
        
        if self._testFunc(value):
            raise ValueError(self._testMsg)
        
        self.value = value
        return
    
#####################################
#       Enum property objects       #
#####################################

class EnumProperty:
    r'''Define a property which stores a Enum object.'''
    
    def __init__(self, value: Enum, 
                 testFunc: Callable[[List[str]], bool] = lambda value: False, 
                 testMsg: str ='', **kwargs) -> None:
    
        r'''
        .. codeauthor:: Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>
            
        Init the enum property object.
    
        :param Enum default: default value used at init
    
        :param testFunc: (**Optional**) a test function with the value to test as argument which must not be passed in order to set a value. This can be used to add additional checks which are not taken into account by default.
        :param testMsg: (**Optional**) a test message used to throw an error if testFunc returns False
        '''
        
        if not callable(testFunc) or not isinstance(testMsg, str):
            raise TypeError('test function and test message must be a callable object and of type str respectively.')
        
        self._testFunc = testFunc
        self._testMsg  = testMsg
        self.default   = value
        self.set(value)
        
    def __str__(self, *args, **kwargs) -> str:
        r'''
        .. codeauthor:: Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>
        
        Implement a string representation of the class.
        '''
        
        return self.value.value
       
    @check_type(Enum)
    def set(self, value: Enum, *args, **kwargs) -> None:
        r'''
        .. codeauthor:: Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>
        
        Set the current value.

        :param value: new value
        
        :raises TypeError: if **value** is not of type Enum
        :raises ValueError: if the test function does not pass
        '''
            
        if self._testFunc(value):
            raise ValueError(self._testMsg)
            
        self.value = value
        return
    
    