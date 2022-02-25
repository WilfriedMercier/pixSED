Example 1: Generating a resolved stellar mass map with LePhare
==============================================================

.. _os.path: https://docs.python.org/fr/3/library/os.path.html
.. _SED: https://github.com/WilfriedMercier/SED
.. _astropy.io.fits: https://docs.astropy.org/en/stable/io/fits/index.html

.. role:: python(code)
  :language: python
  :class: highlight

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
    galName    = '1'                                                             # Galaxy number
    zeropoints = [25.68, 26.51, 25.69, 25.94, 24.87, 26.27, 26.23, 26.45, 25.94] # HST zeropoints
    redshift   = 0.622                                                           # Redshift of the galaxy
    bands      = ['435', '606', '775', '814', '850', '105', '125', '140', '160'] # Bands
    band_names = ['ACS_WFC.F435W', 'ACS_WFC.F606W', 'ACS_WFC.F775W',             # Names of the band for LePhare
                  'ACS_WFC.F814W', 'ACS_WFC.F850LP', 'WFC3_IR.F105W',
                  'WFC3_IR.F125W', 'WFC3_IR.F140W', 'WFC3_IR.F160W']
    
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

Then, we build the filter list, update the table to include Poisson noise to the variance map and convert it to a catalogue

.. code-block:: python
     
    filts      = []
    for band, data, data2, var, zpt in zip(bands, dataFiles, data2Files, varFiles, zeropoints):
       filts.append(SED.Filter(band, data, data2, var, zpt))
    
    flist      = SED.FilterList(filts, mask, code=SED.SEDcode.LEPHARE, redshift=redshift)
    flist.genTable(cleanMethod=SED.CleanMethod.ZERO, scaleFactor=100, texpFac=4)
    catalogue  = flist.toCatalogue(f'{galName}')

We also need to make a sed object. To do so, we provide a few parameters, namely the filters file names (relative to :file:`{$LEPHAREDIR}/filt` directory) and the quadratic errors added to each filter

.. code-block:: python
    
    hst_filt   = [] # Filter names for LePhare
    err        = [] # Quadratic errors to add to the magnitudes of each band
    
    for band in band_names:
       filt    = opath.join('hst_perso', f'HST_{band}')
       hst_filt.append(filt)
       err.append(0.03)
    
    properties = {'FILTER_LIST' : hst_filt, 'ERR_SCALE' : err}
    sed        = SED.LePhareSED(galName, properties=properties)

We can now run LePhare linking the data catalogue and providing a list of parameters to extract from the SED fitting

.. code-block:: python
    
    params     = ['MASS_BEST', 'MASS_INF', 'MASS_MED', 'MASS_SUP', 'SFR_BEST', 'SFR_INF', 'SFR_MED', 'SFR_SUP']
    skip       = {'skipSEDgen' : True, 'skipFilterGen' : True, 'skipMagGal' : True, 'skipMagQSO' : True, 'skipMagStar' : True}
    output     = sed(catalogue, outputParams=params, **skip)

To generate a resolved stellar mass map we need to provide additional parameters. The simplest method is to link the filter list to the output object

.. code:: python
    
    from   matplotlib        import rc
    import matplotlib        as     mpl
    import matplotlib.pyplot as     plt
    
    output.link(flist)
    mass_star = output.toImage('mass_med')
    
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
    band_names = ['ACS_WFC.F435W', 'ACS_WFC.F606W', 'ACS_WFC.F775W',             # Names of the band for LePhare
                  'ACS_WFC.F814W', 'ACS_WFC.F850LP', 'WFC3_IR.F105W',
                  'WFC3_IR.F125W', 'WFC3_IR.F140W', 'WFC3_IR.F160W']
    
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
    
    ###   1. Generate a FilterList object   ###
    filts      = []
    for band, data, data2, var, zpt in zip(bands, dataFiles, data2Files, varFiles, zeropoints):
       filts.append(SED.Filter(band, data, data2, var, zpt))
    
    flist      = SED.FilterList(filts, mask, code=SED.SEDcode.LEPHARE, redshift=redshift)
    
    ###   2. Update data table and add Poisson noise (texpFac != 0)   ###
    flist.genTable(cleanMethod=SED.CleanMethod.ZERO, scaleFactor=100, texpFac=4)
    
    ###   6. Generate a resolved stellar mass map   ###
    output = SED.LePhareOutput(opath.join('..', '..', 'example', galName, f'{galName}.out'))
    output.link(flist)
    mass_star  = output.toImage('mass_med')
    
    ###   7. Plot   ###
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