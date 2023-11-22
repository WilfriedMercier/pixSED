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
    r'''
    .. codeauthor:: Wilfried Mercier - IRAP/LAM <wilfried.mercier@irap.omp.eu>
    
    Class implementing all data related to a single filter.
    
    .. note::
        
        Data and variance maps can be given in any units, but the **unit of the variance map is expected to be the square of that of the data map**. No unit check is performed using header information.
        
        The code will convert the data map using the **zeropoint** following the expression:
        
        .. math::
            
            d_{\rm{new}} = d_{\rm{original}} \times 10^{-(zpt + 48.6)/2.5}
            
        where :math:`d_{\rm{original}}` is the original data map in any arbitrary unit and :math:`d_{\rm{new}}` is the new data map converted in :math:`\rm erg\,s^{-1}\,Hz^{-1}\,cm^{-2}`. Thus, the **zeropoint** must be chosen so that the conversion is properly done to that unit.
    
        The variance map will be converted by first taking the square root to have the std and then performing the same conversion as above.
        
    .. important::
        
        The code assumes by default that all noise types are included in the variance map. If the Poisson noise is missing, one can provide the **file2** parameter which is the file containing the data map convolved by the square of the PSF. The code will then use that file to compute its own Poisson noise that will be added in quadrature to the given variance map.
    
    :param str filt: filter name. This name must be compatible with the filter names availble in the chosen SED fitting code.
    :type filt: :python:`str`
    :param file: file name of the data flux map. File must exist and be a loadable FITS file.
    :type file: :python:`str`
    :param varFile: file name of the variance flux map. File must exist and be a loadable FITS file.
    :type varFile: :python:`str`
    :param zeropoint: magnitude zeropoint (see note above)
    :type zeropoint: :python:`float`
    
    :param ext: (**Optional**) extension number in the data FITS file
    :type ext: :python:`int`
    :param ext2: (**Optional**) extension number in the data squared FITS file
    :type ext2: :python:`int`
    :param extErr: (**Optional**) extension number in the variance FITS file
    :type extErr: :python:`int`
    :param file2: (**Optional**) file name for the data convolved by the square of the PSF. File must exist and be a loadable FITS file. If :python:`None`, no file is loaded and Poisson noise will not be added to the variance map.
    :type file2: :python:`str`
    :param verbose: (**Optional**) whether to print info messages or not
    :type verbose: :python:`bool`
    
    :raises TypeError:
            
        * if **filt** is not of type :python:`str`
        * if **file** is not of type :python:`str`
        * if **varFile** is not of type :python:`str`
        * if **file2** is not :python:`None` and not of type :python:`str`
        * if **zeropoint** is neither :python:`int` nor :python:`float`
    '''
    
    def __init__(self, filt: str, file: str, varFile: str, zeropoint: float, 
                 ext    : int           = 0, 
                 ext2   : int           = 0, 
                 extErr : int           = 0,
                 file2  : Optional[str] = None,
                 verbose: bool          = True) -> None:
        r'''Init method.'''
        
        if not isinstance(filt, str):
            raise TypeError(f'filt parameter has type {type(filt)} but it must be of type list.')
            
        if not isinstance(file, str):
            raise TypeError(f'file parameter has type {type(file)} but it must be of type str.')
            
        if not isinstance(varFile, str):
            raise TypeError(f'varFile parameter has type {type(varFile)} but it must be of type str.')
            
        if file2 is not None and not isinstance(file2, str):
            raise TypeError(f'file2 parameter has type {type(file2)} but it must be either of type str or None.')
            
        if not isinstance(zeropoint, (int, float)):
            raise TypeError(f'zeropoint parameter has type {type(zeropoint)} but it must be of type int or float.')
            
        if not isinstance(verbose, bool):
            raise TypeError(f'verbose parameter has type {type(verbose)} but it must be of type bool.')
            
        self.verbose              = verbose
        self.filter               = filt
        self.zpt                  = zeropoint
        self.fname                = file
        self.fname2               = file2
        self.ename                = varFile
        
        self.hdr,  self.data      = self._loadFits(self.fname,  ext=ext)
        self.ehdr, self.var       = self._loadFits(self.ename,  ext=extErr)
        
        if self.fname2 is None:
            self.hdr2             = None
            self.data2            = None
            self.texp             = None
        
            if self.verbose: print(f'{WARNING} No data convolved with the square of the PSF was provided. Poisson noise is assumed to be already contained in the variance map.')
        else:
            self.hdr2, self.data2 = self._loadFits(self.fname2, ext=ext2)
        
        if self.data.shape != self.var.shape:
            raise ShapeError(self.data, self.var, msg=f' in filter {self.filter}')
         
        if self.data2 is not None and self.data.shape != self.data2.shape:
            raise ShapeError(self.data, self.data2, msg=f' in filter {self.filter}')
            
        # Check that exposure time is in the header (otherwise Poisson noise cannot be computed)
        if self.fname2 is not None:
            
            try:
                self.texp         = self.hdr['TEXPTIME']
            except KeyError:
                self.texp         = None
                
                if self.verbose: print(f'{WARNING} data header in {self.filter} does not have TEXPTIME key. Poisson noise cannot be computed...')
            
            
    ###############################
    #       Private methods       #
    ###############################
    
    @staticmethod
    def _mask(arr: ndarray, mask: ndarray, *args, **kwargs) -> ndarray:
        r'''
        .. codeauthor:: Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>
        
        Apply the given mask by placing NaN values onto the array.
        
        :param ndarary arr: array to mask
        :type arr: `ndarray`_
        :param ndarary[bool] mask: mask with boolean values
        :type mask: `ndarray`_ [:python:`bool`]
        
        :returns: array with masked values
        :rtype: `ndarray`_
        '''
        
        # We make a deep copy to be sure we do not modify the input arrays
        arr       = deepcopy(arr)
        arr[mask] = np.nan
        
        return arr
            
    def _checkFile(self, file: str, *args, **kwargs) -> bool:
        r'''
        .. codeauthor:: Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>
            
        Check whether a file exists.
        
        :param file: file name
        :type file: :python:`str`
        
        :returns: 
            
            * :python:`True` if **file** exists
            * :python:`False` otherwise
            
        :raises TypeError: if **file** is not of type :python:`str`
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

        :param file: file name
        :type file: :python:`str`
        :param ext: (**Optional**) extension to load data from
        :type ext: :python:`str`

        :returns: 
            * (None, None) if the file cannot be loaded as a FITS file or if the hdu extension is too large
            * (header, data)
            
        :rtype: (`Astropy Header`_, `ndarray`_)
        
        :raises TypeError: if **ext** is not an :python:`int`
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
                print(f'{ERROR} file {file} could not be loaded as a FITS file.')
            except IndexError:
                print(f'{ERROR} extension number {ext} for file {file} too large.')
                
        return None, None


class FilterList:
    r'''
    .. codeauthor:: Wilfried Mercier - IRAP/LAM <wilfried.mercier@irap.omp.eu>
    
    Base class implementing the object used to stored SED fitting into.
    
    :param filters: filters used to perform the SED fitting
    :type filters: :python:`list` [Filter]
    :param mask: mask for bad pixels (:python:`True` for bad pixels, :python:`False` for good ones)
    :type mask: `ndarray`_ [:python:`bool`]
    
    :param SEDcode code: (**Optional**) code used to perform the SED fitting. Either :py:attr:`~.SEDcode.LEPHARE` or :py:attr:`~.SEDcode.CIGALE` are accepted.
    :param redshift: (**Optional**) redshift of the galaxy
    :type redshift: :python:`int` or :python:`float`
    
    :param \**kwargs: additional parameters to pass to :py:meth:`~.FilterList.setCode` and :py:meth:`~.FilterList.genTable`
    
    :raises TypeError:
        
        * if **filters** is not a :python:`list`
        * if **redshift** is neither an :python:`int` nor a :python:`float`
        * if one of the **filters** is not of type :py:class:`~.Filter`
    '''
    
    def __init__(self, filters: List[Filter], mask: ndarray,
                 code    : SEDcode           = SEDcode.CIGALE,
                 redshift: Union[int, float] = 0, 
                 **kwargs) -> None:
        r'''Init method.'''
            
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
        :type filters: :python:`list` [:py:class:`~.Filter`]
        
        :returns: list of checked Filter objects
        :rtype: :python:`list` [:py:class:`~.Filter`]
        
        :raises TypeError: if one of the **filters** is not of type :py:class:`~.Filter`
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
        
        :param msg: (**Optional**) message to append to the error message
        :type msg: :python:`str`
        
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
            
            This function should always be used instead of :py:meth:`~._toLePhareCat` or :py:meth:`~._toCigaleCat` private methods as it automatically builds the correct catalogue object.
            
            See their definition to know which parameters to pass.
        
        :param fname: name of the output file containing the catalogue when it is saved
        :type fname: :python:`str`
        
        :param \*args: (**Optional**) arguments to pass to the private method building the catalogue
        :param \**kwargs: (**Optional**) keyword aguments to pass to the private method building the catalogue
        
        :raises ValueError: if **self.code** is not recognised
        '''
        
        if self.code is SEDcode.LEPHARE:        
            return self._toLePhareCat(fname, *args, **kwargs)
        elif self.code is SEDcode.CIGALE:
            return self._toCigaleCat(fname, *args, **kwargs)
        else:
            raise ValueError(f'Code {self.code} not recognised.')
            
    def _toCigaleCat(self, fname: str) -> CigaleCat:
        r'''
        .. codeauthor:: Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>
        
        Construct a :py:class:`~.CigaleCat` instance given the table associated to the filter list.
        
        :param fname: name of the output file containing the catalogue when it is saved
        :type fname: :python:`str`
        
        :returns: a Cigale catalogue instance
        :rtype: :py:class:`~.CigaleCat`
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
        
        Construct a :py:class:`~.LePhareCat` instance given the table associated to the filter list.
        
        :param fname: name of the output file containing the catalogue when it is saved
        :type fname: :python:`str`
        
        :param TableUnit tunit: (**Optional**) unit of the table data. Must either be :py:attr:`~.TableUnit.MAG` for magnitude or :py:attr:`~.TableUnit.FLUX` for flux.
        :param MagType magtype: (**Optional**) magnitude type if data are in magnitude unit. Must either be :py:attr:`~.MagType.AB` or :py:attr:`~.MagType.VEGA`.
        :param TableFormat tformat: (**Optional**) format of the table. Must either be :py:attr:`~.TableFormat.MEME` if data and error columns are intertwined or :py:attr:`~.TableFormat.MMEE` if columns are first data and then errors.
        :param TableType ttype: (**Optional**) data type. Must either be :py:attr:`~.TableType.SHORT` or :py:attr:`~.TableType.LONG`.
        
        :returns: a LePhare catalogue instance
        :rtype: :py:class:`~.LePhareCat`
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
         
         :param CleanMethod cleanMethod: (**Optional**) method used to clean pixel with negative values. Accepted values are :py:attr:`~.CleanMethod.ZERO` or :py:attr:`~.CleanMethod.MIN`.
         :param scaleFactor: (**Optional**) factor used to multiply data and std map
         :type scaleFactor: :python:`int` or :python:`float`
         :param texpFac: (**Optional**) exposure factor used to divide the exposure time when computing Poisson noise. A value of :python:`0` means no Poisson noise is added to the variance map.
         :type texpFac: :python:`int`
         
         :returns: (columns, column names and column types)
         :rtype: (:python:`list[int/float/str], list[str], list[Any]`)
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
        
        :param CleanMethod cleanMethod: (**Optional**) method used to clean pixel with negative values. Accepted values are :py:attr:`~.CleanMethod.ZERO` or :py:attr:`~.CleanMethod.MIN`.
        :param texpFac: (**Optional**) exposure factor used to divide the exposure time when computing Poisson noise. A value of :python:`0` means no Poisson noise is added to the variance map.
        :type texpFac: :python:`int`
        
        :returns: (columns, column names and column types)
        :rtype: (:python:`list[int/float/str], list[str], list[Any]`)
        '''
       
        data               = []
        var                = []
       
        for pos, filt in enumerate(self.filters):

            # Clean and add noise to variance map
            d, v           = self.cleanAndNoise(filt.data, filt.data2, filt.var, self.mask, cleanMethod=cleanMethod, texp=filt.texp, texpFac=texpFac)
            data.append(d)
            var.append( v)
        
        # Go to 1D version
        data, var, indices = self.arraysTo1D(data, var, indices=True)
        
        # Compute std and convert std and data to mJy unit
        dataList           = []
        stdList            = []
        
        for d, err, filt in zip(data, np.sqrt(var), self.filters):
            
            data, std      = countToFlux(d, err, filt.zpt)
            
            # Append data and std to list
            dataList.append(data.to('mJy').value)
            stdList.append( std.to( 'mJy').value)
            
        # Redshift column
        ll                 = len(self.filters)
        ld                 = len(data)
        zs                 = [self.redshift]*ld
        
        dtypes             = [int, float]       + [float]*2*ll
        colnames           = ['id', 'redshift'] + [val for f in self.filters for val in [f.filter, f'{f.filter}_err']]
        columns            = [indices, zs]      + [val for d, s in zip(dataList, stdList) for val in [d, s]]
        
        return columns, colnames, dtypes
        
    
    def genTable(self, cleanMethod: CleanMethod = CleanMethod.ZERO, scaleFactor: Union[int, float] = 100, texpFac : int = 0, **kwargs) -> Table:
        r'''
        .. codeauthor:: Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>
        
        Generate an input table for the SED fitting codes.
        
        :param CleanMethod cleanMethod: (**Optional**) method used to clean pixel with negative values. Accepted values are :py:attr:`~.CleanMethod.ZERO` or :py:attr:`~.CleanMethod.MIN`.
        :param scaleFactor: (**Optional**) factor used to multiply data and std map. Only used if SED fitting code is LePhare.
        :type scaleFactor: :python:`int` or :python:`float`
        :param texpFac: (**Optional**) exposure factor used to divide the exposure time when computing Poisson noise. A value of :python:`0` means no Poisson noise is added to the variance map.
        :type texpFac: :python:`int`
        
        :returns: an output table
        :rtype: `Astropy Table`_
        
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
    def arraysTo1D(data: List[ndarray], var: List[ndarray], indices: bool = False):
        '''
        Convert list of data and variance maps into 1D vectors and remove nan values.
        
        .. note::
            
            Provide indices = True to get the indices of the non-NaN pixels in the 1D array (before NaN are removed).
            
        :param data: data map
        :type data: `ndarray`_
        :param var: variance map
        :type var: `ndarray`_
        
        :param indices: (**Optional**) whether to return the list of indices of non-NaN values or not
        :type indices: :python:`bool`
        
        :returns: (1D data, 1D variance (and the indices if **indices** is :python:`True`))
        :rtype: (`ndarray`_, `ndarray`_) or (`ndarray`_, `ndarray`_, `ndarray`_ [:python:`int`])
        
        :raises TypeError:
            
            * if **data** or **var** are not :python:`list`
            * if one element of **data** or **var** is not a `ndarray`_
            * if **indices** is not a :python:`bool`
        '''
        
        if not isinstance(data, list):
            raise TypeError(f'data has type {type(data)} but it must be a list of numpy.ndarray.')
        
        if not isinstance(var, list):
            raise TypeError(f'var has type {type(var)} but it must be a list of numpy.ndarray.')
            
        if any((not isinstance(i, ndarray) for i in data)):
            raise TypeError('One element of data is not a numpy.ndarray.')
        
        if any((not isinstance(i, ndarray) for i in var)):
            raise TypeError('One element of var is not a numpy.ndarray.')
            
        if not isinstance(indices, bool):
            raise TypeError(f'indices parameter has type {type(indices)} but it must of type bool.')
        
        # Avoid to overwrite original arrays
        data        = deepcopy(data)
        var         = deepcopy(var)
        
        length      = np.prod(data[0].shape)
    
        # Transform data and error maps into 1D vectors
        data        = [i.reshape(length) for i in data]
        var         = [i.reshape(length) for i in var ]
        
        # Compute mask of non-NaN values that is the intersection of the masks in all the bands
        nanMask = True
        for d, v in zip(data, var):
            nanMask = nanMask & ~(np.isnan(d) | np.isnan(v))
            
        data        = [i[nanMask] for i in data]
        var         = [i[nanMask] for i in var ]
        
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
                
            * If **method** is :py:attr:`~.CleanMethod.ZERO`, negative values in the data and error maps are set to 0
            * If **method** is :py:attr:`~.CleanMethod.MIN`, negative values in the data and error maps are set to the minimum value in the array
            
        :param data: data map
        :type data: `ndarray`_
        :param var: variance map
        :type var: `ndarray`_
        :param mask: mask used to apply NaN values
        :type mask: `ndarray`_ [:python:`bool`]
        
        :param CleanMethod method: (**Optional**) method to deal with negative values. Possible values are: :py:attr:`~.CleanMethod.ZERO` or :py:attr:`~.CleanMethod.MIN`.
        
        :returns: cleaned data and variance maps
        :rtype: (`ndarray`_, `ndarray`_)
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
            
            If **texpFac** is :python:`0` or **texp** is :python:`None`, no Poisson noise is added to the variance map
            
        :param data: data map
        :type data: `ndarray`_
        :param data2: data map convolved by the square of the PSF used to add Poisson noise
        :type data2: `ndarray`_
        :param var: variance map
        :type var: `ndarray`_
        :param mask: mask map
        :type mask: `ndarray`_ [:python:`bool`]
        
        :param CleanMethod cleanMethod: (**Optional**) method used for the cleaning process
        :param texp: (**Optional**) exposition time
        :type texp: :python:`int` or :python:`float`
        :param texpFac: (**Optional**) factor used to divide the exposition time
        :type texpFac: :python:`int`
        
        :returns: cleaned data and cleaned variance map with Poisson noise added
        :rtype: (`ndarray`_, `ndarray`_)
        '''
        
        # Clean data and error maps of bad pixels and pixels with negative values
        data, var = self.clean(data, var, mask, method=cleanMethod)
            
        # Add Poisson noise to the variance map
        if texp is not None and data2 is not None:
            print('Adding Poisson noise...')
            var  += self.poissonVar(data2, texp=texp, texpFac=texpFac)
        
        return data, var
    
    def computeMeanMap(self, maskVal: Union[int, float] = 0, **kwargs) -> Tuple[ndarray]:
        r'''
        .. codeauthor:: Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>
        
        Compute the averaged data and error maps over the spectral dimension for non masked pixels.
        
        :param maskVal: (**Optional**) value to put into masked pixels
        :type maskVal: :python:`int` or :python:`float`
        
        :returns: averaged data and averaged error map
        :rtype: (`ndarray`_, `ndarray`_)
        
        :raises TypeError: if **maskVal** is neither :python:`int` nor :python:`float`
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
        
        
        #where :math:`F` is the square of the flux map and :math:`\alpha` is a scale factor defined as
        where :math:`F` is the flux map and :math:`\alpha` is a scale factor defined as
        
        .. math::
                
            \alpha = {\rm{TEXP / TEXPFAC}}
        
        
        where :math:`\rm{TEXP}` is the exposure time and :math:`\rm{TEXPFAC}` is a coefficient used to scale it down.
        
        :param data2: flux map convolved by the square of the PSF
        :type data2: `ndarray`_
        
        :param texp: (**Optional**) exposure time in seconds
        :type texp: :python:`int` or :python:`float`
        :param texpFac: (**Optional**) exposure factor
        :type texpFac: :python:`int` or :python:`float`
        
        :raises TypeError: if **texp** or **texpFac** are not both :python:`int` or :python:`float`
        :raises ValueError:
            
            * if :python:`texp <= 0`
            * if :python:`texpFac < 0`
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
        
        :param data: data map
        :type data: `ndarray`_
        :param var: variance map
        :type var: `ndarray`_
        :param norm: normalisation map which divides data and error maps
        :type norm: `ndarray`_
        
        :param factor: (**Optional**) scale factor which multiplies the output array
        :type factor: :python:`int` or :python:`float`
        
        :returns: scaled data and variance maps
        :rtype: (`ndarray`_, `ndarray`_)
        
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
            If you want a table with different parameters you must run :py:meth:`~FilterList.genTable` again, for e.g.
            
            >>> from SED.misc import SEDcode, CleanMethod
            >>> flist = FilterList(filters, mask)          # setCode and genTable methods are called with default SED fitting code name
            >>> flist.setCode(SEDcode.LEPHARE,             # setCode and genTable methods are called with 'lephare' SED fitting code name
                              cleanMethod=CleanMethod.MIN, # Additional parameters are passed to genTable
                              scaleFactor=50)                             
        
        :param SEDcode code: code used for SED fitting. Acceptable values are :py:attr:`~.SEDcode.CIGALE` and :py:attr:`~.SEDcode.LEPHARE`.
        
        :raises TypeError: if **code** is not of type :py:class:`~.SEDcode`
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