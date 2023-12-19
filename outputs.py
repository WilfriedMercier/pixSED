#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
.. codeauthor:: Hugo Plombat - LUPM <hugo.plombat@umontpellier.fr> & Wilfried Mercier - IRAP/LAM <wilfried.mercier@lam.fr>

Classes used by the sed objects to generate objects loading output tables and producing resolved maps.
"""

import os.path          as     opath
import astropy.io.ascii as     asci
import numpy            as     np
from   numpy            import ndarray
from   abc              import ABC, abstractmethod
from   typing           import Tuple, Union, Optional, Dict, Any
from   astropy.io       import fits
from   astropy.table    import Table
from   astropy.units    import Quantity
from   .misc.enum       import LePhareOutputParam
from   .filters         import FilterList

class Output(ABC):
   r'''
   .. codeauthor:: Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>
   
   Abstract SED fitting code output class.
   
   :param file: name of the SED fitting outut file
   :type file: :python:`str`
   '''

   def __init__(self, file: str, *args, **kwargs) -> None:
      r'''Init method.'''
      
      if not isinstance(file, str):
         raise TypeError(f'file parameter has type {type(file)} but it must have type str.')
         
      fullFile                    = opath.expandvars(file)
      if not opath.isfile(fullFile):
         raise ValueError(f'file {file} (expanded as {fullFile}) not found.')
         
      #: SED fitting code output file name used
      self.file: str              = fullFile
      
      #: Image properties corresponding to the output table (keys are None by default, update using the link method with a FilterList object)
      self.imProp: Dict[str, Any] = {'shape'   : None,
                                     'scale'   : None,
                                     'meanMap' : None
                                     }
      
      #: Configuration dictionary with info from the header
      self.config: str            = {}
      
      #: Table gathering data
      self.table: Table           = None
      
   @abstractmethod
   def load(self, *args, **kwargs) -> Table:
      r'''
      .. codeauthor:: Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>
      
      Load data from a file into an astropy Table object.
      
      :returns: the astropy table
      :rtype: `Astropy Table`_
      '''
   
      return
  
   def link(self, filterList: FilterList, *args, **kwargs) -> None:
      r'''
      .. codeauthor:: Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>
      
      Provide the default image properties from a FilterList object.
      
      :param FilterList filterList: FilterList object from which the image properties are retrieved
      
      :raises TypeError: if **filterList** is not of type :py:class:`~.FilterList`
      '''
      
      if not isinstance(filterList, FilterList):
         raise TypeError(f'filterList parameter has type {type(filterList)} but it must be of type FilterList.')
         
      self.imProp['shape']   = filterList.shape
      self.imProp['scale']   = filterList.scaleFac
      self.imProp['meanMap'] = filterList.meanMap
      
      return
  
   @abstractmethod
   def toImage(self, *args, **kwargs) -> Quantity:
       r'''
       .. codeauthor:: Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>
       
       Generate a resolved map.
       
       :returns: the image
       :rtype: `Astropy Quantity`_
       '''
       
       return

class CigaleOutput(Output):
    r'''
    .. codeauthor:: Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>
    
    Init the output class.
    
    :param file: name of the SED fitting outut file
    :type file: :python:`str`
    '''
    
    def __init__(self, file: str, *args, **kwargs):
        r'''Init method.'''
        
        super().__init__(file, *args, **kwargs)
        
        #: Mapping between column names and units
        self.units = {}
        print(self.file)
        self.load()
        
    def _getUnits(self, hdr: fits.Header, *args, **kwargs) -> Dict[str, str]:
        r'''
        .. codeauthor:: Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>
        
        Get and return the units from a Cigale output fits file header and map them to their column names.
        
        :param hdr: header to read the units from
        :type hdr: `Astropy Header`_
        
        :returns: mapping between column names and units
        :rtype: :python:`dict[str, str]`
        '''
        
        self.units = {hdr[f'TTYPE{i}'] : hdr[f'TUNIT{i}'] if f'TUNIT{i}' in hdr else '' for i in range(1, hdr['TFIELDS']+1)}
        
        return self.units

    def link(self, filterList: FilterList, *args, **kwargs) -> None:
       r'''
       .. codeauthor:: Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>
       
       Provide the default image properties from a FilterList object.
       
       :param FilterList filterList: FilterList object from which the image properties are retrieved
       
       :raises TypeError: if **filterList** is not of type :py:class:`~.FilterList`
       '''
       
       if not isinstance(filterList, FilterList):
          raise TypeError(f'filterList parameter has type {type(filterList)} but it must be of type FilterList.')
          
       # Scale and meanMap are not used when generating the catalogue for cigale so no need to retrieve them
       self.imProp['shape']   = filterList.shape
       
       return

    def load(self, *args, **kwargs) -> Table:
       r'''Load data from Cigale output fits file.'''
       
       with fits.open(self.file) as hdul:
           self._getUnits(hdul[1].header)
           table = Table(hdul[1].data)
       
       self.table = table
       
       return table
  
    def toImage(self, name: str, 
                shape: Optional[Tuple[int]] = None, **kwargs) -> Quantity:
       r'''
       .. codeauthor:: Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>
       
       Generate an image from the Astropy Table given column name.
       
       :param name: name of the column to generate the image from
       :type name: :python:`str`
       
       :param tuple[int] shape: (**Optional**) shape of the output image. The shape must be such that :python:`shape[0]*shape[1] == len(self.table)`. If :python:`None`, the default value provided in the :py:meth:`~.CigaleOutput.link` method is used.
       :type shape: :python:`tuple[int]`
       
       :returns: output image as an `Astropy Quantity`_. Use .data method to only get the array.
       :rtype: `Astropy Quantity`_
       
       :raises TypeError:
           
           * if **name** is not of type :python:`str`
           * if **shape** is neither a :python:`tuple` nor a :python:`list`
           
       :raises ValueError: if **shape** is not of length 2
       '''
       
       if not isinstance(name, str):
          raise TypeError(f'column name has type {type(name)} but it must have type str.')
       
       # Check shape parameter
       if self.imProp['shape'] is None and shape is None:
          raise ValueError('an image shape must be provided either in this function call or using the link method.')
       
       if shape is not None:

          if not isinstance(shape, (tuple, list)):
             raise TypeError(f'shape parameter has type {type(shape)} but it must have type tuple or list.')
               
          if len(shape) != 2:
             raise ValueError(f'shape parameter has length {len(shape)} but it must have a length of 2.')
             
       else:
          shape        = self.imProp['shape']
       
       # Location of good pixels
       indices         = self.table['id']
           
       # Output array (NaN for bad pixels - default NaN everywhere)
       data            = np.full(shape[0]*shape[1], np.nan)
       data[indices]   = self.table[name]
       data            = data.reshape(shape)
       
       return Quantity(data, unit=self.units[name])

   
class LePhareOutput(Output):
   r'''
   .. codeauthor:: Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>
   
   Implement an output class for LePhare.
   
   :param file: name of the SED fitting outut file
   :type file: :python:`str`
   '''
   
   def __init__(self, file: str, *args, **kwargs) -> None:
      r'''Init method.'''
      
      super().__init__(file, *args, **kwargs)
      
      self.load()
   
   def load(self, *args, **kwargs) -> Table:
      r'''
      .. codeauthor:: Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>
      
      Load data from LePhare output file.
      
      :returns: the astropy table
      :rtype: `Astropy Table`_
      '''
      
      # Read header first
      colMap     = self.readHeader()
      
      # Select columns from the header and map them to the names given in the Enum object
      colNames   = [f'{i}' if i[-2:] != '()' else f'{i[:-2]}_2' for i in colMap.keys()]
      colDef     = [f'col{i}' for i in colMap.values()]
      
      tcolNames  = []
      tcolUnits  = []
      tcolLog    = []
      for i in colNames:
      
         if i == 'IDENT':
            tcolNames.append('ID')
            tcolUnits.append('')
            tcolLog.append(False)
         else:
            
            # Get names which will appear in the Astropy table column headers
            tcolNames.append(LePhareOutputParam[i].value.name)
      
            # Get units which will appear in the Astropy table colulmn headers
            tcolUnits.append(LePhareOutputParam[i].value.unit)
      
            # Get log flag for each column
            tcolLog.append(LePhareOutputParam[i].value.log)
      
      # Read full Table
      table                  = asci.read(self.file, comment='#')
      
      # Only keep desired columns, rename them and add unit
      table                  = table[colDef]
      
      for tcname, tcunit, tclog, cdef in zip(tcolNames, tcolUnits, tcolLog, colDef):
          table.rename_column(cdef, tcname)
          table[tcname].unit = tcunit
          
          if tclog:
             table[tcname]   = 10**table[tcname]
      
      self.table             = table
      
      return table
  
   def readHeader(self, *args, **kwargs) -> Dict[str, str]:
      r'''
      .. codeauthor:: Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>
      
      Read the header of LePhare output file.
      
      :returns: dict mapping between column names and column number
      :rtype: :python:`dict[str, str]`
      '''
      
      with open(self.file, 'r') as f:
         
         # Go through header lines till output format line
         for line in f:
            
            line = line.strip()
            if line == '# Output format                       #':
               break
            elif ':' not in line:
               continue
            else:
               key, value       = (i.strip() for i in line.strip('#').rsplit(':', maxsplit=1))
               self.config[key] = value
               
         else:
            raise IOError('Output format line could not be reached.')
            
         # Go through the lines which tell us which parameters to extract and where
         colMap  = {}
         for line in f:
            
            line = line.strip()
            if line == '#######################################':
               break
            else:

               items          = line.strip('#, ').split(',')
               for item in items:
                  key, val    = item.split()
                  colMap[key] = int(val)
                  
         else:
            raise IOError('End of SED fitting code output file header could not be reached.')
            
         return colMap
     
   def toImage(self, name: str, 
               shape: Optional[Tuple[int]] = None, 
               scaleFactor: Optional[Union[int, float]] = None,
               meanMap: Optional[ndarray] = None, **kwargs) -> Quantity:
      r'''
      .. codeauthor:: Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>
      
      Generate an image from the Astropy Table given column name.
      
      .. note::
          
          Depending on the type of output quantity one wants to generate an image from, **scaleFactor** can have different values:
              
              * if the output quantity is extensive, then this is the same scaleFactor which was used to scale down the filters data
              * if the output quantity is intensive, then it must be :python:`1`
              
          The **shape**, **scaleFactor** and **meanMap** parameters can also be passed as default values using
          
          .. code:: python
              
              output = LePhareOutput('someFileName.out')
              output.link(filterList)
          
          where filterList is the :py:class:`~.FilterList` object used to perform the SED fitting.
          
          These parameters always override the default values if provided.
      
      :param name: name of the column to generate the image from
      :type name: :python:`str`
      
      :param shape: (**Optional**) shape of the output image. The shape must be such that :python:`shape[0]*shape[1] == len(self.table)`. If :python:`None`, the default value provided in the :py:meth:`~.LePhareOutput.link` method is used.
      :type shape: :python:`tuple[int]`
      :param scaleFactor: (**Optional**) scale factor used to scale up the image. If :python:`None`, the default value provided in the :py:meth:`~.Output.link` method is used.
      :type scaleFactor: :python:`int/float`
      :param meanMap: (**Optional**) mean map used during the filterList table creation to normalise the data. If :python:`None`, the default value provided in the :py:meth:`~.Output.link` method is used.
      :type meanMap: `ndarray`_
      
      :returns: output image as an Astropy Quantity. Use .data method to only get the array.
      :rtype: `Astropy Quantity`_
      
      :raises TypeError:
            
          * if **name** is not of type :python:`str`
          * if **shape** is neither a :python:`tuple` nor a :python:`list`
          * if **scaleFactor** is neither an :python:`int` nor a :python:`float`
          * if **meanMap** is not a `ndarray`_
          
      :raises ValueError: if **shape** is not of length 2
      '''
      
      if not isinstance(name, str):
         raise TypeError(f'column name has type {type(name)} but it must have type str.')
      
      # Check shape parameter
      if self.imProp['shape'] is None and shape is None:
         raise ValueError('an image shape must be provided either in this function call or using the link method.')
      
      if shape is not None:

         if not isinstance(shape, (tuple, list)):
            raise TypeError(f'shape parameter has type {type(shape)} but it must have type tuple or list.')
              
         if len(shape) != 2:
            raise ValueError(f'shape parameter has length {len(shape)} but it must have a length of 2.')
            
      else:
         shape        = self.imProp['shape']
          
      # Check scaleFactor parameter
      if self.imProp['scale'] is None and scaleFactor is None:
         raise ValueError('a scale facor must be provided either in this function call or using the link method.')
           
      if scaleFactor is not None:
          
         if not isinstance(scaleFactor, (int, float)):
            raise TypeError(f'scaleFactor parameter has type {type(scaleFactor)} but it must have type int or float.')
          
         if scaleFactor <= 0:
            raise ValueError(f'scaleFactor parameter has value {scaleFactor} but it must be strictly positive.')
      else:
         scaleFactor  = self.imProp['scale']
      
      # Check meanMap parameter
      if meanMap is not None:
         if not isinstance(meanMap, ndarray):
            raise TypeError(f'meanMap parameter has type {type(meanMap)} but it must have type ndarray.')
      else:
         meanMap      = self.imProp['meanMap']
      
      if shape != meanMap.shape:
         raise ValueError(f'meanMap has shape {meanMap.shape} but is must have shape {shape}.')
          
      # Location of good pixels
      indices         = self.table['ID']
          
      # Output array (NaN for bad pixels - default NaN everywhere)
      data            = np.full(shape[0]*shape[1], np.nan)
      data[indices]   = self.table[name].data / scaleFactor
      data            = data.reshape(shape)
      
      # Multiply by mean map only where it is non zero
      if meanMap is not None:
          mask        = meanMap != 0
          data[mask] *= meanMap[mask]
      
      return Quantity(data, unit=self.table[name].unit)