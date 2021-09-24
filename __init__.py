#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
.. codeauthor:: Hugo Plombat - LUPM <hugo.plombat@umontpellier.fr> & Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>

Init file for the SED fitting parser library.
"""

from .filters    import Filter, FilterList
from .sed        import LePhareSED
from .catalogues import LePhareCat
from .misc       import SEDcode, CleanMethod, MagType, TableFormat, TableType, TableUnit, YESNO, ANDOR
