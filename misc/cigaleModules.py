#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
.. codeauthor:: Wilfried Mercier - IRAP/LAM <wilfried.mercier@lam.fr>

Modules which can be used with Cigale.
"""

from   abc           import ABC, abstractmethod
from   .enum         import IMF
from   .properties   import BoolProperty, PathProperty, StrProperty, EnumProperty, ListIntProperty, ListFloatProperty
from   typing        import List, Any

##########################################
#        Star Formation Histories        #
##########################################

class SFHmodule(ABC):
    r'''
    .. codeauthor:: Wilfried Mercier - IRAP/LAM <wilfried.mercier@lam.fr>
    
    Base class implementing a module to deal with SFH models.
    
    :param name: identifier for the class
    
    **Keyword arguments**
    
    :param normalise: whether to normalise the SFH to produce one solar mass
    :type normalise: :python:`bool`
    '''
    
    def __init__(self, name: Any, normalise: bool = True) -> None:
        r'''Init method.'''
        
        self.name      = name
        self.normalise = BoolProperty(normalise)
        
    @abstractmethod
    def __str__(self, *args, **kwargs) -> str:
        r'''
        .. codeauthor:: Wilfried Mercier - IRAP/LAM <wilfried.mercier@ilam.fr>
        
        Implement a string representation of the class used to make Cigale parameter files.
        '''
        
        return
    
    @property
    @abstractmethod
    def spec(self, *args, **kwargs) -> str:
        r'''
        .. codeauthor:: Wilfried Mercier - IRAP/LAM <wilfried.mercier@lam.fr>
        
        Implement a string representation for the .spec file of Cigale parameters.
        '''
        
        return
    
class SFH2EXPmodule(SFHmodule):
    r'''
    .. codeauthor:: Wilfried Mercier - IRAP/LAM <wilfried.mercier@lam.fr>
    
    Class implementing a module for an SFH with two exponential components. Each component has an SFH of the form:
        
    .. math::
        
        {\rm SFH}(t) \propto \exp \lbrace -t/\tau \rbrace,
        
    with :math:`\tau` equal to **tau_main** for the first stellar population and **tau_burst** for the second one. The time :math:`t` starts at the age of the stellar populations, so **age_main** for the first one and **age_burst** for the second one. The final SFH is the sum of the two individual SFHs.
    
    **Keyword arguments**
    
    :param tau_main: e-folding time of the main stellar population model in :math:`\rm Myr`. Minimum is :math:`0\,\rm Myr`.
    :type tau_main: :python:`list[int]`
    :param tau_burst: e-folding time of the late starburst population model in :math:`\rm Myr`. Minimum is :math:`0\,\rm Myr`.
    :type tau_burst: :python:`list[int]`
    :param f_burst: mass fraction of the late burst population. Minimum is :math:`0.0`, maximum is :math:`0.9999`.
    :type f_burst: :python:`list[float]`
    :param list age: age of the main stellar population in :math:`\rm Myr`. Minimum is :math:`0\,\rm Myr`.
    :type age: :python:`list[int]`
    :param list burst_age: age of the late burst in :math:`\rm Myr`. Minimum is :math:`0\,\rm Myr`.
    :type burst_age: :python:`list[int]`
    :param list sfr_0: value of SFR at t = 0 in :math:`\rm M_{\odot}\,yr^{-1}`. Minimum is :math:`0.0\,\rm M_{\odot}\,yr^{-1}`.
    :type sfr_0: :python:`list[float]`
    :param bool normalise: whether to normalise the SFH to produce one solar mass or not
    :type normalise: :python:`bool`
    '''
    
    def __init__(self, 
                 tau_main:  List[int]   = [6000], 
                 tau_burst: List[int]   = [50],
                 f_burst:   List[float] = [0.01], 
                 age:       List[int]   = [5000], 
                 burst_age: List[int]   = [20], 
                 sfr_0:     List[float] = [1.0],
                 normalise: bool        = True
                ) -> None:
        
        r'''Init method.'''
        
        super().__init__('sfh2exp', normalise=normalise)
        
        self.tau_main  = ListIntProperty(  tau_main,  minBound=0)
        self.tau_burst = ListIntProperty(  tau_burst, minBound=0)
        self.f_burst   = ListFloatProperty(f_burst,   minBound=0.0, maxBound=0.9999)
        self.age       = ListIntProperty(  age,       minBound=0)
        self.burst_age = ListIntProperty(  burst_age, minBound=0)
        self.sfr_0     = ListFloatProperty(sfr_0,     minBound=0.0)
        
    def __str__(self, *args, **kwargs) -> str:
        r'''
        .. codeauthor:: Wilfried Mercier - IRAP/LAM <wilfried.mercier@lam.fr>
        
        Implement a string representation of the class used to make Cigale parameter files.
        '''
        
        text = f'''\
        [[sfh2exp]]
          # e-folding time of the main stellar population model in Myr.
          tau_main = {self.tau_main}
          # e-folding time of the late starburst population model in Myr.
          tau_burst = {self.tau_burst}
          # Mass fraction of the late burst population.
          f_burst = {self.f_burst}
          # Age of the main stellar population in the galaxy in Myr. The precision
          # is 1 Myr.
          age = {self.age}
          # Age of the late burst in Myr. The precision is 1 Myr.
          burst_age = {self.burst_age}
          # Value of SFR at t = 0 in M_sun/yr.
          sfr_0 = {self.sfr_0}
          # Normalise the SFH to produce one solar mass.
          normalise = {self.normalise}
        '''
        
        return text
    
    @property
    def spec(self, *args, **kwargs) -> str:
        r'''
        .. codeauthor:: Wilfried Mercier - IRAP/LAM <wilfried.mercier@lam.fr>
        
        Implement a string representation for the .spec file of Cigale parameters.
        '''
        
        text = '''\
        [[sfh2exp]]
          tau_main = cigale_list()
          tau_burst = cigale_list()
          f_burst = cigale_list(minvalue=0., maxvalue=0.9999)
          age = cigale_list(dtype=int, minvalue=0.)
          burst_age = cigale_list(dtype=int, minvalue=1.)
          sfr_0 = cigale_list(minvalue=0.)
          normalise = boolean()\
        '''
        
        return text
    
    
class SFHDELAYEDmodule(SFHmodule):
    r'''
    .. codeauthor:: Wilfried Mercier - IRAP/LAM <wilfried.mercier@lam.fr>
    
    Class implementing a module for a delayed exponential SFH with a potential exponential burst. Without any burst, the SFH is equal to:
        
    .. math::
        
        {\rm SFH}(t) = {\rm SFR_A} \times \frac{t}{\tau_{\rm main}^2} \exp \lbrace -t/\tau_{\rm main} \rbrace.
        
    After that a time **age_burst** has elapsed and if **f_burst** is different from 0, the SFH is increased by an amount:
        
    .. math::
        
        {\rm SFH}(t) \propto \exp \lbrace -t/\tau_{\rm burst} \rbrace,
        
    where :math:`t` is counted starting from **age\_burst** and the amplitude of the burst is controlled by its mass fraction **f_burst**.
    
    **Keyword arguments**
    
    :param tau_main: e-folding time of the main stellar population model in :math:`\rm Myr`. Minimum is :math:`0\,\rm Myr`.
    :type tau_main: :python:`list[int]`
    :param age_main: age of the main stellar population in the galaxy in :math:`\rm Myr`. Minimum is :math:`0\,\rm Myr`.
    :type age_main: :python:`list[int]`
    :param tau_burst: e-folding time of the late starburst population model in :math:`\rm Myr`. Minimum is :math:`0\,\rm Myr`.
    :type tau_burst: :python:`list[int]`
    :param age_burst: age of the late burst in :math:`\rm Myr`. Minimum is :math:`0\,\rm Myr`.
    :type age_burst: :python:`list[int]`
    :param f_burst: mass fraction of the late burst population. Minimum is :math:`0.0`, maximum is :math:`0.9999`.
    :type f_burst: :python:`list[float]`
    :param sfr_A: multiplicative factor controlling the amplitude of the SFR in :math:`\rm M_{\odot}\,yr^{-1}` if **normalise** is :python:`True`. Minimum is :math:`0.0\,\rm M_{\odot}\,yr^{-1}`. For instance without any burst: SFR(t)=sfr_A×t×exp(-t/τ)/τ².
    :type sfr_A: :python:`list[float]`
    :param normalise: whether to normalise the SFH to produce one solar mass or not
    :type normalise: :python:`bool`
    '''
    
    def __init__(self, 
                 tau_main:  List[int]   = [2000], 
                 age_main:  List[int]   = [5000],
                 tau_burst: List[int]   = [50],
                 age_burst: List[int]   = [20], 
                 f_burst:   List[float] = [0.0],  
                 sfr_A:     List[float] = [1.0],
                 normalise: bool        = True
                ) -> None:
        
        r'''Init method.'''
        
        super().__init__('sfhdelayed', normalise=normalise)
        
        self.tau_main  = ListIntProperty(  tau_main,  minBound=0)
        self.age_main  = ListIntProperty(  age_main,  minBound=0)
        self.tau_burst = ListIntProperty(  tau_burst, minBound=0)
        self.age_burst = ListIntProperty(  age_burst, minBound=0)
        self.f_burst   = ListFloatProperty(f_burst,   minBound=0.0, maxBound=0.9999)
        self.sfr_A     = ListFloatProperty(sfr_A,     minBound=0.0)
        
    def __str__(self, *args, **kwargs) -> str:
        r'''
        .. codeauthor:: Wilfried Mercier - IRAP/LAM <wilfried.mercier@lam.fr>
        
        Implement a string representation of the class used to make Cigale parameter files.
        '''
        
        text = f'''\
        [[sfhdelayed]]
          # e-folding time of the main stellar population model in Myr.
          tau_main = {self.tau_main}
          # Age of the main stellar population in the galaxy in Myr. The precision
          # is 1 Myr.
          age_main = {self.age_main}
          # e-folding time of the late starburst population model in Myr.
          tau_burst = {self.tau_burst}
          # Age of the late burst in Myr. The precision is 1 Myr.
          age_burst = {self.age_burst}
          # Mass fraction of the late burst population.
          f_burst = {self.f_burst}
          # Multiplicative factor controlling the SFR if normalise is False. For
          # instance without any burst: SFR(t)=sfr_A×t×exp(-t/τ)/τ²
          sfr_A = {self.sfr_A}
          # Normalise the SFH to produce one solar mass.
          normalise = {self.normalise}
        '''
        
        return text
    
    @property
    def spec(self, *args, **kwargs) -> str:
        r'''
        .. codeauthor:: Wilfried Mercier - IRAP/LAM <wilfried.mercier@lam.fr>
        
        Implement a string representation for the .spec file of Cigale parameters.
        '''
        
        text = '''\
        [[sfhdelayed]]
          tau_main = cigale_list()
          age_main = cigale_list(dtype=int, minvalue=0.)
          tau_burst = cigale_list()
          age_burst = cigale_list(dtype=int, minvalue=1.)
          f_burst = cigale_list(minvalue=0., maxvalue=0.9999)
          sfr_A = cigale_list(minvalue=0.)
          normalise = boolean()\
        '''
        
        return text
    
    
class SFHDELAYEDBQmodule(SFHmodule):
    r'''
    .. codeauthor:: Wilfried Mercier - IRAP/LAM <wilfried.mercier@lam.fr>
    
    Class implementing a module for a delayed exponential SFH with a burst/quench episode. Without any burst/quench episode, the SFH is equal to:
        
    .. math::
        
        {\rm SFH}(t) = {\rm SFR_A} \times \frac{t}{\tau_{\rm main}^2} \exp \lbrace -t/\tau_{\rm main} \rbrace.
        
    After that a time **age_bq** has elapsed and if **r_sfr** is different from 0, the SFH becomes a constant value equal to:
        
    .. math::
        
        {\rm SFH_{after}}(t) = {\rm SFH_{before}} \times r_{\rm SFR},
        
    where :math:`\rm SFH_{before}` is the value of the SFH just before the burst/quench episode.
    
    
    **Keyword arguments**
    
    :param tau_main: e-folding time of the main stellar population model in :math:`\rm Myr`. Minimum is :math:`0\,\rm Myr`.
    :type tau_main: :python:`list[int]`
    :param age_main: age of the main stellar population in the galaxy in :math:`\rm Myr`. Minimum is :math:`0\,\rm Myr`.
    :type age_main: :python:`list[int]`
    :param age_bq: age of the burst/quench episode in :math:`\rm Myr`. Minimum is :math:`0\,\rm Myr`.
    :type age_bq: :python:`list[int]`
    :param r_sfr: ratio of the SFR after/before age_bq. Minimum is :math:`0.0`.
    :type r_sfr: :python:`list[float]`
    :param sfr_A: multiplicative factor controlling the SFR if **normalise** is False. Minimum is :math:`0.0`. For instance without any burst: SFR(t)=sfr_A×t×exp(-t/τ)/τ²
    :type sfr_A: :python:`list[float]`
    :param normalise: whether to normalise the SFH to produce one solar mass
    :type normalise: :python:`bool`
    '''
    
    def __init__(self, 
                 tau_main:  List[int]   = [2000], 
                 age_main:  List[int]   = [5000],
                 age_bq:    List[int]   = [500],
                 r_sfr:     List[float] = [0.1], 
                 sfr_A:     List[float] = [1.0],
                 normalise: bool        = True
                ) -> None:
        
        r'''Init method.'''
        
        super().__init__('sfhdelayedbq', normalise=normalise)
        
        self.tau_main  = ListIntProperty(  tau_main,  minBound=0)
        self.age_main  = ListIntProperty(  age_main,  minBound=0)
        self.age_bq    = ListIntProperty(  age_bq,    minBound=0)
        self.r_sfr     = ListFloatProperty(r_sfr,     minBound=0.0)
        self.sfr_A     = ListFloatProperty(sfr_A,     minBound=0.0)
        
    def __str__(self, *args, **kwargs) -> str:
        r'''
        .. codeauthor:: Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>
        
        Implement a string representation of the class used to make Cigale parameter files.
        '''
        
        text = f'''\
        [[sfhdelayedbq]]
          # e-folding time of the main stellar population model in Myr.
          tau_main = {self.tau_main}
          # Age of the main stellar population in the galaxy in Myr. The precision
          # is 1 Myr.
          age_main = {self.age_main}
          # Age of the burst/quench episode. The precision is 1 Myr.
          age_bq = {self.age_bq}
          # Ratio of the SFR after/before age_bq.
          r_sfr = {self.r_sfr}
          # Multiplicative factor controlling the SFR if normalise is False. For
          # instance without any burst/quench: SFR(t)=sfr_A×t×exp(-t/τ)/τ²
          sfr_A = {self.sfr_A}
          # Normalise the SFH to produce one solar mass.
          normalise = {self.normalise}    
        '''
        
        return text

    @property
    def spec(self, *args, **kwargs) -> str:
        r'''
        .. codeauthor:: Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>
        
        Implement a string representation for the .spec file of Cigale parameters.
        '''
        
        text = '''\
        [[sfhdelayedbq]]
          tau_main = cigale_list()
          age_main = cigale_list(dtype=int, minvalue=0.)
          age_bq = cigale_list(dtype=int)
          r_sfr = cigale_list(minvalue=0.)
          sfr_A = cigale_list(minvalue=0.)
          normalise = boolean()\
        '''
        
        return text
    
    
class SFHFROMFILEmodule(SFHmodule):
    r'''
    .. codeauthor:: Wilfried Mercier - IRAP/LAM <wilfried.mercier@lam.fr>
    
    Class implementing a module for a SFH read from a FITS or VOtable file.
    
    .. note::
        
        The first column of the input file must be the time in :math:`\rm Myr`, starting from :math:`0\,\rm Myr` with a step of :math:`1\,\rm Myr`. Other columns contain the SFHs in :math:`\rm M_{\odot}\,yr^{-1}`.
    
    **Keyword arguments**
    
    :param filename: name of the input FITS or VOtable file containing the SFH
    :type filename: :python:`str`
    :param sfr_column: list of column indices where the SFHs are located in the input file. The first SFH column has the index 1.
    :type sfr_column: :python:`list[int]`
    :param age: age in :math:`\rm Myr` at which the SFHs start
    :type age: :python:`list[int]`
    :param normalise: whether to normalise the SFH to produce one solar mass or not
    :type normalise: :python:`bool`
    '''
    
    def __init__(self, 
                 filename:   str       = '',
                 sfr_column: List[int] = [1],
                 age:        List[int] = [1000],
                 normalise:  bool      = True
                ) -> None:
        
        r'''Init method.'''
        
        super().__init__('sfrfromfile', normalise=normalise)
        
        self.filename   = PathProperty(filename)
        self.sfr_column = ListIntProperty(sfr_column)
        self.age        = ListIntProperty(age, minBound=0)
        
    def __str__(self, *args, **kwargs) -> str:
        r'''
        .. codeauthor:: Wilfried Mercier - IRAP/LAM <wilfried.mercier@lam.fr>
        
        Implement a string representation of the class used to make Cigale parameter files.
        '''
        
        text = f'''\
        [[sfhfromfile]]
          # Name of the file containing the SFH. The first column must be the time
          # in Myr, starting from 0 with a step of 1 Myr. The other columns must
          # contain the SFR in Msun/yr.[Msun/yr].
          filename = {self.filename}
          # List of column indices of the SFR. The first SFR column has the index
          # 1.
          sfr_column = {self.sfr_column}
          # Age in Myr at which the SFH will be looked at.
          age = {self.age}
          # Normalise the SFH to one solar mass produced at the given age.
          normalise = {self.normalise}
        '''
        
        return text
    
    @property
    def spec(self, *args, **kwargs) -> str:
        r'''
        .. codeauthor:: Wilfried Mercier - IRAP/LAM <wilfried.mercier@lam.fr>
        
        Implement a string representation for the .spec file of Cigale parameters.
        '''
        
        text = '''\
        [[sfhfromfile]]
          filename = string()
          sfr_column = cigale_list(dtype=int)
          age = cigale_list(dtype=int, minvalue=0.)
          normalise = boolean()\
        '''
        
        return text
    
    
class SFHPERIODICmodule(SFHmodule):
    r'''
    .. codeauthor:: Wilfried Mercier - IRAP/LAM <wilfried.mercier@lam.fr>
    
    Class implementing a module for a SFH with periodic bursts. The first burst will start at an age **age_burst**, and then each burst will follow the previous one after a time **delta_bursts** has elapsed. 
    
    Three burst SFHs are possible:
    
    * Exponential: :math:`{\rm SFH} (t) = {\rm SFR_A} \times \exp \lbrace - t / \tau_{\rm burst} \rbrace`
    * Delayed exponential: :math:`{\rm SFH} (t) = {\rm SFR_A} \times \frac{t}{\tau_{\rm burst}^2} \exp \lbrace - t / \tau_{\rm burst} \rbrace`
    * Rectangular: :math:`{\rm SFH} (t) = {\rm SFR_A}` for :math:`0 < t  < \tau_{\rm burst}` and :math:`{\rm SFH} (t) = 0\,\rm M_{\odot}\,yr^{-1}` otherwise. For each burst, :math:`t` is counted at the start of the burst.

    The total SFH is simply the sum of all individual SFHs.
    
    **Keyword arguments**
    
    :param type_bursts: type of the individual star formation episodes. Options are 0 for exponential, 1 for delayed, and 2 for rectangle.
    :type type_bursts: :python:`list[int]`
    :param delta_bursts: elapsed time between the beginning of each burst in :math:`\rm Myr`
    :type delta_bursts: :python:`list[int]`
    :param tau_burst: duration of the bursts. For exponential and delayed types, this corresponds to the e-folding time and for rectangular bursts this corresponds to their duration.
    :type tau_bursts: :python:`list[int]`
    :param age: age of the main stellar population in the galaxy in :math:`\rm Myr`
    :type age: :python:`list[int]`
    :param sfr_A: multiplicative factor controlling the amplitude of SFR (valid for each event)
    :type sfr_A: :python:`list[float]`
    :param normalise: whether to normalise the SFH to produce one solar mass or not
    :type normalise: :python:`bool`
    '''
    
    def __init__(self, 
                 type_bursts:  List[int]   = [0],
                 delta_bursts: List[int]   = [50],
                 tau_bursts:   List[int]   = [20],
                 age:          List[int]   = [1000],
                 sfr_A:        List[float] = [1.0],
                 normalise:    bool        = True
                ) -> None:
        
        r'''Init method.'''
        
        super().__init__('sfhperiodic', normalise=normalise)
        
        self.type_bursts  = ListIntProperty(  type_bursts,  minBound=0, maxBound=2)
        self.delta_bursts = ListIntProperty(  delta_bursts, minBound=0)
        self.tau_bursts   = ListIntProperty(  tau_bursts,   minBound=0)
        self.age          = ListIntProperty(  age,          minBound=0)
        self.sfr_A        = ListFloatProperty(sfr_A,        minBound=0.0)
        
    def __str__(self, *args, **kwargs) -> str:
        r'''
        .. codeauthor:: Wilfried Mercier - IRAP/LAM <wilfried.mercier@lam.fr>
        
        Implement a string representation of the class used to make Cigale parameter files.
        '''
        
        text = f'''\
        [[sfhperiodic]]
          # Type of the individual star formation episodes. 0: exponential, 1:
          # delayed, 2: rectangle.
          type_bursts = {self.type_bursts}
          # Elapsed time between the beginning of each burst in Myr. The precision
          # is 1 Myr.
          delta_bursts = {self.delta_bursts}
          # Duration (rectangle) or e-folding time of all short events in Myr. The
          # precision is 1 Myr.
          tau_bursts = {self.tau_bursts}
          # Age of the main stellar population in the galaxy in Myr. The precision
          # is 1 Myr.
          age = {self.age}
          # Multiplicative factor controlling the amplitude of SFR (valid for each
          # event).
          sfr_A = {self.sfr_A}
          # Normalise the SFH to produce one solar mass.
          normalise = {self.normalise}
        '''
        
        return text
    
    @property
    def spec(self, *args, **kwargs) -> str:
        r'''
        .. codeauthor:: Wilfried Mercier - IRAP/LAM <wilfried.mercier@lam.fr>
        
        Implement a string representation for the .spec file of Cigale parameters.
        '''
        
        text = '''\
        [[sfhperiodic]]
          type_bursts = cigale_list(dtype=int, options=0. & 1. & 2.)
          delta_bursts = cigale_list(dtype=int, minvalue=0.)
          tau_bursts = cigale_list()
          age = cigale_list(dtype=int, minvalue=0.)
          sfr_A = cigale_list(minvalue=0.)
          normalise = boolean()\
        '''
        
        return text
    
class SFH_BUATmodule(SFHmodule):
    r'''
    .. codeauthor:: Wilfried Mercier - IRAP/LAM <wilfried.mercier@lam.fr>
    
    Class implementing a module for a SFH from Buat et al. (2008). The SFH writes:
        
    .. math::
        
        \log_{10} {\rm SFH} (t) = a (V) + b (V) \times \log_{10} t + c (V) \times t^{1/2},
        
    where :math:`a`, :math:`b`, and :math:`c` are functions of the rotational velocity :math:`V` of the galaxy.
    
    .. note::
        
        The functional forms of :math:`a`, :math:`b`, and :math:`c` only work for :math:`40 < V [{\rm km\,s^{-1}}] <360`.
    
    **Keyword arguments**
    
    :param velocity: rotational velocity of the galaxy in :math:`\rm km\,s^{-1}`. Must be between 40 :math:`\rm km\,s^{-1}` and 360 :math:`\rm km\,s^{-1}` (included).
    :type velocity: :python:`list[float]`
    :param age: age of the oldest stars in the galaxy in :math:`\rm Myr`
    :type age: :python:`list[int]`
    :param normalise: whether to normalise the SFH to produce one solar mass or not
    :type normalise: :python:`bool`
    '''
    
    def __init__(self, 
                 velocity  : List[float] = [200.0],
                 age       : List[int]   = [5000],
                 normalise : bool        = True
                ) -> None:
        
        r'''Init method.'''
        
        super().__init__('sfh_buat2008', normalise=normalise)
        
        self.velocity = ListFloatProperty(velocity, minBound=40.0, maxBound=360.0)
        self.age      = ListIntProperty(  age,      minBound=0)
        
    def __str__(self, *args, **kwargs) -> str:
        r'''
        .. codeauthor:: Wilfried Mercier - IRAP/LAM <wilfried.mercier@lam.fr>
        
        Implement a string representation of the class used to make Cigale parameter files.
        '''
        
        text = f'''\
        [[sfh_buat08]]
          # Rotational velocity of the galaxy in km/s. Must be between 40 and 360
          # (included).
          velocity = {self.velocity}
          # Age of the oldest stars in the galaxy. The precision is 1 Myr.
          age = {self.age}
          # Normalise the SFH to produce one solar mass.
          normalise = {self.normalise}
        '''
        
        return text
    
    @property
    def spec(self, *args, **kwargs) -> str:
        r'''
        .. codeauthor:: Wilfried Mercier - IRAP/LAM <wilfried.mercier@lam.fr>
        
        Implement a string representation for the .spec file of Cigale parameters.
        '''
        
        text = '''\
        [[sfh_buat08]]
          velocity = cigale_list(minvalue=40., maxvalue=360.)
          age = cigale_list(dtype=int, minvalue=0.)
          normalise = boolean()\
        '''
        
        return text
    
class SFH_QUENCHING_SMOOTHmodule(SFHmodule):
    r'''
    .. codeauthor:: Wilfried Mercier - IRAP/LAM <wilfried.mercier@lam.fr>
    
    Class implementing a module that linearly quenches any SFH module by a factor **1 - quenching_factor**. If the SFH is equal to :math:`{\rm SFH} (t_{\rm before})` just before the quenching which is happening at the lookback time **quenching_time**, the SFH becomes after:
    
    .. math::
        
        {\rm SFH} (t) = {\rm SFH} (t_{\rm before}) \times \left ( 1 - f_{\rm q} \times \frac{t - t_{\rm main} + t_{\rm q}}{t_{\rm q}} \right ),
        
    where :math:`f_{\rm q}` is **quenching_factor**, :math:`t_{\rm main}` is the age of the main SFH, and :math:`t_{\rm q}` is **quenching_time**. Thus, 
    
    * right at the beginning of the quenching phase, :math:`t = t_{\rm main} - t_{\rm q}`, meaning that :math:`{\rm SFH} (t) = {\rm SFH} (t_{\rm before})`.
    * at the end of the quenching phase, :math:`t = t_{\rm main}`, meaning that :math:`{\rm SFH} (t) = {\rm SFH} (t_{\rm before}) \times (1 - f_{\rm q})`
    
    .. important::
        
        This module does not work in standalone since it only quenches another SFH. Thus, at least one other SFH module must be provided for the main stellar populations in combination with this one.
    
    **Keyword arguments**
    
    :param quenching_time: look-back time when the quenching starts in :math:`\rm Myr`. Minimum is :math:`0\,\rm Myr`.
    :type quenching_time: :python:`list[int]`
    :param quenching_factor: quenching factor between 0 and 1 applied to the SFH when quenching starts. It must be between 0.0 (no quenching) and 1.0 (SFH equal to :math:`0\,\rm M_{\odot}\,yr^{-1}`).
    :type quenching_factor: :python:`list[float]`
    :param normalise: whether to normalise the SFH to produce one solar mass or not
    :type normalise: :python:`bool`
    '''
    
    def __init__(self, 
                 quenching_time   : List[int]   = [0],
                 quenching_factor : List[float] = [0.0],
                 normalise        : bool        = True
                ) -> None:
        
        r'''Init method.'''
        
        super().__init__('sfh_quenching_smooth', normalise=normalise)
        
        self.quenching_time   = ListIntProperty(  quenching_time,   minBound=0)
        self.quenching_factor = ListFloatProperty(quenching_factor, minBound=0.0, maxBound=1.0)
        
    def __str__(self, *args, **kwargs) -> str:
        r'''
        .. codeauthor:: Wilfried Mercier - IRAP/LAM <wilfried.mercier@lam.fr>
        
        Implement a string representation of the class used to make Cigale parameter files.
        '''
        
        text = f'''\
        [[sfh_quenching_smooth]]
          # Look-back time when the quenching starts in Myr.
          quenching_time = {self.quenching_time}
          # Quenching factor applied to the SFH. After the quenching time, the SFR
          # is multiplied by 1 - quenching factor and made constant. The factor
          # must be between 0 (no quenching) and 1 (no more star formation).
          quenching_factor = {self.quenching_factor}
          # Normalise the SFH to produce one solar mass.
          normalise = {self.normalise}
        '''
        
        return text
    
    @property
    def spec(self, *args, **kwargs) -> str:
        r'''
        .. codeauthor:: Wilfried Mercier - IRAP/LAM <wilfried.mercier@lam.fr>
        
        Implement a string representation for the .spec file of Cigale parameters.
        '''
        
        text = '''\
        [[sfh_quenching_smooth]]
          quenching_time = cigale_list(dtype=int, minvalue=0.)
          quenching_factor = cigale_list(minvalue=0., maxvalue=1.)
          normalise = boolean()\
        '''
        
        return text
    
class SFH_QUENCHING_TRUNKmodule(SFHmodule):
    r'''
    .. codeauthor:: Wilfried Mercier - IRAP/LAM <wilfried.mercier@lam.fr>
    
    Class implementing a module that quenches to a constant value any SFH module by multiplying it by a factor **1 - quenching_factor**. If the SFH is equal to :math:`{\rm SFH} (t_{\rm before})` just before the quenching which is happening at the lookback time **quenching_time**, the SFH becomes after:

    .. math::
        
        {\rm SFH} (t) = {\rm SFH} (t_{\rm before}) \times ( 1 - f_{\rm q} ),
    
    where :math:`f_{\rm q}` is **quenching_factor**.
    
    .. important::
        
        This module does not work in standalone since it only quenches another SFH. Thus, at least one other SFH module must be provided for the main stellar populations in combination with this one.
    
    **Keyword arguments**
    
    :param quenching_age: look-back time when the quenching happens in :math:`\rm Myr`
    :type quenching_age: :python:`list[int]`
    :param quenching_factor: quenching factor applied to the SFH.
    :type quenching_factor: :python:`list[float]`
    :param normalise: whether to normalise the SFH to produce one solar mass or not
    :type normalise: :python:`bool`
    '''
    
    def __init__(self, 
                 quenching_age    : List[int]   = [0],
                 quenching_factor : List[float] = [0.0],
                 normalise        : bool        = True
                ) -> None:
        
        r'''Init method.'''
        
        super().__init__('sfh_quenching_smooth', normalise=normalise)
        
        self.quenching_age    = ListIntProperty(  quenching_age,    minBound=0)
        self.quenching_factor = ListFloatProperty(quenching_factor, minBound=0.0, maxBound=1.0)
        
    def __str__(self, *args, **kwargs) -> str:
        r'''
        .. codeauthor:: Wilfried Mercier - IRAP/LAM <wilfried.mercier@lam.fr>
        
        Implement a string representation of the class used to make Cigale parameter files.
        '''
        
        text = f'''\
        [[sfh_quenching_trunk]]
          # Look-back time when the quenching happens in Myr.
          quenching_age = {self.quenching_age}
          # Quenching factor applied to the SFH. After the quenching time, the SFR
          # is multiplied by 1 - quenching factor and made constant. The factor
          # must be between 0 (no quenching) and 1 (no more star formation).
          quenching_factor = {self.quenching_factor}
          # Normalise the SFH to produce one solar mass.
          normalise = {self.normalise}
        '''
        
        return text
    
    @property
    def spec(self, *args, **kwargs) -> str:
        r'''
        .. codeauthor:: Wilfried Mercier - IRAP/LAM <wilfried.mercier@lam.fr>
        
        Implement a string representation for the .spec file of Cigale parameters.
        '''
        
        text = '''\
        [[sfh_quenching_trunk]]
          quenching_age = cigale_list(dtype=int, minvalue=0.)
          quenching_factor = cigale_list(minvalue=0., maxvalue=1.)
          normalise = boolean()\
        '''
        
        return text
    
############################################
#        Single Stellar Populations        #
############################################

class SSPmodule(ABC):
    r'''
    .. codeauthor:: Wilfried Mercier - IRAP/LAM <wilfried.mercier@lam.fr>
    
    Base class implementing a module to deal with SSP models.
    
    :param name: identifier for the class
    
    **Keyword arguments**
    
    :param imf: initial mass function. Options are given in :class:`~pixSED.misc.enum.IMF`.
    :type imf: :python:`list[pixSED.misc.enum.IMF]`
    :param separation_age: age in :math:`\rm Myr` of the separation between the young and the old star populations. Set to 0 to not differentiate ages (only an old population).
    :type separation_age: :python:`list[int]`
    '''
    
    def __init__(self, 
                 name           : Any,
                 imf            : IMF       = IMF.SALPETER,
                 separation_age : List[int] = [10]
                ) -> None:
        
        r'''Init method.'''
        
        self.name           = name
        self.imf            = EnumProperty(imf)
        self.separation_age = ListIntProperty(separation_age, minBound=0)
        
    @abstractmethod
    def __str__(self, *args, **kwargs) -> str:
        r'''
        .. codeauthor:: Wilfried Mercier - IRAP/LAM <wilfried.mercier@lam.fr>
        
        Implement a string representation of the class used to make Cigale parameter files.
        '''
        
        return
    
    @property
    @abstractmethod
    def spec(self, *args, **kwargs) -> str:
        r'''
        .. codeauthor:: Wilfried Mercier - IRAP/LAM <wilfried.mercier@lam.fr>
        
        Implement a string representation for the .spec file of Cigale parameters.
        '''
        
        return
    
class BC03module(SSPmodule):
    r'''
    .. codeauthor:: Wilfried Mercier - IRAP/LAM <wilfried.mercier@lam.fr>
    
    Class implementing a Bruzual et Charlot (2003) SSP module.
    
    **Keyword arguments**
    
    :param imf: initial mass function. Options are :attr:`~pixSED.misc.enum.IMF.CHABRIER` or :attr:`~pixSED.misc.enum.IMF.SALPETER`.
    :type imf: :python:`list[pixSED.misc.enum.IMF]`
    :param separation_age: age in :math:`\rm Myr` of the separation between the young and the old star populations. Set to 0 to not differentiate ages (only an old population).
    :type separation_age: :python:`list[int]`
    :param list metallicity: possible values are 0.0001, 0.0004, 0.004, 0.008, 0.02, 0.05
    :type metallicity: :python:`list[float]`
    '''
    
    def __init__(self, 
                 imf            : IMF         = IMF.SALPETER,
                 separation_age : List[int]   = [10],
                 metallicity    : List[float] = [0.02]
                ) -> None:
        
        r'''Init method.'''
        
        super().__init__('bc03', imf=imf, separation_age=separation_age)
        
        self.metallicity = ListFloatProperty(metallicity, minBound=0.0001, maxBound=0.05, 
                                             testFunc=lambda value: any((i not in [0.0001, 0.0004, 0.004, 0.008, 0.02, 0.05] for i in value)),
                                             testMsg='Metallicity for bc03 module must be one of 0.0001, 0.0004, 0.004, 0.008, 0.02, 0.05.')
        
    def __str__(self, *args, **kwargs) -> str:
        r'''
        .. codeauthor:: Wilfried Mercier - IRAP/LAM <wilfried.mercier@lam.fr>
        
        Implement a string representation of the class used to make Cigale parameter files.
        '''
        
        text = f'''\
        [[bc03]]
          # Initial mass function: 0 (Salpeter) or 1 (Chabrier).
          imf = {self.imf}
          # Metalicity. Possible values are: 0.0001, 0.0004, 0.004, 0.008, 0.02,
          # 0.05.
          metallicity = {self.metallicity}
          # Age [Myr] of the separation between the young and the old star
          # populations. The default value in 10^7 years (10 Myr). Set to 0 not to
          # differentiate ages (only an old population).
          separation_age = {self.separation_age}
        '''
        
        return text
    
    @property
    def spec(self, *args, **kwargs) -> str:
        r'''
        .. codeauthor:: Wilfried Mercier - IRAP/LAM <wilfried.mercier@lam.fr>
        
        Implement a string representation for the .spec file of Cigale parameters.
        '''
        
        text = '''\
        [[bc03]]
          imf = cigale_list(dtype=int, options=0. & 1.)
          metallicity = cigale_list(options=0.0001 & 0.0004 & 0.004 & 0.008 & 0.02 & 0.05)
          separation_age = cigale_list(dtype=int, minvalue=0)\
        '''
        
        return text
    
class M2005module(SSPmodule):
    r'''
    .. codeauthor:: Wilfried Mercier - IRAP/LAM <wilfried.mercier@lam.fr>
    
    Class implementing a Maraston (2005) SSP module.
    
    .. warning:
        
        This module cannot be combined with :class:`~pixSED.misc.cigaleModules.NEBULARmodule`.
    
    **Keyword arguments**
    
    :param imf: initial mass function. Options are :attr:`~pixSED.misc.enum.IMF.SALPETER` or :attr:`~pixSED.misc.enum.IMF.KROUPA`.
    :type imf: :python:`list[pixSED.misc.enum.IMF]`
    :param separation_age: age in in :math:`\rm Myr` of the separation between the young and old stellar populations. Set to 0 not to differentiate ages (only an old population).
    :type separation_age: :python:`list[int]`
    :param metallicity: possible values are 0.001, 0.01, 0.02, 0.04
    :type metallicity: :python:`list[float]`
    '''
    
    def __init__(self, 
                 imf            : IMF         = IMF.SALPETER,
                 separation_age : List[int]   = [10],
                 metallicity    : List[float] = [0.02]
                ) -> None:
        
        r'''Init method.'''
        
        super().__init__('m2005', imf=imf, separation_age=separation_age)
        
        self.metallicity = ListFloatProperty(metallicity, minBound=0.001, maxBound=0.04, 
                                             testFunc=lambda value: any((i not in [0.001, 0.01, 0.02, 0.04] for i in value)),
                                             testMsg='Metallicity for bc03 module must be one of 0.001, 0.01, 0.02, 0.04.')
        
    def __str__(self, *args, **kwargs) -> str:
        r'''
        .. codeauthor:: Wilfried Mercier - IRAP/LAM <wilfried.mercier@lam.fr>
        
        Implement a string representation of the class used to make Cigale parameter files.
        '''
        
        text = f'''\
        [[m2005]]
          # Initial mass function: 0 (Salpeter) or 1 (Kroupa)
          imf = {self.imf}
          # Metallicity. Possible values are: 0.001, 0.01, 0.02, 0.04.
          metallicity = {self.metallicity}
          # Age [Myr] of the separation between the young and the old star
          # populations. The default value in 10^7 years (10 Myr). Set to 0 not to
          # differentiate ages (only an old population).
          separation_age = {self.separation_age}
        '''
        
        return text
    
    @property
    def spec(self, *args, **kwargs) -> str:
        r'''
        .. codeauthor:: Wilfried Mercier - IRAP/LAM <wilfried.mercier@lam.fr>
        
        Implement a string representation for the .spec file of Cigale parameters.
        '''
        
        text = '''\
        [[m2005]]
          imf = cigale_list(dtype=int, options=0. & 1.)
          metallicity = cigale_list(options=0.001 & 0.01 & 0.02 & 0.04)
          separation_age = cigale_list(dtype=int, minvalue=0.)\
        '''
        
        return text
    
##################################
#        Nebular emission        #
##################################

class NEBULARmodule:
    r'''
    .. codeauthor:: Wilfried Mercier - IRAP/LAM <wilfried.mercier@lam.fr>
    
    Class implementing a module to deal with nebular emission.
    
    .. warning:
        
        This module cannot be combined with :class:`~pixSED.misc.cigaleModules.M2005module`.
    
    **Keyword arguments**
    
    :param logU: ionisation parameter. Minimum value is -4.0, maximum is -1.0 and steps of 0.1 only are accepted (i.e. -1.5 is ok but not -1.53).
    :type logU: :python:`list[float]`
    :param f_esc: fraction of Lyman continuum photons escaping the galaxy
    :type f_esc: :python:`list[float]`
    :param f_dust: fraction of Lyman continuum photons absorbed by dust
    :type f_dust: :python:`list[float]`
    :param lines_width: line width in in :math:`\rm km\,s^{-1}`
    :type lines_width: :python:`list[float]`
    :param include_emission: whether to include the nebular emission or not
    :type include_emission: :python:`bool`
    '''
    
    def __init__(self, 
                 logU             : List[float] = [-2.0],
                 f_esc            : List[float] = [0.0],
                 f_dust           : List[float] = [0.0],
                 lines_width      : List[float] = [300.0],
                 include_emission : bool        = True
                ) -> None:
        
        r'''Init method.'''
        
        self.name        = 'nebular'
        
        logURange        = [i/10 for i in range(-40, -9, 1)]
        
        self.logU        = ListFloatProperty(logU, minBound=-4.0, maxBound=-1.0,
                                             testFunc=lambda value: any((i not in logURange for i in value)),
                                             testMsg=f'One on the logU values is not accepted. Accepted values must be in the list {logURange}')
        
        self.f_esc       = ListFloatProperty(f_esc,       minBound=0, maxBound=1)
        self.f_dust      = ListFloatProperty(f_dust,      minBound=0, maxBound=1)
        self.lines_width = ListFloatProperty(lines_width, minBound=0)
        self.emission    = BoolProperty(include_emission)
        
    def __str__(self, *args, **kwargs) -> str:
        r'''
        .. codeauthor:: Wilfried Mercier - IRAP/LAM <wilfried.mercier@lam.fr>
        
        Implement a string representation of the class used to make Cigale parameter files.
        '''
        
        text = f'''\
        [[nebular]]
          # Ionisation parameter
          logU = {self.logU}
          # Fraction of Lyman continuum photons escaping the galaxy
          f_esc = {self.f_esc}
          # Fraction of Lyman continuum photons absorbed by dust
          f_dust = {self.f_dust}
          # Line width in km/s
          lines_width = {self.lines_width}
          # Include nebular emission.
          emission = {self.emission}
        '''
        
        return text
    
    @property
    def spec(self, *args, **kwargs) -> str:
        r'''
        .. codeauthor:: Wilfried Mercier - IRAP/LAM <wilfried.mercier@lam.fr>
        
        Implement a string representation for the .spec file of Cigale parameters.
        '''
        
        text = '''\
        [[nebular]]
          logU = cigale_list(options=-4.0 & -3.9 & -3.8 & -3.7 & -3.6 & -3.5 & -3.4 & -3.3 & -3.2 & -3.1 & -3.0 & -2.9 & -2.8 & -2.7 & -2.6 & -2.5 & -2.4 & -2.3 & -2.2 & -2.1 & -2.0 & -1.9 & -1.8 & -1.7 & -1.6 & -1.5 & -1.4 & -1.3 & -1.2 & -1.1 & -1.0)
          f_esc = cigale_list(minvalue=0., maxvalue=1.)
          f_dust = cigale_list(minvalue=0., maxvalue=1.)
          lines_width = cigale_list(minvalue=0.)
          emission = boolean()\
        '''
        
        return text
    
##################################
#        Dust attenuation        #
##################################

class ATTENUATIONmodule(ABC):
    r'''
    .. codeauthor:: Wilfried Mercier - IRAP/LAM <wilfried.mercier@lam.fr>
    
    Base class implementing a module to deal with dust attenuation.
    
    :param name: identifier for the class
    
    **Keyword arguments**
    
    :param filters: filters for which the attenuation will be computed and added to the SED information dictionary. You can give several filter names separated by a & (don't use commas).
    :type filters: :python:`str`
    '''
    
    def __init__(self, name: Any, filters: str = 'V_B90 & FUV') -> None:
        r'''Init method.'''
        
        self.name    = name
        self.filters = StrProperty(filters)
        
    @abstractmethod
    def __str__(self, *args, **kwargs) -> str:
        r'''
        .. codeauthor:: Wilfried Mercier - IRAP/LAM <wilfried.mercier@lam.fr>
        
        Implement a string representation of the class used to make Cigale parameter files.
        '''
        
        return
    
    @property
    @abstractmethod
    def spec(self, *args, **kwargs) -> str:
        r'''
        .. codeauthor:: Wilfried Mercier - IRAP/LAM <wilfried.mercier@lam.fr>
        
        Implement a string representation for the .spec file of Cigale parameters.
        '''
        
        return
    
class DUSTATT_POWERLAWmodule(ATTENUATIONmodule):
    r'''
    .. codeauthor:: Wilfried Mercier - IRAP/LAM <wilfried.mercier@lam.fr>
    
    Class implementing a single powerlaw attenuation law module.
    
    **Keyword arguments**
    
    :param filters: filters for which the attenuation will be computed and added to the SED information dictionary. You can give several filter names separated by a & (don't use commas).
    :type filters: :python:`str`
    :param Av_young: V-band attenuation of the young stellar population
    :type Av_young: :python:`list[float]`
    :param list Av_old_factor: reduction factor for the V-band attenuation of the old population compared to the young one. It must be between 0 and 1.
    :type Av_old_factor: :python:`list[float]`
    :param uv_bump_wavelength: central wavelength of the UV bump in :math:`\rm nm`
    :type uv_bump_wavelength: :python:`list[float]`
    :param uv_bump_width: width (FWHM) of the UV bump in :math:`\rm nm`
    :type uv_bump_width: :python:`list[float]`
    :param uv_bump_amplitude: amplitude of the UV bump. For the Milky Way: 0.75.
    :type uv_bump_amplitude: :python:`list[float]`
    :param powerlaw_slope: slope delta of the power law modifying the attenuation curve
    :type powerlaw_slope: :python:`list[float]`
    '''
    
    def __init__(self, 
                 filters            : str         = 'V_B90 & FUV',
                 Av_young           : List[float] = [1.0],
                 Av_old_factor      : List[float] = [0.44],
                 uv_bump_wavelength : List[float] = [217.5],
                 uv_bump_width      : List[float] = [35.0],
                 uv_bump_amplitude  : List[float] = [0.0],
                 powerlaw_slope     : List[float] = [-0.7]
                ) -> None:
        
        r'''Init method.'''
        
        super().__init__('dustatt_powerlaw', filters=filters)
        
        self.filters            = StrProperty(filters)
        self.Av_young           = ListFloatProperty(Av_young,           minBound=0.0)
        self.Av_old_factor      = ListFloatProperty(Av_old_factor,      minBound=0.0, maxBound=1.0)
        self.uv_bump_wavelength = ListFloatProperty(uv_bump_wavelength, minBound=0.0)
        self.uv_bump_width      = ListFloatProperty(uv_bump_width,      minBound=0.0)
        self.uv_bump_amplitude  = ListFloatProperty(uv_bump_amplitude,  minBound=0.0)
        self.powerlaw_slope     = ListFloatProperty(powerlaw_slope)
        
    def __str__(self, *args, **kwargs) -> str:
        r'''
        .. codeauthor:: Wilfried Mercier - IRAP/LAM <wilfried.mercier@lam.fr>
        
        Implement a string representation of the class used to make Cigale parameter files.
        '''
        
        text = f'''\
        [[dustatt_powerlaw]]
          # V-band attenuation of the young population.
          Av_young = {self.Av_young}
          # Reduction factor for the V-band attenuation of the old population
          # compared to the young one (<1).
          Av_old_factor = {self.Av_old_factor}
          # Central wavelength of the UV bump in nm.
          uv_bump_wavelength = {self.uv_bump_wavelength}
          # Width (FWHM) of the UV bump in nm.
          uv_bump_width = {self.uv_bump_width}
          # Amplitude of the UV bump. For the Milky Way: 0.75
          uv_bump_amplitude = {self.uv_bump_amplitude}
          # Slope delta of the power law continuum.
          powerlaw_slope = {self.powerlaw_slope}
          # Filters for which the attenuation will be computed and added to the
          # SED information dictionary. You can give several filter names
          # separated by a & (don't use commas).
          filters = {self.filters}
        '''
        
        return text
    
    @property
    def spec(self, *args, **kwargs) -> str:
        r'''
        .. codeauthor:: Wilfried Mercier - IRAP/LAM <wilfried.mercier@lam.fr>
        
        Implement a string representation for the .spec file of Cigale parameters.
        '''
        
        text = '''\
        [[dustatt_powerlaw]]
          Av_young = cigale_list(minvalue=0.)
          Av_old_factor = cigale_list(minvalue=0., maxvalue=1.)
          uv_bump_wavelength = cigale_list(minvalue=0.)
          uv_bump_width = cigale_list(minvalue=0.)
          uv_bump_amplitude = cigale_list(minvalue=0.)
          powerlaw_slope = cigale_list()
          filters = string()\
        '''
        
        return text
    
class DUSTATT_2POWERLAWSmodule(ATTENUATIONmodule):
    r'''
    .. codeauthor:: Wilfried Mercier - IRAP/LAM <wilfried.mercier@lam.fr>
    
    Class implementing a double powerlaw attenuation law module: a birth cloud power law applied only to the young star population and an ISM power law applied to both the young and the old stellar populations.
    
    **Keyword arguments**
    
    :param filters: filters for which the attenuation will be computed and added to the SED information dictionary. You can give several filter names separated by a & (don't use commas).
    :type filters: :python:`str`
    :param Av_BC: V-band attenuation in the birth clouds. Minimum is 0.
    :type Av_BC: :python:`list[float]`
    :param slope_BC: power law slope of the attenuation in the birth clouds
    :type slope_BC: :python:`list[float]`
    :param BC_to_ISM_factor: Av ISM / Av BC. Must be between 0 and 1.
    :type BC_to_ISM_factor: :python:`list[float]`
    :param slope_ISM: power law slope of the attenuation in the ISM
    :type slope_ISM: :python:`list[float]`
    '''
    
    def __init__(self, 
                 filters          : str         = 'V_B90 & FUV',
                 Av_BC            : List[float] = [1.0],
                 slope_BC         : List[float] = [-1.3],
                 BC_to_ISM_factor : List[float] = [0.44],
                 slope_ISM        : List[float] = [-0.7]
                ) -> None:
        
        r'''Init method.'''
        
        super().__init__('dustatt_2powerlaws', filters=filters)
        
        self.filters          = StrProperty(filters)
        self.Av_BC            = ListFloatProperty(Av_BC,            minBound=0.0)
        self.slope_BC         = ListFloatProperty(slope_BC)
        self.BC_to_ISM_factor = ListFloatProperty(BC_to_ISM_factor, minBound=0.0, maxBound=1.0)
        self.slope_ISM        = ListFloatProperty(slope_ISM)
        
    def __str__(self, *args, **kwargs) -> str:
        r'''
        .. codeauthor:: Wilfried Mercier - IRAP/LAM <wilfried.mercier@lam.fr>
        
        Implement a string representation of the class used to make Cigale parameter files.
        '''
        
        text = f'''\
        [[dustatt_2powerlaws]]
          # V-band attenuation in the birth clouds.
          Av_BC = {self.av_BC}
          # Power law slope of the attenuation in the birth clouds.
          slope_BC = {self.slope_BC}
          # Av ISM / Av BC (<1).
          BC_to_ISM_factor = {self.BC_to_ISM_factor}
          # Power law slope of the attenuation in the ISM.
          slope_ISM = {self.slope_ISM}
          # Filters for which the attenuation will be computed and added to the
          # SED information dictionary. You can give several filter names
          # separated by a & (don't use commas).
          filters = {self.filters}
        '''
        
        return text
    
    @property
    def spec(self, *args, **kwargs) -> str:
        r'''
        .. codeauthor:: Wilfried Mercier - IRAP/LAM <wilfried.mercier@lam.fr>
        
        Implement a string representation for the .spec file of Cigale parameters.
        '''
        
        text = '''\
        [[dustatt_2powerlaws]]
          Av_BC = cigale_list(minvalue=0)
          slope_BC = cigale_list()
          BC_to_ISM_factor = cigale_list(minvalue=0., maxvalue=1.)
          slope_ISM = cigale_list()
          filters = string()\
        '''
        
        return text
    
class DUSTATT_CALZLETTImodule(ATTENUATIONmodule):
    r'''
    .. codeauthor:: Wilfried Mercier - IRAP/LAM <wilfried.mercier@lam.fr>
    
    Class implementing a Calzetti et al. (2000) and  Leitherer et al. (2002) attenuation law module.
    
    **Keyword arguments**
    
    :param filters: filters for which the attenuation will be computed and added to the SED information dictionary. You can give several filter names separated by a & (don't use commas).
    :type filters: :python:`str`
    :param E_BVs_young: E(B-V)*, the colour excess of the stellar continuum light for the young population. Minimum is 0.
    :type E_BVs_young: :python:`list[float]`
    :param E_BVs_old_factor: reduction factor for the E(B-V)* of the old population compared to the young one. Must be between 0 and 1.
    :type E_BVs_old_factor: :python:`list[float]`
    :param uv_bump_wavelength: central wavelength of the UV bump in :math:`\rm nm`. Minimum is :math:`0\,\rm nm`.
    :type uv_bump_wavelength: :python:`list[float]`
    :param uv_bump_width: width (FWHM) of the UV bump in :math:`\rm nm`. Minimum is :math:`0\,\rm nm`.
    :type uv_bump_width: :python:`list[float]`
    :param uv_bump_amplitude: amplitude of the UV bump. For the Milky Way: 3. Minimum is 0.
    :type uv_bump_amplitude: :python:`list[float]`
    :param powerlaw_slope: slope delta of the power law modifying the attenuation curve.
    :type powerlaw_slope: :python:`list[float]`
    '''
    
    def __init__(self, 
                 filters            : str         = 'B_B90 & V_B90 & FUV',
                 E_BVs_young        : List[float] = [0.3],
                 E_BVs_old_factor   : List[float] = [1.0],
                 uv_bump_wavelength : List[float] = [217.5],
                 uv_bump_width      : List[float] = [35.0],
                 uv_bump_amplitude  : List[float] = [0.0],
                 powerlaw_slope     : List[float] = [0.0]
                ) -> None:
        
        r'''Init method.'''
        
        super().__init__('dustatt_calzleit', filters=filters)
        
        self.filters            = StrProperty(filters)
        self.E_BVs_young        = ListFloatProperty(E_BVs_young,        minBound=0.0)
        self.E_BVs_old_factor   = ListFloatProperty(E_BVs_old_factor,   minBound=0.0, maxBound=0.0)
        self.uv_bump_wavelength = ListFloatProperty(uv_bump_wavelength, minBound=0.0)
        self.uv_bump_width      = ListFloatProperty(uv_bump_width,      minBound=0.0)
        self.uv_bump_amplitude  = ListFloatProperty(uv_bump_amplitude,  minBound=0.0)
        self.powerlaw_slope     = ListFloatProperty(powerlaw_slope)
        
    def __str__(self, *args, **kwargs) -> str:
        r'''
        .. codeauthor:: Wilfried Mercier - IRAP/LAM <wilfried.mercier@lam.fr>
        
        Implement a string representation of the class used to make Cigale parameter files.
        '''
        
        text = f'''\
        [[dustatt_calzleit]]
          # E(B-V)*, the colour excess of the stellar continuum light for the
          # young population.
          E_BVs_young = {self.E_BVs_young}
          # Reduction factor for the E(B-V)* of the old population compared to the
          # young one (<1).
          E_BVs_old_factor = {self.E_BVs_old_factor}
          # Central wavelength of the UV bump in nm.
          uv_bump_wavelength = {self.uv_bump_wavelength}
          # Width (FWHM) of the UV bump in nm.
          uv_bump_width = {self.uv_bump_width}
          # Amplitude of the UV bump. For the Milky Way: 3.
          uv_bump_amplitude = {self.uv_bump_amplitude}
          # Slope delta of the power law modifying the attenuation curve.
          powerlaw_slope = {self.powerlaw_slope}
          # Filters for which the attenuation will be computed and added to the
          # SED information dictionary. You can give several filter names
          # separated by a & (don't use commas).
          filters = {self.filters}
        '''
        
        return text
    
    @property
    def spec(self, *args, **kwargs) -> str:
        r'''
        .. codeauthor:: Wilfried Mercier - IRAP/LAM <wilfried.mercier@lam.fr>
        
        Implement a string representation for the .spec file of Cigale parameters.
        '''
        
        text = '''\
        [[dustatt_calzleit]]
          E_BVs_young = cigale_list(minvalue=0.)
          E_BVs_old_factor = cigale_list(minvalue=0., maxvalue=1.)
          uv_bump_wavelength = cigale_list(minvalue=0.)
          uv_bump_width = cigale_list()
          uv_bump_amplitude = cigale_list(minvalue=0.)
          powerlaw_slope = cigale_list()
          filters = string()\
        '''
        
        return text
    
class DUSTATT_MODIFIED_CF00module(ATTENUATIONmodule):
    r'''
    .. codeauthor:: Wilfried Mercier - IRAP/LAM <wilfried.mercier@lam.fr>
    
    Class implementing a modified Charlot & Fall 2000 attenuation law module.
    
    **Keyword arguments**
    
    :param filters: filters for which the attenuation will be computed and added to the SED information dictionary. You can give several filter names separated by a & (don't use commas).
    :type filters: :python:`str`
    :param Av_ISM: V-band attenuation in the interstellar medium. Minimum is 0.
    :type Av_ISM: :python:`list[float]`
    :param mu: Av_ISM / (Av_BC+Av_ISM). Must be between 0.0001 and 1.
    :type mu: :python:`list[float]`
    :param list slope_ISM: power law slope of the attenuation in the ISM
    :type slope_ISM: :python:`list[float]`
    :param list slope_BC: power law slope of the attenuation in the birth clouds
    :type slope_BC: :python:`list[float]`
    '''
    
    def __init__(self, 
                 filters   : str         = 'V_B90 & FUV',
                 Av_ISM    : List[float] = [1.0],
                 mu        : List[float] = [0.44],
                 slope_ISM : List[float] = [-0.7],
                 slope_BC  : List[float] = [-1.3]
                ) -> None:
        
        r'''Init method.'''
        
        super().__init__('dustatt_modified_cf00', filters=filters)
        
        self.filters   = StrProperty(filters)
        self.Av_ISM    = ListFloatProperty(Av_ISM, minBound=0.0)
        self.mu        = ListFloatProperty(mu,     minBound=0.0001, maxBound=1.0)
        self.slope_ISM = ListFloatProperty(slope_ISM)
        self.slope_ISM = ListFloatProperty(slope_BC)
        
    def __str__(self, *args, **kwargs) -> str:
        r'''
        .. codeauthor:: Wilfried Mercier - IRAP/LAM <wilfried.mercier@lam.fr>
        
        Implement a string representation of the class used to make Cigale parameter files.
        '''
        
        text = f'''\
        [[dustatt_modified_CF00]]
          # V-band attenuation in the interstellar medium.
          Av_ISM = {self.Av_ISM}
          # Av_ISM / (Av_BC+Av_ISM)
          mu = {self.mu}
          # Power law slope of the attenuation in the ISM.
          slope_ISM = {self.slope_ISM}
          # Power law slope of the attenuation in the birth clouds.
          slope_BC = {self.slope_BC}
          # Filters for which the attenuation will be computed and added to the
          # SED information dictionary. You can give several filter names
          # separated by a & (don't use commas).
          filters = {self.filters}
        '''
        
        return text
    
    @property
    def spec(self, *args, **kwargs) -> str:
        r'''
        .. codeauthor:: Wilfried Mercier - IRAP/LAM <wilfried.mercier@lam.fr>
        
        Implement a string representation for the .spec file of Cigale parameters.
        '''
        
        text = '''\
        [[dustatt_modified_CF00]]
          Av_ISM = cigale_list(minvalue=0)
          mu = cigale_list(minvalue=.0001, maxvalue=1.)
          slope_ISM = cigale_list()
          slope_BC = cigale_list()
          filters = string()\
        '''
        
        return text
    
class DUSTATT_MODIFIED_STARBURSTmodule(ATTENUATIONmodule):
    r'''
    .. codeauthor:: Wilfried Mercier - IRAP/LAM <wilfried.mercier@lam.fr>
    
    Class implementing a modified Calzetti 2000 attenuation law module.
    
    **Keyword arguments**
    
    :param filters: filters for which the attenuation will be computed and added to the SED information dictionary. You can give several filter names separated by a & (don't use commas).
    :type filters: :python:`str`
    :param E_BV_lines: E(B-V)l, the colour excess of the nebular lines light for both the young and old stellar population. Minimum is 0.
    :type E_BV_lines: :python:`list[float]`
    :param E_BV_factor: reduction factor to apply on E_BV_lines to compute E(B-V)s the stellar continuum attenuation. Both young and old population are attenuated with E(B-V)s. Must be between 0 and 1.
    :type E_BV_factor: :python:`list[float]`
    :param uv_bump_wavelength: central wavelength of the UV bump in :math:`\rm nm`. Minimum is :math:`0\,\rm nm`.
    :type uv_bump_wavelength: :python:`list[float]`
    :param uv_bump_width: width (FWHM) of the UV bump in :math:`\rm nm`. Minimum is :math:`0\,\rm nm`.
    :type uv_bump_width: :python:`list[float]`
    :param uv_bump_amplitude: amplitude of the UV bump. For the Milky Way: 3. Minimum is 0.
    :type uv_bump_amplitude: :python:`list[float]`
    :param powerlaw_slope: slope delta of the power law modifying the attenuation curve
    :type powerlaw_slope: :python:`list[float]`
    :param Ext_law_emission_lines: extinction law to use for attenuating the emission lines flux. Possible values are: 1, 2, 3. 1: Milky Way, 2: Large Magellanic Cloud, 3: Small Magellanic Cloud. MW is modelled using CCM89, SMC and LMC using Pei92.
    :type Ext_law_emission_lines: :python:`list[int]`
    :param Rv: ratio of total to selective extinction, A_V / E(B-V), for the extinction curve applied to emission lines. Standard value is 3.1 for MW using CCM89, but can be changed. For SMC and LMC, using Pei92, the value is automatically set to 2.93 and 3.16 respectively, no matter the value you provide.
    :type Rv: :python:`list[float]`
    '''
    
    def __init__(self, 
                 filters                : str         = 'B_B90 & V_B90 & FUV',
                 E_BV_lines             : List[float] = [0.3],
                 E_BV_factor            : List[float] = [0.44],
                 uv_bump_wavelength     : List[float] = [217.5],
                 uv_bump_width          : List[float] = [35.0],
                 uv_bump_amplitude      : List[float] = [0.0],
                 powerlaw_slope         : List[float] = [0.0],
                 Ext_law_emission_lines : List[int]   = 1,
                 Rv                     : List[float] = 3.1
                ) -> None:
        
        r'''Init method.'''
        
        super().__init__('dustatt_modified_starbust', filters=filters)
        
        self.filters                = StrProperty(filters)
        self.E_BV_lines             = ListFloatProperty(E_BV_lines,           minBound=0.0)
        self.E_BV_factor            = ListFloatProperty(E_BV_factor,          minBound=0.0, maxBound=1.0)
        self.uv_bump_wavelength     = ListFloatProperty(uv_bump_wavelength,   minBound=0.0)
        self.uv_bump_width          = ListFloatProperty(uv_bump_width,        minBound=0.0)
        self.uv_bump_amplitude      = ListFloatProperty(uv_bump_amplitude,    minBound=0.0)
        self.powerlaw_slope         = ListFloatProperty(powerlaw_slope)
        self.Ext_law_emission_lines = ListIntProperty(Ext_law_emission_lines, minBound=1, maxBound=3)
        self.Rv                     = ListFloatProperty(Rv)
        
    def __str__(self, *args, **kwargs) -> str:
        r'''
        .. codeauthor:: Wilfried Mercier - IRAP/LAM <wilfried.mercier@lam.fr>
        
        Implement a string representation of the class used to make Cigale parameter files.
        '''
        
        text = f'''\
        [[dustatt_modified_starburst]]
          # E(B-V)l, the colour excess of the nebular lines light for both the
          # young and old population.
          E_BV_lines = {self.E_BV_lines}
          # Reduction factor to apply on E_BV_lines to compute E(B-V)s the stellar
          # continuum attenuation. Both young and old population are attenuated
          # with E(B-V)s.
          E_BV_factor = {self.E_BV_factor}
          # Central wavelength of the UV bump in nm.
          uv_bump_wavelength = {self.uv_bump_wavelength}
          # Width (FWHM) of the UV bump in nm.
          uv_bump_width = {self.uv_bump_width}
          # Amplitude of the UV bump. For the Milky Way: 3.
          uv_bump_amplitude = {self.uv_bump_amplitude}
          # Slope delta of the power law modifying the attenuation curve.
          powerlaw_slope = {self.powerlaw_slope}
          # Extinction law to use for attenuating the emissio  n lines flux.
          # Possible values are: 1, 2, 3. 1: MW, 2: LMC, 3: SMC. MW is modelled
          # using CCM89, SMC and LMC using Pei92.
          Ext_law_emission_lines = {self.Ext_law_emission_lines}
          # Ratio of total to selective extinction, A_V / E(B-V), for the
          # extinction curve applied to emission lines.Standard value is 3.1 for
          # MW using CCM89, but can be changed.For SMC and LMC using Pei92 the
          # value is automatically set to 2.93 and 3.16 respectively, no matter
          # the value you write.
          Rv = {self.Rv}
          # Filters for which the attenuation will be computed and added to the
          # SED information dictionary. You can give several filter names
          # separated by a & (don't use commas).
          filters = {self.filters}
        '''
        
        return text
    
    @property
    def spec(self, *args, **kwargs) -> str:
        r'''
        .. codeauthor:: Wilfried Mercier - IRAP/LAM <wilfried.mercier@lam.fr>
        
        Implement a string representation for the .spec file of Cigale parameters.
        '''
        
        text = '''\
        [[dustatt_modified_starburst]]
          E_BV_lines = cigale_list(minvalue=0.)
          E_BV_factor = cigale_list(minvalue=0., maxvalue=1.)
          uv_bump_wavelength = cigale_list(minvalue=0.)
          uv_bump_width = cigale_list()
          uv_bump_amplitude = cigale_list(minvalue=0.)
          powerlaw_slope = cigale_list()
          Ext_law_emission_lines = cigale_list(dtype=int, options=1 & 2 & 3)
          Rv = cigale_list()
          filters = string()\
        '''
        
        return text
    
###############################
#        Dust emission        #
###############################

class DUSTmodule(ABC):
    r'''
    .. codeauthor:: Wilfried Mercier - IRAP/LAM <wilfried.mercier@lam.fr>
    
    Class implementing a module to deal with dust emission.
    
    :param name: identifier for the class
    '''
    
    def __init__(self, name, *args, **kwargs):
        r'''Init method.'''
        
        self.name = name
        
        return
        
    @abstractmethod
    def __str__(self, *args, **kwargs) -> str:
        r'''
        .. codeauthor:: Wilfried Mercier - IRAP/LAM <wilfried.mercier@lam.fr>
        
        Implement a string representation of the class used to make Cigale parameter files.
        '''
        
        return
    
    @property
    @abstractmethod
    def spec(self, *args, **kwargs) -> str:
        r'''
        .. codeauthor:: Wilfried Mercier - IRAP/LAM <wilfried.mercier@lam.fr>
        
        Implement a string representation for the .spec file of Cigale parameters.
        '''
        
        return
    
class MBBmodule(DUSTmodule):
    r'''
    .. codeauthor:: Wilfried Mercier - IRAP/LAM <wilfried.mercier@lam.fr>
    
    Class implementing a modified black body dust emission module.
    
    **Keyword arguments**
    
    :param epsilon_mbb: fraction of L_dust(energy balance) in the MBB. Must be between 0 and 1.
    :type epsilon_mbb: :python:`list[float]`
    :param t_mbb: temperature of black body in :math:`\rm K`. Minimum is :math:`0\,\rm K`.
    :type t_mbb: :python:`list[float]`
    :param beta_mbb: emissivity index of modified black body
    :type beta_mbb: :python:`list[float]`
    :param energy_balance: whether to check for energy balance or not. If :python:`False`, Lum[MBB] is not taken into account in the energy balance.
    :type energy_balance: :python:`bool`
    '''
    
    def __init__(self, 
                 epsilon_mbb    : List[float] = [0.5],
                 t_mbb          : List[float] = [50.0],
                 beta_mbb       : List[float] = [1.5],
                 energy_balance : bool        = False
                ) -> None:
        
        r'''Init method.'''
            
        super().__init__('mbb')
        
        self.epsilon_mbb    = ListFloatProperty(epsilon_mbb, minBound=0.0, maxBound=1.0)
        self.t_mbb          = ListFloatProperty(t_mbb,       minBound=0.0)
        self.beta_mbb       = ListFloatProperty(beta_mbb)
        self.energy_balance = BoolProperty(energy_balance)
            
    def __str__(self, *args, **kwargs):
        r'''
        .. codeauthor:: Wilfried Mercier - IRAP/LAM <wilfried.mercier@lam.fr>
        
        Implement a string representation of the class used to make Cigale parameter files.
        '''
        
        text = f'''\
        [[mbb]]
          # Fraction [>= 0] of L_dust(energy balance) in the MBB
          epsilon_mbb = {self.epsilon_mbb}
          # Temperature of black body in K.
          t_mbb = {self.t_mbb}
          # Emissivity index of modified black body.
          beta_mbb = {self.beta_mbb}
          # Energy balance checked?If False, Lum[MBB] not taken into account in
          # energy balance
          energy_balance = {self.energy_balance}
        '''
        
        return text
    
    @property
    def spec(self, *args, **kwargs) -> str:
        r'''
        .. codeauthor:: Wilfried Mercier - IRAP/LAM <wilfried.mercier@lam.fr>
        
        Implement a string representation for the .spec file of Cigale parameters.
        '''
        
        text = '''\
        [[mbb]]
          epsilon_mbb = cigale_list(minvalue=0., maxvalue=1.)
          t_mbb = cigale_list(minvalue=0.)
          beta_mbb = cigale_list()
          energy_balance = boolean()\
        '''
        
        return text
    
class SCHREIBERmodule(DUSTmodule):
    r'''
    .. codeauthor:: Wilfried Mercier - IRAP/LAM <wilfried.mercier@lam.fr>
    
    Class implementing Schreiber at al. (2016) dust emission module.
    
    **Keyword arguments**
    
    :param tdust: temperature of the dust in :math:`\rm K`. Must be between :math:`15\,\rm K` and :math:`60\,\rm K`.
    :type tdust: :python:`list[int]`
    :param fpah: emissivity index of the dust. Must be between 0 and 1.
    :type fpah: :python:`list[float]`
    '''
    
    def __init__(self, 
                 tdust : List[int]   = [20],
                 fpah  : List[float] = [0.05]
                ) -> None:
        
        r'''Init method.'''
            
        super().__init__('schreiber2016')
        
        tdustRange = [15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60]
            
        self.tdust = ListIntProperty(tdust, minBound=15, maxBound=60,
                                     testFunc=lambda value: any((i not in tdustRange for i in value)),
                                     testMsg=f'one of tdust values is not in the list {tdustRange}')
        
        self.fpah  = ListFloatProperty(fpah, minBound=0.0, maxBound=1.0)
            
    def __str__(self, *args, **kwargs):
        r'''
        .. codeauthor:: Wilfried Mercier - IRAP/LAM <wilfried.mercier@lam.fr>
        
        Implement a string representation of the class used to make Cigale parameter files.
        '''
        
        text = f'''\
        [[schreiber2016]]
          # Dust temperature. Between 15 and 60K, with 1K step.
          tdust = {self.tdust}
          # Mass fraction of PAH. Between 0 and 1.
          fpah = {self.fpah}
        '''
        
        return text
    
    @property
    def spec(self, *args, **kwargs) -> str:
        r'''
        .. codeauthor:: Wilfried Mercier - IRAP/LAM <wilfried.mercier@lam.fr>
        
        Implement a string representation for the .spec file of Cigale parameters.
        '''
        
        text = '''\
        [[schreiber2016]]
          tdust = cigale_list(options=15. & 16. & 17. & 18. & 19. & 20. & 21. & 22. & 23. & 24. & 25. & 26. & 27. & 28. & 29. & 30. & 31. & 32. & 33. & 34. & 35. & 36. & 37. & 38. & 39. & 40. & 41. & 42. & 43. & 44. & 45. & 46. & 47. & 48. & 49. & 50. & 51. & 52. & 53. & 54. & 55. & 56. & 57. & 58. & 59. & 60.)
          fpah = cigale_list(minvalue=0., maxvalue=1.)\
        '''
        
        return text
    
class CASEYmodule(DUSTmodule):
    r'''
    .. codeauthor:: Wilfried Mercier - IRAP/LAM <wilfried.mercier@lam.fr>
    
    Class implementing Casey et al. (2012) dust emission module.
    
    **Keyword arguments**
    
    :param temperature: temperature of the dust in in :math:`\rm K`. Minimum is :math:`0\,\rm K`.
    :type temperature: :python:`list[float]`
    :param beta: emissivity index of the dust. Minimum is 0.
    :type beta: :python:`list[float]`
    :param alpha: mid-infrared powerlaw slope. Minimum is 0.
    :type alpha: :python:`list[float]`
    '''
    
    def __init__(self, 
                 temperature : List[float] = [35.0],
                 beta        : List[float] = [1.6],
                 alpha       : List[float] = [2.0]
                ) -> None:
        
        r'''Init method.'''
            
        super().__init__('casey2012')
            
        self.temperature = ListFloatProperty(temperature, minBound=0.0)
        self.beta        = ListFloatProperty(beta,        minBound=0.0)
        self.alpha       = ListFloatProperty(alpha,       minBound=0.0)
            
    def __str__(self, *args, **kwargs):
        r'''
        .. codeauthor:: Wilfried Mercier - IRAP/LAM <wilfried.mercier@lam.fr>
        
        Implement a string representation of the class used to make Cigale parameter files.
        '''
        
        text = f'''\
        [[casey2012]]
          # Temperature of the dust in K.
          temperature = {self.temperature}
          # Emissivity index of the dust.
          beta = {self.beta}
          # Mid-infrared powerlaw slope.
          alpha = {self.alpha}
        '''
        
        return text
    
    @property
    def spec(self, *args, **kwargs) -> str:
        r'''
        .. codeauthor:: Wilfried Mercier - IRAP/LAM <wilfried.mercier@lam.fr>
        
        Implement a string representation for the .spec file of Cigale parameters.
        '''
        
        text = '''\
        [[casey2012]]
          temperature = cigale_list(minvalue=0.)
          beta = cigale_list(minvalue=0.)
          alpha = cigale_list(minvalue=0.)\
        '''
        
        return text
    
class DALEmodule(DUSTmodule):
    r'''
    .. codeauthor:: Wilfried Mercier - IRAP/LAM <wilfried.mercier@lam.fr>
    
    Class implementing Dale et al. (2014) dust emission module.
    
    .. important::
        
        It is not recommended to combine this AGN emission with the models of Fritz et al. (2006).
    
    **Keyword arguments**
    
    :param fracAGN: AGN fraction. Must be between 0 and 1.
    :type fracAGN: :python:`list[float]`
    :param alpha: mid-infrared powerlaw slope. Accepted values are 0.0625, 0.125, 0.1875, 0.25, 0.3125, 0.375, 0.4375, 0.5, 0.5625, 0.625, 0.6875, 0.75, 0.8125, 0.875, 0.9375, 1, 1.0625, 1.125, 1.1875, 1.25, 1.3125, 1.375, 1.4375, 1.5, 1.5625, 1.625, 1.6875, 1.75, 1.8125, 1.875, 1.9375, 2, 2.0625, 2.125, 2.1875, 2.25, 2.3125, 2.375, 2.4375, 2.5, 2.5625, 2.625, 2.6875, 2.75, 2.8125, 2.875, 2.9375, 3, 3.0625, 3.125, 3.1875, 3.25, 3.3125, 3.375, 3.4375, 3.5, 3.5625, 3.625, 3.6875, 3.75, 3.8125, 3.875, 3.9375, 4.
    :type alpha: :python:`list[float]`
    '''
    
    def __init__(self, 
                 fracAGN : List[float] = [0.0],
                 alpha   : List[float] = [2.0]
                ) -> None:
    
        r'''Init method.'''
        
        super().__init__('dale2014')
        
        # Accepted values for alpha
        alphaRange = [0.0625, 0.1250, 0.1875, 0.2500, 0.3125, 0.3750, 0.4375, 0.5000, 0.5625, 0.6250, 0.6875, 0.7500,
                      0.8125, 0.8750, 0.9375, 1.0000, 1.0625, 1.1250, 1.1875, 1.2500, 1.3125, 1.3750, 1.4375, 1.5000, 
                      1.5625, 1.6250, 1.6875, 1.7500, 1.8125, 1.8750, 1.9375, 2.0000, 2.0625, 2.1250, 2.1875, 2.2500,
                      2.3125, 2.3750, 2.4375, 2.5000, 2.5625, 2.6250, 2.6875, 2.7500, 2.8125, 2.8750, 2.9375, 3.0000, 
                      3.0625, 3.1250, 3.1875, 3.2500, 3.3125, 3.3750, 3.4375, 3.5000, 3.5625, 3.6250, 3.6875, 3.7500,
                      3.8125, 3.8750, 3.9375, 4.0000]
        
        self.fracAGN = ListFloatProperty(fracAGN, minBound=0.0,    maxBound=1.0)
        self.alpha   = ListFloatProperty(alpha,   minBound=0.0625, maxBound=4.0,
                                         testFunc=lambda value: any((i not in alphaRange for i in value)),
                                         testMsg=f'One on the alpha values is not accepted. Accepted values must be in the list {alphaRange}.')
        
    def __str__(self, *args, **kwargs):
        r'''
        .. codeauthor:: Wilfried Mercier - IRAP/LAM <wilfried.mercier@lam.fr>
        
        Implement a string representation of the class used to make Cigale parameter files.
        '''
        
        text = f'''\
        [[dale2014]]
          # AGN fraction. It is not recommended to combine this AGN emission with
          # the of Fritz et al. (2006) models.
          fracAGN = {self.fracAGN}
          # Alpha slope. Possible values are: 0.0625, 0.1250, 0.1875, 0.2500,
          # 0.3125, 0.3750, 0.4375, 0.5000, 0.5625, 0.6250, 0.6875, 0.7500,
          # 0.8125, 0.8750, 0.9375, 1.0000, 1.0625, 1.1250, 1.1875, 1.2500,
          # 1.3125, 1.3750, 1.4375, 1.5000, 1.5625, 1.6250, 1.6875, 1.7500,
          # 1.8125, 1.8750, 1.9375, 2.0000, 2.0625, 2.1250, 2.1875, 2.2500,
          # 2.3125, 2.3750, 2.4375, 2.5000, 2.5625, 2.6250, 2.6875, 2.7500,
          # 2.8125, 2.8750, 2.9375, 3.0000, 3.0625, 3.1250, 3.1875, 3.2500,
          # 3.3125, 3.3750, 3.4375, 3.5000, 3.5625, 3.6250, 3.6875, 3.7500,
          # 3.8125, 3.8750, 3.9375, 4.0000
          alpha = {self.alpha}
        '''
        
        return text
    
    @property
    def spec(self, *args, **kwargs) -> str:
        r'''
        .. codeauthor:: Wilfried Mercier - IRAP/LAM <wilfried.mercier@lam.fr>
        
        Implement a string representation for the .spec file of Cigale parameters.
        '''
        
        text = '''\
        [[dale2014]]
          fracAGN = cigale_list(minvalue=0., maxvalue=1.)
          alpha = cigale_list(options=0.0625 & 0.1250 & 0.1875 & 0.2500 & 0.3125 & 0.3750 & 0.4375 & 0.5000 & 0.5625 & 0.6250 & 0.6875 & 0.7500 & 0.8125 & 0.8750 & 0.9375 & 1.0000 & 1.0625 & 1.1250 & 1.1875 & 1.2500 & 1.3125 & 1.3750 & 1.4375 & 1.5000 & 1.5625 & 1.6250 & 1.6875 & 1.7500 & 1.8125 & 1.8750 & 1.9375 & 2.0000 & 2.0625 & 2.1250 & 2.1875 & 2.2500 & 2.3125 & 2.3750 & 2.4375 & 2.5000 & 2.5625 & 2.6250 & 2.6875 & 2.7500 & 2.8125 & 2.8750 & 2.9375 & 3.0000 & 3.0625 & 3.1250 & 3.1875 & 3.2500 & 3.3125 & 3.3750 & 3.4375 & 3.5000 & 3.5625 & 3.6250 & 3.6875 & 3.7500 & 3.8125 & 3.8750 & 3.9375 & 4.0000)\
        '''
        
        return text
    
class DL07module(DUSTmodule):
    r'''
    .. codeauthor:: Wilfried Mercier - IRAP/LAM <wilfried.mercier@lam.fr>
    
    Class implementing Draine & Li (2007) dust emission module.
    
    **Keyword arguments**
    
    :param qpah: mass fraction of PAH. Accepted values are 0.47, 1.12, 1.77, 2.5, 3.19, 3.9, 4.58.
    :type qpah: :python:`list[float]`
    :param umin: minimum radiation field. Accepted values are 0.1, 0.15, 0.2, 0.3, 0.4, 0.5, 0.7, 0.8, 1, 1.2, 1.5, 2, 2.5, 3, 4, 5, 7, 8, 10, 12, 15, 20, 25.
    :type umin: :python:`list[float]`
    :param umax: maximum radiation field. Accepted values are 1e3, 1e4, 1e5, 1e6.
    :type umax: :python:`list[float]`
    :param gamma: fraction illuminated from Umin to Umax. Must be between 0 and 1.
    :type gamma: :python:`list[float]`
    '''
    
    def __init__(self, 
                 qpah  : List[float] = [2.5],
                 umin  : List[float] = [1.0],
                 umax  : List[float] = [1000000.0],
                 gamma : List[float] = [0.1]
                ) -> None:
    
        r'''Init method.'''
        
        super().__init__('dl2077')
        
        # Accepted values for qpah
        qpahRange = [0.47, 1.12, 1.77, 2.50, 3.19, 3.90, 4.58]
        
        # Accepted values for umin
        uminRange = [0.10, 0.15, 0.20, 0.30, 0.40, 0.50, 0.70, 0.80, 1.00, 1.20, 1.50, 2.00, 2.50, 
                     3.00, 4.00, 5.00, 7.00, 8.00, 10.0, 12.0, 15.0, 20.0, 25.0]
        
        # Accepted values for umax
        umaxRange = [1e3, 1e4, 1e5, 1e6]
        
        self.qpah: List[float]  = ListFloatProperty(qpah, minBound=0.47, maxBound=4.58,
                                                    testFunc=lambda value: any((i not in qpahRange for i in value)),
                                                    testMsg=f'One on the qpah values is not accepted. Accepted values must be in the list {qpahRange}.')
        
        
        self.umin: List[float]  = ListFloatProperty(umin, minBound=0.1, maxBound=25.0,
                                                    testFunc=lambda value: any((i not in uminRange for i in value)),
                                                    testMsg=f'One on the umin values is not accepted. Accepted values must be in the list {uminRange}.')
        
        
        self.umax: List[float]  = ListFloatProperty(umax, minBound=1e3, maxBound=1e6,
                                                    testFunc=lambda value: any((i not in umaxRange for i in value)),
                                                    testMsg=f'One on the umax values is not accepted. Accepted values must be in the list {umaxRange}.')
        
        self.gamma: List[float] = ListFloatProperty(gamma, minBound=0.0, maxBound=1.0)
        
    def __str__(self, *args, **kwargs):
        r'''
        .. codeauthor:: Wilfried Mercier - IRAP/LAM <wilfried.mercier@lam.fr>
        
        Implement a string representation of the class used to make Cigale parameter files.
        '''
        
        text = f'''\
        [[dl2007]]
          # Mass fraction of PAH. Possible values are: 0.47, 1.12, 1.77, 2.50,
          # 3.19, 3.90, 4.58.
          qpah = {self.qpah}
          # Minimum radiation field. Possible values are: 0.10, 0.15, 0.20, 0.30,
          # 0.40, 0.50, 0.70, 0.80, 1.00, 1.20, 1.50, 2.00, 2.50, 3.00, 4.00,
          # 5.00, 7.00, 8.00, 10.0, 12.0, 15.0, 20.0, 25.0.
          umin = {self.umin}
          # Maximum radiation field. Possible values are: 1e3, 1e4, 1e5, 1e6.
          umax = {self.umax}
          # Fraction illuminated from Umin to Umax. Possible values between 0 and
          # 1.
          gamma = {self.gamma}
        '''
        
        return text
    
    @property
    def spec(self, *args, **kwargs) -> str:
        r'''
        .. codeauthor:: Wilfried Mercier - IRAP/LAM <wilfried.mercier@lam.fr>
        
        Implement a string representation for the .spec file of Cigale parameters.
        '''
        
        text = '''\
        [[dl2007]]
          qpah = cigale_list(options=0.47 & 1.12 & 1.77 & 2.50 & 3.19 & 3.90 & 4.58)
          umin = cigale_list(options=0.10 & 0.15 & 0.20 & 0.30 & 0.40 & 0.50 & 0.70 & 0.80 & 1.00 & 1.20 & 1.50 & 2.00 & 2.50 & 3.00 & 4.00 & 5.00 & 7.00 & 8.00 & 10.0 & 12.0 & 15.0 & 20.0 & 25.0)
          umax = cigale_list(options=1e3 & 1e4 & 1e5 & 1e6)
          gamma = cigale_list(minvalue=0., maxvalue=1.)\
        '''
        
        return text
    
class DL14module(DUSTmodule):
    r'''
    .. codeauthor:: Wilfried Mercier - IRAP/LAM <wilfried.mercier@lam.fr>
    
    Class implementing Draine et al. 2014 update dust emission module.
    
    **Keyword arguments**
    
    :param qpah: mass fraction of PAH. Accepted values are 0.47, 1.12, 1.77, 2.5, 3.19, 3.9, 4.58, 5.26, 5.95, 6.63, 7.32.
    :type qpah: :python:`list[float]`
    :param umin: minimum radiation field. Accepted values are 0.1, 0.12, 0.15, 0.17, 0.2, 0.25, 0.3, 0.35, 0.4, 0.5, 0.6, 0.7, 0.8, 1, 1.2, 1.5, 1.7, 2, 2.5, 3, 3.5, 4, 5, 6, 7, 8, 10, 12, 15, 17, 20, 25, 30, 35, 40, 50.
    :type umin: :python:`list[float]`
    :param alpha: powerlaw slope dU/dM propto U^alpha. Accepted values are 1, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 2, 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8, 2.9, 3
    :type alpha: :python:`list[float]`
    :param gamma: fraction illuminated from Umin to Umax. Must be between 0 and 1.
    :type gamma: :python:`list[float]`
    '''
    
    def __init__(self, 
                 qpah  : List[float] = [2.5],
                 umin  : List[float] = [1.0],
                 gamma : List[float] = [0.1],
                 alpha : List[float] = [2.0]
                ) -> None:
    
        r'''Init method.'''
        
        super().__init__('dl2014')
        
        # Accepted values for qpah
        qpahRange  = [0.47, 1.12, 1.77, 2.50, 3.19, 3.90, 4.58, 5.26, 5.95, 6.63, 7.32]
        
        # Accepted values for umin
        uminRange  = [0.100, 0.120, 0.150, 0.170, 0.200, 0.250, 0.300, 0.350, 0.400, 0.500, 0.600, 0.700, 0.800,
                      1.000, 1.200, 1.500, 1.700, 2.000, 2.500, 3.000, 3.500, 4.000, 5.000, 6.000, 7.000, 8.000, 
                      10.00, 12.00, 15.00, 17.00, 20.00, 25.00, 30.00, 35.00, 40.00, 50.00]
        
        # Accepted values for alpha
        alphaRange = [1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 2.0, 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8, 2.9, 3.0]
        
        self.qpah: List[float]  = ListFloatProperty(qpah, minBound=0.47, maxBound=7.32,
                                                    testFunc=lambda value: any((i not in qpahRange for i in value)),
                                                    testMsg=f'One on the qpah values is not accepted. Accepted values must be in the list {qpahRange}.')
        
        
        self.umin: List[float]  = ListFloatProperty(umin, minBound=0.1, maxBound=50.0,
                                                    testFunc=lambda value: any((i not in uminRange for i in value)),
                                                    testMsg=f'One on the umin values is not accepted. Accepted values must be in the list {uminRange}.')
        
        self.alpha: List[float] = ListFloatProperty(alpha, minBound=1.0, maxBound=3.0,
                                                    testFunc=lambda value: any((i not in alphaRange for i in value)),
                                                    testMsg=f'One on the alpha values is not accepted. Accepted values must be in the list {alphaRange}.')
        
        self.gamma: List[float] = ListFloatProperty(gamma, minBound=0.0, maxBound=1.0)
        
    def __str__(self, *args, **kwargs):
        r'''
        .. codeauthor:: Wilfried Mercier - IRAP/LAM <wilfried.mercier@lam.fr>
        
        Implement a string representation of the class used to make Cigale parameter files.
        '''
        
        text = f'''\
        [[dl2014]]
          # Mass fraction of PAH. Possible values are: 0.47, 1.12, 1.77, 2.50,
          # 3.19, 3.90, 4.58, 5.26, 5.95, 6.63, 7.32.
          qpah = {self.qpah}
          # Minimum radiation field. Possible values are: 0.100, 0.120, 0.150,
          # 0.170, 0.200, 0.250, 0.300, 0.350, 0.400, 0.500, 0.600, 0.700, 0.800,
          # 1.000, 1.200, 1.500, 1.700, 2.000, 2.500, 3.000, 3.500, 4.000, 5.000,
          # 6.000, 7.000, 8.000, 10.00, 12.00, 15.00, 17.00, 20.00, 25.00, 30.00,
          # 35.00, 40.00, 50.00.
          umin = {self.umin}
          # Powerlaw slope dU/dM propto U^alpha. Possible values are: 1.0, 1.1,
          # 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 2.0, 2.1, 2.2, 2.3, 2.4, 2.5,
          # 2.6, 2.7, 2.8, 2.9, 3.0.
          alpha = {self.alpha}
          # Fraction illuminated from Umin to Umax. Possible values between 0 and
          # 1.
          gamma = {self.gamma}
        '''
        
        return text
    
    @property
    def spec(self, *args, **kwargs) -> str:
        r'''
        .. codeauthor:: Wilfried Mercier - IRAP/LAM <wilfried.mercier@lam.fr>
        
        Implement a string representation for the .spec file of Cigale parameters.
        '''
        
        text = '''\
        [[dl2014]]
          qpah = cigale_list(options=0.47 & 1.12 & 1.77 & 2.50 & 3.19 & 3.90 & 4.58 & 5.26 & 5.95 & 6.63 & 7.32)
          umin = cigale_list(options=0.10 & 0.12 & 0.15 & 0.17 & 0.20 & 0.25 & 0.30 & 0.35 & 0.40 & 0.50 & 0.60 & 0.70 & 0.80 & 1.00 & 1.20 & 1.50 & 1.70 & 2.00 & 2.50 & 3.00 & 3.50 & 4.00 & 5.00 & 6.00 & 7.00 & 8.00 & 10.00 & 12.00 & 15.00 & 17.00 & 20.00 & 25.00 & 30.00 & 35.00 & 40.00 & 50.00)
          alpha = cigale_list(options=1.0 & 1.1 & 1.2 & 1.3 & 1.4 & 1.5 & 1.6 & 1.7 & 1.8 & 1.9 & 2.0 & 2.1 & 2.2 & 2.3 & 2.4 & 2.5 & 2.6 & 2.7 & 2.8 & 2.9 & 3.0)
          gamma = cigale_list(minvalue=0., maxvalue=1.)\
        '''
        
        return text
    
class THEMISmodule(DUSTmodule):
    r'''
    .. codeauthor:: Wilfried Mercier - IRAP/LAM <wilfried.mercier@lam.fr>
    
    Class implementing Themis dust emission models from Jones et al. 2017.
    
    **Keyword arguments**
    
    :param qhac: mass fraction of hydrocarbon solids i.e., a-C(:H) smaller than :math:`1.5\,\rm nm`, also known as HAC. Accepted values are 0.02, 0.06, 0.1, 0.14, 0.17, 0.2, 0.24, 0.28, 0.32, 0.36, 0.4.
    :type qhac: :python:`list[float]`
    :param umin: minimum radiation field. Accepted values are 0.1, 0.12, 0.15, 0.17, 0.2, 0.25, 0.3, 0.35, 0.4, 0.5, 0.6, 0.7, 0.8, 1, 1.2, 1.5, 1.7, 2, 2.5, 3, 3.5, 4, 5, 6, 7, 8, 10, 12, 15, 17, 20, 25, 30, 35, 40, 50.
    :type umin: :python:`list[float]`
    :param alpha: powerlaw slope dU/dM propto U^alpha. Accepted values are 1, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 2, 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8, 2.9, 3
    :type alpha: :python:`list[float]`
    :param gamma: fraction illuminated from Umin to Umax. Must be between 0 and 1.
    :type gamma: :python:`list[float]`
    '''
    
    def __init__(self, qhac: List[float] = [0.17],
                 umin: List[float]       = [1.0],
                 gamma: List[float]      = [0.1],
                 alpha: List[float]      = [2.0]) -> None:
    
        r'''Init method.'''
        
        super().__init__('themis')
        
        # Accepted values for qpah
        qhacRange  = [0.02, 0.06, 0.10, 0.14, 0.17, 0.20, 0.24, 0.28, 0.32, 0.36, 0.40]
        
        # Accepted values for umin
        uminRange  = [0.100, 0.120, 0.150, 0.170, 0.200, 0.250, 0.300, 0.350, 0.400, 0.500, 0.600, 0.700, 0.800,
                      1.000, 1.200, 1.500, 1.700, 2.000, 2.500, 3.000, 3.500, 4.000, 5.000, 6.000, 7.000, 8.000, 
                      10.00, 12.00, 15.00, 17.00, 20.00, 25.00, 30.00, 35.00, 40.00, 50.00, 80.00]
        
        # Accepted values for alpha
        alphaRange = [1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 2.0, 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8, 2.9, 3.0]
        
        self.qhac: List[float]  = ListFloatProperty(qhac, minBound=0.02, maxBound=0.4,
                                                    testFunc=lambda value: any((i not in qhacRange for i in value)),
                                                    testMsg=f'One on the qhac values is not accepted. Accepted values must be in the list {qhacRange}.')
        
        
        self.umin: List[float]  = ListFloatProperty(umin, minBound=0.1, maxBound=80.0,
                                                    testFunc=lambda value: any((i not in uminRange for i in value)),
                                                    testMsg=f'One on the umin values is not accepted. Accepted values must be in the list {uminRange}.')
        
        self.alpha: List[float] = ListFloatProperty(alpha, minBound=1.0, maxBound=3.0,
                                                    testFunc=lambda value: any((i not in alphaRange for i in value)),
                                                    testMsg=f'One on the alpha values is not accepted. Accepted values must be in the list {alphaRange}.')
        
        self.gamma: List[float] = ListFloatProperty(gamma, minBound=0.0, maxBound=1.0)
        
    def __str__(self, *args, **kwargs):
        r'''
        .. codeauthor:: Wilfried Mercier - IRAP/LAM <wilfried.mercier@lam.fr>
        
        Implement a string representation of the class used to make Cigale parameter files.
        '''
        
        text = f'''\
        [[themis]]
          # Mass fraction of hydrocarbon solids i.e., a-C(:H) smaller than 1.5 nm,
          # also known as HAC. Possible values are: 0.02, 0.06, 0.10, 0.14, 0.17,
          # 0.20, 0.24, 0.28, 0.32, 0.36, 0.40.
          qhac = {self.qhac}
          # Minimum radiation field. Possible values are: 0.100, 0.120, 0.150,
          # 0.170, 0.200, 0.250, 0.300, 0.350, 0.400, 0.500, 0.600, 0.700, 0.800,
          # 1.000, 1.200, 1.500, 1.700, 2.000, 2.500, 3.000, 3.500, 4.000, 5.000,
          # 6.000, 7.000, 8.000, 10.00, 12.00, 15.00, 17.00, 20.00, 25.00, 30.00,
          # 35.00, 40.00, 50.00, 80.00.
          umin = {self.umin}
          # Powerlaw slope dU/dM propto U^alpha. Possible values are: 1.0, 1.1,
          # 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 2.0, 2.1, 2.2, 2.3, 2.4, 2.5,
          # 2.6, 2.7, 2.8, 2.9, 3.0.
          alpha = {self.alpha}
          # Fraction illuminated from Umin to Umax. Possible values between 0 and
          # 1.
          gamma = {self.gamma}
        '''
        
        return text
    
    @property
    def spec(self, *args, **kwargs) -> str:
        r'''
        .. codeauthor:: Wilfried Mercier - IRAP/LAM <wilfried.mercier@lam.fr>
        
        Implement a string representation for the .spec file of Cigale parameters.
        '''
        
        text = '''\
        [[themis]]
          qhac = cigale_list(options=0.02 & 0.06 & 0.10 & 0.14 & 0.17 & 0.20 & 0.24 & 0.28 & 0.32 & 0.36 & 0.40)
          umin = cigale_list(options=0.10 & 0.12 & 0.15 & 0.17 & 0.20 & 0.25 & 0.30 & 0.35 & 0.40 & 0.50 & 0.60 & 0.70 & 0.80 & 1.00 & 1.20 & 1.50 & 1.70 & 2.00 & 2.50 & 3.00 & 3.50 & 4.00 & 5.00 & 6.00 & 7.00 & 8.00 & 10.00 & 12.00 & 15.00 & 17.00 & 20.00 & 25.00 & 30.00 & 35.00 & 40.00 & 50.00 & 80.00)
          alpha = cigale_list(options=1.0 & 1.1 & 1.2 & 1.3 & 1.4 & 1.5 & 1.6 & 1.7 & 1.8 & 1.9 & 2.0 & 2.1 & 2.2 & 2.3 & 2.4 & 2.5 & 2.6 & 2.7 & 2.8 & 2.9 & 3.0)
          gamma = cigale_list(minvalue=0., maxvalue=1.)\
        '''
        
        return text
    
#####################
#        AGN        #
#####################

class AGNmodule(ABC):
    r'''
    .. codeauthor:: Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>
    
    Class implementing a module to deal with dust emission.
    
    :param name: identifier for the class
    :param list fracAGN: (**Optional**) AGN fraction
    '''
    
    def __init__(self, name, fracAGN: List[float] = [0.1], **kwargs) -> None:
        r'''Init method.'''
        
        self.name    = name
        self.fracAGN = ListFloatProperty(fracAGN, minBound=0.0, maxBound=1.0)
        
        return
        
    @abstractmethod
    def __str__(self, *args, **kwargs) -> str:
        r'''
        .. codeauthor:: Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>
        
        Implement a string representation of the class used to make Cigale parameter files.
        '''
        
        return
    
    @property
    @abstractmethod
    def spec(self, *args, **kwargs) -> str:
        r'''
        .. codeauthor:: Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>
        
        Implement a string representation for the .spec file of Cigale parameters.
        '''
        
        return

class FRITZmodule(AGNmodule):
    r'''
    .. codeauthor:: Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>
    
    Class implementing a module to deal with Fritz et al. 2006 AGN model.
    
    :param list r_ratio: (**Optional**) ratio of the maximum to minimum radii of the dust torus. Possible values are: 10, 30, 60, 100, 150.
    :param list tau: (**Optional**) optical depth at 9.7 microns. Possible values are: 0.1, 0.3, 0.6, 1.0, 2.0, 3.0, 6.0, 10.0.
    :param list beta: (**Optional**) beta. Possible values are: -1.00, -0.75, -0.50, -0.25, 0.00.
    :param list gamma: (**Optional**) gamma. Pssible values are: 0.0, 2.0, 4.0, 6.0.
    :param list opening_angle: (**Optional**) full opening angle of the dust torus (Fig 1 of Fritz 2006). Possible values are: 60., 100., 140.
    :param list psy: (**Optional**) angle between equatorial axis and line of sight. Psy = 90◦ for type 1 and Psy = 0° for type 2. Possible values are: 0.001, 10.100, 20.100, 30.100, 40.100, 50.100, 60.100, 70.100, 80.100, 89.990.
    :param list fracAGN: (**Optional**) AGN fraction
    '''
    
    def __init__(self, r_ratio: List[int] = [60.0],
                 tau: List[float]         = [1.0],
                 beta: List[float]        = [-0.5],
                 gamma: List[int]         = [4],
                 opening_angle: List[int] = [100],
                 psy: List[float]         = [50.1],
                 fracAGN: List[float]     = [0.1]) -> None:
        
        r'''Init method.'''
        
        super().__init__('fritz2006', fracAGN=fracAGN)
        
        # Accepted values for r_ratio
        r_ratioRange       = [10, 30, 60, 100, 150]
        
        # Accepted values for tau
        tauRange           = [0.1, 0.3, 0.6, 1.0, 2.0, 3.0, 6.0, 10.0]
        
        # Accepted values for beta
        betaRange          = [-1.0, -0.75, -0.5, -0.25, 0.0]
        
        # Accepted values for gamma
        gammaRange         = [0, 2, 4, 6]
        
        # Accepted values for opening_angle
        opening_angleRange = [60, 100, 140]
        
        # Accepted values for psy
        psyRange           = [0.001, 10.10, 20.10, 30.10, 40.10, 50.10, 60.10, 70.10, 80.10, 89.99]
        
        
        self.r_ratio       = ListFloatProperty(r_ratio, minBound=10, maxBound=150,
                                               testFunc=lambda value: any((i not in r_ratioRange for i in value)),
                                               testMsg=f'One on the r_ratio values is not accepted. Accepted values must be in the list {r_ratioRange}.')
        
        
        self.tau           = ListFloatProperty(tau, minBound=0.1, maxBound=10.0,
                                               testFunc=lambda value: any((i not in tauRange for i in value)),
                                               testMsg=f'One on the tau values is not accepted. Accepted values must be in the list {tauRange}.')
        
        self.beta          = ListFloatProperty(beta, minBound=-1.0, maxBound=0.0,
                                               testFunc=lambda value: any((i not in betaRange for i in value)),
                                               testMsg=f'One on the beta values is not accepted. Accepted values must be in the list {betaRange}.')
        
        self.gamma         = ListFloatProperty(gamma, minBound=0, maxBound=6,
                                               testFunc=lambda value: any((i not in gammaRange for i in value)),
                                               testMsg=f'One on the gamma values is not accepted. Accepted values must be in the list {gammaRange}.')
        
        self.opening_angle = ListFloatProperty(opening_angle, minBound=60, maxBound=140,
                                               testFunc=lambda value: any((i not in opening_angleRange for i in value)),
                                               testMsg=f'One on the opening_angle values is not accepted. Accepted values must be in the list {opening_angleRange}.')
        
        self.psy           = ListFloatProperty(psy, minBound=0.001, maxBound=89.99,
                                               testFunc=lambda value: any((i not in psyRange for i in value)),
                                               testMsg=f'One on the psy values is not accepted. Accepted values must be in the list {psyRange}.')
        
    def __str__(self, *args, **kwargs) -> str:
        r'''
        .. codeauthor:: Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>
        
        Implement a string representation of the class used to make Cigale parameter files.
        '''
        
        text = f'''\
        [[fritz2006]]
          # Ratio of the maximum to minimum radii of the dust torus. Possible
          # values are: 10, 30, 60, 100, 150.
          r_ratio = {self.r_ratio}
          # Optical depth at 9.7 microns. Possible values are: 0.1, 0.3, 0.6, 1.0,
          # 2.0, 3.0, 6.0, 10.0.
          tau = {self.tau}
          # Beta. Possible values are: -1.00, -0.75, -0.50, -0.25, 0.00.
          beta = {self.beta}
          # Gamma. Possible values are: 0.0, 2.0, 4.0, 6.0.
          gamma = {self.gamma}
          # Full opening angle of the dust torus (Fig 1 of Fritz 2006). Possible
          # values are: 60., 100., 140.
          opening_angle = {self.opening_angle}
          # Angle between equatorial axis and line of sight. Psy = 90◦ for type 1
          # and Psy = 0° for type 2. Possible values are: 0.001, 10.100, 20.100,
          # 30.100, 40.100, 50.100, 60.100, 70.100, 80.100, 89.990.
          psy = {self.psy}
          # AGN fraction.
          fracAGN = {self.fracAGN}
        '''
        
        return text
    
    @property
    def spec(self, *args, **kwargs) -> str:
        r'''
        .. codeauthor:: Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>
        
        Implement a string representation for the .spec file of Cigale parameters.
        '''
        
        text = '''\
        [[fritz2006]]
          r_ratio = cigale_list(options=10. & 30. & 60. & 100. & 150.)
          tau = cigale_list(options=0.1 & 0.3 & 0.6 & 1.0 & 2.0 & 3.0 & 6.0 & 10.0)
          beta = cigale_list(options=-1.00 & -0.75 & -0.50 & -0.25 & 0.00)
          gamma = cigale_list(options=0.0 & 2.0 & 4.0 & 6.0)
          opening_angle = cigale_list(options=60. & 100. & 140.)
          psy = cigale_list(options=0.001 & 10.100 & 20.100 & 30.100 & 40.100 & 50.100 & 60.100 & 70.100 & 80.100 & 89.990)
          fracAGN = cigale_list(minvalue=0., maxvalue=1.)\
        '''
        
        return text
    
class SKIRTORmodule(AGNmodule):
    r'''
    .. codeauthor:: Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>
    
    Class implementing a module to deal with a SKIRTOR 2016 (Stalevski et al., 2016) AGN dust torus emission model.
    
    :param list t: (**Optional**) average edge-on optical depth at 9.7 micron; the actual one along the line of sight may vary depending on the clumps distribution. Possible values are: 3, 5, 7, 8, and 11.
    :param list pl: (**Optional**) power-law exponent that sets radial gradient of dust density. Possible values are: 0., 0.5, 1., and 1.5.
    :param list q: (**Optional**) index that sets dust density gradient with polar angle. Possible values are:  0., 0.5, 1., and 1.5.
    :param list oa: (**Optional**) angle measured between the equatorial plan and edge of the torus. Half-opening angle of the dust-free cone is 90-oa. Possible values are: 10, 20, 30, 40, 50, 60, 70, and 80
    :param list R: (**Optional**) ratio of outer to inner radius, R_out/R_in. Possible values are: 10, 20, and 30.
    :param list Mcl: (**Optional**) fraction of total dust mass inside clumps. 0.97 means 97% of total mass is inside the clumps and 3% in the interclump dust. Possible values are: 0.97.
    :param list i: (**Optional**) inclination, i.e. viewing angle, i.e. position of the instrument w.r.t. the AGN axis. i=0: face-on, type 1 view; i=90: edge-on, type 2 view. Possible values are: 0, 10, 20, 30, 40, 50, 60, 70, 80, and 90.
    :param list fracAGN: (**Optional**) AGN fraction
    '''
    
    def __init__(self, t: List[int]   = [3],
                 pl: List[float]      = [1.0],
                 q: List[float]       = [1.0],
                 oa: List[int]        = [40],
                 R: List[int]         = [20],
                 Mcl: List[float]     = [0.97],
                 i: List[int]         = [40],
                 fracAGN: List[float] = [0.1]) -> None:
        
        r'''Init method.'''
        
        super().__init__('skirtor2016', fracAGN=fracAGN)
        
        # Accepted values for t
        tRange    = [3, 5, 7, 9, 11]
        
        # Accepted values for pl and q
        pl_qRange = [0.0, 0.5, 1.0, 1.5]
        
        # Accepted values for oa
        oaRange   = [10, 20, 30, 40, 50, 60, 70, 80]
        
        # Accepted values for R
        RRange    = [10, 20, 30]
        
        # Accepted values for Mcl
        MclRange  = [0.97]
        
        # Accepted values for i
        iRange    = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90]
        
        
        self.t   =  ListIntProperty(t, minBound=3, maxBound=11,
                                    testFunc=lambda value: any((i not in tRange for i in value)),
                                    testMsg=f'One on the t values is not accepted. Accepted values must be in the list {tRange}.')
        
        
        self.pl   = ListFloatProperty(pl, minBound=0.0, maxBound=1.5,
                                      testFunc=lambda value: any((i not in pl_qRange for i in value)),
                                      testMsg=f'One on the pl values is not accepted. Accepted values must be in the list {pl_qRange}.')
        
        self.q    = ListFloatProperty(q, minBound=0.0, maxBound=1.5,
                                      testFunc=lambda value: any((i not in pl_qRange for i in value)),
                                      testMsg=f'One on the q values is not accepted. Accepted values must be in the list {pl_qRange}.')
        
        self.oa   = ListIntProperty(oa, minBound=10, maxBound=80,
                                    testFunc=lambda value: any((i not in oaRange for i in value)),
                                    testMsg=f'One on the oa values is not accepted. Accepted values must be in the list {oaRange}.')
        
        self.R    = ListFloatProperty(R, minBound=10, maxBound=30,
                                      testFunc=lambda value: any((i not in RRange for i in value)),
                                      testMsg=f'One on the R values is not accepted. Accepted values must be in the list {RRange}.')
        
        self.Mcl  = ListFloatProperty(Mcl, minBound=0.97, maxBound=0.97,
                                      testFunc=lambda value: any((i not in MclRange for i in value)),
                                      testMsg=f'One on the Mcl values is not accepted. Accepted values must be in the list {MclRange}.')
        
        self.i    = ListIntProperty(i, minBound=0, maxBound=90,
                                    testFunc=lambda value: any((i not in iRange for i in value)),
                                    testMsg=f'One on the i values is not accepted. Accepted values must be in the list {iRange}.')
        
    def __str__(self, *args, **kwargs) -> str:
        r'''
        .. codeauthor:: Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>
        
        Implement a string representation of the class used to make Cigale parameter files.
        '''
        
        text = f'''\
        [[skirtor2016]]
          # Average edge-on optical depth at 9.7 micron; the actual one alongthe
          # line of sight may vary depending on the clumps distribution. Possible
          # values are: 3, 5, 7, 8, and 11.
          t = {self.ts}
          # Power-law exponent that sets radial gradient of dust density.Possible
          # values are: 0., 0.5, 1., and 1.5.
          pl = {self.pl}
          # Index that sets dust density gradient with polar angle.Possible values
          # are:  0., 0.5, 1., and 1.5.
          q = {self.q}
          # Angle measured between the equatorial plan and edge of the torus.
          # Half-opening angle of the dust-free cone is 90-oaPossible values are:
          # 10, 20, 30, 40, 50, 60, 70, and 80
          oa = {self.oa}
          # Ratio of outer to inner radius, R_out/R_in.Possible values are: 10,
          # 20, and 30
          R = {self.R}
          # fraction of total dust mass inside clumps. 0.97 means 97% of total
          # mass is inside the clumps and 3% in the interclump dust. Possible
          # values are: 0.97.
          Mcl = {self.Mcl}
          # inclination, i.e. viewing angle, i.e. position of the instrument
          # w.r.t. the AGN axis. i=0: face-on, type 1 view; i=90: edge-on, type 2
          # view.Possible values are: 0, 10, 20, 30, 40, 50, 60, 70, 80, and 90.
          i = {self.i}
          # AGN fraction.
          fracAGN = {self.fracAGN}
        '''
        
        return text
    
    @property
    def spec(self, *args, **kwargs) -> str:
        r'''
        .. codeauthor:: Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>
        
        Implement a string representation for the .spec file of Cigale parameters.
        '''
        
        text = '''\
        [[skirtor2016]]
          t = cigale_list(options=3 & 5 & 7 & 9 & 11)
          pl = cigale_list(options=0. & .5 & 1. & 1.5)
          q = cigale_list(options=0. & .5 & 1. & 1.5)
          oa = cigale_list(options=10 & 20 & 30 & 40 & 50 & 60 & 70 & 80)
          R = cigale_list(options=10 & 20 & 30)
          Mcl = cigale_list(options=0.97)
          i = cigale_list(options=0 & 10 & 20 & 30 & 40 & 50 & 60 & 70 & 80 & 90)
          fracAGN = cigale_list(minvalue=0., maxvalue=1.)\
        '''
        
        return text
    
#######################
#        Radio        #
#######################

class RADIOmodule:
    r'''
    .. codeauthor:: Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>
    
    Class implementing a module to deal with synchrotron emission module.
    
    :param list qir: (**Optional**) the value of the FIR/radio correlation coefficient
    :param list alpha: (**Optional**) the slope of the power-law synchrotron emission
    '''
    
    def __init__(self, qir: List[float] = [2.58],
                 alpha: List[float]     = [0.8]) -> None:
        
        r'''Init method.'''
        
        self.name  = 'radio'
        self.qir   = ListFloatProperty(qir, minBound=0.0)
        self.alpha = ListFloatProperty(alpha)
        
    def __str__(self, *args, **kwargs) -> str:
        r'''
        .. codeauthor:: Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>
        
        Implement a string representation of the class used to make Cigale parameter files.
        '''
        
        text = f'''\
        [[radio]]
          # The value of the FIR/radio correlation coefficient.
          qir = {self.qir}
          # The slope of the power-law synchrotron emission.
          alpha = {self.alpha}
        '''
        
        return text
    
    @property
    def spec(self, *args, **kwargs) -> str:
        r'''
        .. codeauthor:: Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>
        
        Implement a string representation for the .spec file of Cigale parameters.
        '''
        
        text = '''\
        [[radio]]
          qir = cigale_list(minvalue=0.)
          alpha = cigale_list()\
        '''
        
        return text
    
#######################################
#        Rest-frame parameters        #
#######################################

class RESTFRAMEmodule:
    r'''
    .. codeauthor:: Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>
    
    Class implementing a module for rest-frame parameters.
    
    :param bool beta_calz94: (**Optional**) UV slope measured in the same way as in Calzetti et al. (1994)
    :param bool D4000: (**Optional**) D4000 break using the Balogh et al. (1999) definition
    :param bool IRX: (**Optional**) IRX computed from the GALEX FUV filter and the dust luminosity
    :param str EW_lines: (**Optional**) central wavelength of the emission lines for which to compute the equivalent width. The half-bandwidth must be indicated after the '/' sign. For instance 656.3/1.0 means oth the nebular line and the continuum are integrated over 655.3-657.3 nm.
    :param str colours_filters: (**Optional**) rest-frame colours to be computed. You can give several colours separated by a & (don't use commas).
    '''
    
    def __init__(self, beta_calz94: bool = False,
                 D4000: bool             = False,
                 IRX: bool               = False,
                 EW_lines: str           = '500.7/1.0 & 656.3/1.0',
                 luminosity_filters: str = 'FUV & V_B90',
                 colours_filters: str    = 'FUV-NUV & NUV-r_prime') -> None:
        
        r'''Init method.'''
        
        def check_EW(ew):
            r'''Check that the format given for the equivalent width is correct.'''
            
            # If no / is found, then the format is incorrect
            if '/' not in ew:
                return True
             
            for es in ew.split('&'):
                for e in es.split('/'):
                    
                    # If casting to float does not work, the format is incorrect
                    try:
                        float(e)
                    except ValueError:
                        return True
            
            return False
        
        self.name               = 'restframe_parameters'
        self.beta_calz94        = BoolProperty(beta_calz94)
        self.D4000              = BoolProperty(D4000)
        self.IRX                = BoolProperty(IRX)
        self.EW_lines           = StrProperty(EW_lines, 
                                              testFunc = check_EW,
                                              testMsg='The value for EW_lines is not accepted.')
        
        self.luminosity_filters = StrProperty(luminosity_filters)
        self.colours_filters    = StrProperty(colours_filters)
        
    def __str__(self, *args, **kwargs) -> str:
        r'''
        .. codeauthor:: Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>
        
        Implement a string representation of the class used to make Cigale parameter files.
        '''
        
        text = f'''\
        [[restframe_parameters]]
          # UV slope measured in the same way as in Calzetti et al. (1994).
          beta_calz94 = {self.beta_calz94}
          # D4000 break using the Balogh et al. (1999) definition.
          D4000 = {self.D4000}
          # IRX computed from the GALEX FUV filter and the dust luminosity.
          IRX = {self.IRX}
          # Central wavelength of the emission lines for which to compute the
          # equivalent width. The half-bandwidth must be indicated after the '/'
          # sign. For instance 656.3/1.0 means oth the nebular line and the
          # continuum are integrated over 655.3-657.3 nm.
          EW_lines = {self.EW_lines}
          # Filters for which the rest-frame luminosity will be computed. You can
          # give several filter names separated by a & (don't use commas).
          luminosity_filters = {self.luminosity_filters}
          # Rest-frame colours to be computed. You can give several colours
          # separated by a & (don't use commas).
          colours_filters = {self.colours_filters}
        '''
        
        return text
    
    @property
    def spec(self, *args, **kwargs) -> str:
        r'''
        .. codeauthor:: Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>
        
        Implement a string representation for the .spec file of Cigale parameters.
        '''
        
        text = '''\
        [[restframe_parameters]]
          beta_calz94 = boolean()
          D4000 = boolean()
          IRX = boolean()
          EW_lines = string()
          luminosity_filters = string()
          colours_filters = string()\
        '''
        
        return text
    
#############################
#        Redshifting        #
#############################

class REDSHIFTmodule:
    r'''
    .. codeauthor:: Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>
    
    Class implementing a module for redshifting and IGM.
    
    :param list redshift: redshift of the objects. Leave empty to use the redshifts from the input file.
    '''
    
    def __init__(self, redshift: List[float] = []) -> None:
        
        r'''Init method.'''
        
        self.name         = 'redshifting'
        
        if redshift == []:
            self.redshift = StrProperty('')
        else:
            self.redshift = ListFloatProperty(redshift, minBound=0.0)
            
        
    def __str__(self, *args, **kwargs) -> str:
        r'''
        .. codeauthor:: Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>
        
        Implement a string representation of the class used to make Cigale parameter files.
        '''
        
        text = f'''\
        [[redshifting]]
          # Redshift of the objects. Leave empty to use the redshifts from the
          # input file.
          redshift = {self.redshift}
        '''
        
        return text
    
    @property
    def spec(self, *args, **kwargs) -> str:
        r'''
        .. codeauthor:: Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>
        
        Implement a string representation for the .spec file of Cigale parameters.
        '''
        
        text = '''\
        [[redshifting]]
          redshift = cigale_list(minvalue=0.)\
        '''
        
        return text