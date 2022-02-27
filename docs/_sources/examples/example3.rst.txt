Example 3: Generating a resolved stellar mass map with Cigale
=============================================================

.. _os.path: https://docs.python.org/fr/3/library/os.path.html
.. _SED: https://github.com/WilfriedMercier/SED
.. _astropy.io.fits: https://docs.astropy.org/en/stable/io/fits/index.html

We start by importing `os.path`_ module (useful to deal with paths between different OS), this library (`SED`_) and `astropy.io.fits`_ to open the mask file.

We define the galaxy name, the bands used, their zeropoints and the absolute path of the flux and variance maps. Note that in this case our variance maps do not include Poisson noise so we need to add it. To do so, we also provide the flux maps convolved with the square of the PSF.

.. code-block:: python
    
    import os.path           as     opath
    from   astropy.io        import fits
    import SED
    
    from   matplotlib        import rc
    import matplotlib        as     mpl
    import matplotlib.pyplot as     plt
    
    # Define data file names
    galName    = '1'                                                                # Galaxy number
    zeropoints = [25.68, 26.51, 25.69, 25.94, 24.87, 26.27, 26.23, 26.45, 25.94]    # HST zeropoints
    redshift   = 0.622                                                              # Redshift of the galaxy
    bands      = ['435', '606', '775', '814', '850', '105', '125', '140', '160']    # Bands
    band_names = [f'F{band}LP' if band == '850' else f'F{band}W' for band in bands] # Bands names in Cigale
    
    dataFiles  = [] # Flux maps
    data2Files = [] # Flux maps convolved by the PSF squared
    varFiles   = [] # Variance maps
    
    for band in bands:
    
       file    = opath.abspath(opath.join('data', f'{galName}_{band}.fits'))
       dataFiles.append(file)
    
       file2   = opath.abspath(opath.join('data', f'{galName}_{band}_PSF2.fits'))
       data2Files.append(file2)
    
       vfile   = opath.abspath(opath.join('data', f'{galName}_{band}_var.fits'))
       varFiles.append(vfile)

We also need to manually open the mask file (must be an array of :python:`True` and :python:`False` values)

.. code-block:: python
    
    mfile      = opath.abspath(opath.join('data', f'{galName}_mask.fits'))
    with fits.open(mfile) as hdul:
       mask    = hdul[0].data == 0

Then, we build the filter list, include Poisson noise to the variance map (by passing :python:`texpFac != 0`) and convert it to a catalogue object

.. code-block:: python
     
    filts      = []
    for band, data, data2, var, zpt in zip(bands, dataFiles, data2Files, varFiles, zeropoints):
       filts.append(SED.Filter(band, data, data2, var, zpt))
    
    flist      = SED.FilterList(filts, mask, 
                                code=SED.SEDcode.LEPHARE, 
                                redshift=redshift,
                                cleanMethod=SED.CleanMethod.ZERO, 
                                scaleFactor=1, 
                                texpFac=4)

    catalogue  = flist.toCatalogue(galName)

.. note::

    We do not normalise the data as for LePhare since it is not necessary in Cigale. Thus, whathever :python:`scaleFactor` value is fine (it will not be used).

We also need to make a sed object. To do so, we must define the modules Cigale will use for the SED fitting. Among these, at least one SFH and one SSP modules must be provided

.. code-block:: python
    
    # Star formation history module to use
    SFH        = [SED.cigmod.SFHDELAYEDBQmodule(tau_main  = [250, 500, 1000, 2000, 4000, 6000, 8000],
                                                age_main  = [2500, 5000, 7500, 10000, 12500],
                                                age_bq    = [10, 25, 50, 75, 100, 150, 200],
                                                r_sfr     = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0, 1.25, 1.5, 1.75, 2.0, 5.0, 10.0],
                                                sfr_A     = [1.0],
                                                normalise = True
                                               )]

    # Single Stellar population module to use
    SSP        = [SED.cigmod.BC03module(imf            = SED.IMF.CHABRIER,
                                        separation_age = [8],
                                        metallicity    = [0.02]
                                   )] 

    # Nebular emission module to use
    nebular    = [SED.cigmod.NEBULARmodule(logU             = [-2.0],
                                           f_esc            = [0.0],
                                           f_dust           = [0.0],
                                           lines_width      = [300.0],
                                           include_emission = True
                                         )]

    # Dust attenuation module to use
    attenuation = [SED.cigmod.DUSTATT_POWERLAWmodule(Av_young           = [0.0, 0.25, 0.5, .75, 1.0, 1.25, 1.5, 1.75, 2.0, 2.25, 2.5, 2.75, 3.0],
                                                     Av_old_factor      = [0.44],
                                                     uv_bump_wavelength = [217.5],
                                                     uv_bump_width      = [35.0],
                                                     uv_bump_amplitude  = [0.0, 1.5, 3.0],
                                                     powerlaw_slope     = [-0.7],
                                                     filters            = ' & '.join(band_names)
                                                    )]
                                                    
    sedobj      = SED.CigaleSED(galName, band_names,
                                uncertainties = [True]*len(band_names),
                                SFH           = SFH,
                                SSP           = SSP,
                                nebular       = nebular,
                                attenuation   = attenuation,
                              )

We give :python:`True` for all the bands since we want to use the uncertainties on all of them. We can now run Cigale linking the data catalogue and providing a list of parameters to extract from the SED fitting (in our case we extract all parameters using :python:`None`)

.. code-block:: python
    
    output = sedobj(catalogue,
                    ncores              = 8,           # Number of threads to use (to be updated)
                    physical_properties = None,        # None means all properties will be computed
                    bands               = band_names,  # We estimate the flux for all the bands
                    save_best_sed       = False,
                    save_chi2           = False,
                    lim_flag            = False,
                    redshift_decimals   = 2,
                    blocks              = 1
                   )

To generate a resolved stellar mass map we need to provide additional parameters. The simplest method is to link the filter list to the output object

.. code:: python
    
    from   matplotlib        import rc
    import matplotlib        as     mpl
    import matplotlib.pyplot as     plt
    
    output.link(flist)
    mass_star = output.toImage('best.stellar.m_star')
    
    rc('font', **{'family': 'serif', 'serif': ['Times']})
    rc('text', usetex=True)
    mpl.rcParams['text.latex.preamble'] = r'\usepackage{newtxmath}'
    rc('figure', figsize=(5, 4.5))
    
    ret = plt.imshow(mass_star.data, origin='lower', cmap='rainbow')
    plt.xlabel('X [pixel]', size=13)
    plt.ylabel('Y [pixel]', size=13)
    
    cbar = plt.colorbar(ret, orientation='vertical', shrink=0.9)
    cbar.set_label(r'$M_{\star}$ [M$_{\odot}$]', size=13)
    plt.show()

.. plot::
    
    import os.path           as     opath
    from   astropy.io        import fits
    import SED
    
    from   matplotlib        import rc
    import matplotlib        as     mpl
    import matplotlib.pyplot as     plt
    
    # Define data file names
    galName    = '1'                                                             # Galaxy number
    zeropoints = [25.68, 26.51, 25.69, 25.94, 24.87, 26.27, 26.23, 26.45, 25.94] # HST zeropoints
    redshift   = 0.622                                                           # Redshift of the galaxy
    bands      = ['435', '606', '775', '814', '850', '105', '125', '140', '160'] # Bands
    band_names = [f'F{band}LP' if band == '850' else f'F{band}W' for band in bands] # Bands names in Cigale
    
    dataFiles  = [] # Flux maps
    data2Files = [] # Flux maps convolved by the PSF squared
    varFiles   = [] # Variance maps
    
    for band in bands:
    
       file    = opath.abspath(opath.join('..', '..', 'example', 'data', f'{galName}_{band}.fits'))
       dataFiles.append(file)
    
       file2   = opath.abspath(opath.join('..', '..', 'example', 'data', f'{galName}_{band}_PSF2.fits'))
       data2Files.append(file2)
    
       vfile   = opath.abspath(opath.join('..', '..', 'example', 'data', f'{galName}_{band}_var.fits'))
       varFiles.append(vfile)
    
    # Get mask file
    mfile      = opath.abspath(opath.join('..', '..', 'example', 'data', f'{galName}_mask.fits'))
    with fits.open(mfile) as hdul:
       mask    = hdul[0].data == 0
    
    filts      = []
    for band, data, data2, var, zpt in zip(bands, dataFiles, data2Files, varFiles, zeropoints):
       filts.append(SED.Filter(band, data, data2, var, zpt))
    
    flist      = SED.FilterList(filts, mask, 
                                code=SED.SEDcode.LEPHARE, 
                                redshift=redshift, 
                                cleanMethod=SED.CleanMethod.ZERO,
                                scaleFactor=1, 
                                texpFac=4
                               )
    
    output = SED.CigaleOutput(opath.join('..', '..', 'example', galName, 'out', 'results.fits'))
    output.link(flist)
    mass_star  = output.toImage('best.stellar.m_star')
    
    rc('font', **{'family': 'serif', 'serif': ['Times']})
    rc('text', usetex=True)
    mpl.rcParams['text.latex.preamble'] = r'\usepackage{newtxmath}'
    rc('figure', figsize=(5, 4.5))
    
    ret = plt.imshow(mass_star.data, origin='lower', cmap='rainbow')
    plt.xlabel('X [pixel]', size=13)
    plt.ylabel('Y [pixel]', size=13)
    
    cbar = plt.colorbar(ret, orientation='vertical', shrink=0.9)
    cbar.set_label(r'$M_{\star}$ [M$_{\odot}$]', size=13)
    plt.show()