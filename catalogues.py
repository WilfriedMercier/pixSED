#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
.. codeauthor:: Hugo Plombat - LUPM <hugo.plombat@umontpellier.fr> & Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>

Base classes used to generate catalogues for LePhare or Cigale SED fitting codes.
"""

from   abc                        import ABC, abstractmethod
from   typing                     import List
import os.path                    as     opath
from   astropy.table              import Table
from   .misc                      import TableUnit, MagType, TableFormat, TableType, EnumProperty, ListIntProperty

class Catalogue(ABC):
    r'''Class implementing a catalogue consisting of as Astropy Table and additional information used by the SED fitting codes.'''
    
    def __init__(self, fname: str, table: Table, *args, **kwargs) -> None:
        r'''
        .. codeauthor:: Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>
        
        Init general catalogue. This is supposed to be subclassed to account for specificities of LePhare or Cigale catalogues.

        :param str fname: name of the catalogue file where the catalogue is written into when saving
        :param table: input table
        :type table: Astropy Table
        
        :raises TypeError:
             
            * if **table** is not an astropy Table
            * if **fname** is not of type str
        ''' 
        
        if not isinstance(table, Table):
            raise TypeError(f'table has type {type(table)} but it must be an Astropy Table.')
            
        if not isinstance(fname, str):
            raise TypeError(f'fname parameter has type {type(fname)} but it must have type str.')
            
        self.name   = fname
        self.data   = table
        
    def save(self, path: str ='', **kwargs) -> None:
        r'''
        .. codeauthor:: Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>
        
        Save the catalogue into the given file.
        
        :param str path:(**Optional**) a path to append to the file name
        :param kwargs: optional parameters passed to Astropy.table.Table.writeto method
        
        :raises TypeError: if **path** is not of type str
        '''

        if not isinstance(path, str):
            raise TypeError(f'path as type {type(path)} but it must have type str.')
            
        fname = opath.join(path, self.name)
        self.data.write(fname, overwrite=True, **kwargs)
        return
    
    @property
    @abstractmethod
    def text(self, *args, **kwargs) -> str:
        r'''
        .. codeauthor:: Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>
        
        Return a text representation of the catalogue used when making the parameter files.
        '''
        
        return
    
class CigaleCat(Catalogue):

    def __init__(self, *args, **kwargs):
        
        raise NotImplementedError('Cigale not implemented yet.')
    
class LePhareCat(Catalogue):
    r'''Class implementing a catalogue compatible with LePhare SED fitting code.'''
    
    def __init__(self, fname: str, table: Table, 
                 tunit: TableUnit     = TableUnit.MAG,
                 magtype: MagType     = MagType.AB, 
                 tformat: TableFormat = TableFormat.MEME, 
                 ttype: TableType     = TableType.LONG, 
                 nlines: List[int]    = [0, 100000000]) -> None:
        r'''
        .. codeauthor:: Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>
        
        Init LePhare catalogue.

        :param str fname: name of the output file containing the catalogue when it is saved
        :param table: input table
        :type table: Astropy Table
        
        :param TableUnit tunit: (**Optional**) unit of the table data. Must either be TableUnit.MAG for magnitude or TableUnit.FLUX for flux.
        :param MagType magtype: (**Optional**) magnitude type if data are in magnitude unit. Must either be MagType.AB or MagType.VEGA.
        :param TableFormat tformat: (**Optional**) format of the table. Must either be TableFormat.MEME if data and error columns are intertwined or TableFormat.MMEE if columns are first data and then errors.
        :param TableType ttype: (**Optional**) data type. Must either be TableType.SHORT or TableType.LONG.
        :param list[int] nlines: (**Optional**) first and last line of the catalogue to be used during the SED fitting

        :raises TypeError:
             
            * if **table** is not an astropy Table
            * if **fname** is not of type str
            * if **nlines** is not a list
            
        :raises ValueError: if **nlines** values are not int, or if first value is less than 0, or if second value is less than the first one
        ''' 
            
        super().__init__(fname, table)
        
        #####################################################
        #             Define default properties             #
        #####################################################
        
        self.unit   = EnumProperty(TableUnit.MAG)
        self.mtype  = EnumProperty(MagType.AB)
        self.format = EnumProperty(TableFormat.MEME)
        self.ttype  = EnumProperty(TableType.LONG)
        
        self.nlines = ListIntProperty([0, 100000000], minBound=0,
                                      testFunc = lambda value: value[1] < value[0],
                                      testMsg  = f'maximum number of lines ({nlines[1]}) is less than minimum one ({nlines[0]}).')
         
        #################################################
        #              Set to given values              #
        #################################################
        
        self.unit.set(  tunit)
        self.mtype.set( magtype)
        self.format.set(tformat)
        self.ttype.set( ttype)
        self.nlines.set(nlines)
    
    @property
    def text(self, *args, **kwargs) -> str:
        r'''
        .. codeauthor:: Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>
        
        Return a text representation of the catalogue used when making the parameter files.
        
        :returns: output representation
        :rtype: str
        '''
        
        text =  f'''
        #-------    Input Catalog Informations   
        CAT_IN \t\t{self.name}

        INP_TYPE \t{self.unit} \t\t# Input type (F:Flux or M:MAG)
        CAT_MAG \t{self.mtype} \t\t# Input Magnitude (AB or VEGA)
        CAT_FMT \t{self.format} \t\t# MEME: (Mag,Err)i or MMEE: (Mag)i,(Err)i  
        CAT_LINES \t{self.nlines} \t# MIN and MAX RANGE of ROWS used in input cat [def:-99,-99]
        CAT_TYPE \t{self.ttype} \t\t# Input Format (LONG,SHORT-def)
        '''
        
        return text
    
    def save(self, path: str = '', **kwargs) -> None:
        r'''
        .. codeauthor:: Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>
        
        Save LePhare catalogue into the given file.
        
        :param str path:(**Optional**) a path to append to the file name
        :param kwargs: optional parameters passed to Astropy.table.Table.writeto method
        
        :raises TypeError: if **path** is not of type str
        '''
            
        if not isinstance(path, str):
            raise TypeError(f'path as type {type(path)} but it must have type str.')
        
        fname = opath.join(path, self.name)
        self.data.write(fname, format='ascii.fast_no_header', overwrite=True, **kwargs)
        return