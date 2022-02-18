#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
.. codeauthor:: Hugo Plombat - LUPM <hugo.plombat@umontpellier.fr> & Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>

Base classes used to generate resolved stellar and SFR maps with LePhare or Cigale SED fitting codes.
"""

import os.path          as     opath
import numpy            as     np
import astropy.io.fits  as     fits
from   astropy.table    import Table
from   copy             import deepcopy
from   functools        import partialmethod

from   numpy            import ndarray
from   typing           import Tuple, List, Union, Any, Optional

from   .misc.enum       import SEDcode, CleanMethod, TableUnit, MagType, TableFormat, TableType
from   .misc.misc       import ShapeError
from   .catalogues      import LePhareCat, CigaleCat, Catalogue
from   .photometry      import countToMag, countToFlux
from   .coloredMessages import warningMessage, errorMessage

import warnings

# Custom colored messages
WARNING = warningMessage('Warning:')
ERROR   = errorMessage('Error:')

class Filter:
    r'''Base class implementing data related to a single filter.'''
    
    def __init__(self, filt: str, file: str, file2: str, errFile: str, zeropoint: float, 
                 ext: int = 0, ext2: int = 0, extErr: int = 0) -> None:
        r'''
        .. codeauthor:: Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>
            
        Initialise filter object.

        :param str filt: filter name
        :param str file: data file name. File must exist and be a loadable FITS file.
        :param str file2: file name for the square of data. File must exist and be a loadable FITS file.
        :param str errFile: error file name. File must exist and be a loadable FITS file. Error file is assumed to be the variance map.
        :param float zeropoint: filter AB magnitude zeropoint
        
        :param int ext: (**Optional**) extension in the data FITS file
        :param int ext2: (**Optional**) extension in the data squared FITS file
        :param int extErr: (**Optional**) extension in the error FITS file
        
        :raises TypeError:
            
            * if **filt** is not of type str
            * if **zeropoint** is neither an int nor a float
        '''
        
        if not isinstance(filt, str):
            raise TypeError(f'filt parameter has type {type(filt)} but it must be of type list.')
            
        if not isinstance(zeropoint, (int, float)):
            raise TypeError(f'zeropoint parameter has type {type(zeropoint)} but it must be of type int or float.')
            
        self.filter          = filt
        self.zpt             = zeropoint
        self.fname           = file
        self.fname2          = file2
        self.ename           = errFile
        
        self.hdr,  self.data  = self._loadFits(self.fname,  ext=ext)
        self.hdr2, self.data2 = self._loadFits(self.fname2, ext=ext2)
        self.ehdr, self.var   = self._loadFits(self.ename,  ext=extErr)
        
        if self.data.shape != self.var.shape:
            raise ShapeError(self.data, self.var, msg=f' in filter {self.filter}')
            
        if self.data.shape != self.data2.shape:
            raise ShapeError(self.data, self.data2, msg=f' in filter {self.filter}')
            
        # Check that exposure time is in the header (otherwise Poisson noise cannot be computed)
        try:
            self.texp        = self.hdr['TEXPTIME']
        except KeyError:
            self.texp        = None
            print(f'{WARNING}data header in {filt.filter} does not have TEXPTIME key.')
            
            
    ###############################
    #       Private methods       #
    ###############################
    
    @staticmethod
    def _mask(arr: ndarray, mask: ndarray, *args, **kwargs) -> ndarray:
        r'''
        .. codeauthor:: Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>
        
        Apply the given mask by placing NaN values onto the array.
        
        :param ndarary arr: array to mask
        :param ndarary[bool] mask: mask with boolean values
        
        :returns: array with masked values
        :rtype: ndarray
        '''
        
        # We make a deep copy to be sure we do not modify the input arrays
        arr       = deepcopy(arr)
        arr[mask] = np.nan
        
        return arr
            
    def _checkFile(self, file: str, *args, **kwargs) -> bool:
        r'''
        .. codeauthor:: Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>
            
        Check whether a file exists.
        
        :param str file: file name
        
        :returns: 
            * True if the file exists
            * False otherwise
            
        :raises TypeError: if **file** is not of type str
        '''
        
        if not isinstance(file, str):
            raise TypeError(f'file has type {type(file)} but it must have type str.')
        
        if not opath.isfile(file):
            print(f'{ERROR} file {file} not found.')
            return False
        return True
    
    def _loadFits(self, file: str, ext: int = 0, **kwargs) -> Tuple[Any]:
        r'''
        .. codeauthor:: Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>
        
        Load data and header from a FITS file at the given extension.

        :param str file: file name
        :param int ext: (**Optional**) extension to load data from

        :returns: 
            * None, None if the file cannot be loaded as a FITS file or if the hdu extension is too large
            * header, data
        :rtype: astropy Header, ndarray
        
        :raises TypeError: if **ext** is not an int
        :raises ValueError: if **ext** is negative
        '''
        
        if not isinstance(ext, int):
            raise TypeError(f'ext has type {type(ext)} but it must have type int.')
        elif ext < 0:
            raise ValueError(f'ext has value {ext} but it must be larger than or equal to 0.')
        
        if self._checkFile(file):
            try:
                with fits.open(file) as hdul:
                    hdu = hdul[ext]
                    return hdu.header, hdu.data
                    
            # If an error is triggered, we always return None, None
            except OSError:
                print(f'{ERROR} file file could not be loaded as a FITS file.')
            except IndexError:
                print(f'{ERROR} extension number {ext} too large.')
                
        return None, None


class FilterList:
    r'''Base class implementing the object used to stored SED fitting into.'''
    
    def __init__(self, filters: List[Filter], mask: ndarray,
                 code: SEDcode = SEDcode.LEPHARE, redshift: Union[int, float] = 0, **kwargs) -> None:
        r'''
        .. codeauthor:: Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>
            
        Initialise filter list object.

        :param list[Filter] filters: filters used to perform the SED fitting
        :param ndarray[bool] mask: mask for bad pixels (True for bad pixels, False for good ones)
        
        :param SEDcode code: (**Optional**) code used to perform the SED fitting. Either SEDcode.LEPHARE or SEDcode.CIGALE or accepted.
        :param redshift: (**Optional**) redshift of the galaxy
        :type redshift: int or float
        
        :param **kwargs: additional parameters to pass to :py:method:`setCode` and :py:method:`genTable`
        
        :raises TypeError: 
            * if **filters** is not a list
            * if **redshift** is neither an int nor a float
            * if one of the filters is not of type Filter
        '''
            
        if not isinstance(redshift, (int, float)):
            raise TypeError(f'redshift parameter has type {type(redshift)} but it must be of type int or float.')
            
        if not isinstance(filters, list):
            raise TypeError(f'filters parameter has type {type(filters)} but they must be of type list.')
        
        # :Redshift of the galaxy
        self.redshift = redshift
        
        # :Define a mask which hides pixels
        self.mask     = mask
        
        # :Table used by SED fitting code (default is None)
        self.table    = None
        
        #: Mean map used when building the table (default is None, updated each time meanMap method is called)
        self.meanMap  = None
        
        #: Scale factor used to normalise the data and error maps (default is None, updated each time genTable method is called)
        self.scaleFac = None
        
        #: Filter list
        self.filters  = []
        self.filters  = self._buildFilters(filters)
                    
        # Check that data in all filters have the same shape
        self._checkFilters(msg=' in filter list')
                    
        #: Data shape for easy access
        self.shape    = self.filters[0].data.shape
                    
        # Set SED fitting code. This rebuilds the table since SED fitting codes do not expect tables with the same columns
        self.setCode(code, **kwargs)
       
        
    ###############################
    #       Private methods       #
    ###############################
    
    def _buildFilters(self, filters: List[Filter]) -> list:
        r'''
        .. codeauthor:: Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>
        
        :param list[Filter] filters: list of Filter objects
        
        :returns: list of checked Filter objects
        :rtype: List[Filter]
        
        :raises TypeError: if one of the filters is not of type Filter
        '''
        
        out = []
        for filt in filters:
            
            if filt.filter in [i.filter for i in self.filters]:
                print(f'{WARNING} filter {filt.filter} already present in filter list.')
                print(errorMessage(f'Skipping filter {filt.filter}...'))
            else:
                
                if not isinstance(filt, Filter):
                    raise TypeError(f'One of the filters has type {type(filt)} but it must have type Filter.')
                
                elif np.any([i is None for i in [filt.data, filt.var, filt.hdr, filt.ehdr]]):
                    print(errorMessage(f'Skipping filter {filt.filter}...'))
                else:
                    out.append(filt)
                    
        return out
    
    def _checkFilters(self, msg: str = '', **kwargs) -> None:
        r'''
        .. codeauthor:: Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>
        
        :param str msg: (**Optional**) message to append to the error message
        
        :raises ShapeError: if at least one filter has a different shape
        '''
        
        if len(self.filters) > 0:
            for f in self.filters[1:]:
                if f.data.shape != self.filters[0].data.shape:
                    raise ShapeError(f.data, self.filters[0], msg=' in filter list')
        
        return
        
        
    ################################
    #       Calogue creation       #
    ################################
    
    def toCatalogue(self, fname: str, *args, **kwargs) -> Catalogue:
        r'''
        .. codeauthor:: Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>
        
        Construct a Catalogue instance given the table associated to the filter list and the given SED fitting code.
        
        .. note::
            
            This function should always be used instead of :py:meth:`_toLePhareCat` or :py:meth:`_toCigaleCat` private methods as it automatically builds the correct catalogue object.
            
            See their definition to know which parameters to pass.
        
        :param str fname: name of the output file containing the catalogue when it is saved
        
        :param *args: (**Optional**) arguments to pass to the private method building the catalogue
        :param **kwargs: (**Optional**) keyword aguments to pass to the private method building the catalogue
        
        :raises ValueError: if code is not recognised
        '''
        
        if self.code is SEDcode.LEPHARE:        
            return self._toLePhareCat(fname, *args, **kwargs)
        elif self.code is SEDcode.CIGALE:
            return self._toCigaleCat(fname, *args, **kwargs)
        else:
            raise ValueError(f'Code {self.code} not recognised.')
            
    def _toCigaleCat(self, fname: str) -> CigaleCat: # XXX to be completed
        r'''
        .. codeauthor:: Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>
        
        Construct a :class:`catalogues.CigaleCat` instance given the table associated to the filter list.
        
        :param str fname: name of the output file containing the catalogue when it is saved
        '''
        
        if self.code is not SEDcode.CIGALE:
            raise ValueError(f'code is {self.code} but it needs to be SEDcode.CIGALE to build a Cigale catalogue object.')
        
        return CigaleCat(fname, self.table)
    
    def _toLePhareCat(self, fname: str,
                     tunit: TableUnit     = TableUnit.MAG, 
                     magtype: MagType     = MagType.AB, 
                     tformat: TableFormat = TableFormat.MEME, 
                     ttype: TableType     = TableType.LONG, **kwargs) -> LePhareCat:
        r'''
        .. codeauthor:: Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>
        
        Construct a LePhareCat instance given the table associated to the filter list.
        
        :param str fname: name of the output file containing the catalogue when it is saved
        
        :param TableUnit tunit: (**Optional**) unit of the table data. Must either be TableUnit.MAG for magnitude or TableUnit.FLUX for flux.
        :param MagType magtype: (**Optional**) magnitude type if data are in magnitude unit. Must either be MagType.AB or MagType.VEGA.
        :param TableFormat tformat: (**Optional**) format of the table. Must either be TableFormat.MEME if data and error columns are intertwined or TableFormat.MMEE if columns are first data and then errors.
        :param TableType ttype: (**Optional**) data type. Must either be TableType.SHORT or TableType.LONG.
        
        :returns: LePhare catalogue object
        :rtype: LePhareCat
        '''
        
        if self.code is not SEDcode.LEPHARE:
            raise ValueError(f'code is {self.code} but it needs to be SEDcode.LEPHARE to build a LePhare catalogue object.')
        
        return LePhareCat(fname, self.table, tunit=tunit, magtype=magtype, tformat=tformat, ttype=ttype)
        
     
    ################################
    #        Table creation        #
    ################################
    
    def _LePhareTableFactory(self, cleanMethod: CleanMethod = CleanMethod.ZERO, scaleFactor: Union[int, float] = 100, texpFac : int = 0, **kwargs) -> Tuple[list]:
        r'''
         .. codeauthor:: Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>
         
         Factory function used to build a data table for LePhare SED fitting code.
         
         :param CleanMethod cleanMethod: (**Optional**) method used to clean pixel with negative values. Accepted values are CleanMethod.ZERO or CleanMethod.MIN.
         :param scaleFactor: (**Optional**) factor used to multiply data and std map
         :type scaleFactor: int or float
         :param int texpFac: (**Optional**) exposure factor used to divide the exposure time when computing Poisson noise. A value of 0 means no Poisson noise is added to the variance map.
         
         :returns: columns, column names and column types
         :rtype: list[int/float/str], list[str], list[data type]
         '''
         
        # Compute mean map to scale data
        meanMap, _                 = self.computeMeanMap(maskVal=0)
        
        dataList                   = []
        stdList                    = []
        for pos, filt in enumerate(self.filters):
                  
            # Clean and add noise to variance map
            data, var              = self.cleanAndNoise(filt.data, filt.data2, filt.var, self.mask, cleanMethod=cleanMethod, texp=filt.texp, texpFac=texpFac)
           
            # Scale data to have compatible values with LePhare for the flux
            data, var              = self.scale(data, var, meanMap, factor=scaleFactor)
            
            # Go to 1D version
            if pos==0:
                data, var, indices = self.arrayTo1D(data, var, indices=True)
            else:
                data, var          = self.arrayTo1D(data, var, indices=False)
                
            # 0 values are cast to NaN otherwise corresponding magnitude would be infinite
            mask0                  = (np.asarray(data == 0) | np.asarray(var == 0))
            data[mask0]            = np.nan
            var[ mask0]            = np.nan
            
            # Compute std instead of variance and go to mag
            data, std              = countToMag(data, np.sqrt(var), filt.zpt)
            
            # Cast back pixels with NaN values to -99 mag to specify they are not to be used in the SED fitting
            data[mask0]            = -99
            std[ mask0]            = -99
            
            # Append data and std to list
            dataList.append(data)
            stdList.append( std)
            
        # Redshift column
        lf                         = len(self.filters)
        ld                         = len(data)
        zs                         = [self.redshift]*ld
        
        # Compute context (number of filters used - see LePhare documentation) and redshift columns
        context                    = [2**lf - 1]*ld
        dtypes                     = [int]     + [float]*2*lf                                                       + [int, float]
        colnames                   = ['ID']    + [val for f in self.filters for val in [f.filter, f'e_{f.filter}']] + ['Context', 'zs']
        columns                    = [indices] + [val for d, s in zip(dataList, stdList) for val in [d, s]]         + [ context, zs]
        
        return columns, colnames, dtypes
    
        
    def _CigaleTableFactory(self, cleanMethod: CleanMethod = CleanMethod.ZERO, texpFac : int = 0, **kwargs) -> Tuple[list]:
        r'''
        .. codeauthor:: Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>
        
        Factory function used to build a data table for Cigale SED fitting code.
        
        :param CleanMethod cleanMethod: (**Optional**) method used to clean pixel with negative values. Accepted values are CleanMethod.ZERO or CleanMethod.MIN.
        :param int texpFac: (**Optional**) exposure factor used to divide the exposure time when computing Poisson noise. A value of 0 means no Poisson noise is added to the variance map.
        
        :returns: columns, column names and column types
        :rtype: list[int/float/str], list[str], list[data type]
        '''
       
        dataList                   = []
        stdList                    = []
        for pos, filt in enumerate(self.filters):

            # Clean and add noise to variance map
            data, var              = self.cleanAndNoise(filt.data, filt.data2, filt.var, self.mask, cleanMethod=cleanMethod, texp=filt.texp, texpFac=texpFac)
            
            # Go to 1D version
            if pos==0:
                data, var, indices = self.arrayTo1D(data, var, indices=True)
            else:
                data, var          = self.arrayTo1D(data, var, indices=False)
        
            # Compute std and convert std and data to mJy unit
            data, std              = [i.to('mJy').value for i in countToFlux(data, np.sqrt(var), filt.zpt)]
            
            # Append data and std to list
            dataList.append(data)
            stdList.append( std)
            
        # Redshift column
        ll                         = len(self.filters)
        ld                         = len(data)
        zs                         = [self.redshift]*ld
        
        dtypes                     = [int, float]       + [float]*2*ll
        colnames                   = ['id', 'redshift'] + [val for f in self.filters for val in [f.filter, f'{f.filter}_err']]
        columns                    = [indices, zs]      + [val for d, s in zip(dataList, stdList) for val in [d, s]]
        
        return columns, colnames, dtypes
        
    
    def genTable(self, cleanMethod: CleanMethod = CleanMethod.ZERO, scaleFactor: Union[int, float] = 100, texpFac : int = 0, **kwargs) -> Table:
        r'''
        .. codeauthor:: Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>
        
        Generate an input table for the SED fitting codes.
        
        :param CleanMethod cleanMethod: (**Optional**) method used to clean pixel with negative values. Accepted values are CleanMethod.ZERO or CleanMethod.MIN.
        :param scaleFactor: (**Optional**) factor used to multiply data and std map. Only used if SED fitting code is LePhare.
        :type scaleFactor: int or float
        :param int texpFac: (**Optional**) exposure factor used to divide the exposure time when computing Poisson noise. A value of 0 means no Poisson noise is added to the variance map.
        
        :returns: output table
        :rtype: Astropy Table
        
        :raises ValueError: if there are no filters in the filter list
        '''
        
        if len(self.filters) < 1:
            raise ValueError('At least one filter must be in the filter list to build a table.')

        if self.code is SEDcode.LEPHARE:
            col, names, dtypes = self._LePhareTableFactory(cleanMethod=cleanMethod, scaleFactor=scaleFactor, texpFac=texpFac)
        elif self.code is SEDcode.CIGALE:
            col, names, dtypes = self._CigaleTableFactory(cleanMethod=cleanMethod, texpFac=texpFac)
            
        # Generate the output Table
        self.table             = Table(col, names=names, dtype=dtypes)
        
        return self.table
     
        
    #############################
    #       Data handling       #
    #############################
    
    @staticmethod
    def arrayTo1D(data: ndarray, var: ndarray, indices: bool = False):
        '''
        Convert data and variance maps into 1D vectors and remove nan values.
        
        .. note::
            
            Provide indices = True to get the indices of the non-NaN pixels in the 1D array (brefore NaN are removed).
            
        :param ndarray data: data map
        :param ndarray var: variance map
        
        :param bool indices: (**Optional**) whether to return the list of indices of non-NaN values or not
        
        :returns: 1D data, 1D variance (and the indices if **indices** is True)
        
        :raises TypeError:
            
            * if **data** or **var** are not ndarray
            * if **indices** is not a bool
        '''
        
        if not any((isinstance(i, ndarray) for i in [data, var])):
            raise TypeError('either data or variance maps is not a ndarray.')
            
        if not isinstance(indices, bool):
            raise TypeError(f'indices parameter has type {type(indices)} but it must of type bool.')
        
        # Avoid to overwrite original arrays
        data    = deepcopy(data)
        var     = deepcopy(var)
        
        shp     = data.shape        
        
        # Transform data and error maps into 1D vectors
        data    = data.reshape(shp[0]*shp[1])
        var     = var.reshape( shp[0]*shp[1])
        
        # Get rid of NaN values
        nanMask = ~(np.isnan(data) | np.isnan(var))
        data    = data[nanMask]
        var     = var[ nanMask]
        
        if indices:
            return data, var, np.where(nanMask)[0]
        else:
            return data, var
    
    @staticmethod
    def clean(data: ndarray, var: ndarray, mask: ndarray, method: CleanMethod = CleanMethod.ZERO, **kwargs) -> Tuple[ndarray]:
        r'''
        .. codeauthor:: Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>
        
        Clean given data and error maps by masking pixels and dealing with negative values.
        
        .. note::
                
            * If **method** is CleanMethod.ZERO, negative values in the data and error maps are set to 0
            * If **method** is CleanMethod.MIN, negative values in the data and error maps are set to the minimum value in the array
            * If **method** is neither, 'zero' is used as default
            
        :param ndarray data: data map
        :param ndarray var: variance map
        :param ndarray[bool] mask: mask used to apply NaN values
        
        :param CleanMethod method: (**Optional**) method to deal with negative values
        
        :returns: cleaned data and variance maps
        :rtype: ndarray, ndarray
        '''
        
        if not isinstance(method, CleanMethod):
            raise TypeError(f'method parameter has type {type(method)} but it must have type CleanMethod.')
        
        # Deep copies to avoid to overwrite input arrays
        data              = deepcopy(data)
        var               = deepcopy(var)
        
        # Apply mask
        data[mask]        = np.nan
        var[ mask]        = np.nan
        
        # Mask pixels having negative values
        negMask           = (data < 0) | (var < 0)
        if method is CleanMethod.ZERO:
            data[negMask] = 0
            var[ negMask] = 0
        elif method == CleanMethod.MIN:
            mini          = np.nanmin(data[~negMask])
            data[negMask] = mini
            var[ negMask] = mini
            
        return data, var
    
    def cleanAndNoise(self, data, data2, var, mask, 
                      cleanMethod: CleanMethod = CleanMethod.ZERO, 
                      texp: Optional[Union[int, float]] = None, 
                      texpFac: int = 0, **kwargs) -> Tuple[ndarray]:
        r'''
        .. codeauthor:: Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>
        
        Clean data and variance maps from bad pixels and add Poisson noise to the variance map.
        
        .. note::
            
            If **texpFac** is 0 or **texp** is None, no Poisson noise is added to the variance map
            
        :param ndarray data: data map
        :param ndarray data2: square of data map used to add Poisson noise
        :param ndarray var: variance map
        :param ndarray[bool] mask: mask map
        
        :param CleanMethod cleanMethod: (**Optional**) method used for the cleaning process
        :param texp: (**Optional**) exposition time
        :type texp: int or float
        :param int texpFac: (**Optional**) factor used to divide the exposition time
        
        :returns: cleaned data and cleaned variance map with Poisson noise added
        :rtype: ndarray, ndarray
        '''
        
        # Clean data and error maps of bad pixels and pixels with negative values
        data, var = self.clean(data, var, mask, method=cleanMethod)
            
        # Add Poisson noise to the variance map
        if texp is not None:
            var  += self.poissonVar(data2, texp=texp, texpFac=texpFac)
        
        return data, var
    
    def computeMeanMap(self, maskVal: Union[int, float] = 0, **kwargs) -> Tuple[ndarray]:
        r'''
        .. codeauthor:: Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>
        
        Compute the averaged data and error maps over the spectral dimension for non masked pixels.
        
        :param maskVal: (**Optional**) value to put into masked pixels
        :type maskVal: int or float
        
        :returns: averaged data and averaged error map
        :rtype: ndarray, ndarray
        
        :raises TypeError: if **maskVal** is neither int nor float
        '''
        
        if not isinstance(maskVal, (int, float)):
            raise TypeError(f'maskVal parameter has type {type(maskVal)} but it must have type int or float.')
            
        # Compute masked arrays
        data      = [f._mask(f.data, self.mask) for f in self.filters]
        err       = [f._mask(f.var,  self.mask) for f in self.filters]
        
        # Compute mean value along spectral dimension
        with warnings.catch_warnings():
            warnings.filterwarnings('ignore', 'Mean of empty slice')
            data  = np.nanmean(data, axis=0)
            err   = np.nanmean(err,  axis=0)
            
        # Replace NaN values
        np.nan_to_num(data, copy=False, nan=maskVal)
        np.nan_to_num(err,  copy=False, nan=maskVal)
        
        # Store mean data map for easy access
        self.meanMap = data
        
        return data, err
    
    @staticmethod
    def poissonVar(data2: ndarray, texp: Union[int, float] = 1, texpFac: Union[int, float] = 1, **kwargs) -> ndarray:
        r'''
        .. codeauthor:: Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>
        
        Compute a scaled Poisson variance term from a given flux map. The variance :math:`(\Delta F)^2` is computed as
        
        .. math::
            
            (\Delta F)^2 = | \alpha F |
        
        
        where :math:`F` is the square of the flux map and :math:`\alpha` is a scale factor defined as
        
        .. math::
                
            \alpha = {\rm{TEXP / TEXPFAC}}
        
        
        where :math:`\rm{TEXP}` is the exposure time and :math:`\rm{TEXPFAC}` is a coefficient used to scale it down.
        
        :param ndarray data2: square of flux map
        
        :param texp: (**Optional**) exposure time in seconds
        :type text: int or float
        :param texpFac: (**Optional**) exposure factor
        :type texpFac: int or float
        
        :raises TypeError: if **texp** or **texpFac** are not both int or float
        :raises ValueError:
            
            * if **texp** is less than or equal to 0
            * if **texpFac** is less than 0
        '''
        
        if not all([isinstance(i, (int, float)) for i in [texp, texpFac]]):
            raise TypeError(f'texp and texpFac parameters have types {type(texp)} and {type(texpFac)} but they must have type int or float.')
            
        if texp <= 0:
            raise ValueError(f'texp has value {texp} but it must be positive.')
            
        if texpFac < 0:
            raise ValueError(f'texpFac has value {texpFac} but it must be positive or null.')
        
        return np.abs(data2) * texpFac / texp
    
    def scale(self, data: ndarray, var: ndarray, norm: ndarray, factor: Union[int, float] = 100) -> Tuple[ndarray]:
        r'''
        .. codeauthor:: Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>
        
        Normalise given data and error maps using a norm map and scale by a certain amount. Necessary for LePhare SED fitting code.
        
        :param ndarray data: data map
        :param ndarray var: variance map
        :param ndarray norm: normalisation map which divides data and error maps
        
        :param factor: (**Optional**) scale factor which multiplies the output array
        :type factor: int or float
        
        :returns: scaled data and variance maps
        :rtype: ndarray, ndarray
        
        :raises ValueError: if **data** and **norm** do not have the same shapes
        '''
        
        if norm.shape != data.shape:
            raise ValueError(f'Incompatible norm and data shapes. norm map has shape {norm.shape} but data map has shape {self.data.shape}.')
        
        # Deep copies to avoid to overwrite input arrays
        d             = deepcopy(data)
        v             = deepcopy(var)
        
        mask          = norm != 0
        d[mask]      *= factor/norm[mask]
        v[mask]      *= (factor*factor/(norm[mask]*norm[mask])) # Variance normalisation is squared
        
        # Store scale factor for easy access
        self.scaleFac = factor
        
        return d, v
        
        
    ####################
    #       Misc       #
    ####################    
    
    def setCode(self, code: SEDcode, *args, **kwargs) -> None:
        r'''
        .. codeauthor:: Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>
        
        Set the SED fitting code.
        
        .. warning::
            
            This function also recomputes and rewrites the output table used for the SED fitting.
            If you want a table with different parameters you must run :py:meth:`FilterList.genTable` again, for e.g.
            
            >>> from SED.misc import SEDcode, CleanMethod
            >>> flist = FilterList(filters, mask)          # setCode and genTable methods are called with default SED fitting code name
            >>> flist.setCode(SEDcode.LEPHARE,             # setCode and genTable methods are called with 'lephare' SED fitting code name
                              cleanMethod=CleanMethod.MIN, # Additional parameters are passed to genTable
                              scaleFactor=50)                             
        
        :param SEDcode code: code used for SED fitting. Acceptable values are SEDcode.CIGALE and SEDcode.LEPHARE.
        
        :raises TypeError: if **code** is not of type str
        '''
        
        if not isinstance(code, SEDcode):
            raise TypeError(f'code parameter has type {type(code)} but it must be of type SEDcode.')
        
        self.code = code
            
        # Update output table with default parameters
        self.genTable(*args, **kwargs)
        return
    
    
    #############################
    #      Partial methods      #
    #############################
    
    #: Set Cigale as fitting code
    setCigale  = partialmethod(setCode, SEDcode.CIGALE)
    
    #: Set LePhare as fitting code
    setLePhare = partialmethod(setCode, SEDcode.LEPHARE)