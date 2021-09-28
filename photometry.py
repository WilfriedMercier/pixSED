#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
.. codeauthor:: Hugo Plombat - LUPM <hugo.plombat@umontpellier.fr> & Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>

Photometry functions.
"""

import numpy         as np
import astropy.units as u

def countToMag(data, err, zeropoint):
    r'''
    Convert data counts and their associated error into AB magnitudes using the formula
    
    .. math::
        
        d [{\rm{mag}}] = -2.5 \log_{10} d [{\rm{e^{-}/s}}] + {\rm{zpt}}
        
    where :math:`d` is the data and :math:`\rm{zpt}` is the magnitude zeropoint. The error is given by
    
    .. math::
        
        \Delta d [{\rm{mag}}] = 1.08 \Delta d [{\rm{e^{-}/s}}] / d [{\rm{e^{-}/s}}]
    
    :param data: data in electron/s
    :type data: float or ndarray[float]
    :param err: std errors in electron/s
    :type err: float or ndarray[foat]
    :param float zeropoint: zeropoint associated to the data
    
    :returns: AB magnitude and associated error
    :rtype: float or ndarray[float], float or ndarray[float]
    '''

    mag  = -2.5 * np.log10(data) + zeropoint
    emag = 1.08 * err/data
    
    return mag, emag

def countToFlux(data, err, zeropoint):
    r'''
    Convert data counts and their associated error into flux in :math:`\rm{erg/cm^2/s/Hz}`.
    
    :param data: data in :math:`electron/s`
    :type data: float or ndarray[float]
    :param err: std errors in :math:`electron/s`
    :type err: float or ndarray[float]
    :param float zeropoint: zeropoint associated to the data
    
    :returns: AB magnitude and associated error
    :rtype: Astropy Quantity, Astropy Quantity
    '''

    flux  = u.Quantity(data * 10**(-(zeropoint+48.6)/2.5), unit='erg/(s*Hz*cm^2)')
    eflux = u.Quantity(err  * 10**(-(zeropoint+48.6)/2.5), unit='erg/(s*Hz*cm^2)')
    
    return flux, eflux
