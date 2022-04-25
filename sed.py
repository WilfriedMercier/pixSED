#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
.. codeauthor:: Hugo Plombat - LUPM <hugo.plombat@umontpellier.fr> & Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>

Utilties related to generating 2D mass and SFR maps using LePhare SED fitting codes.
"""

import subprocess
import shutil
import os
import os.path          as     opath

from   distutils.spawn  import find_executable
from   copy             import deepcopy
from   typing           import List, Any, Optional, Dict, Union
from   io               import TextIOBase
from   abc              import ABC, abstractmethod
from   textwrap         import dedent, indent
from   functools        import partialmethod

from   .outputs         import LePhareOutput, CigaleOutput
from   .catalogues      import LePhareCat, CigaleCat
from   .coloredMessages import errorMessage, warningMessage
from   .misc.properties import IntProperty, FloatProperty, StrProperty, ListIntProperty, ListFloatProperty, ListStrProperty, PathProperty, ListPathProperty, EnumProperty, BoolProperty
from   .misc.enum       import MagType, YESNO, ANDOR, LePhareOutputParam
from   .misc            import cigaleModules as cigmod
                         
     
ERROR   = errorMessage('Error:')
WARNING = warningMessage('Warning:')

class SED(ABC):
    r'''
    .. codeauthor:: Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>
    
    Abstract SED object used for inheritance.
    '''
    
    def __init__(self, *args, **kwargs) -> None:
        r'''Init SED oject.'''
        
        #: Log file
        self.log: List = []
    
    @abstractmethod
    def __call__(self, *args, **kwargs):
        r'''
        .. codeauthor:: Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>
        
        Run the SED fitting code.
        '''
        
        return
    
    def appendLog(self, text: str, f: TextIOBase, verbose: bool = False, **kwargs) -> None:
        r'''
        .. codeauthor:: Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>
        
        Append a new text line to the log file.
        
        :param text: text to append
        :type text: :python:`str`
        :param f: file-like opened obect to write into
        :type f: `TextIOBase`_
        
        :param verbose: (**Optional**) whether to also print the log line or not
        :type verbose: :python:`bool`
        
        :raises TypeError:
            
            * if **text** is not of type :python:`str`
            * if **verbose** is not of type :python:`bool`
            * if **f** is not of type `TextIOBase`_
        '''
        
        if not isinstance(text, str):
            raise TypeError(f'log text has type {type(text)} but it must have type str.')
            
        if not isinstance(verbose, bool):
            raise TypeError(f'verbose parameter has type {type(verbose)} but it must have type bool.')
            
        if not isinstance(f, TextIOBase):
            raise TypeError(f'f parameter has type {type(f)} but it must have type TextIOBase.')
            
        if verbose:
            print(text, end='')
        
        f.write(text)
        return
    
    def startProcess(self, commands: List[str], log: TextIOBase = None, errMsg: str = ''):
        '''
        .. codeauthor:: Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>

        Start a process.
        
        :param commands: list of commands to use with Popen
        :type commands: :python:`list[str]`
        
        :param log: (**Optional**) oppened log file
        :type log: `TextIOBase`_
        :param errMsg: (**Optional**) message error to show if the process failed
        :type errMsg: :python:`str`
        
        :raises TypeError: 
            
            * if **errMsg** is not of type :python:`str`
            * if **commands** is not of type :python:`list`
            * if one of the commands in **commands** is not of type :python:`str`
            
        :raises OSError: if the first command in **commands** is not a valid file/script name
        :raises ValueError: if **log** is :python:`None`
        '''

        if not isinstance(errMsg, str):
            raise TypeError(f'errMsg parameter has type {type(errMsg)} but it must have type str.')
        
        if not isinstance(commands, list):
            raise TypeError(f'commands parameter has type {type(commands)} but it must have type list.')
            
        if any((not isinstance(command, str) for command in commands)):
            raise TypeError('one of the commands does not have the type str.')
            
        if log is None:
            raise ValueError('You need to provide a log file-like object.')
            
        command     = opath.expandvars(commands[0])
        if find_executable(command) is None:
            raise OSError(f'script/excutable {commands[0]} (expanded as {command}) not found.')

        commands[0] = command

        with subprocess.Popen(commands, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, bufsize=1, universal_newlines=True) as p:
            for line in p.stdout:
                self.appendLog(line, log, verbose=True)
                
        if p.returncode != 0:
            raise OSError(errMsg)
                
        return


class CigaleSED(SED):
    r'''
    .. codeauthor:: Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>
    
    Implements Cigale SED object.
    
    .. important:
        
        If you want to consider the uncertainties, you must specify it for each band. That is, the following line will not consider uncertainties
        
        :python:`sedobj = CigaleSED('someID', ['F160W', 'F125W', 'F850LP'])`
        
        On the other hand, the follwing line will consider the uncertainties for the first and last filters (F160W and F850LP) only
        
        :python:`sedobj = CigaleSED('someID', ['F160W', 'F125W', 'F850LP'], uncertainties=[True, False, True])`
    
    :param ID: an identifier used to name the output files created during the SED fitting process
    :param filters: filters to use for the SED fitting
    :type filters: :python:`list`
    
    :param uncertainties: (**Optional**) list of bool to specify which uncertainties to use. If provided, it must be same length as **filters**.
    :type uncertainties: :python:`list[bool]`
    :param SFH: (**Optional**) star formation history modules to use. **At least one module must be given.**
    :type SFH: :python:`list` [:py:class:`~.cigmod.SFHmodule`]
    :param SSP: (**Optional**) single stellar population modules to use. **At least one module must be given.**
    :type SSP: :python:`list` [:py:class:`~.cigmod.SSPmodule`]
    :param nebular: (**Optional**) nebular emission modules to use. Empty list means no module is used.
    :type nebular: :python:`list` [:py:class:`~.cigmod.NEBULARmodule`]
    :param attenuation: (**Optional**) dust attenuation modules to use. Empty list means no module is used.
    :type attenuation: :python:`list` [:py:class:`~.cigmod.ATTENUATIONmodule`]
    :param dust: (**Optional**) dust emission modules to use. Empty list means no module is used.
    :type dust: :python:`list` [:py:class:`~.cigmod.DUSTmodule`]
    :param agn: (**Optional**) agn modules to use. Empty list means no module is used.
    :type agn: :python:`list` [:py:class:`cigmod.AGNmodule`]
    :param radio: (**Optional**) synchrotron radiation modules to use. Empty list means no module is used.
    :type radio: :python:`list` [:py:class:`cidmog.AGNmodule`]
    :param restframe: (**Optional**) restframe parameters modules to use. Empty list means no module is used.
    :type restframe: :python:`list` [:py:class:`cigmod.RESTFRAMEmodule`]
    :param redshifting: (**Optional**) redshifitng+IGM modules to use. Empty list means no module is used.
    :type redshifting: :python:`list` [:py:class:`cigmod.REDSHIFTINGmodule`]
    :param flux_uncertainty: additional uncertainty to add to the flux, given as a fraction of the flux (i.e. 0.1 means 10% of flux added to the uncertainty in quadrature)
    :type flux_uncertainty: :python:`int` or :python:`float`
    
    :raises TypeError: if any of the keyword parameters if not a :python:`list`
    :raises ValueError: if no **SFH**, **SSP** and **redshifting** modules are provided
    '''
    
    def __init__(self, ID: Any, filters: List[str], 
                 uncertainties: Optional[List[bool]]         = None,
                 SFH: List[cigmod.SFHmodule]                 = [cigmod.SFH2EXPmodule()],
                 SSP: List[cigmod.SSPmodule]                 = [cigmod.BC03module()],
                 nebular: List[cigmod.NEBULARmodule]         = [],
                 attenuation: List[cigmod.ATTENUATIONmodule] = [],
                 dust: List[cigmod.DUSTmodule]               = [],
                 agn: List[cigmod.AGNmodule]                 = [],
                 radio: List[cigmod.RADIOmodule]             = [],
                 restframe: List[cigmod.RESTFRAMEmodule]     = [],
                 redshifting: List[cigmod.REDSHIFTmodule]    = [cigmod.REDSHIFTmodule()],
                 flux_uncertainty: Union[int, float]         = 0,
                 **kwargs) -> None:
        
        super().__init__(**kwargs)
        
        if not isinstance(filters, list):
            raise TypeError(f'parameter filters has type {type(filters)} but it must be a list.')
        
        # If no uncertainty is given, we do not use the filters
        if uncertainties is None:
            uncertainties = [False]*len(filters)
        
        for var, name in zip([uncertainties, SFH, SSP, nebular, attenuation, dust, agn, radio, restframe, redshifting], 
                             ['uncertainties','SFH', 'SSP', 'nebular', 'attenuation', 'dust', 'agn', 'radio', 'restframe', 'redshifting']):
            
            if not isinstance(var, list):
                raise TypeError(f'parameter {name} has type {type(var)} but it must be a list.')
                
        if len(filters) != len(uncertainties):
            raise ValueError(f'uncertainties has length {len(uncertainties)} and filters has length {len(filters)} but they must have the same length.')
            
        if any((not isinstance(i, bool) for i in uncertainties)):
            raise TypeError('one of the values in uncertainties is not a bool.')
                
        if len(SFH) < 1:
            raise ValueError('at least one SFH module must be provided.')
            
        if len(SSP) < 1:
            raise ValueError('at least one SSP module must be provided.')
            
        if len(redshifting) < 1:
            raise ValueError('at least one redshifting module must be provided.')
            
        if not isinstance(flux_uncertainty, (int, float)):
            raise TypeError(f'flux uncertainty has type {type(flux_uncertainty)} but it must have type int or float.')
            
        if flux_uncertainty < 0:
            raise ValueError('flux uncertainty must be positive.')
            
            
        #: Will be used to generate a custom directory
        self.id: Any                               = ID
        
        # Flux uncertainty
        self.flux_uncertainty                      = flux_uncertainty
        
        #: Filters to use for the SED fitting
        self.filters: ListStrProperty              = ListStrProperty(filters + [f'{filt}_err' for filt, uncertainty in zip(filters, uncertainties) if uncertainty])
        
        # For now we set this parameter to an empty str and we only allow pdf_analysis method (no savefluxes)
        self.analysis                              = StrProperty('pdf_analysis')
        self.parameters_file                       = StrProperty('')
        self.properties                            = StrProperty('')
        
        #: SFH modules to use
        self.SFH: cigmod.SFHmodule                 = self._checkModule(SFH, cigmod.SFHmodule) 
        
        #: SSP modules to use
        self.SSP: cigmod.SSPmodule                 = self._checkModule(SSP, cigmod.SSPmodule)
        
        #: Nebular emission modules to use
        self.nebular: cigmod.NEBULARmodule         = self._checkModule(nebular, cigmod.NEBULARmodule)
        
        #: Dust attenuation modules to use
        self.attenuation: cigmod.ATTENUATIONmodule = self._checkModule(attenuation, cigmod.ATTENUATIONmodule)
        
        #: Dust emission modules to use
        self.dust: cigmod.DUSTmodule               = self._checkModule(dust, cigmod.DUSTmodule)
        
        #: AGN modules to use
        self.agn: cigmod.AGNmodule                 = self._checkModule(agn, cigmod.AGNmodule)
        
        #: Synchrotron radiation modules to use
        self.radio: cigmod.RADIOmodule             = self._checkModule(radio, cigmod.RADIOmodule)
        
        #: Rest-frame parameters modules to use
        self.restframe: cigmod.RESTFRAMEmodule     = self._checkModule(restframe, cigmod.RESTFRAMEmodule)
        
        #: Redshifting modules to use
        self.redshifting: cigmod.REDSHIFTmodule    = self._checkModule(redshifting, cigmod.REDSHIFTmodule)
        
        #: Modules names list
        self.moduleNames: ListStrProperty           = ListStrProperty([i.name for i in self.SFH + self.SSP + self.nebular + self.attenuation + self.dust + self.agn + self.radio + self.restframe + self.redshifting])
        
        #: Modules parameters in str format
        self.modulesStr: str                        = ''
        
        #: Modules spec parameters in str format
        self.modulesSpec: str                       = ''
        
        for pos, module in enumerate(self.SFH + self.SSP + self.nebular + self.attenuation + self.dust + self.agn + self.radio + self.restframe + self.redshifting):
            self.modulesStr                        += f'\n\n{module}' if pos != 0 else f'\n{module}'
            self.modulesSpec                       += indent(dedent(f'\n{module.spec}' if pos != 0 else f'{module.spec}'), '   ')

    @staticmethod
    def _checkModule(modules: List[Any], inheritedClass: Any) -> bool:
        r'''
        .. codeauthor:: Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>
        
        Check that the given list of Cigale modules belong to the correct class they should inherit from.
        
        :param modules: modules to check the inheritance
        :type modules: :python:`list`
        :param inheritedClass: class to check against for inheritance
        
        :returns: the list of modules if all the modules inherit from the given class
        :rtype: :python:`list`
        
        :raises TypeError: if one of the modules in **modules** does not inherit from **inheritedClass**
        '''
        
        for module in modules:
            if not isinstance(module, inheritedClass):
                raise TypeError(f'module {module.__name__} is not an instance of a subclass of {inheritedClass.__name__}.')

        return modules
    
    ###############################
    #       Text formatting       #
    ###############################
    
    def analysisParamsModule(self, physical_properties: Optional[List[str]], bands: Optional[List[str]], save_best_sed: bool,
                             save_chi2: bool, lim_flag: bool, mock_flag: bool, redshift_decimals: int, blocks: int, 
                             **kwargs) -> str:
        r'''
        .. codeauthor:: Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>
        
        Generate the analysis_params module text for Cigale.
        
        :param physical_properties: physical properties to estimate at the end of the SED fitting. If :python:`None`, all properties are computed.
        :type physical_properties: :python:`list[str]`
        :param bands: list of bands for which to estimate the fluxes. Note that this is independent from the fluxes actually fitted to estimate the physical properties. If :python:`None`, the same bands as the ones provided in **filters** will be used.
        :type bands: :python:`list[str]`
        :param save_best_sed: whether to save the best SED for each observation into a file or not
        :type save_best_sed: :python:`bool`
        :param save_chi2: whether to save the raw chi2 or not. It occupies ~15 MB/million models/variable.
        :type save_chi2: :python:`bool`
        :param lim_flag: if :python:`True`, for each object check whether upper limits are present and analyse them
        :type lim_flag: :python:`bool`
        :param mock_flag: if :python:`True`, for each object we create a mock object and analyse them
        :type bool_mock: :python:`bool`
        :param redshift_decimals: when redshifts are not given explicitly in the redshifting module, number of decimals to round the observed redshifts to compute the grid of models. To disable rounding give :python:`-1`. Do not round if you use narrow-band filters.
        :type redshift_decimals: :python:`int`
        :param int blocks: number of blocks to compute the models and analyse the observations. If there is enough memory, we strongly recommend this to be set to :python:`1`.
        :type blocks: :python:`int`
        
        :returns: module text for the analysis parameters
        :rtype: :python:`str`
        '''
        
        text = dedent(f'''
        # Configuration of the statistical analysis method.
        [analysis_params]
          # List of the physical properties to estimate. Leave empty to analyse
          # all the physical properties (not recommended when there are many
          # models).
          variables = {physical_properties}
          # List of bands for which to estimate the fluxes. Note that this is
          # independent from the fluxes actually fitted to estimate the physical
          # properties.
          bands = {bands}
          # If true, save the best SED for each observation to a file.
          save_best_sed = {save_best_sed}
          # If true, for each observation and each analysed property, save the raw
          # chi2. It occupies ~15 MB/million models/variable.
          save_chi2 = {save_chi2}
          # If true, for each object check whether upper limits are present and
          # analyse them.
          lim_flag = {lim_flag}
          # If true, for each object we create a mock object and analyse them.
          mock_flag = {mock_flag}
          # When redshifts are not given explicitly in the redshifting module,
          # number of decimals to round the observed redshifts to compute the grid
          # of models. To disable rounding give a negative value. Do not round if
          # you use narrow-band filters.
          redshift_decimals = {redshift_decimals}
          # Number of blocks to compute the models and analyse the observations.
          # If there is enough memory, we strongly recommend this to be set to 1.
          blocks = {blocks}
        ''')
        
        return text

    @property
    def parameters(self, *args, **kwargs) -> str:
        r'''
        .. codeauthor:: Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>
        
        Generate a parameter file text used by the SED fitting code.
        
        :returns: the text
        :rtype: :python:`str`
        '''
        
        # %INPUTCATALOGUEINFORMATION% and %NCORES% are replaced when the run method is launched
        
        text1 = dedent(f'''\
        # File containing the input data. The columns are 'id' (name of the
        # object), 'redshift' (if 0 the distance is assumed to be 10 pc),
        # 'distance' (Mpc, optional, if present it will be used in lieu of the
        # distance computed from the redshift), the filter names for the fluxes,
        # and the filter names with the '_err' suffix for the uncertainties. The
        # fluxes and the uncertainties must be in mJy for broadband data and in
        # W/m² for emission lines. This file is optional to generate the
        # configuration file, in particular for the savefluxes module.
        data_file = %INPUTCATALOGUEINFORMATION%
        
        # Optional file containing the list of physical parameters. Each column
        # must be in the form module_name.parameter_name, with each line being a
        # different model. The columns must be in the order the modules will be
        # called. The redshift column must be the last one. Finally, if this
        # parameter is not empty, cigale will not interpret the configuration
        # parameters given in pcigale.ini. They will be given only for
        # information. Note that this module should only be used in conjonction
        # with the savefluxes module. Using it with the pdf_analysis module will
        # yield incorrect results.
        parameters_file = {self.parameters_file}
        
        # Avaiable modules to compute the models. The order must be kept.
        # SFH:
        # * sfh2exp (double exponential)
        # * sfhdelayed (delayed SFH with optional exponential burst)
        # * sfhdelayedbq (delayed SFH with optional constant burst/quench)
        # * sfhfromfile (arbitrary SFH read from an input file)
        # * sfhperiodic (periodic SFH, exponential, rectangle or delayed)
        # SSP:
        # * bc03 (Bruzual and Charlot 2003)
        # * m2005 (Maraston 2005; note that it cannot be combined with the nebular module)
        # Nebular emission:
        # * nebular (continuum and line nebular emission)
        # Dust attenuation:
        # * dustatt_modified_CF00 (modified Charlot & Fall 2000 attenuation law)
        # * dustatt_modified_starburst (modified Calzetti 2000 attenuaton law)
        # Dust emission:
        # * casey2012 (Casey 2012 dust emission models)
        # * dale2014 (Dale et al. 2014 dust emission templates)
        # * dl2007 (Draine & Li 2007 dust emission models)
        # * dl2014 (Draine et al. 2014 update of the previous models)
        # * themis (Themis dust emission models from Jones et al. 2017)
        # AGN:
        # * fritz2006 (AGN models from Fritz et al. 2006)
        # Radio:
        # * radio (synchrotron emission)
        # Restframe parameters:
        # * restframe_parameters (UV slope (β), IRX, D4000, EW, etc.)
        # Redshift+IGM:
        # * redshifting (mandatory, also includes the IGM from Meiksin 2006)
        sed_modules = {self.moduleNames}
        
        # Method used for statistical analysis. Available methods: pdf_analysis,
        # savefluxes.
        analysis_method = {self.analysis}
        
        # Number of CPU cores available. This computer has 8 cores.
        cores = %NCORES%
        
        # Bands to consider. To consider uncertainties too, the name of the band
        # must be indicated with the _err suffix. For instance: FUV, FUV_err.
        bands = {self.filters}
        
        # Properties to be considered. All properties are to be given in the
        # rest frame rather than the observed frame. This is the case for
        # instance the equivalent widths and for luminosity densities.
        properties = {self.properties}
        
        # Relative error added in quadrature to the uncertainties of the fluxes
        # and the extensive properties.
        additionalerror = {self.flux_uncertainty}
        
        # Configuration of the SED creation modules.
        [sed_modules_params]
        ''')
        
        text2 = indent(dedent(f'{self.modulesStr}'), '   ')
        
        return text1 + text2
    
    @property
    def specParameters(self, *args, **kwargs) -> str:
        r'''
        .. codeauthor:: Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>
        
        Generate the spec parameter file text associated to the given sed modules.
        
        :returns: spec parameter file text
        :rtype: :python:`str`
        '''
        
        text = dedent('''\
        data_file = string()
        parameters_file = string()
        sed_modules = cigale_string_list()
        analysis_method = string()
        cores = integer(min=1)
        bands = cigale_string_list()
        properties = cigale_string_list()
        additionalerror = float()
        [sed_modules_params]
        %MODULESSPEC%
        [analysis_params]
          variables = cigale_string_list()
          save_best_sed = boolean()
          save_chi2 = boolean()
          lim_flag = boolean()
          mock_flag = boolean()
          redshift_decimals = integer()
          blocks = integer(min=1)
        ''')
        
        return text.replace('%MODULESSPEC%', self.modulesSpec)
    
    #############################
    #        Run methods        #
    #############################
    
    def startCigale(self, log: TextIOBase = None):
        r'''
        .. codeauthor:: Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>
        
        Wrapper around default :py:meth:`SED.startProcess` which allows to run Cigale.
        
        :param log: (**Optional**) oppened log file
        :type log: `TextIOBase`_
        '''
        
        return self.startProcess(['pcigale', 'run'], log=log, errMsg='SED fitting failed.')
    
    def __call__(self, catalogue: CigaleCat, 
                 ncores: int                              = 4,
                 physical_properties: Optional[List[str]] = None,
                 bands: Optional[List[str]]               = None,
                 save_best_sed: bool                      = False,
                 save_chi2: bool                          = False,
                 lim_flag: bool                           = False,
                 mock_flag: bool                          = False,
                 redshift_decimals: int                   = 2,
                 blocks: int                              = 1,
                 **kwargs) -> CigaleOutput:
        r'''
        .. codeauthor:: Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>
        
        Start the SED fitting on the given data using the built-in SED fitting parameters.
        
        :param CigaleCat catalogue: catalogue to use for the SED-fitting
        
        :param ncores: (**Optional**) number of cores (technically threads) to use to generate the grid of parameters
        :type ncores: :python:`int`
        :param physical_properties: (**Optional**) physical properties to estimate at the end of the SED fitting. If :python:`None`, all properties are computed.
        :type physical_properties: :python:`list[str]`
        :param bands: (**Optional**) list of bands for which to estimate the fluxes. Note that this is independent from the fluxes actually fitted to estimate the physical properties. If :python:`None`, the same bands as the ones provided in **filters** will be used.
        :type bands: :python:`list[str]`
        :param save_best_sed: (**Optional**) whether to save the best SED for each observation into a file or not
        :type save_best_sed: :python:`bool`
        :param save_chi2: (**Optional**) whether to save the raw chi2 or not. It occupies ~15 MB/million models/variable.
        :type save_chi2: :python:`bool`
        :param lim_flag: (**Optional**) if :python:`True`, for each object check whether upper limits are present and analyse them
        :type lim_flag: :python:`bool`
        :param mock_flag: (**Optional**) if :python:`True`, for each object we create a mock object and analyse them
        :type mock_flag: :python:`bool`
        :param redshift_decimals: (**Optional**) when redshifts are not given explicitly in the redshifting module, number of decimals to round the observed redshifts to compute the grid of models. To disable rounding give :python:`-1`. Do not round if you use narrow-band filters.
        :type redshift_decimals: :python:`int`
        :param blocks: (**Optional**) number of blocks to compute the models and analyse the observations. If there is enough memory, we strongly recommend this to be set to :python:`1`.
        :type blocks: :python:`int`
        
        :returns: Cigale output file object with data from the loaded file
        :rtype: CigaleOutput
    
        :raises TypeError: if **catalogue** is not of type :py:class:`~.LePhareCat`
        '''
        
        if not isinstance(catalogue, CigaleCat):
            raise TypeError(f'catalogue has type {type(catalogue)} but it must be a CigaleCat instance.')
            
        # Check parameters
        ncores            = IntProperty(ncores, minBound=1)
        phys_prop         = ListStrProperty(physical_properties if physical_properties is not None else [''])
        bands             = ListStrProperty(bands if bands is not None else self.filters.value)
        save_best_sed     = BoolProperty(save_best_sed)
        save_chi2         = BoolProperty(save_chi2)
        lim_flag          = BoolProperty(lim_flag)
        mock_flag         = BoolProperty(mock_flag)
        redshift_decimals = IntProperty(redshift_decimals, minBound=-1)
        blocks            = IntProperty(blocks, minBound=1)
        
        # Make output directory
        directory = f'{self.id}'
        if not opath.isdir(directory):
            os.mkdir(directory)
            
        # Delete output directory in the galaxy directory if already present (otherwise Cigale will make a new one with a different name)
        outDir    = opath.join(directory, 'out')
        if opath.isdir(outDir):
            shutil.rmtree(outDir)
        
        # Param file in cigale works in a weird way, better to always use the default name (pcigale.ini and pcigale.ini.spec)
        paramFile = 'pcigale.ini'
        pfile     = opath.join(directory, paramFile)
        sfile     = opath.join(directory, 'pcigale.ini.spec')
        logFile   = opath.join(directory, catalogue.name.replace('.mag', '_cig.log'))
        oCatFile  = opath.join(outDir,    'results.fits')
        
        # Generate and write parameters file
        beg_param = self.parameters.replace('%INPUTCATALOGUEINFORMATION%', catalogue.name).replace('%NCORES%', f'{ncores}')
        end_param = self.analysisParamsModule(phys_prop, bands, save_best_sed, save_chi2, lim_flag, mock_flag, redshift_decimals, blocks)
        
        with open(pfile, 'w') as f:
            f.write(beg_param + end_param) 
            
        # Generate and write spec file
        with open(sfile, 'w') as f:
            f.write(self.specParameters)
        
        # Write catalogue
        catalogue.save(path=directory)
        
        with open(logFile, 'a') as log:
            
            ###################################
            #         Run SED fitting         #
            ###################################
            
            # Move to directory
            os.chdir(directory)
            
            self.startCigale(log=log)
            
            # Move back to parent directory
            os.chdir('..')
            
        return CigaleOutput(oCatFile) 
                

class LePhareSED(SED):
    r'''
    .. codeauthor:: Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>
    
    Implements LePhare SED object.
    
    :param ID: an identifier used to name the output files created during the SED fitting process
    
    :param properties: (**Optional**) properties to be passed to LePhare to compute the models grid and perform the SED fitting
    :type properties: :python:`dict[str, str]`
    
    :raises TypeError: if one of the properties keys is not of type :python:`str`
    :raises ValueError: if one of the properties does not have a valid name (see list below)
    
    **Accepted properties are:**
    
        * **STAR_SED** [:python:`str`]: stellar library list file (full path)
        * **STAR_FSCALE** [:python:`float`]: stellar flux scale
        * **STAR_LIB** [:python:`str`]: stellar library to use (default libraries found at :file:`$LEPHAREWORK/lib_bin`). To not use a stellar library, provide :python:`'NONE'`.
        * **QSO_SED** [:python:`str`]: QSO list file (full path)
        * **QSO_FSCALE** [:python:`float`]: QSO flux scale
        * **QSO_LIB** [:python:`str`]: QSO library to use (default libraries found at :file:`LEPHAREWORK/lib_bin`). To not use a QSO library, provide :python:`'NONE'`.
        * **GAL_SED** [:python:`str`]: galaxy library list file (full path)
        * **GAL_FSCALE** [:python:`float`]: galaxy flux scale
        * **GAL_LIB** [:python:`str`]: galaxy library to use (default libraries found at :file:`$LEPHAREWORK/lib_bin`). To not use a galaxy library, provide :python:`'NONE'`.
        * **SEL_AGE** [:python:`str`]: stellar ages list (full path)
        * **AGE_RANGE** [:python:`list[float]`]: minimum and maximum ages in years
        * **FILTER_LIST** [:python:`list[str]`]: list of filter names used for the fit (must all be located in :file:`$LEPHAREDIR/filt directory`)
        * **TRANS_TYPE** [:python:`int`]: transmission type (:python:`0` for Energy, :python:`1` for photons)
        * **FILTER_CALIB** [:python:`int`]: filter calibration (:python:`0` for fnu=ctt, :python:`1` for nu.fnu=ctt, :python:`2` for fnu=nu, :python:`3` for fnu=Black Body @ T=10000K, :python:`4` for MIPS (leff with nu fnu=ctt and flux with BB @ 10000K) 
        * **FILTER_FILE** [:python:`str`]: filter file (must be located in :file:`$LEPHAREWORK/filt` directory)
        * **STAR_LIB_IN** [:python:`str`]: input stellar library (dupplicate with **STAR_LIB** ?)
        * **STAR_LIB_OUT** [:python:`str`]: output stellar magnitudes
        * **QSO_LIB_IN** [:python:`str`]: input QSO library (dupplicate with **QSO_LIB** ?)
        * **QSO_LIB_OUT** [:python:`str`]: output QSO magnitudes
        * **GAL_LIB_IN** [:python:`str`]: input galaxy library (dupplicate with **GAL_LIB** ?)
        * **GAL_LIB_OUT** [:python:`str`]: output galaxy magnitudes
        * **MAGTYPE** [:py:class:`~.MagType`]: magnitude system used (:py:attr:`~.MagType.AB` or :py:attr:`~.MagType.VEGA`)
        * **Z_STEP** [:python:`list[int/float]`]: redshift step properties. Values are in this order: redshift step, max redshift, redshift step for redshifts above 6 (coarser sampling).
        * **COSMOLOGY** [:python:`list[int/float]`]: cosmology parameters. Values are in this order: Hubble constant :math:`H_0`, baryon fraction :math:`\Omega_{m, 0}`, cosmological constant fraction :math:`\Omega_{\lambda, 0}`.
        * **MOD_EXTINC** [:python:`list[int/float]`]: minimum and maximum model extinctions
        * **EXTINC_LAW** [:python:`str`]: extinction law file (in :file:`$LEPHAREDIR/ext`)
        * **EB_V** [:python:`list[int/float]`]: color excess :math:`E(B-V)`. It must contain less than 50 values.
        * **EM_LINES** [:py:class:`~.YESNO`]: whether to consider emission lines or not. Accepted values are :py:attr:`~.YESNO.YES` or :py:attr:`~.YESNO.NO`.
        * **BD_SCALE** [:python:`int`]: number of bands used for scaling (:python:`0` means all bands). See LePhare documentation for more details.
        * **GLB_CONTEXT** [:python:`int`]: context number (:python:`0` means all bands). See LePhare documentation for more details.
        * **ERR_SCALE** [:python:`list[int/float]`]: magnitude errors per band to add in quadrature
        * **ERR_FACTOR** [:python:`int/float`]: scaling factor to apply to the errors
        * **ZPHOTLIB** [:python:`list[str]`]: librairies used to compute the :math:`\chi^2`. Maximum number is :python:`3`.
        * **ADD_EMLINES** [:py:class:`~.YESNO`]: whether to add emission lines or not (dupplicate with **EM_LINES** ?). Accepted values are :py:attr:`~.YESNO.YES` or :py:attr:`~.YESNO.NO`.
        * **FIR_LIB** [:python:`str`]: far IR library
        * **FIR_LMIN** [:python:`int/float`]: minimum wavelength (in microns) for the far IR analysis
        * **FIR_CONT** [:python:`int/float`]: far IR continuum. Use :python:`-1` for no continuum.
        * **FIR_SCALE** [:python:`int/float`]: far IR flux scale. Use :python:`-1` to skip flux scale.
        * **FIR_FREESCALE** [:python:`str`]: whether to let the far IR spectrum freely scale
        * **FIR_SUBSTELLAR** [:python:`str`]: ???
        * **PHYS_LIB** [:python:`str`]: physical stochastic library
        * **PHYS_CONT** [:python:`int/float`]: physical continuum. Use :python:`-1` for no continuum.
        * **PHYS_SCALE** [:python:`int/float`]: physical flux scale. Use :python:`-1` to skip flux scale.
        * **PHYS_NMAX** [:python:`int`]: ???
        * **MAG_ABS** [:python:`list[int/float]`]: minimum and maximum values for the magnitudes.
        * **MAG_REF** [:python:`int`]: reference band used by **MAG_ABS**
        * **Z_RANGE** [:python:`list[int/float]`]: minimum and maximum redshifts used by the galaxy library
        * **EBV_RANGE** [:python:`list[int/float]`]: minimum and maximum colour excess :math:`E(B-V)`
        * **ZFIX** [:py:class:`~.YESNO`]: whether to fix the redshift or let it free. Accepted values are :py:attr:`~.YESNO.YES` or :py:attr:`~.YESNO.NO`.
        * **Z_INTERP** [:py:class:`~.YESNO`]: whether to perform an interpolation to find the redshift. Accepted values are :py:attr:`~.YESNO.YES` or :py:attr:`~.YESNO.NO`.
        * **DZ_WIN** [:python:`int/float`]: window search for second peak. Must be between :python:`0` and :python:`5`.
        * **MIN_THRES** [:python:`int/float`]: minimum threshold for second peak. Must be between :python:`0` and :python:`1`.
        * **MABS_METHOD** [:python:`int`]: method used to compute magnitudes (:python:`0` : obs->Ref, :python:`1` : best obs->Ref, :python:`2` : fixed obs->Ref, :python:`3` : mag from best SED, :python:`4` : Zbin). See LePhare documentation for more details.
        * **MABS_CONTEXT** [:python:`int`]: context for absolute magnitudes. See LePhare documentation for more details.
        * **MABS_REF** [:python:`int`]: reference band used to compute the absolute magnitudes. This is only used if :python:`MABS_METHOD = 2`.
        * **MABS_FILT** [:python:`list[int]`]: filters used in each redshift bin (see **MABS_ZBIN**). This is only used if :python:`MABS_METHOD = 4`.
        * **MABS_ZBIN** [:python:`list[int/float]`]: redshift bins (must be an even number). This is only used if :python:`MABS_METHOD = 4`.
        * **SPEC_OUT** [:py:class:`~.YESNO`]: whether to output the spectrum of each object or not. Accepted values are :py:attr:`~.YESNO.YES` or :py:attr:`~.YESNO.NO`.
        * **CHI2_OUT** [:py:class:`~.YESNO`]: whether to generate an output file with all the values or not. Accepted values are :py:attr:`~.YESNO.YES` or :py:attr:`~YESNO.NO`.
        * **PDZ_OUT** [:python:`str`]: output file name for the PDZ analysis. To not do the pdz analysis, provide :python:`'NONE'`.
        * **PDZ_MABS_FILT** [:python:`list[int]`]: absolute magnitude for reference filters to be extracted. See LePhare documentation for more details.
        * **FAST_MODE** [:py:class:`~.YESNO`]: whether to perform a fast computation or not. Accepted values are :py:attr:`~.YESNO.YES` or :py:attr:`~.YESNO.NO`.
        * **COL_NUM** [:python:`int`]: number of colors used
        * **COL_SIGMA** [:python:`int/float`]: quantity by which to enlarge the errors on the colors
        * **COL_SEL** [:py:class:`~.ANDOR`]: operation used to combine colors. Accepted values are :py:attr:`~.ANDOR.AND` or :py:attr:`~.ANDOR.OR`.
        * **AUTO_ADAPT** [:py:class:`~.YESNO`]: whether to use an adaptive method with a z-spec sample. Accepted values are :py:attr:`~.YESNO.YES` or :py:attr:`~.YESNO.NO`.
        * **ADAPT_BAND** [:python:`list[int]`]: reference band, band1 and band2 for colors
        * **ADAPT_LIM** [:python:`list[int/float]`]: magnitude limit for spectro in reference band
        * **ADAPT_POLY** [:python:`int`]: number of coefficients in polynomial. Maximum is :python:`4`.
        * **ADAPT_METH** [:python:`int`]: fit method, :python:`1` for color model, :python:`2` for redshift, :python:`3` for models. See LePhare documentation for more details.
        * **ADAPT_CONTEXT** [:python:`int`]: context for the bands used for training. See LePhare documentation for more details.
        * **ADAPT_ZBIN** [:python:`list[int/float]`]: minimum and maximum redshift interval used for training.
        
    .. warning::
        
        It is mandatory to define on your OS two environment variables:
            
            * :file:`$LEPHAREWORK` which points to LePhare working directory
            * :file:`$LEPHAREDIR` which points to LePhare main directory
            
        These paths may be expanded to check whether the given files exist and can be used by the user to shorten some path names when providing the SED properties.
    '''
    
    def __init__(self, ID: Any, properties: dict = {}, **kwargs) -> None:
        
        if not isinstance(properties, dict):
            raise TypeError(f'properties parameter has type {type(properties)} but it must be a dict.')
        
        super().__init__(**kwargs)
        
        #: Will be used to generate a custom directory
        self.id: Any         = ID
        
        # Output parameter file is defined through the ID
        self.outputParamFile = f'{self.id}_output.para'
        self.outParam        = {f'{i}' : False for i in LePhareOutputParam}
        
        #: Allowed keys and corresponding allowed types
        self.prop: Dict[str, Any] = {'STAR_SED'       : PathProperty(opath.join('$LEPHAREDIR', 'sed', 'STAR', 'STAR_MOD.list')),
                     
                     'STAR_FSCALE'    : FloatProperty(3.432e-09, minBound=0),
                     
                     'STAR_LIB'       : PathProperty('LIB_STAR_bc03', path=opath.join('$LEPHAREWORK', 'lib_bin'), ext='.bin'),
                     
                     'QSO_SED'        : PathProperty(opath.join('$LEPHAREDIR', 'sed', 'QSO', 'QSO_MOD.list')),
                     
                     'QSO_FSCALE'     : FloatProperty(1.0, minBound=0),
                     
                     'QSO_LIB'        : PathProperty('LIB_QSO_bc03', path=opath.join('$LEPHAREWORK', 'lib_bin'), ext='.bin'),
                     
                     'GAL_SED'        : PathProperty(opath.join('$LEPHAREDIR', 'sed', 'GAL', 'BC03_CHAB', 'BC03_MOD.list')),
                     
                     'GAL_FSCALE'     : FloatProperty(1.0, minBound=0),
                     
                     'GAL_LIB'        : PathProperty('LIB_bc03', path=opath.join('$LEPHAREWORK', 'lib_bin'), ext='.bin'),
                     
                     'SEL_AGE'        : PathProperty(opath.join('$LEPHAREDIR', 'sed', 'GAL', 'BC03_CHAB', 'BC03_AGE.list')),
                     
                     'AGE_RANGE'      : ListFloatProperty([3e9, 11e9], minBound=0, 
                                                 testFunc=lambda value: len(value)!=2 or value[1] < value[0], 
                                                 testMsg='AGE_RANGE property must be a length 2 list.'),
                     
                     'FILTER_LIST'    : ListPathProperty(['hst/acs_f435w.pb', 'hst/acs_f606w.pb', 'hst/acs_f775w.pb', 'hst/acs_f850lp.pb'], 
                                                         path=opath.join('$LEPHAREDIR', 'filt')),
                     
                     'TRANS_TYPE'     : IntProperty(0, minBound=0, maxBound=1),
                     
                     'FILTER_CALIB'   : IntProperty(0, minBound=0, maxBound=4),
                     
                     'FILTER_FILE'    : PathProperty('HDF_bc03.filt', path=opath.join('$LEPHAREWORK', 'filt')),
                     
                     'STAR_LIB_IN'    : PathProperty('LIB_STAR_bc03', path=opath.join('$LEPHAREWORK', 'lib_bin'), ext='.bin'),
                     
                     'STAR_LIB_OUT'   : StrProperty('STAR_HDF_bc03'),
                     
                     'QSO_LIB_IN'     : PathProperty('LIB_QSO_bc03', path=opath.join('$LEPHAREWORK', 'lib_bin'), ext='.bin'),
                     
                     'QSO_LIB_OUT'    : StrProperty('QSO_HDF_bc03'),
                     
                     'GAL_LIB_IN'     : PathProperty('LIB_bc03', path=opath.join('$LEPHAREWORK', 'lib_bin'), ext='.bin'),
                     
                     'GAL_LIB_OUT'    : StrProperty('HDF_bc03'),
                     
                     'MAGTYPE'        : EnumProperty(MagType.AB),
                     
                     'Z_STEP'         : ListFloatProperty([0.01, 2.0, 0.1], minBound=0,
                                                          testFunc=lambda value: len(value)!=3 or value[2] < value[0], 
                                                          testMsg='Z_STEP property must be a length 3 list where the last step must be larger than the first one.'),
                     
                     'COSMOLOGY'      : ListFloatProperty([70.0, 0.3, 0.7], minBound=0,
                                                          testFunc=lambda value: len(value)!=3, 
                                                          testMsg='Z_STEP property must be a length 3 list.'),
                     
                     'MOD_EXTINC'     : ListIntProperty([0, 27],
                                                 testFunc=lambda value: len(value)!=2 or value[1] < value[0], 
                                                 testMsg='MOD_EXTINC property must be an increasing length 2 list.'),
                     
                     'EXTINC_LAW'     : PathProperty('calzetti.dat', path=opath.join('$LEPHAREDIR', 'ext')),
                     
                     'EB_V'           : ListFloatProperty([0.0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5],
                                                          testFunc=lambda value: len(value)>49 or any((j<=i for i, j in zip(value[:-1], value[1:]))), 
                                                          testMsg='EB_V property must be an increasing list with a maximum length of 49.'),
                     
                     'EM_LINES'       : EnumProperty(YESNO.NO),
                     
                     'LIB_ASCII'      : EnumProperty(YESNO.NO),
                     
                     'BD_SCALE'       : IntProperty(0, minBound=0),
                     
                     'GLB_CONTEXT'    : IntProperty(0, minBound=0),
                     
                     'ERR_SCALE'      : ListFloatProperty([0.03, 0.03, 0.03, 0.03], minBound=0),
                     
                     'ERR_FACTOR'     : FloatProperty(1.0, minBound=0),
                     
                     'ZPHOTLIB'       : ListStrProperty(['HDF_bc03', 'STAR_HDF_bc03', 'QSO_HDF_bc03']),
                     
                     'ADD_EMLINES'    : EnumProperty(YESNO.NO),
                     
                     'FIR_LIB'        : PathProperty('NONE'),
                     
                     'FIR_LMIN'       : FloatProperty(7.0, minBound=0),
                     
                     'FIR_CONT'       : FloatProperty('-1'),
                     
                     'FIR_SCALE'      : FloatProperty('-1'),
                     
                     'FIR_FREESCALE'  : EnumProperty(YESNO.NO),
                     
                     'FIR_SUBSTELLAR' : EnumProperty(YESNO.NO),
                     
                     'PHYS_LIB'       : PathProperty('NONE'),
                     
                     'PHYS_CONT'      : FloatProperty('-1'),
                     
                     'PHYS_SCALE'     : FloatProperty('-1'),
                     
                     'PHYS_NMAX'      : IntProperty(100000),
                     
                     'MAG_ABS'        : ListFloatProperty([-20.0, -30.0],
                                                          testFunc=lambda value: len(value)!=2,
                                                          testMsg='MAG_ABS property must be a length 2 list.'),
                     
                     'MAG_REF'        : IntProperty(1, minBound=0),
                     
                     'Z_RANGE'        : ListFloatProperty([0.2, 2.0], minBound=0,
                                                          testFunc=lambda value: len(value)!=2 or value[1] < value[0],
                                                          testMsg='Z_RANGE property must be an increasing length 2 list.'),
                     
                     'EBV_RANGE'      : ListFloatProperty([0.0, 9.0],
                                                          testFunc=lambda value: len(value)!=2 or value[1] < value[0],
                                                          testMsg='EBV_RANGE_RANGE property must be an increasing length 2 list.'),
                     
                     'ZFIX'           : EnumProperty(YESNO.YES),
                     
                     'Z_INTERP'       : EnumProperty(YESNO.NO),
                     
                     'DZ_WIN'         : FloatProperty(0.5, minBound=0, maxBound=5),
                     
                     'MIN_THRES'      : FloatProperty(0.1, minBound=0, maxBound=1),
                     
                     'MABS_METHOD'    : IntProperty( 1, minBound=0, maxBound=4),
                     
                     'MABS_CONTEXT'   : IntProperty(-1),
                     
                     'MABS_REF'       : IntProperty( 0),
                     
                     'MABS_FILT'      : ListIntProperty([1, 2, 3, 4], minBound=0),
                     
                     'MABS_ZBIN'      : ListFloatProperty([0.0, 0.5, 1.0, 1.5, 2.0, 3.0, 3.5, 4.0], minBound=0,
                                                          testFunc=lambda value: len(value)%2!=0 or any((j<=i for i, j in zip(value[:-1], value[1:]))), 
                                                          testMsg='MABS_ZBIN property must be an increasing list with an even length.'),
                     
                     'SPEC_OUT'       : EnumProperty(YESNO.NO),
                     
                     'CHI2_OUT'       : EnumProperty(YESNO.NO),
                     
                     'PDZ_OUT'        : PathProperty('NONE'),
                     
                     'PDZ_MABS_FILT'  : ListIntProperty([2, 10, 14], minBound=0),
                     
                     'FAST_MODE'      : EnumProperty(YESNO.NO),
                     
                     'COL_NUM'        : IntProperty(3, minBound=0),
                     
                     'COL_SIGMA'      : IntProperty(3, minBound=0),
                     
                     'COL_SEL'        : EnumProperty(ANDOR.AND),
                     
                     'AUTO_ADAPT'     : EnumProperty(YESNO.NO),
                     
                     'ADAPT_BAND'     : ListIntProperty([4, 2, 4], minBound=0),
                     
                     'ADAPT_LIM'      : ListFloatProperty([20.0, 40.0],
                                                          testFunc=lambda value: len(value)!=2 or value[1] < value[0],
                                                          testMsg='ADAPT_LIM property must be an increasing length 2 list.'),
                     
                     'ADAPT_POLY'     : IntProperty( 1, minBound=1, maxBound=4),
                     
                     'ADAPT_METH'     : IntProperty( 1, minBound=1, maxBound=3),
                     
                     'ADAPT_CONTEXT'  : IntProperty(-1),
                     
                     'ADAPT_ZBIN'     : ListFloatProperty([0.01, 6.0], minBound=0,
                                                          testFunc=lambda value: len(value)!=2 or value[1] < value[0],
                                                          testMsg='ADAPT_ZBIN property must be an increasing length 2 list.'),
                     
                     'ADAPT_MODBIN'   : ListIntProperty([1, 1000], minBound=1, maxBound=1000,
                                                        testFunc=lambda value: len(value)!=2 or value[1] < value[0],
                                                        testMsg='ADAPT_MODBIN property must be an increasing length 2 list.'),
                     
                     'ERROR_ADAPT'    : EnumProperty(YESNO.NO)
                     }
        
        # Set properties given by the user
        for item, value in properties.items():
            
            if not isinstance(item, str):
                raise TypeError(f'item {item} in properties has type {type(item)} but it must have type str')
            
            item = item.upper()
            if item not in self.prop:
                raise ValueError(f'item {item} in properties does not correspond to a valid item name.')
                
            # Set Property value
            self.prop[item].set(value)
        
        
    ###############################
    #       Text formatting       #
    ###############################
    
    def output_parameters(self, params: List[str] = [], *args, **kwargs) -> str:
        r'''
        .. codeauthor:: Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>
        
        Generate an output parameter file used by the SED fitting code.
        
        :param params: list of parameters to activate in the ouput parameters file
        :type params: :python:`list[str]`
        
        .. note ::
            
            To know which output parameters can be passed print outParam property, i.e.
            
            >>> sed = LePhareSED('identifier')
            >>> print(sed.outParams)
        '''
        
        if not isinstance(params, list):
            raise TypeError(f'params has type {type(params)} but it must have type list.')
            
        if any((not isinstance(param, str) for param in params)):
            raise TypeError('one of the values in params is not of type str.')
        
        # Check and then set given parameters to True
        newParams                = deepcopy(self.outParam)
        for param in params:
            
            if param not in newParams:
                print(f'{WARNING} invalid parameter name {param}.')
            else:
                newParams[param] = True
        
        # Produce the formatted string
        return 'IDENT\n' + '\n'.join([f'{key}' if value else f'#{key}' for key, value in newParams.items()])
        
    @property
    def parameters(self, *args, **kwargs) -> str:
        r'''
        .. codeauthor:: Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>
        
        Generate a parameter file text used by the SED fitting code.
        
        :returns: the text
        :rtype: :python:`str`
        '''
        
        # %INPUTCATALOGUEINFORMATION% is replaced when the run method is launched
        
        text = f'''\
        ##############################################################################
        #                CREATION OF LIBRARIES FROM SEDs List                        #
        # $LEPHAREDIR/source/sedtolib -t (S/Q/G) -c $LEPHAREDIR/config/zphot.para    #
        # help : $LEPHAREDIR/source/sedtolib -h (or -help)                           #
        ##############################################################################
        #
        #------      STELLAR LIBRARY (ASCII SEDs)
        #
        STAR_SED \t{self.prop['STAR_SED']} \t# STAR list (full path)
        STAR_FSCALE\t{self.prop['STAR_FSCALE']} \t# Arbitrary Flux Scale
        STAR_LIB \t{self.prop['STAR_LIB']} \t# Bin. STAR LIBRARY -> $LEPHAREWORK/lib_bin
        #
        #------      QSO LIBRARY (ASCII SEDs)
        #
        QSO_SED \t{self.prop['QSO_SED']} \t# QSO list (full path)
        QSO_FSCALE \t{self.prop['QSO_FSCALE']} \t# Arbitrary Flux Scale 
        QSO_LIB	\t{self.prop['QSO_LIB']} \t# Bin. QSO LIBRARY -> $LEPHAREWORK/lib_bin
        #
        #------      GALAXY LIBRARY (ASCII or BINARY SEDs)
        #
        GAL_SED	\t{self.prop['GAL_SED']} \t# GAL list (full path)
        GAL_FSCALE \t{self.prop['GAL_FSCALE']} \t# Arbitrary Flux Scale
        GAL_LIB	\t{self.prop['GAL_LIB']} \t# Bin. GAL LIBRARY -> $LEPHAREWORK/lib_bin
        SEL_AGE \t{self.prop['SEL_AGE']} \t# Age list(full path, def=NONE)	
        AGE_RANGE \t{self.prop['AGE_RANGE']} \t# Age Min-Max in yr
        #
        #############################################################################
        #                           FILTERS                                         #
        #  $LEPHAREDIR/source/filter  -c $LEPHAREDIR/config/zphot.para              #
        #  help: $LEPHAREDIR/source/filter  -h (or -help)                           #
        #############################################################################
        #
        FILTER_LIST \t{self.prop['FILTER_LIST']} \t# (in $LEPHAREDIR/filt/*)
        TRANS_TYPE \t\t{self.prop['TRANS_TYPE']} \t# TRANSMISSION TYPE
        FILTER_CALIB \t{self.prop['FILTER_CALIB']} \t# 0[-def]: fnu=ctt, 1: nu.fnu=ctt, 2: fnu=nu, 3: fnu=Black Body @ T=10000K, 4: for MIPS (leff with nu fnu=ctt and flux with BB @ 10000K
        FILTER_FILE \t{self.prop['FILTER_FILE']} \t# output name of filter's file -> $LEPHAREWORK/filt/
        #
        ############################################################################
        #                 THEORETICAL  MAGNITUDES                                  #
        # $LEPHAREDIR/source/mag_star -c  $LEPHAREDIR/config/zphot.para (star only)#
        # help: $LEPHAREDIR/source/mag_star -h (or -help)                          #
        # $LEPHAREDIR/source/mag_gal  -t (Q or G) -c $LEPHAREDIR/config/zphot.para #
        #                                                         (for gal. & QSO) #
        # help: $LEPHAREDIR/source/mag_gal  -h (or -help)                          #
        ############################################################################
        #
        #-------     From STELLAR LIBRARY
        #
        STAR_LIB_IN \t{self.prop['STAR_LIB_IN']} \t# Input STELLAR LIBRARY in $LEPHAREWORK/lib_bin/
        STAR_LIB_OUT \t{self.prop['STAR_LIB_OUT']} \t# Output STELLAR MAGN -> $LEPHAREWORK/lib_mag/
        #
        #-------     From QSO     LIBRARY   
        #
        QSO_LIB_IN \t\t{self.prop['QSO_LIB_IN']} \t# Input QSO LIBRARY in $LEPHAREWORK/lib_bin/
        QSO_LIB_OUT \t{self.prop['QSO_LIB_OUT']} \t# Output QSO MAGN -> $LEPHAREWORK/lib_mag/
        #
        #-------     From GALAXY  LIBRARY  
        #
        GAL_LIB_IN \t\t{self.prop['GAL_LIB_IN']} \t# Input GAL LIBRARY in $LEPHAREWORK/lib_bin/
        GAL_LIB_OUT \t{self.prop['GAL_LIB_OUT']} \t# Output GAL LIBRARY -> $LEPHAREWORK/lib_mag/ 
        #
        #-------   MAG + Z_STEP + EXTINCTION + COSMOLOGY
        #
        MAGTYPE \t{self.prop['MAGTYPE']} \t# Magnitude type (AB or VEGA)
        Z_STEP \t\t{self.prop['Z_STEP']} \t# dz, zmax, dzsup(if zmax>6)
        COSMOLOGY \t{self.prop['COSMOLOGY']} \t# H0,om0,lbd0 (if lb0>0->om0+lbd0=1)
        MOD_EXTINC \t{self.prop['MOD_EXTINC']} \t\t# model range for extinction 
        EXTINC_LAW \t{self.prop['EXTINC_LAW']} \t# ext. law (in $LEPHAREDIR/ext/*)
        EB_V \t\t{self.prop['EB_V']} \t# E(B-V) (<50 values)
        EM_LINES \t{self.prop['EM_LINES']}
        # Z_FORM 	8,7,6,5,4,3 	# Zformation for each SED in GAL_LIB_IN
        #
        #-------   ASCII OUTPUT FILES OPTION
        #
        LIB_ASCII \t{self.prop['LIB_ASCII']} \t# Writes output in ASCII in working directory
        #
        ############################################################################
        #              PHOTOMETRIC REDSHIFTS                                       #
        # $LEPHAREDIR/source/zphot -c $LEPHAREDIR/config/zphot.para                #
        # help: $LEPHAREDIR/source/zphot -h (or -help)                             #
        ############################################################################ 
        #
        %INPUTCATALOGUEINFORMATION%
        CAT_OUT \t{self.id}.out \t
        PARA_OUT \t{self.outputParamFile} \t# Ouput parameter (full path)
        BD_SCALE \t{self.prop['BD_SCALE']} \t# Bands used for scaling (Sum 2^n; n=0->nbd-1, 0[-def]:all bands)
        GLB_CONTEXT\t{self.prop['GLB_CONTEXT']} \t# Overwrite Context (Sum 2^n; n=0->nbd-1, 0 : all bands used, -1[-def]: used context per object)
        # FORB_CONTEXT -1               # context for forbitten bands
        ERR_SCALE \t{self.prop['ERR_SCALE']} \t# errors per band added in quadrature
        ERR_FACTOR \t{self.prop['ERR_FACTOR']} \t# error scaling factor 1.0 [-def]       
        #
        #-------    Theoretical libraries
        #
        ZPHOTLIB \t{self.prop['ZPHOTLIB']} \t# Library used for Chi2 (max:3)
        ADD_EMLINES\t{self.prop['ADD_EMLINES']}
        #
        ########    PHOTOMETRIC REDSHIFTS OPTIONS      ###########
        #
        # FIR LIBRARY
        #
        FIR_LIB \t\t{self.prop['FIR_LIB']}
        FIR_LMIN \t\t{self.prop['FIR_LMIN']} \t# Lambda Min (micron) for FIR analysis 
        FIR_CONT \t\t{self.prop['FIR_CONT']}
        FIR_SCALE \t\t{self.prop['FIR_SCALE']}
        FIR_FREESCALE \t{self.prop['FIR_FREESCALE']} \t# ALLOW FOR FREE SCALING 
        FIR_SUBSTELLAR \t{self.prop['FIR_SUBSTELLAR']}
        #
        # PHYSICAL LIBRARY with Stochastic models from  BC07  
        #
        PHYS_LIB \t\t{self.prop['PHYS_LIB']}  
        PHYS_CONT \t\t{self.prop['PHYS_CONT']}
        PHYS_SCALE \t\t{self.prop['PHYS_SCALE']}
        PHYS_NMAX \t\t{self.prop['PHYS_NMAX']}
        #
        #-------     Priors  
        #
        # MASS_SCALE	0.,0.		# Lg(Scaling) min,max [0,0-def]
        MAG_ABS \t{self.prop['MAG_ABS']} \t# Mabs_min, Mabs_max [0,0-def]
        MAG_REF \t{self.prop['MAG_REF']} \t# Reference number for band used by Mag_abs
        # ZFORM_MIN	5,5,5,5,5,5,3,1	# Min. Zformation per SED -> Age constraint
        Z_RANGE \t{self.prop['Z_RANGE']} \t# Z min-max used for the Galaxy library 
        EBV_RANGE \t{self.prop['EBV_RANGE']} \t# E(B-V) MIN-MAX RANGE of E(B-V) used  
        # NZ_PRIOR      4,2,4           # I Band for prior on N(z)
        #                          
        #-------     Fixed Z   (need format LONG for input Cat)
        #
        ZFIX \t{self.prop['ZFIX']} \t# fixed z and search best model [YES,NO-def]
        #
        #-------     Parabolic interpolation for Zbest  
        #
        Z_INTERP \t{self.prop['Z_INTERP']} \t# redshift interpolation [YES,NO-def]
        #
        #-------  Analysis of normalized ML(exp-(0.5*Chi^2)) curve 
        #-------  Secondary peak analysis       
        #
        DZ_WIN \t\t{self.prop['DZ_WIN']} \t# Window search for 2nd peaks [0->5;0.25-def]
        MIN_THRES \t{self.prop['MIN_THRES']} \t# Lower threshold for 2nd peaks[0->1; 0.1-def]
        #
        #-------  Probability (in %) per redshift intervals
        #
        # PROB_INTZ     0,0.5,0.5,1.,1.,1.5     # even number
        #
        #########    ABSOLUTE MAGNITUDES COMPUTATION   ###########
        #
        MABS_METHOD \t{self.prop['MABS_METHOD']} \t# 0[-def] : obs->Ref, 1 : best  obs->Ref, 2 : fixed obs->Ref, 3 : mag from best SED, 4 : Zbin
        MABS_CONTEXT \t{self.prop['MABS_CONTEXT']} \t# CONTEXT for Band used for MABS 
        MABS_REF \t{self.prop['MABS_REF']} \t# 0[-def]: filter obs chosen for Mabs (ONLY USED IF MABS_METHOD=2)
        MABS_FILT \t{self.prop['MABS_FILT']} \t# Chosen filters per redshift bin (MABS_ZBIN - ONLY USED IF MABS_METHOD=4)
        MABS_ZBIN \t{self.prop['MABS_ZBIN']} \t# Redshift bins (even number - ONLY USED IF MABS_METHOD=4)
        #
        #########   OUTPUT SPECTRA                     ###########
        #
        SPEC_OUT \t{self.prop['SPEC_OUT']} \t\t# spectrum for each object? [YES,NO-def]
        CHI2_OUT \t{self.prop['CHI2_OUT']} \t\t# output file with all values : z,mod,chi2,E(B-V),... BE CAREFUL can take a lot of space !!
        #
        #########  OUTPUT PDZ ANALYSIS  
        #
        PDZ_OUT \t\t{self.prop['PDZ_OUT']} \t# pdz output file name [def-NONE] - add automatically PDZ_OUT[.pdz/.mabsx/.mod/.zph] 
        PDZ_MABS_FILT \t{self.prop['PDZ_MABS_FILT']} \t# MABS for REF FILTERS to be extracted
        # 
        #########   FAST MODE : color-space reduction        #####
        #
        FAST_MODE \t{self.prop['FAST_MODE']} \t# Fast computation [NO-def] 
        COL_NUM	\t{self.prop['COL_NUM']} \t# Number of colors used [3-def]
        COL_SIGMA \t{self.prop['COL_SIGMA']} \t# Enlarge of the obs. color-errors[3-def]
        COL_SEL \t{self.prop['COL_SEL']} \t# Combination between used colors [AND/OR-def]
        #
        #########   MAGNITUDE SHIFTS applied to libraries   ######
        #
        # APPLY_SYSSHIFT  0.             # Apply systematic shifts in each band
                                         # used only if number of shifts matches
                                         # with number of filters in the library    
        #
        #########   ADAPTIVE METHOD using Z spectro sample     ###
        #
        AUTO_ADAPT \t\t{self.prop['AUTO_ADAPT']} \t# Adapting method with spectro [NO-def]
        ADAPT_BAND \t\t{self.prop['ADAPT_BAND']} \t# Reference band, band1, band2 for color 
        ADAPT_LIM \t\t{self.prop['ADAPT_LIM']} \t# Mag limits for spectro in Ref band [18,21.5-def]
        ADAPT_POLY \t\t{self.prop['ADAPT_POLY']} \t# Number of coef in  polynom (max=4) [1-def]
        ADAPT_METH \t\t{self.prop['ADAPT_METH']} \t# Fit as a function of 1 : Color Model  [1-def], 2 : Redshift, 3 : Models
        ADAPT_CONTEXT \t{self.prop['ADAPT_CONTEXT']} \t# Context for bands used for training, -1[-def] used context per object
        ADAPT_ZBIN \t\t{self.prop['ADAPT_ZBIN']} \t# Redshift's interval used for training [0.001,6-Def]
        ADAPT_MODBIN \t{self.prop['ADAPT_MODBIN']} \t# Model's interval used for training [1,1000-Def]
        ERROR_ADAPT \t{self.prop['ERROR_ADAPT']} \t# [YES,NO-def] Add error in quadrature according to the difference between observed and predicted apparent magnitudes 
        #
        '''      
        
        return text
    
    #############################
    #        Run methods        #
    #############################
    
    def runScript(self, commands: List[str], file: str = '', log: TextIOBase = None, errMsg: str = ''):
        r'''
        .. codeauthor:: Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>
        
        Wrapper around default :py:meth:`~.SED.startProcess` which allows to separately provide the commands and the file.
        
        :param commands: list of commands to use with Popen
        :type commands: :python:`list[str]`
        
        :param file: (**Optional**) file to run the process or script against
        :type file: :python:`str`
        :param log: (**Optional**) oppened log file
        :type log: `TextIOBase`_
        :param errMsg: (**Optional**) message error to show if the process failed
        :type errMsg: :python:`str`
        '''
        
        if not isinstance(commands, list):
            raise TypeError(f'commands parameter has type {type(commands)} but it must have type list.')
        print('XXX:', file)
        return self.startProcess(commands + [file], log=log, errMsg=errMsg)
    
    genQSOModel  = partialmethod(runScript, ['$LEPHAREDIR/source/sedtolib', '-t', 'QSO',     '-c'], errMsg='QSO models generation failed.')
    genGalModel  = partialmethod(runScript, ['$LEPHAREDIR/source/sedtolib', '-t', 'Galaxy',  '-c'], errMsg='Galaxy models generation failed.')
    genStarModel = partialmethod(runScript, ['$LEPHAREDIR/source/sedtolib', '-t', 'Stellar', '-c'], errMsg='Stellar models generation failed.')
    genFilters   = partialmethod(runScript, ['$LEPHAREDIR/source/filter', '-c'],                    errMsg='Filters generation failed.')
    genMagQSO    = partialmethod(runScript, ['$LEPHAREDIR/source/mag_gal', '-t', 'Q', '-c'],        errMsg='QSO magnitudes failed.')
    genMagStar   = partialmethod(runScript, ['$LEPHAREDIR/source/mag_star', '-c'],                  errMsg='Stellar magnitudes failed.')
    genMagGal    = partialmethod(runScript, ['$LEPHAREDIR/source/mag_gal', '-t', 'G', '-c'],        errMsg='Galaxy magnitudes failed.')
    startLePhare = partialmethod(runScript, ['$LEPHAREDIR/source/zphota', '-c'],                    errMsg='SED fitting failed.')
    
    def __call__(self, catalogue: LePhareCat, 
                 outputParams: List[str] = [], 
                 skipSEDgen: bool = False, 
                 skipFilterGen: bool = False, 
                 skipMagQSO: bool = False, 
                 skipMagStar: bool = False, 
                 skipMagGal: bool = False, **kwargs) -> LePhareOutput:
        r'''
        .. codeauthor:: Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>
        
        Start the SED fitting on the given data using the built-in SED fitting parameters.
        
        :param LePhareCat catalogue: catalogue to use for the SED-fitting
        
        :param outputParams: (**Optional**) output parameters
        :type outputParams: :python:`list[str]`
        :param skipSEDgen: (**Optional**) whether to skip the SED models generation. Useful to gain time if the same SED are used for multiple sources.
        :type skipSEDgen: :python:`bool`
        :param skipFilterGen: (**Optional**) whether to skip the filters generation. Useful to gain time if the same filters are used for multiple sources.
        :type skipFilterGen: :python:`bool`
        :param skipMagQSO: (**Optional**) whether to skip the predicted magnitude computations for the QS0. Useful to gain time if the same libraries/parameters are used for multiple sources.
        :type skipMagQSO: :python:`bool`
        :param skipMagStar: (**Optional**) whether to skip the predicted magnitude computations for the stars. Useful to gain time if the same libraries/parameters are used for multiple sources.
        :type skipMagStar: :python`bool`
        :param skipMagGal: (**Optional**) whether to skip the predicted magnitude computations for the galaxies. Useful to gain time if the same libraries/parameters are used for multiple sources.
        :type skipMagGal: :python:`bool`

        :returns: LePhare output file object with data from the file loaded
        :rtype: LePhareOutput

        :raises TypeError: if **catalogue** is not of type :py:class:`~.LePhareCat`
        '''
        
        if not isinstance(catalogue, LePhareCat):
            raise TypeError(f'catalogue has type {type(catalogue)} but it must be a LePhareCat instance.')
        
        # Make output directory
        directory = f'{self.id}'
        if not opath.isdir(directory):
            os.mkdir(directory)
            
        # Different SED fitting output file names
        paramFile = catalogue.name.replace('.in', '.para')
        pfile     = opath.join(directory, paramFile)
        logFile   = opath.join(directory, catalogue.name.replace('.in', '_lephare.log'))
        oCatFile  = opath.join(directory, catalogue.name.replace('.in', '.out'))
        
        # Generate and write parameters file
        params    = dedent(self.parameters.replace('%INPUTCATALOGUEINFORMATION%', catalogue.text))
        with open(pfile, 'w') as f:
            f.write(params)
            
        # Write catalogue
        catalogue.save(path=directory)
        
        # Generate and write output parameters file
        oparams   = self.output_parameters(outputParams)
        ofile     = opath.join(directory, self.outputParamFile)
        with open(ofile, 'w') as f:
            f.write(oparams)
        
        with open(logFile, 'a') as log:

            #########################################
            #          Generate SED models          #
            #########################################
            
            # Generate QSO, Star and Galaxy models
            if not skipSEDgen:
                self.genQSOModel( file=pfile, log=log)
                self.genStarModel(file=pfile, log=log)
                self.genGalModel( file=pfile, log=log)
                
            ####################################
            #         Generate filters         #
            ####################################
            
            if not skipFilterGen:
                self.genFilters(file=pfile, log=log)
            
            ##############################################
            #        Compute predicted magnitudes        #
            ##############################################
            
            # QSO magnitudes
            if not skipMagQSO:
                self.genMagQSO(file=pfile, log=log)
                
            # Star magnitudes
            if not skipMagStar:
                self.genMagStar(file=pfile, log=log)
                    
            # Galaxy magnitudes
            if not skipMagGal:
                self.genMagGal(file=pfile, log=log)
            
            ###################################
            #         Run SED fitting         #
            ###################################
            
            # Move to directory
            os.chdir(directory)
            
            self.startLePhare(file=paramFile, log=log)
            
            # Move back to parent directory
            os.chdir('..')
            
        return LePhareOutput(oCatFile) 
 