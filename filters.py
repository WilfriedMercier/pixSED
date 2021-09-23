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
from   typing           import Tuple, List, Union, Any

from   .misc            import SEDcode, CleanMethod, TableUnit
from   .catalogues      import LePhareCat, Catalogue
from   .photometry      import countToMag, countToFlux
from   .coloredMessages import warningMessage, errorMessage

import warnings

# Custom colored messages
WARNING = warningMessage('Warning: ')
ERROR   = errorMessage('Error: ')

class Filter:
    r'''Base class implementing data related to a single filter.'''
    
    def __init__(self, filt: str, file: str, errFile: str, zeropoint: float, ext: int = 0, extErr: int = 0) -> None:
        r'''
        .. codeauthor:: Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>
            
        Initialise filter object.

        :param str filt: filter name
        :param str file: data file name. File must exist and be a loadable FITS file.
        :param str errFile: error file name. File must exist and be a loadable FITS file. Error file is assumed to be the variance map.
        :param float zeropoint: filter AB magnitude zeropoint
        
        :param int ext: (**Optional**) extension in the data FITS file
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
        self.ename           = errFile
        
        self.hdr,  self.data = self._loadFits(self.fname, ext=ext)
        self.ehdr, self.var  = self._loadFits(self.ename, ext=extErr)
        
        if self.data.shape != self.var.shape:
            raise ShapeError(self.data, self.var, msg=f' in filter {self.filter}')
            
            
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
            print(ERROR + 'file ' + brightMessage(file) + ' not found.')
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
                print(ERROR + ' file ' + brightMessage(file) + ' could not be loaded as a FITS file.')
            except IndexError:
                print(ERROR + f' extension number {ext} too large.')
                
        return None, None


class FilterList:
    r'''Base class implementing the object used to stored SED fitting into.'''
    
    def __init__(self, filters: List[Filter], mask: ndarray, code: SEDcode = SEDcode.LEPHARE, redshift: Union[int, float] = 0, **kwargs) -> None:
        r'''
        .. codeauthor:: Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>
            
        Initialise filter list object.

        :param list[Filter] filters: filters used to perform the SED fitting
        :param ndarray[bool] mask: mask for bad pixels (True for bad pixels, False for good ones)
        
        :param SEDcode code: (**Optional**) code used to perform the SED fitting. Either SEDcode.LEPHARE or SEDcode.CIGALE or accepted.
        :param redshift: (**Optional**) redshift of the galaxy
        :type redshift: int or float
        
        :raises TypeError: 
            * if **filters** is not a list
            * if **redshift** is neither an int nor a float
            * if one of the filters is not of type Filter
        '''
        
        ##############################
        #      Check parameters      #
        ##############################
            
        if not isinstance(redshift, (int, float)):
            raise TypeError(f'redshift parameter has type {type(redshift)} but it must be of type int or float.')
            
        if not isinstance(filters, list):
            raise TypeError(f'filters parameter has type {type(filters)} but they must be of type list.')
        
        ###################################
        #         Init attributes         #
        ###################################
        
        # :Redshift of the galaxy
        self.redshift = redshift
        
        # :Define a mask which hides pixels
        self.mask     = mask
        
        # :Table used by SED fitting code (default is None)
        self.table    = None
        
        #########################################
        #           Build filter list           #
        #########################################
        
        self.filters = []
        for filt in filters:
            
            if filt in [i.filter for i in self.filters]:
                print(WARNING + 'filter ' +  brightMessage(filt.filter) +  ' already present in filter list.')
                print(errorMessage(f'Skipping filter {filt.filter}...'))
            else:
                
                if not isinstance(filt, Filter):
                    raise TypeError(f'One of the filters has type {type(filt)} but it must have type Filter.')
                
                elif np.any([i is None for i in [filt.data, filt.var, filt.hdr, filt.ehdr]]):
                    print(errorMessage(f'Skipping filter {filt.filter}...'))
                else:
                    self.filters.append(filt)
                    
        # Check that data in all filters have the same shape
        if len(self.filters) > 0:
            for f in self.filters[1:]:
                if f.data.shape != self.filters[0].data.shape:
                    raise ShapeError(f.data, self.filters[0], msg=' in filter list')
                    
        # Set SED fitting code. This rebuilds the table since SED fitting codes do not expect tables with the same columns
        self.setCode(code)
        
        
    ############################################
    #       Table and catalogue creation       #
    ############################################
    
    def toCatalogue(self, fname: str, *args, **kwargs) -> Catalogue:
        r'''
        .. codeauthor:: Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>
        
        Construct a Catalogue instance given the table associated to the filter list.
        
        :param str fname: name of the output file containing the catalogue when it is saved
        
        .. seealso:: :py:class:`Catalogue`
        '''
        
        return Catalogue(fname, self.table, *args, **kwargs)
    
    def toLePhareCat(self, fname: str, 
                     tunit: TableUnit = TableUnit.MAG, 
                     magtype: str = 'AB', 
                     tformat: str = 'MEME', 
                     ttype: str = 'LONG', **kwargs) -> LePhareCat:
        r'''
        .. codeauthor:: Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>
        
        Construct a Catalogue instance given the table associated to the filter list.
        
        :param str fname: name of the output file containing the catalogue when it is saved
        
        .. seealso:: :py:class:`LePhareCat`
        '''
        
        if self.code is not SEDcode.LEPHARE:
            raise ValueError(f'code is {self.code} but it needs to be SED.SEDcode to build a LePhare catalogue object.')
        
        return LePhareCat(fname, self.table, tunit=tunit, magtype=magtype, tformat=tformat, ttype=ttype)
        
    
    def toTable(self, cleanMethod: CleanMethod = CleanMethod.ZERO, scaleFactor: int = 100, texpFac : int = 0, **kwargs) -> Table:
        r'''
        .. codeauthor:: Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>
        
        Generate an input table for the SED fitting codes.
        
        :param CleanMethod cleanMethod: (**Optional**) method used to clean pixel with negative values. Accepted values are CleanMethod.ZERO or CleanMethod.MIN.
        :param scaleFactor: (**Optional**) factor used to multiply data and std map. Only used if SED fitting code is LePhare.
        :type scaleFactor: int or float
        :param int texpFactor: (**Optional**) exposure factor used to divide the exposure time when computing Poisson noise. A value of 0 means no Poisson noise is added to the variance map.
        
        :returns: output table
        :rtype: Astropy Table
        
        :raises ValueError: if there are no filters in the filter list
        '''
        
        if len(self.filters) < 1:
            raise ValueError('At least one filter must be in the filter list to build a table.')
        
        # Mean map (NaN values are set to 0 once the mean map is computed)
        if self.code is SEDcode.LEPHARE:
            meanMap, _      = self.meanMap(maskVal=0)

        dataList            = []
        stdList             = []
        for filt in self.filters:
            
            # Clean data and error maps of bad pixels and pixels with negative values
            data, var       = self.clean(filt.data, filt.var, self.mask, method=cleanMethod)
            shp             = data.shape
            
            #print(np.where(data<0))
        
            # Add Poisson noise to the variance map
            try:
                texp        = filt.hdr['TEXPTIME']
            except KeyError:
                print(ERROR + f'data header in {filt.filter} does not have TEXPTIME key. Cannot compute poisson variance.')
            else:
                var         = self.poissonVar(data, texp=texp, texpFac=texpFac)
    
            # Scaling data for LePhare
            if self.code is SEDcode.LEPHARE:
                data, var   = self.scale(data, var, meanMap, factor=scaleFactor)
            
            # Transform data and error maps into 1D vectors
            data            = data.reshape(shp[0]*shp[1])
            var             = var.reshape( shp[0]*shp[1])
            
            # Get rid of NaN values
            nanMask         = ~(np.isnan(data) | np.isnan(var))
            data            = data[nanMask]
            var             = var[ nanMask]
            
            # Convert flux and variance to AB mag for LePhare
            if self.code is SEDcode.LEPHARE:
                
                # 0 values are cast to NaN otherwise corresponding magnitude would be infinite
                mask0       = (np.asarray(data == 0) | np.asarray(var == 0))
                data[mask0] = np.nan
                var[ mask0] = np.nan
                
                # Compute std instead of variance
                data, std   = countToMag(data, np.sqrt(var), filt.zpt)
                
                # Cast back pixels with NaN values to -99 mag to specify they are not to be used in the SED fitting
                data[mask0] = -99
                std[ mask0] = -99
                
            # Convert to mJy for Cigale
            elif self.code is SEDcode.CIGALE:
                
                # Compute std and convert std and data to mJy unit
                data, std   = [i.to('mJy').value for i in countToFlux(data, np.sqrt(var), filt.zpt)]
            
            # Append data and std to list
            dataList.append(data)
            stdList.append( std)
            
        # Keep track of indices with correct values (identical between filters)
        indices             = np.where(nanMask)[0]
        
        # Consistency check
        ll                  = len(indices)
        if ll != len(dataList[0]) or ll != len(stdList[0]):
            raise ValueError(f'indices have length {ll} but dataList and stdList have shapes {np.shape(dataList)} and {np.shape(stdList)}.')
        
        ####################################
        #         Generate columns         #
        ####################################
        
        # Shared between LePhare and Cigale
        zs                  = [self.redshift]*ll
        
        if self.code is SEDcode.LEPHARE:
            
            # Compute context (number of filters used - see LePhare documentation) and redshift columns
            context         = [2**len(self.filters) - 1]*ll
            dtypes          = [int]     + [float]*2*len(self.filters)                                        + [int, float]
            colnames        = ['ID']    + [val for f in self.filters for val in [f.filter, f'e_{f.filter}']] + ['Context', 'zs']
            columns         = [indices] + [val for d, s in zip(dataList, stdList) for val in [d, s]]         + [ context, zs]
        
        elif self.code is SEDcode.CIGALE:
            
            dtypes          = [int, float]       + [float]*len(self.filters)
            colnames        = ['id', 'redshift'] + [val for f in self.filters for val in [f.filter, f'{f.filter}_err']]
            columns         = [indices, zs]      + [val for d, s in zip(dataList, stdList) for val in [d, s]]
        
        # Generate the output Table
        self.table          = Table(columns, names=colnames, dtype=dtypes)
        
        return self.table
     
        
    #############################
    #       Data handling       #
    #############################
    
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
    
    def meanMap(self, maskVal: Union[int, float] = 0, **kwargs) -> Tuple[ndarray]:
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
        data  = [f._mask(f.data, self.mask) for f in self.filters]
        err   = [f._mask(f.var,  self.mask) for f in self.filters]
        
        # Compute mean value along spectral dimension
        with warnings.catch_warnings():
            warnings.filterwarnings('ignore', 'Mean of empty slice')
            data  = np.nanmean(data, axis=0)
            err   = np.nanmean(err,  axis=0)
            
        # Replace NaN values
        np.nan_to_num(data, copy=False, nan=maskVal)
        np.nan_to_num(err,  copy=False, nan=maskVal)
        
        return data, err
    
    @staticmethod
    def poissonVar(data: ndarray, texp: Union[int, float] = 1, texpFac: Union[int, float] = 1, **kwargs) -> ndarray:
        r'''
        .. codeauthor:: Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>
        
        Compute a scaled Poisson variance term from a given flux map. The variance :math:`(\Delta F)^2` is computed as
        
        .. math::
            
            (\Delta F)^2 = | \alpha F |
        
        
        where :math:`F` is the flux map and :math:`\alpha` is a scale factor defined as
        
        .. math::
                
            \alpha = {\rm{TEXP / TEXPFAC}}
        
        
        where :math:`\rm{TEXP}` is the exposure time and :math:`\rm{TEXPFAC}` is a coefficient used to scale it down.
        
        :param ndarray data: flux map
        
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
        
        return np.abs(data) * texpFac / texp
    
    @staticmethod
    def scale(data: ndarray, var: ndarray, norm: ndarray, factor: Union[int, float] = 100) -> Tuple[ndarray]:
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
        d        = deepcopy(data)
        v        = deepcopy(var)
        
        mask     = norm != 0
        d[mask] *= factor/norm[mask]
        v[mask] *= (factor*factor/(norm[mask]*norm[mask])) # Variance normalisation is squared
        
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
            If you want a table with different parameters you must run :py:meth:`FilterList.toTable` again, for e.g.
            
            >>> from SED.misc import SEDcode, CleanMethod
            >>> flist = FilterList(filters, mask)                          # setCode and toTable methods are called with default SED fitting code name
            >>> flist.setCode(SEDcode.LEPHARE)                             # setCode and toTable methods are called with 'lephare' SED fitting code name
            >>> flist.toTable(cleanMethod=CleanMethod.MIN, scaleFactor=50) # toTable is run again with different parameters but still 'lephare' SED fitting code name
        
        :param SEDcode code: code used for SED fitting. Acceptable values are SEDcode.CIGALE and SEDcode.LEPHARE.
        
        :raises TypeError: if **code** is not of type str
        '''
        
        if not isinstance(code, SEDcode):
            raise TypeError(f'code parameter has type {type(code)} but it must be of type SEDcode.')
        
        self.code = code
            
        # Update output table with default parameters
        self.toTable()
        return
    
    
    #############################
    #      Partial methods      #
    #############################
    
    #: Set Cigale as fitting code
    setCigale  = partialmethod(setCode, SEDcode.CIGALE)
    
    #: Set LePhare as fitting code
    setLePhare = partialmethod(setCode, SEDcode.LEPHARE)