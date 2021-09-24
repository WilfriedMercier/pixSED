#!/usr/bin/env python3
# -*- coding: utf-8 -*-
f"""
.. codeauthor:: Hugo Plombat - LUPM <hugo.plombat@umontpellier.fr> & Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>

Classes used by the sed objects to generate objects loading output tables and producing resolved maps.
"""

import os.path          as     opath
import astropy.io.ascii as     asci
from   abc              import ABC, abstractmethod
from   typing           import Tuple
from   astropy.table    import Table
from   numpy            import ndarray
from   .misc.enum       import LePhareOutputParam

class Output(ABC):
   r'''Abstract SED fitting code output class.'''


   def __init__(self, file: str, *args, **kwargs) -> None:
      r'''
      Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>
      
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
      
      #: Configuration dictionary with info from the header
      self.config = {}
      
   @abstractmethod
   def load(self, *args, **kwargs) -> Table:
      r'''Load data from a file into an astropy Table object.'''
   
      return
   
   
class LePhareOutput(Output):
   r'''Implement an output class for LePhare.'''
   
   def __init__(self, file: str, *args, **kwargs) -> None:
      r'''
      Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>
      
      Init the output class.
      
      :param str file: name of the SED fitting outut file
      '''
      
      super().__init__(file, *args, **kwargs)
      
      self.load()
      
   
   def readHeader(self, *args, **kwargs) -> dict:
      r'''
      Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>
      
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

               items       = line.strip('#, ').split(',')
               for item in items:
                  key, val    = item.split()
                  colMap[key] = int(val)
                  
         else:
            raise IOError('End of SED fitting code output file header could not be reached.')
            
         return colMap
   
   def load(self, *args, **kwargs) -> Table:
      r'''
      Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>
      
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
      
     
   def toImage(self, name: str, shape: Tuple[int] = (100, 100), scaleFactor: int = 100) -> ndarray:
      r'''
      Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>
      
      Generate an image from the Astropy Table given column name.
      
      :param str name: name of the column to generate the image from
      '''
      
      return
         
      
      
      
      
      
      
      
      
      
      