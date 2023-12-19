#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
.. codeauthor:: Hugo Plombat - LUPM <hugo.plombat@umontpellier.fr> & Wilfried Mercier - IRAP/LAM <wilfried.mercier@lam.fr> & Maxime Tarrasse - IRAP <Maxime.Tarrasse@irap.omp.eu>

Photometry functions.
"""

from   typing        import Union, Tuple
import numpy         as     np
import astropy.units as     u

def countToMag(data: Union[float, np.ndarray], err: Union[float, np.ndarray], zeropoint: float) -> Tuple[Union[float, np.ndarray], Union[float, np.ndarray]]:
    r'''
    .. codeauthor:: Hugo Plombat - LUPM <hugo.plombat@umontpellier.fr> & Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>
    
    Convert data counts and their associated error into AB magnitudes using the formula
    
    .. math::
        
        d [{\rm{mag}}] = -2.5 \log_{10} d [{\rm{e^{-}/s}}] + {\rm{zpt}}
        
    where :math:`d` is the data and :math:`\rm{zpt}` is the magnitude zeropoint. The error is given by
    
    .. math::
        
        \Delta d [{\rm{mag}}] = 1.08 \Delta d [{\rm{e^{-}/s}}] / d [{\rm{e^{-}/s}}]
    
    :param data: data in :math:`\rm{e^{-1}/s}`
    :type data: :python:`float` or `ndarray`_ [:python:`float`]
    :param err: std errors in :math:`\rm{e^{-1}/s}`
    :type err: :python:`float` or `ndarray`_ [:python:`float`]
    :param zeropoint: zeropoint associated to the data
    :type zeropoint: :python:`float`
    
    :returns: AB magnitude and associated error
    :rtype: (:python:`float` or `ndarray`_ [:python:`float`], :python:`float` or `ndarray`_ [:python:`float`]
    '''

    mag  = -2.5 * np.log10(data) + zeropoint
    emag = 1.08 * err/data
    
    return mag, emag

def countToFlux(data: Union[float, np.ndarray], err: Union[float, np.ndarray], zeropoint: float) -> Tuple[u.Quantity, u.Quantity]:
    r'''
    .. codeauthor:: Hugo Plombat - LUPM <hugo.plombat@umontpellier.fr> & Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>
    
    Convert data counts and their associated error into flux in :math:`\rm{erg/cm^2/s/Hz}`.
    
    :param data: data in :math:`electron/s`
    :type data: :python:`float` or `ndarray`_ [:python:`float`]
    :param err: std errors in :math:`\rm{e^{-1}/s}`
    :type err: :python:`float` or `ndarray`_ [:python:`float`]
    :param zeropoint: zeropoint associated to the data
    :type zeropoint: :python:`float`
    
    :returns: flux in :math:`\rm{erg/cm^2/s/Hz}` and associated error
    :rtype: (`Astropy Quantity`_, `Astropy Quantity`_)
    '''

    flux  = u.Quantity(data * 10**(-(zeropoint+48.6)/2.5), unit='erg/(s*Hz*cm^2)')
    eflux = u.Quantity(err  * 10**(-(zeropoint+48.6)/2.5), unit='erg/(s*Hz*cm^2)')
    
    return flux, eflux

def FluxToCount(flux: Union[float, np.ndarray, u.Quantity], eflux: Union[float, np.ndarray, u.Quantity], zeropoint: float) -> Tuple[Union[float, np.ndarray], Union[float, np.ndarray]]:
    r'''
    .. codeauthor:: Hugo Plombat - LUPM <hugo.plombat@umontpellier.fr> & Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>
    
    Convert flux values and their associated error into dta count in :math:`\rm{e^{-}/s}`.
    
    :param flux: flux in :math:`\rm{erg/cm^2/s/Hz}`. If provided as an Astropy Quantity it will be parsed to this unit.
    :type flux: :python:`float`, `ndarray`_ [:python:`float`] or `Astropy Quantity`_
    :param eflux: std errors in :math:`\rm{erg/cm^2/s/Hz}`. If provided as an Astropy Quantity it will be parsed to this unit.
    :type eflux: :python:`float`, `ndarray`_ [:python:`float`] or `Astropy Quantity`_
    :param zeropoint: zeropoint associated to the data
    :type zeropoint: :python:`float`
    
    :returns: data count in :math:`\rm{e^{-}/s}` and associated error
    :rtype: (:python:`float` or `ndarray`_ [:python:`float`], :python:`float` or `ndarray`_ [:python:`float`])
    '''
    
    if isinstance(flux, u.Quantity):
        flux  = flux.to( 'erg/(s*Hz*cm^2)').value
        eflux = eflux.to('erg/(s*Hz*cm^2)').value
        
    fac   = 10**((zeropoint+48.6)/2.5)
    count = flux * fac
    err   = flux * fac
    
    return count, err

def MagTocount(mag: Union[float, np.ndarray], emag: Union[float, np.ndarray], zeropoint: float) -> Tuple[Union[float, np.ndarray], Union[float, np.ndarray]]:
    r'''
    .. codeauthor:: Maxime Tarrasse - IRAP <Maxime.Tarrasse@irap.omp.eu>

    Converts magnitudes and their associated error into data counts and their associated errors.
    
    :param mag: AB magnitude 
    :type mag: :python:`float` or `ndarray`_ [:python:`float`]
    :param emag: error on AB magnitudes
    :type emag: :python:`float` or `ndarray`_ [:python:`float`]
    :param zeropoint: zeropoint associated to the data
    :type zeropoint: :python:`float`

    :returns : data in :math:`\rm{e^{-}/s}` and associated errors
    :rtype: (:python:`float` or `ndarray`_ [:python:`float`], :python:`float` or `ndarray`_ [:python:`float`])
    '''	

    data = 10**((zeropoint-mag)/2.5)
    err  = data*emag/1.08
	
    return data, err
	


