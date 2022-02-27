#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
.. codeauthor:: Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>

Property classes used in other parts of the code.
"""

from   abc     import ABC, abstractmethod
from   typing  import Any, Callable, List, Optional
from   enum    import Enum
from   .misc   import check_type, check_type_in_list
import os.path as     opath

########################################
#           Property objects           #
########################################
        
class Property(ABC):
    r'''
    .. codeauthor:: Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>
    
    Abstract class which defines a property object used by SED objects to store SED parameters.
    
    You must subclass it with __str__ and set methods or used a default subclass in order to use it.
    
    :param default: default value used at init

    :param minBound: (**Optional**) minimum value for the property. If :python:`None`, it is ignored.
    :param maxBound: (**Optional**) maximum value for the property. If :python:`None`, it is ignored.
    :param testFunc: (**Optional**) a test function with the value to test as argument which must not be passed in order to set a value. This can be used to add additional checks which are not taken into account by default.
    :type testFunc: :python:`Callable`
    :param testMsg: (**Optional**) a test message used to throw an error if **testFunc** returns :python:`False`
    :type testMsg: :python:`str`
    
    :raises TypeError: 
        
        * if **testFunc** is not a :python:`Callable`
        * if **testMsg** is not of type :python:`str`
        
    :raises ValueError: if **minBound** is larger than **maxBound** and both are not :python:`None`
    '''
    
    def __init__(self, default: Any,
                 minBound: Optional[Any] = None, 
                 maxBound: Optional[Any] = None, 
                 testFunc: Callable[[Any], bool] = lambda value: False, 
                 testMsg: str ='', 
                 **kwargs) -> None:
        r'''Init method.'''
        
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
        
        :returns: the string representation
        :rtype: :python:`str`
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
        :param func: test function with the value to test as argument which must not be passed in order to set a value. This can be used to add additional checks which are not taken into account by default.
        :type func: :python:`Callable`
        :param msg: test message used to throw an error if testFunc returns False
        :type msg: :python:`str`
        
        :raises ValueError:
            
            * if :python:`value < mini`
            * if :python:`value > maxi`
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
    
    
class BoolProperty(Property):
    r'''
    .. codeauthor:: Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>
    
    Define a property object which stores a single boolean.
    
    :param default: default value used at init
    :type default: :python:`bool`
    
    :param testFunc: (**Optional**) a test function with the value to test as argument which must not be passed in order to set a value. This can be used to add additional checks which are not taken into account by default.
    :type testFunc: :python:`Callable`
    :param testMsg: (**Optional**) a test message used to throw an error if **testFunc** returns :python:`False`
    :type testMsg: :python:`str`
    '''
    
    def __init__(self, default: bool,
                 testFunc: Callable[[Any], bool] = lambda value: False, 
                 testMsg: str ='', **kwargs) -> None:
        
        r'''Init method.'''
        
        super().__init__(default, minBound=None, maxBound=None, testFunc=testFunc, testMsg=testMsg)
        
        # Set the value to check data type (default property has already been set)
        self.set(default)
        
    def __str__(self, *args, **kwargs) -> str:
        r'''
        .. codeauthor:: Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>
        
        Implement a string representation of the class.
        
        :returns: the string representation
        :rtype: :python:`str`
        '''
        
        return f'{self.value}'
    
    @check_type(bool)
    def set(self, value: bool, *args, **kwargs) -> None:
        r'''
        .. codeauthor:: Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>
        
        Set the current value.

        :param value: new value
        :type value: :python:`bool`
        '''
        
        self.check_bounds(value, None, None, self._testFunc, self._testMsg)
        self.value = value
        return
        
    
class IntProperty(Property):
    r'''
    .. codeauthor:: Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>
    
    Define a property object which stores a single integer.
    
    :param default: default value used at init
    :type default: :python:`int`

    :param minBound: (**Optional**) minimum value for the property. If :python:`None`, it is ignored.
    :type minBound: :python:`int`
    :param maxBound: (**Optional**) maximum value for the property. If :python:`None`, it is ignored.
    :type maxBound: :python:`int`
    :param testFunc: (**Optional**) a test function with the value to test as argument which must not be passed in order to set a value. This can be used to add additional checks which are not taken into account by default.
    :type testFunc: :python:`Callable`
    :param testMsg: (**Optional**) a test message used to throw an error if **testFunc** returns :python:`False`
    :type testMsg: :python:`str`
    '''
    
    def __init__(self, default: int,
                 minBound: int = None, 
                 maxBound: int = None, 
                 testFunc: Callable[[int], bool] = lambda value: False, 
                 testMsg: str ='', **kwargs) -> None:
        
        r'''Init method.'''
        
        super().__init__(default, minBound=minBound, maxBound=maxBound, testFunc=testFunc, testMsg=testMsg)
        
        # Set the value to check data type (default property has already been set)
        self.set(default)
        
    def __str__(self, *args, **kwargs) -> str:
        r'''
        .. codeauthor:: Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>
        
        Implement a string representation of the class.
        
        :returns: the string representation
        :rtype: :python:`str`
        '''
        
        return f'{self.value}'
    
    @check_type(int)
    def set(self, value: int, *args, **kwargs) -> None:
        r'''.. codeauthor:: Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>
        
        Set the current value.

        :param value: new value. Must be within bounds.
        :type value: :python:`int`
        '''
        
        self.check_bounds(value, self.min, self.max, self._testFunc, self._testMsg)
        self.value = value
        return
    
class FloatProperty(Property):
    r'''
    .. codeauthor:: Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>
    
    Define a property object which stores a single float.
    
    :param default: default value used at init
    :type default: :python:`float`

    :param minBound: (**Optional**) minimum value for the property. If :python:`None`, it is ignored.
    :type minBound: :python:`float`
    :param maxBound: (**Optional**) maximum value for the property. If :python:`None`, it is ignored.
    :type maxBound: :python:`float`
    :param testFunc: (**Optional**) a test function with the value to test as argument which must not be passed in order to set a value. This can be used to add additional checks which are not taken into account by default.
    :type testFunc: :python:`Callable`
    :param testMsg: (**Optional**) a test message used to throw an error if **testFunc** returns :python:`False`
    :type testMsg: :python:`str`
    '''
    
    def __init__(self, default: float,
                 minBound: float = None, 
                 maxBound: float = None, 
                 testFunc: Callable[[float], bool] = lambda value: False, 
                 testMsg: str ='', **kwargs) -> None:
        
        r'''Init method.'''
        
        super().__init__(default, minBound=minBound, maxBound=maxBound, testFunc=testFunc, testMsg=testMsg)
        
        # Set the value to check data type (default property has already been set)
        self.set(default)
        
    def __str__(self, *args, **kwargs) -> str:
        r'''
        .. codeauthor:: Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>
        
        Implement a string representation of the class.
        
        :returns: the string representation
        :type: :python:`str`
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
        r'''
        .. codeauthor:: Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>
        
        Set the current value.

        :param value: new value. Must be within bounds.
        :type value: :python:`float`
        '''
        
        if value != '-1':
            self.check_bounds(value, self.min, self.max, self._testFunc, self._testMsg)
            
        self.value = value
        return
    
class StrProperty(Property):
    r'''
    .. codeauthor:: Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>
    
    Define a property which stores a single str object.
    
    :param default: default value used at init
    :type default: :python:`str`

    :param testFunc: (**Optional**) a test function with the value to test as argument which must not be passed in order to set a value. This can be used to add additional checks which are not taken into account by default.
    :type testFunc: :python:`Callable`
    :param testMsg: (**Optional**) a test message used to throw an error if **testFunc** returns :python:`False`
    :type testMsg: :python:`str`
    '''
    
    def __init__(self, default: str,
                 testFunc: Callable[[str], bool] = lambda value: False, 
                 testMsg: str ='', **kwargs) -> None:
        
        r'''Init method.'''
        
        super().__init__(default, minBound=None, maxBound=None, testFunc=testFunc, testMsg=testMsg)
        
        # Set the value to check data type (default property has already been set)
        self.set(default)
        
    def __str__(self, *args, **kwargs) -> str:
        r'''
        .. codeauthor:: Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>
        
        Implement a string representation of the class.
        
        :returns: the string representatin
        :rtype: :python:`str`
        '''
        
        return self.value
    
    @check_type(str)
    def set(self, value: str, *args, **kwargs) -> None:
        r'''
        .. codeauthor:: Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>
        
        Set the current value.

        :param value: new value. Must be within bounds.
        :type value: :python:`str`
        
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
    .. codeauthor:: Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>
    
    An abstract class which defines a property which stores a list object.
    
    You must subclass it with __str__ and set methods or use a default subclass in order to use it.
    
    :param default: default value used at init

    :param minBound: (**Optional**) minimum value for the property. If :python:`None`, it is ignored.
    :param maxBound: (**Optional**) maximum value for the property. If :python:`None`, it is ignored.
    :param testFunc: (**Optional**) a test function with the value to test as argument which must not be passed in order to set a value. This can be used to add additional checks which are not taken into account by default.
    :type testFunc: :python:`Callable`
    :param testMsg: (**Optional**) a test message used to throw an error if testFunc returns False
    :type testMsg: :python:`str`
    '''
        
    def __init__(self, default: List[Any],
                 minBound: Any = None, 
                 maxBound: Any = None, 
                 testFunc: Callable[[List[Any]], bool] = lambda value: False, 
                 testMsg: str ='', **kwargs) -> None:
        
        r'''Init method.'''
        
        super().__init__(default, minBound=minBound, maxBound=maxBound, testFunc=testFunc, testMsg=testMsg)
        
    ###############################
    #        Miscellaneous        #
    ###############################
    
    @staticmethod
    def check_bounds(value: List[Any], mini: Any, maxi: Any, func: Callable, msg: str) -> None:
        r'''
        .. codeauthor:: Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>
        
        :param value: value to check
        :type value: :python:`list`
        :param mini: minimum value
        :param maxi: maximum value
        :param func: test function with the value to test as argument which must not be passed in order to set a value. This can be used to add additional checks which are not taken into account by default.
        :type func: :python:`Callable`
        :param msg: test message used to throw an error if testFunc returns False
        :type msg: :python:`str`
        
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

        :param value: new value. Must be of correct type, and within bounds.
        :type value: :python:`list`
        '''
        
        return
    
class ListIntProperty(ListProperty):
    r'''
    .. codeauthor:: Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>
    
    Define a property which stores an int list object.
    
    :param default: default value used at init
    :type default: :python:`list[int]`

    :param minBound: (**Optional**) minimum value for the property. If :python:`None`, it is ignored.
    :type minBound: :python:`int`
    :param maxBound: (**Optional**) maximum value for the property. If :python:`None`, it is ignored.
    :type maxBound: :python:`int`
    :param testFunc: (**Optional**) a test function with the value to test as argument which must not be passed in order to set a value. This can be used to add additional checks which are not taken into account by default.
    :type testFunc: :python:`Callable`
    :param testMsg: (**Optional**) a test message used to throw an error if **testFunc** returns :python:`False`
    :type testMsg: :python:`str`
    '''
    
    def __init__(self, default: List[int],
                 minBound: int = None, 
                 maxBound: int = None, 
                 testFunc: Callable[[List[int]], bool] = lambda value: False, 
                 testMsg: str ='', 
                 **kwargs) -> None:
        
        r'''Init method.'''
        
        super().__init__(default, minBound=minBound, maxBound=maxBound, testFunc=testFunc, testMsg=testMsg)
        
        # Set the value to check data type (default property has already been set)
        self.set(default)
        
    def __str__(self, *args, **kwargs) -> str:
        r'''
        .. codeauthor:: Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>
        
        Implement a string representation of the class.
        
        :returns: the string representation
        :rtype: :python:`str`
        '''
        
        return ','.join([f'{i}' for i in self.value])
        
    @check_type(list)
    @check_type_in_list(int)
    def set(self, value: List[int], *args, **kwargs) -> None:
        r'''
        .. codeauthor:: Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>
        
        Set the current value.

        :param value: new value. Must be of correct type, and within bounds.
        :type value: :python:`list[int]`
        '''
        
        self.check_bounds(value, self.min, self.max, self._testFunc, self._testMsg)
        self.value = value
        return
    
class ListFloatProperty(ListProperty):
    r'''
    .. codeauthor:: Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>
    
    Define a property which stores an int list object.
    
    :param default: default value used at init
    :type default: :python:`list[float]`

    :param minBound: (**Optional**) minimum value for the property. If :python:`None`, it is ignored.
    :type minBound: :python:`float`
    :param maxBound: (**Optional**) maximum value for the property. If :python:`None`, it is ignored.
    :type maxBound: :python:`float`
    :param testFunc: (**Optional**) a test function with the value to test as argument which must not be passed in order to set a value. This can be used to add additional checks which are not taken into account by default.
    :type testFunc: :python:`Callable`
    :param testMsg: (**Optional**) a test message used to throw an error if testFunc returns False
    :type testMsg: :python:`str`
    '''
    
    def __init__(self, default: List[float],
                 minBound: float = None, 
                 maxBound: float = None, 
                 testFunc: Callable[[List[float]], bool] = lambda value: False, 
                 testMsg: str ='', 
                 **kwargs) -> None:
        
        r'''Init method.'''
        
        super().__init__(default, minBound=minBound, maxBound=maxBound, testFunc=testFunc, testMsg=testMsg)
        
        # Set the value to check data type (default property has already been set)
        self.set(default)
        
    def __str__(self, *args, **kwargs) -> str:
        r'''
        .. codeauthor:: Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>
        
        Implement a string representation of the class.
        
        :returns: the string representation
        :rtype: :python:`str`
        '''
        
        return ','.join([f'{i:.3f}' if i == 0 or (i > 1e-3 and i < 1e3) else f'{i:.3e}' for i in self.value])
        
    @check_type(list)
    @check_type_in_list(float)
    def set(self, value: List[float], *args, **kwargs) -> None:
        r'''
        .. codeauthor:: Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>
        
        Set the current value.

        :param value: new value. Must be of correct type, and within bounds.
        :type value: :python:`list[float]`
        '''
        
        self.check_bounds(value, self.min, self.max, self._testFunc, self._testMsg)
        self.value = value
        return

class ListStrProperty(ListProperty):
    r'''
    .. codeauthor:: Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>
    
    Define a property which stores an int list object.
    
    :param default: default value used at init
    :type default: :python:`list[str]`

    :param testFunc: (**Optional**) a test function with the value to test as argument which must not be passed in order to set a value. This can be used to add additional checks which are not taken into account by default.
    :type testFunc: :python:`Callable`
    :param testMsg: (**Optional**) a test message used to throw an error if **testFunc** returns :python:`False`
    :type testMsg: :python:`str`
    '''
    
    def __init__(self, default: List[str],
                 testFunc: Callable[[List[str]], bool] = lambda value: False, 
                 testMsg: str ='', **kwargs) -> None:
        
        r'''Init method.'''
        
        super().__init__(default, minBound=None, maxBound=None, testFunc=testFunc, testMsg=testMsg)
        
        # Set the value to check data type (default property has already been set)
        self.set(default)
        
    def __str__(self, *args, **kwargs) -> str:
        r'''
        .. codeauthor:: Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>
        
        Implement a string representation of the class.
        
        :returns: the string representation
        :rtype: :python:`str`
        '''
        
        return ','.join(self.value)
        
    @check_type(list)
    @check_type_in_list(str)
    def set(self, value: List[str], *args, **kwargs) -> None:
        r'''
        .. codeauthor:: Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>
        
        Set the current value.

        :param value: new value. Must be of correct type, and within bounds.
        :type value: :python:`list[str]`
        
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
    r'''
    .. codeauthor:: Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>
    
    Define a property which stores a str object which includes additional checks for paths.
    
    :param default: default value used at init
    :type default: :python:`str`

    :param testFunc: (**Optional**) a test function with the value to test as argument which must not be passed in order to set a value. This can be used to add additional checks which are not taken into account by default.
    :type testFunc: :python:`Callable`
    :param testMsg: (**Optional**) a test message used to throw an error if **testFunc** returns :python:`False`
    :type testMsg: :python:`str`
    :param str path: (**Optional**) path to append each time to the new value
    :type path: :python:`str`
    :param str ext: (**Optional**) extension to append at the end of the file name when checking the path
    :type ext: :python:`str`
    
    :raises TypeError: if neither **path** nor **ext** are :python:`str`
    '''

    def __init__(self, default: str,
                 testFunc: Callable[[str], bool] = lambda value: False, 
                 testMsg: str ='', 
                 path: str = '', 
                 ext: str = '', **kwargs) -> None:
        
        r'''Init method.'''
        
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
        
        :returns: the string representation
        :type: :python:`str`
        '''
        
        return self.value
    
    @check_type(str)
    def set(self, value: str, *args, **kwargs) -> None:
        r'''
        .. codeauthor:: Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>
        
        Set the current value.

        :param value: new value. Must be within bounds.
        :type value: :python:`str`
        
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
    r'''
    .. codeauthor:: Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>
    
    Define a property which stores a str list object which includes additional checks for paths.
    
    :param default: default value used at init
    :type default: :python:`list[str]`

    :param testFunc: (**Optional**) a test function with the value to test as argument which must not be passed in order to set a value. This can be used to add additional checks which are not taken into account by default.
    :type testFunc: :python:`Callable`
    :param testMsg: (**Optional**) a test message used to throw an error if **testFunc** returns :python:`False`
    :type testMsg: :python:`str`
    :param path: (**Optional**) path to append each time to the new value
    :type path: :python:`str`
    :param ext: (**Optional**) extension to append at the end of the file name when checking the path
    :type ext: :python:`str`
    
    :raises TypeError: if neither **path** nor **ext** are :python:`str`
    '''

    def __init__(self, default: List[str],
                 testFunc: Callable[[List[str]], bool] = lambda value: False, 
                 testMsg: str ='', 
                 path: str = '', 
                 ext: str = '', 
                 **kwargs) -> None:
        
        r'''Init method.'''
        
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
        
        :returns: the string representation
        :rtype: :python:`str`
        '''
        
        return ','.join(self.value)
        
    @check_type(list)
    @check_type_in_list(str)
    def set(self, value: List[str], *args, **kwargs) -> None:
        r'''
        .. codeauthor:: Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>
        
        Set the current value.

        :param value: new value. Must be of correct type, and within bounds.
        :type value: :python:`list[str]`
        
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

class EnumProperty(Property):
    r'''
    .. codeauthor:: Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>
    
    Define a property which stores an Enum object.
    
    :param default: default value used at init
    :type default: :python:`enum.Enum`

    :param testFunc: (**Optional**) a test function with the value to test as argument which must not be passed in order to set a value. This can be used to add additional checks which are not taken into account by default.
    :type testFunc: :python:`Callable`
    :param testMsg: (**Optional**) a test message used to throw an error if **testFunc** returns :python:`False`
    :type testMsg: :python:`str`
    '''
    
    def __init__(self, value: Enum, 
                 testFunc: Callable[[List[str]], bool] = lambda value: False, 
                 testMsg: str ='', 
                 **kwargs) -> None:
    
        r'''Init method.'''
        
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
        
        :returns: the string representation
        :rtype: :python:`str`
        '''
        
        return self.value.value
       
    @check_type(Enum)
    def set(self, value: Enum, *args, **kwargs) -> None:
        r'''
        .. codeauthor:: Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>
        
        Set the current value.

        :param value: new value
        :type: :python:`enum.Enum`
        
        :raises TypeError: if **value** is not of type :python:`enum.Enum`
        :raises ValueError: if the test function does not pass
        '''
            
        if self._testFunc(value):
            raise ValueError(self._testMsg)
            
        self.value = value
        return
    
    