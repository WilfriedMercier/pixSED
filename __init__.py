#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
.. codeauthor:: Hugo Plombat - LUPM <hugo.plombat@umontpellier.fr> & Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu> & Maxime Tarrasse - IRAP <Maxime.Tarrasse@irap.omp.eu>

Init file for the SED fitting parser library.
"""

from .filters    import Filter, FilterList
from .sed        import LePhareSED, CigaleSED
from .catalogues import LePhareCat, CigaleCat
from .outputs    import LePhareOutput, CigaleOutput
from .misc       import SEDcode, CleanMethod, MagType, TableFormat, TableType, TableUnit, YESNO, ANDOR, IMF
from .misc       import cigaleModules as cigmod
from .photometry import countToMag, MagTocount, countToFlux