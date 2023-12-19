Examples
========

.. _os.path: https://docs.python.org/fr/3/library/os.path.html
.. _astropy.io.fits: https://docs.astropy.org/en/stable/io/fits/index.html

.. tab-set::

    .. tab-item:: Stellar mass map with `Cigale`_
    
        The goal of this example is to produce a resolved stellar mass map using `Cigale`_ as backend. First, we start by importing `os.path`_ module (to deal with paths independently of the OS), this library and `astropy.io.fits`_ to open the mask file.
        
        .. code-block:: python
            
            from   astropy.io import fits
            import pixSED     as     SED
            import os.path    as     opath

        We define the galaxy name which will be used to make a directory, the bands used for the SED fitting, their zeropoints and the absolute paths of the files containing the flux and variance maps. 
        
        .. note::
        
            In this example, the variance maps do not include Poisson noise so the code will add it in quadrature. To do so, we also provide the absolute paths of the files containing the flux maps convolved with the square of the PSF.
        
        .. code-block:: python
            
            galName    = '1'                                                                # Galaxy name
            zeropoints = [25.68, 26.51, 25.69, 25.94, 24.87, 26.27, 26.23, 26.45, 25.94]    # HST zeropoints
            redshift   = 0.622                                                              # Redshift of the galaxy
            bands      = ['435', '606', '775', '814', '850', '105', '125', '140', '160']    # Band name used in input file names
            band_names = [f'F{band}LP' if band == '850' else f'F{band}W' for band in bands] # Band names in Cigale
            
            dataFiles  = [] # Flux maps
            data2Files = [] # Flux maps convolved by the square of the PSF
            varFiles   = [] # Variance maps
            
            for band in bands:
            
               file    = opath.abspath(opath.join('data', f'{galName}_{band}.fits'))
               dataFiles.append(file)
            
               file2   = opath.abspath(opath.join('data', f'{galName}_{band}_PSF2.fits'))
               data2Files.append(file2)
            
               vfile   = opath.abspath(opath.join('data', f'{galName}_{band}_var.fits'))
               varFiles.append(vfile)
        
        We also need to manually open the mask file. It must be an array of :python:`True` and :python:`False` values, with :python:`True` for the pixels to mask.
        
        .. code-block:: python
            
            mfile   = opath.abspath(opath.join('data', f'{galName}_mask.fits'))
            with fits.open(mfile) as hdul:
               mask = hdul[0].data == 0
        
        Then, we build the :py:class:`~.FilterList`, include Poisson noise to the variance map (by passing :python:`data2` and :python:`texpFac`) and we convert it to a catalogue.
        
        .. note::
        
            For `Cigale`_, no need to normalise the data. Thus, :python:`scaleFactor` will not be used and can be omitted.
            
        .. code-block:: python
             
            filts      = []
            for band, data, data2, var, zpt in zip(bands, dataFiles, data2Files, varFiles, zeropoints):
               filts.append(SED.Filter(band, data, data2, var, zpt))
            
            flist      = SED.FilterList(filts, mask, 
                                        code=SED.SEDcode.LEPHARE, 
                                        redshift=redshift,
                                        cleanMethod=SED.CleanMethod.ZERO, 
                                        texpFac=4,
                                        #scaleFactor=1
                                       )
        
            catalogue  = flist.toCatalogue(galName)
        
        We now have the catalogue. However, we are still missing the SED modules and parameters to start the SED fitting. Any number of modules can be given but `Cigale`_ requires at least to provide one :py:class:`~pixSED.misc.cigaleModules.SFHmodule` and one :py:class:`~pixSED.misc.cigaleModules.SSPmodule`. We will use the following modules:
        
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
                                            
        With all the modules stored in different variables, we can now build a :py:class:`~.CigaleSED` object. This object will be used to start the SED fitting in the background and recover the output properties to reconstruct a stellar mass map.
               
        .. code-block:: python
                                                     
            sedobj = SED.CigaleSED(galName, band_names,
                                   uncertainties = [True]*len(band_names),
                                   SFH           = SFH,
                                   SSP           = SSP,
                                   nebular       = nebular,
                                   attenuation   = attenuation,
                                  )
                                  
        The :python:`uncertainties` argument controls for which bands the uncertainty is used during the fit. We give :python:`True` for all the bands since we want to use all the uncertainties. We can now run `Cigale`_ by providing the catalogue built previously, as well as a list of extra parameters.
        
        .. code-block:: python
            
            output = sedobj(catalogue,
                            ncores              = 8,           # Number of threads to use (to be updated)
                            physical_properties = None,        # None means all properties will be computed
                            bands               = band_names,  # We estimate the flux for all the bands
                            save_best_sed       = False,       # Whether to save in output FITS files the best sed
                            save_chi2           = False,       # Whether to save the chi2 for all models
                            lim_flag            = False,
                            redshift_decimals   = 2,
                            blocks              = 1
                           )
        
        Once the fit is complete, we can plot the stellar mass map. To do so, we can use the :python:`output` variable (of type :py:class:`~.CigaleOutput`). 
        
        .. note::
        
            For `Cigale`_, we must provide only the shape of the map we want to reconstruct. This can be done either when using the :py:meth:`~.CigaleOutput.toImage` method or by linking the original :py:class:`~.FilterList` object to the :python:`output` variable using the :py:meth:`~.CigaleOutput.link` method.
        
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
        
        .. jupyter-execute::
            :hide-code:
            
            import os.path           as     opath
            from   astropy.io        import fits
            import pixSED            as     SED
            
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
            
               file    = opath.abspath(opath.join('example', 'data', f'{galName}_{band}.fits'))
               dataFiles.append(file)
            
               file2   = opath.abspath(opath.join('example', 'data', f'{galName}_{band}_PSF2.fits'))
               data2Files.append(file2)
            
               vfile   = opath.abspath(opath.join('example', 'data', f'{galName}_{band}_var.fits'))
               varFiles.append(vfile)
            
            # Get mask file
            mfile      = opath.abspath(opath.join('example', 'data', f'{galName}_mask.fits'))
            with fits.open(mfile) as hdul:
               mask    = hdul[0].data == 0
            
            filts      = []
            for band, data, data2, var, zpt in zip(bands, dataFiles, data2Files, varFiles, zeropoints):
               filts.append(SED.Filter(band, data, var, zpt, file2=data2))
            
            flist      = SED.FilterList(filts, mask, 
                                        code=SED.SEDcode.LEPHARE, 
                                        redshift=redshift, 
                                        cleanMethod=SED.CleanMethod.ZERO,
                                        texpFac=4,
                                        #scaleFactor=1, 
                                       )
            
            output = SED.CigaleOutput(opath.join('example', galName, 'out', 'results.fits'))
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


    .. tab-item:: Stellar mass map with `LePhare`_
        
        In this example, we want to generate a resolved stellar mass map using `LePhare`_. We start by importing `os.path`_ module (to deal with paths independently of the OS), this library and `astropy.io.fits`_ to open the mask file.
        
        .. code-block:: python
            
            from   astropy.io import fits
            import os.path    as     opath
            import pixSED     as     SED      
            
        We define the galaxy name, the bands used, their zeropoints and the absolute path of the flux and variance maps.
        
        .. note::
        
            In this example, the variance maps do not include Poisson noise so the code will add it in quadrature. To do so, we also provide the absolute paths of the files containing the flux maps convolved with the square of the PSF.
        
        .. code-block:: python
            
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
        
        We also need to manually open the mask file. It must be an array of :python:`True` and :python:`False` values, with :python:`True` for pixels to be masked.
        
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
        
        .. code-block:: python
            
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
        
        .. jupyter-execute::
            :hide-code:
            
            import os.path           as     opath
            from   astropy.io        import fits
            import pixSED            as     SED
            
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
            
               file    = opath.abspath(opath.join('example', 'data', f'{galName}_{band}.fits'))
               dataFiles.append(file)
            
               file2   = opath.abspath(opath.join('example', 'data', f'{galName}_{band}_PSF2.fits'))
               data2Files.append(file2)
            
               vfile   = opath.abspath(opath.join('example', 'data', f'{galName}_{band}_var.fits'))
               varFiles.append(vfile)
            
            # Get mask file
            mfile      = opath.abspath(opath.join('example', 'data', f'{galName}_mask.fits'))
            with fits.open(mfile) as hdul:
               mask    = hdul[0].data == 0
            
            ###   1. Generate a FilterList object   ###
            filts      = []
            for band, data, data2, var, zpt in zip(bands, dataFiles, data2Files, varFiles, zeropoints):
               filts.append(SED.Filter(band, data, var, float(zpt),
                                       file2   = data2,
                                       verbose = False
                                      ))
            
            flist      = SED.FilterList(filts, mask, code=SED.SEDcode.LEPHARE, redshift=redshift)
            
            ###   2. Update data table and add Poisson noise (texpFac != 0)   ###
            flist.genTable(cleanMethod=SED.CleanMethod.ZERO, scaleFactor=100, texpFac=4)
            
            ###   6. Generate a resolved stellar mass map   ###
            output = SED.LePhareOutput(opath.join('example', galName, f'{galName}.out'))
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
    
    
    .. tab-item:: Load a SFR map from an output file from `LePhare`_
        
        This example follows from the previous one. Thus, it is assumed that the SED fitting has already been performed with `LePhare`_ and that there is an associated output file named :file:`example/1/{1.out}`.
        
        Because fluxes had to be scaled up in order to be processed by `LePhare`_, we will need the mean map, scale factor and exposure time in order to scale back the extensive output properties (including mass and SFR). First, we must start by building the :py:class:`~.FilterList` oject:
        
        .. code:: python
        
            from   astropy.io import fits
            import os.path    as     opath
            import pixSED     as     SED
        
            galName    = '1'
            zeropoints = [25.68, 26.51, 25.69, 25.94, 24.87, 26.27, 26.23, 26.45, 25.94]
            redshift   = 0.622
            bands      = ['435', '606', '775', '814', '850', '105', '125', '140', '160']
            
            dataFiles  = []
            data2Files = [] # flux maps convolved by the square of the PSF
            varFiles   = []
            
            for band in bands:
            
               file    = opath.abspath(opath.join('data', f'{galName}_{band}.fits'))
               dataFiles.append(file)
               
               file2   = opath.abspath(opath.join('data', f'{galName}_{band}_PSF2.fits'))
               data2Files.append(file2)
            
               vfile   = opath.abspath(opath.join('data', f'{galName}_{band}_var.fits'))
               varFiles.append(vfile)
               
            mfile      = opath.abspath(opath.join('data', f'{galName}_mask.fits'))
            with fits.open(mfile) as hdul:
               mask    = hdul[0].data == 0
                  
            filts      = []
            for band, data, data2, var, zpt in zip(bands, dataFiles, data2Files, varFiles, zeropoints):
               filts.append(sed.Filter(band, file, file2, var, zpt))
            
            flist      = SED.FilterList(filts, mask, code=SED.SEDcode.LEPHARE, redshift=redshift)
            flist.genTable(cleanMethod=SED.CleanMethod.ZERO, scaleFactor=100, texpFac=4)
            
        This :py:class:`~.FilterList` object now contains all the information required to scale back the data to the right unit. So, we just have to recover the output from LePhare and link the :py:class:`~.FilterList` to this object.
        
        .. code:: python
        
            output = sed.LePhareOutput('1/1.out')
            output.link(flist)
            
        We can now generate a resolved map for the median SFR
        
        .. code:: python
        
            from   matplotlib        import rc
            import matplotlib        as     mpl
            import matplotlib.pyplot as     plt
                
            rc('font', **{'family': 'serif', 'serif': ['Times']})
            rc('text', usetex=True)
            mpl.rcParams['text.latex.preamble'] = r'\usepackage{newtxmath}'
            rc('figure', figsize=(5, 4.5))
        
            sfr = output.toImage('sfr_med')
            
            plt.imshow(sfr.data, origin='lower', cmap='rainbow')
            plt.xlabel('X [pixel]', size=13)
            plt.ylabel('Y [pixel]', size=13)
            
            cbar = plt.colorbar(ret, orientation='vertical', shrink=0.9)
            cbar.set_label(r'SFR [M$_{\odot}$ yr$^{-1}$]', size=13)
            plt.show()
            
        .. jupyter-execute::
            :hide-code:
            
            import os.path           as     opath
            from   astropy.io        import fits
            import pixSED            as     SED
            
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
            
               file    = opath.abspath(opath.join('example', 'data', f'{galName}_{band}.fits'))
               dataFiles.append(file)
            
               file2   = opath.abspath(opath.join('example', 'data', f'{galName}_{band}_PSF2.fits'))
               data2Files.append(file2)
            
               vfile   = opath.abspath(opath.join('example', 'data', f'{galName}_{band}_var.fits'))
               varFiles.append(vfile)
            
            # Get mask file
            mfile      = opath.abspath(opath.join('example', 'data', f'{galName}_mask.fits'))
            with fits.open(mfile) as hdul:
               mask    = hdul[0].data == 0
            
            ###   1. Generate a FilterList object   ###
            filts      = []
            for band, data, data2, var, zpt in zip(bands, dataFiles, data2Files, varFiles, zeropoints):
               filts.append(SED.Filter(band, data, var, zpt, file2=data2, verbose=False))
            
            flist      = SED.FilterList(filts, mask, code=SED.SEDcode.LEPHARE, redshift=redshift)
            
            ###   2. Update data table and add Poisson noise (texpFac != 0)   ###
            flist.genTable(cleanMethod=SED.CleanMethod.ZERO, scaleFactor=100, texpFac=4)
            
            ###   6. Generate a resolved stellar mass map   ###
            output = SED.LePhareOutput(opath.join('example', galName, f'{galName}.out'))
            output.link(flist)
            mass_star  = output.toImage('sfr_med')
            
            ###   7. Plot   ###
            from   matplotlib        import rc
            import matplotlib        as     mpl
            import matplotlib.pyplot as     plt
                
            rc('font', **{'family': 'serif', 'serif': ['Times']})
            rc('text', usetex=True)
            mpl.rcParams['text.latex.preamble'] = r'\usepackage{newtxmath}'
            rc('figure', figsize=(5, 4.5))
        
            sfr = output.toImage('sfr_med')
            
            ret = plt.imshow(sfr.data, origin='lower', cmap='rainbow')
            plt.xlabel('X [pixel]', size=13)
            plt.ylabel('Y [pixel]', size=13)
            
            cbar = plt.colorbar(ret, orientation='vertical', shrink=0.9)
            cbar.set_label(r'SFR [M$_{\odot}$ yr$^{-1}$]', size=13)
            plt.show()
            
