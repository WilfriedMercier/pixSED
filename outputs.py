#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
.. codeauthor:: Hugo Plombat - LUPM <hugo.plombat@umontpellier.fr> & Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>

Classes used by the sed objects to generate objects loading output tables and producing resolved maps.
"""

import os.path          as     opath
import astropy.io.ascii as     asci
import numpy            as     np
from   numpy            import ndarray
from   copy             import deepcopy
from   abc              import ABC, abstractmethod
from   typing           import Tuple, Union, Optional
from   astropy.table    import Table
from   astropy.units    import Quantity
from   numpy            import ndarray
from   .misc.enum       import LePhareOutputParam
from   .filters         import FilterList

class Output(ABC):
   r'''Abstract SED fitting code output class.'''


   def __init__(self, file: str, *args, **kwargs) -> None:
      r'''
      .. codeauthor:: Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>
      
      Init the output class.
      
      :param str file: name of the SED fitting outut file
      '''
      
      if not isinstance(file, str):
         raise TypeError(f'file parameter has type {type(file)} but it must have type str.')
         
      fullFile = opath.expandvars(file)
      if not opath.isfile(fullFile):
         raise ValueError(f'file {file} (expanded as {fullFile}) not found.')
         
      #: SED fitting code output file name used
      self.file   = fullFile
      
      #: Image properties corresponding to the output table (keys are None by default, update using the link method with a FilterList object)
      self.imProp = {'shape'   : None,
                     'scale'   : None,
                     'meanMap' : None
                    }
      
      #: Configuration dictionary with info from the header
      self.config = {}
      
   @abstractmethod
   def load(self, *args, **kwargs) -> Table:
      r'''Load data from a file into an astropy Table object.'''
   
      return
  
   def link(self, filterList: FilterList, *args, **kwargs) -> None:
      r'''
      .. codeauthor:: Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>
      
      Provide the default image properties from a FilterList object.
      
      :param FilterList filterList: FilterList object from which the image properties are retrieved
      
      :raises TypeError: if **filterList** is not of type FilterList
      '''
      
      if not isinstance(filterList, FilterList):
         raise TypeError(f'filterList parameter has type {type(filterList)} but it must be of type FilterList.')
         
      self.imProp['shape']   = filterList.shape
      self.imProp['scale']   = filterList.scaleFac
      self.imProp['meanMap'] = filterList.meanMap
      
      return

   
class LePhareOutput(Output):
   r'''Implement an output class for LePhare.'''
   
   def __init__(self, file: str, *args, **kwargs) -> None:
      r'''
      .. codeauthor:: Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>
      
      Init the output class.
      
      :param str file: name of the SED fitting outut file
      '''
      
      super().__init__(file, *args, **kwargs)
      
      self.load()
      
   
   def readHeader(self, *args, **kwargs) -> dict:
      r'''
      .. codeauthor:: Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>
      
      Read the header of LePhare output file.
      
      :returns: dict mapping between column names and column number
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
   
   def load(self, *args, **kwargs) -> Table:
      r'''
      .. codeauthor:: Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>
      
      Load data from LePhare output file.
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
              * if the output quantity is intensive, then it must be 1
              
          The **shape**, **scaleFactor** and **meanMap** parameters can also be passed as default values using
          
          >>> output = LePhareOutput('someFileName.out')
          >>> output.link(filterList)
          
          where filterList is the FilterList object used to perform the SED fitting.
          
          These parameters always override the default values if provided.
      
      :param str name: name of the column to generate the image from
      
      :param tuple[int] shape: (**Optional**) shape of the output image. The shape must be such that shape[0]*shape[1] == len(self.table)
      :param scaleFactor: (**Optional**) scale factor used to scale up the image
      :type scaleFactor: int or float
      :param ndarray meanMap: (**Optional**) mean map used during the filterList table creation to normalise the data
      
      :returns: output image as an Astropy Quantity. Use .data method to only get the array.
      :rtype: Quantity
      
      :raises TypeError:
          
          * if **name** is not of type str
          * if **shape** is neither a tuple nor a list
          * if **scaleFactor** is neither an int nor a float
          
      :raises ValueError: if **shape** is not of length
      '''
      
      if not isinstance(name, str):
         raise TypeError(f'column name has type {type(name)} but it must have type str.')
      
      # Check shape parameter
      if self.imProp['shape'] is None and shape is None:
         raise ValueError('an image shape must be provided either in this function call or using the link method.')
      
      if shape is not None:

         if not isinstance(shape, (tuple, list)):
            raise TypeError(f'shape parameter has type {type(shape)} but it must have type tuple.')
              
         if len(shape) != 2:
            raise ValueError(f'shape parameter has not a length of 2.')
            
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
         
      
      
      
      
      
      
      
      
      
      