About Poisson noise
===================

In order for Poisson noise to be correctly added to the variance map, a few important details must be understood first.

Theoretical considerations
--------------------------

We assume that for each pixel :math:`(x, y)` on the detector, there is a signal :math:`S(x, y)` which follows a Poisson distribution with an average value (and variance) :math:`\lambda (x,y)`. We also assume that the signal is high enough so that :math:`S` is a good approximation of :math:`\lambda`. This implies that :math:`Var [ S ] \approx S`.

In practice, the variance is not just due to Poisson noise but also to other sources of noise (e.g. readout) which we combine into an additional term :math:`\sigma^2`. The total variance is therefore:

.. math::

    \sigma^2_{\rm tot} (x, y) = S (x, y) + \sigma^2,
    
where :math:`S` and :math:`\sigma^2` must be in units of counts or :math:`e^-`. 

In the expression above, :math:`S` represents the signal measured in a pixel without convolution. With convolution, the signal becomes

.. math::

    S' (x, y) = \sum_{x', y'} {\rm PSF} (x' - x, y' - y) S(x', y').
    
It can be shown (e.g. see Appendix D of `Mercier W. PhDT <https://hal.science/tel-04104122v1>`_) that in such a case and when neglecting covariance between pixels, the variance of :math:`S'` writes

.. math::

    {\rm Var} [S'] (x, y) = \sum_{x', y'} {\rm PSF}^2 (x' - x, y' - y) \sigma^2_{\rm tot} (x', y'),
    
which can be rewritten as

.. math::

    {\rm Var} [S'] (x, y) = \tilde \sigma^2 (x, y) + \sum_{x', y'} {\rm PSF}^2 (x' - x, y' - y) {\rm Var} [S] (x', y'),
    
where :math:`\tilde \sigma^2 (x, y)` is the variance map without Poisson noise (but convolved, hereafter background variance). Finally, remembering that :math:`Var [ S ] \approx S`, we can simplify the expression to

.. math::

    {\rm Var} [S'] (x, y) = \tilde \sigma^2 (x, y) + \tilde S (x, y),
    
where :math:`\tilde S` is the input image convolved by the square of the PSF (and still in units of counts or :math:`e^-`).

Practical implementation
------------------------

If Poisson noise is missing from the input variance map, this code will assume that the variance map provided by the user corresponds to :math:`\tilde \sigma^2`. To add Poisson noise, the first step is to provide the name of a file that contains :math:`\tilde S`, that is the data convolved by the square of the PSF, when creating the :py:class:`~.Filter` objects:

.. code:: python

    filt_435w = SED.Filter('F435W', 'data_F435W.fits', 'var_F435W.fits', 25.68, 
                           file2 = 'data_conv2_F435W.fits'
                          )
 
Dealing with units
------------------

.. _referenceToes:

Data in :math:`e^-\,s^{-1}`
###########################
 
Because this code was developed with HST images in mind, it assumes that the input data and the data convolved by the square of the PSF are in :math:`e^-\,s^{-1}`, and that the variance maps are in :math:`e^-\,s^{-2}`. The code will read from the input image the FITS header keyword :python:`'TEXPTIME'` which will be used to convert the variance to the right unit. The conversion is done with the following reasoning:

* If :math:`\tilde \sigma^2` is the background variance in :math:`e^-\,s^{-2}`, then its value in :math:`e^-` must be given by :math:`\tilde \sigma^2 \times T_e^2`, where :math:`T_e` is the exposure time.
* If :math:`\tilde S` is the signal in :math:`e^-\,s^{-1}`, then its value in :math:`e^-` must be given by :math:`\tilde S \times T_e`.
* If :math:`{\rm Var} [S']` is the total variance in :math:`e^-\,s^{-2}`, then its value in :math:`e^-` must be given by :math:`{\rm Var} [S'] \times T_e^2`.

Therefore, using the expression for :math:`{\rm Var} [S']` and the conversions between :math:`e^-` and :math:`e^-\,s^{-2}` given above, we find that the total variance in :math:`e^-\,s^{-2}` writes

.. math::

    {\rm Var} [S']  (x, y) = \tilde \sigma^2 (x, y) + \tilde S (x, y) / T_e,
    
where :math:`\tilde \sigma^2` is the background variance map in :math:`e^-\,s^{-2}` and :math:`\tilde S` is the data in :math:`e^-\,s^{-1}`.

Data in other units
###################

The methods :py:meth:`~.FilterList.setCode` or :py:meth:`~.FilterList.genTable` can be called with an extra argument to divide the value of the exposure time. For instance

.. code:: python

    flist.genTable(texpFac=10) 
    
will divide the exposure time by a factor of 10 when computing the Poisson noise contribution to the total variance. If :python:`texpFac` is equal to 0, no Poisson noise will be added. 

This argument can be used to properly handle Poisson noise with data that are not in :math:`e^-\,s^{-1}`. Indeed, let us assume that the data are in an arbitrary unit :math:`u`, which can be converted to :math:`e^-\,s^{-1}` with a scale factor :math:`f` (i.e. :math:`S [u] = f \times S [e^-\,s^{-1}]`). Then,

* If :math:`\tilde \sigma^2` is the background variance in unit :math:`u^2`, its value in :math:`e^-` must be given by :math:`\tilde \sigma^2 \times T_e^2 / f^2`
* If :math:`\tilde S` is the signal in unit :math:`u`, then its value in :math:`e^-` must be given by :math:`\tilde S \times T_e / f`.
* If :math:`{\rm Var} [S']` is the total variance in unit :math:`u^2`, then its value in :math:`e^-` must be given by :math:`{\rm Var} [S'] \times T_e^2 / f^2`.

Following the same logic as in :ref:`the previous section <referenceToes>`, the total variance in unit :math:`u^2` writes

.. math::

    {\rm Var} [S']  (x, y) = \tilde \sigma^2 (x, y) + f \times \tilde S (x, y) / T_e,
    
where :math:`\tilde \sigma^2` is the background variance map in unit :math:`u^2` and :math:`\tilde S` is the input data convolved by the square of the PSF in unit :math:`u`.
    
Thus, the keyword argument :python:`texpFac` can be used as a conversion factor to properly compute the contribution of the Poisson noise to the total variance.

Data in :math:`e^-`
###################

If the data are in electrons, then no unit conversion is required. The simplest solution is therefore to read the exposure time from the FITS file header and provide it as a scale factor:

.. code:: python

    from astropy.io import fits
    
    with fits.open('data_F435W.fits') as hdul:
        texp = hdul[0].header['TEXPTIME']
    
    flist.genTable(texpFac=texp)