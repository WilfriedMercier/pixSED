.. toctree::
    :hidden:
    :maxdepth: 2
    
    setup
    nomenclature
    poisson
    examples
    API/index
    
Introduction
============
    
This library provides an interface that allows to **seamlessly perform resolved/pixel-per-pixel SED fitting** using either `Cigale`_ or `LePhare`_ as backend. Thus, this code is not a new SED fitting package but instead relies on pre-installed SED fitting codes. It does however 

1. significantly simplify the procedure to obtain spatially resolved maps of physical parameters (e.g. stellar mass) and
2. retain the full flexibility of the underlying SED fitting codes to potentially perform complex modellings.

For information on how to install the code and the SED backends, check the :doc:`Setup page <setup>`. The general workflow to perform resolved SED fitting with this library is as follows:

* For each band, load data into a :py:class:`~.Filter` object and then combine thoses objects together, along with shared information, into a single :py:class:`~.FilterList` object.
* Choose the SED fitting code backend.
* Transform this :py:class:`~.FilterList` object into a :py:class:`~.Catalogue` object. This new object will be used by this library to automatically parse the input data into a catalogue with the right format for the selected SED fitting code. 
* Create a :py:class:`~.SED` object. Each backend has its own parameters that are specific to the selected SED fitting code. This object contains the SED models and parameters used during the fit.
* Run the SED fitting and recover an :py:class:`~.Output` object which contains the output data, as well as methods to reconstruct the spatially resolved maps.
* Plot the resulting resolved map.
* Optionally, if the SED fitting was performed previously, load the output data into an :py:class:`~.Output` object before plotting the results.

Tutorial
========
    
Below we provide a step-by-step tutorial with both Cigale_ and LePhare_ as backend. 

Pre-processing
--------------

Independently of the backend used, a few assumptions are always made by the code when starting pixel-per-pixel SED fitting. Namely:

.. dropdown:: The code is run on a single galaxy at a single redshift
    :animate: fade-in-slide-down
    
    To run the code on multiple galaxies, the only option that is currently available is to loop on those galaxies and perform resolved SED fitting onto them one by one.

.. dropdown:: Data and variance maps are available in all bands
    :animate: fade-in-slide-down
    
    Data and variance maps are **mandatory**. The variance map can exclude Poisson noise contribution, in which case the code will add it in quadrature if the relevant parameters are provided. Optionally, a mask/segmentation map can be provided to accelerate the fit by only fitting relevant pixels.
    
.. dropdown:: Data, variance, and mask maps all have the same shape, WCS, pixel scale, and spatial resolution
    :animate: fade-in-slide-down

    The code will not perform any re-centering, frame rotation, pixel scale or resolution matching between bands. **These steps must be manually performed beforehand**.
    
.. dropdown:: Spatial resolution is sufficiently high (i.e. small PSF) to fit each pixel separately
    :animate: fade-in-slide-down
    
    The code fits pixels one by one. In practice, the smearing of the PSF should be taken into account by fitting all pixels at once but this is not supported by any backend SED fitting code at the moment.

.. dropdown:: Images can be parsed to :math:`\,\rm erg\,s^{-1}\,Hz^{-1}\,cm^{-2}`
    :animate: fade-in-slide-down

    The backend SED fitting codes are designed to handle flux density units. So the images should have a corresponding zeropoint that allows to perform such a conversion. Variance maps should be parsable to :math:`\,\rm erg^2\,s^{-2}\,Hz^{-2}\,cm^{-4}`.

Loading data
------------

Creating :py:class:`~.Filter` objects
#####################################

Whatever the backend, the first step is to load the data. To do so, two classes must be used: :py:class:`~.Filter` and :py:class:`~.FilterList`. First, we start by creating one :py:class:`~.Filter` per band we want to fit:

.. code-block::

    import pixSED as SED

    filt_435w = SED.Filter('F435W', 'data_F435W.fits', 'var_F435W.fits', 25.68, file2 = None)

Here, we consider the HST F435W band with the data stored in the file :file:`data_F435W.fits` and the variance map in the file :file:`var_F435W.fits`. In this example, the data are in units of :math:`\rm e^{-}\,s^{-1}` and the zeropoint :math:`{\rm zpt} = 25.68` allows to convert the data to :math:`\rm erg\,s^{-1}\,Hz^{-1}\,cm^{-2}` and the variance map to :math:`\,\rm erg^2\,s^{-2}\,Hz^{-2}\,cm^{-4}`.

.. note::

    The keyword argument :python:`file2` is optional and allows the user to provide a FITS file name that contains the data image squared. This image is used to compute the Poisson noise contribution if it is not already present in the given variance map.
    
    **To not add Poisson noise to the variance map, please use** :python:`file2 = None`.

.. important::

    The input data can be given in any unit as long as the zeropoint allows to convert them to :math:`\rm erg\,s^{-1}\,Hz^{-1}\,cm^{-2}`. The formal definition used by the code for the conversion is as follows:
    
    .. math::
    
        d_{\rm conv} = d_{\rm original} \times 10^{-({\rm zpt} + 48.6) / 2.5},
        
    where :math:`d_{\rm conv}` is the data image converted to :math:`\rm erg\,s^{-1}\,Hz^{-1}\,cm^{-2}`, :math:`d_{\rm original}` is the original image given by the user, and :math:`\rm zpt` is the zeropoint given by the user. The same zeropoint will be used to convert the variance map.
    
    Thus, **the unit of the variance map must always be the square of the unit of the data image**.

.. _referenceToFilterList:

Combining :py:class:`~.Filter` objects into a :py:class:`~.FilterList`
######################################################################

Assuming, we have created the following HST filters :python:`filt_435w, filt_606w, filt_775w` as above, we can now combine them into a single :py:class:`~.FilterList` object.

.. tab-set::

    .. tab-item:: Using Cigale_ as backend
    
        .. code:: python
        
            flist = SED.FilterList([filt_435w, filt_606w, filt_775w], None, 
                                   code     = SED.SEDcode.CIGALE, 
                                   redshift = 1.1
                                  )
                              
        where the first argument is the list of :py:class:`~.Filter` objects, the second argument is a boolean mask (of type ndarray_) with the same shape as the input data that must contain :python:`True` for bad pixels to mask and :python:`False` for good pixels to fit. If :python:`None`, no mask is applied (i.e. all pixels in the image are fitted). 
        
        The :python:`redshift` keyword argument will be the same for all pixels.

    .. tab-item:: Using LePhare_ as backend

        Contrary to Cigale_, LePhare_ does not properly handle low fluxes. Thus, the data and the variance map must be scaled up before running the SED fitting and the extensive output properties from LePhare_ will have to be scaled down afterwards. The code can handle that automatically with an additional keyword:

        .. code:: python
        
            flist = SED.FilterList([filt_435w, filt_606w, filt_775w], 
                                   code        = SED.SEDcode.LEPHARE, 
                                   redshift    = 1.1,
                                   scaleFactor = 100
                                  )

        where the first argument is the list of :py:class:`~.Filter` objects, the second argument is a boolean mask (of type ndarray_) with the same shape as the input data that must contain :python:`True` for bad pixels to mask and :python:`False` for good pixels to fit. If :python:`None`, no mask is applied (i.e. all pixels in the image are fitted). 
        
        The :python:`redshift` keyword argument will be the same for all pixels.

        In the example above, the data and its standard deviation will be first normalised and then scaled up by a factor of 100.

        .. note::
        
            In practice, the data are normalised as follows:
            
            * a mean map is computed. This map is the average for each pixel along the spectral dimension.
            * the data in each band is normalised by the mean map
            * the normalised data are scaled up by the value of :python:`scaleFactor`

.. note::

    The keyword argument :python:`scaleFactor` will only be used if the SED fitting code is LePhare_.
        
When the  :py:class:`~.FilterList` object is created, the :py:meth:`~.FilterList.setCode` method is automatically called with the given SED fitting code. This creates an intermediate `Astropy Table`_ where the input data are stored. This table will then have to be converted into a :py:class:`~.Catalogue` afterwards (see :ref:`here <referenceToCatalogue>`).
        
(Optional) Adding Poisson noise in quadrature
#############################################

Some error maps (or related data products such as HST weight maps) do not contain Poisson noise, in which case it should be added in quadrature. This code can handle that automatically with a few important details to keep in mind.

In practice, for Poisson noise to be added, the :python:`file2` keyword argument sould be provided to the relevant :py:class:`~.Filter` objects. This keyword must be the name of a FITS file containing the input data convolved by the square of the PSF. 

.. note::

    When loading the data, the code will look for the exposure time in the FITS header keyword :python:`'TEXPTIME'`. If not found, a value of 1 will be assumed.
    
When the methods :py:meth:`~.FilterList.setCode` or :py:meth:`~.FilterList.genTable` are called (either automatically or by the user), it is possible to pass an extra argument to divide the value of the exposure time:

.. code:: python

    flist.genTable(texpFac=10) 
    
In this example, the exposure time will be divided by a factor of 10 when computing the Poisson noise contribution to the total variance. If :python:`texpFac` is equal to 0, no Poisson noise will be added.

.. important::

    The user interested in adding Poisson noise to some of their variance maps is encouraged to read attentively this :doc:`page <poisson>`.

        
(Optional) Recovering and updating the intermediate table
#########################################################

The interested user can recover the intermediate `Astropy Table`_ as follows

.. code:: python

    table = flist.table
    
Furthermore, the values in this table can be updated using the :py:meth:`~.FilterList.genTable` method. For instance to scale up the fluxes and uncertainties by a factor 100, one can do

.. code:: python
    
    flist.genTable(scaleFactor=100) 
    
Similarly, to change the bad pixel cleaning method, one can do

.. code:: python
    
    flist.genTable(cleanMethod=SED.misc.enum.CleanMethod.ZERO) 
    
.. note::

    The code automatically cleans bad pixels which are identified as having either a negative flux or a negative variance. Two cleaning methods are proposed:

    - :py:attr:`pixSED.misc.enum.CleanMethod.ZERO` which replaces bad pixels by a flux equal to 0 and 
    - :py:attr:`pixSED.misc.enum.CleanMethod.MIN` which replaces bad pixels with the minimum value in the masked image.

There is also the possibility to update the SED fitting code backend as follows:

.. code:: python

    flist.setCode(SED.SEDcode.LEPHARE)
    
.. _referenceToCatalogue:

Generate a :py:class:`~.Catalogue` object
-----------------------------------------

Because each SED fitting code expects the input data to be parsed to different formats, each code as its own :py:class:`~.Catalogue` object that manages this parsing automatically. In each case, the catalogue creation is done as follows:

.. code-block:: python

    catalogue  = flist.toCatalogue('example')
    
where the first argument corresponds to the name of the output file (without extension) that will contain the catalogue used by the SED fitting code. For `Cigale`_, this will create a :py:class:`~.CigaleCat` object, whereas for `LePhare`_ this will create a :py:class:`~.LePhareCat` object. 

.. note::

    For `LePhare`_, other parameters can be given. Please refer to :py:class:`~.LePhareCat` init method for further details.


Create a :py:class:`~.SED` object
---------------------------------

After creating the catalogue that will contain the input data, we need to initialise the parameters of the SED fitting code along with specifying the models used for the SED fitting. `Cigale`_ and `LePhare`_ have different models and ways to handle them, so each has its own :py:class:`~.SED` object to initialise:

.. tab-set::

    .. tab-item:: Using Cigale_ as backend
    
        `Cigale`_ works with modules that can be combined together. This includes modules such as star formation histories, single stellar populations, dust attenuation, dust emission, etc. The full list of modules that are supported by this library are listed :doc:`here <API/misc/cigaleModules/index>`.
                
        In this example, let us define a star-formation history, single stellar population, nebular emission, and dust attenuation as follows:
                
        .. code:: python
                
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

        Then, we can initialise the :py:class:`~.CigaleSED` object as follows:
        
        .. code:: python
        
            sedobj = SED.CigaleSED('example', ['F435W', 'F606W', 'F775W'],
                                   uncertainties = [True]*len(band_names),
                                   SFH           = SFH,
                                   SSP           = SSP,
                                   nebular       = nebular,
                                   attenuation   = attenuation,
                                  )
        
        where :python:`'example'` is the name of the directory within which the output files will be stored, :python:`['F435W', 'F606W', 'F775W']` is the list of filters to use for the SED fitting. The argument :python:`uncertainties` can be used to define for which filters the uncertainties should be used in the fit. 
        
    .. tab-item:: Using LePhare_ as backend
        
        
        .. code-block:: python
        
            prop = {'FILTER_LIST' : ['HST_ACS_WFC.F435W', 'HST_ACS_WFC.F606W', 'HST_ACS_WFC.F775W'],
                    'ERR_SCALE'   : [0.03, 0.03, 0.03]
                   }
            
            sed  = SED.LePhareSED('example', properties=prop)
            
        where :python:`'example'` is the name of the directory within which the output files will be stored. The keyword argument :python:`properties` must be a dictionary that stores the different SED parameters for LePhare_. We give a brief list of the most useful ones below:
        
        * **STAR_SED** [:python:`str`]: stellar library list file (full path)
        * **QSO_SED** [str]: QSO list file (full path)
        * **GAL_SED** [str]: galaxy library list file (full path)
        * **AGE_RANGE** [list[float]]: minimum and maximum ages in years
        * **FILTER_LIST** [list[str]]: list of filter names used for the fit (must all be located in $LEPHAREDIR/filt directory)
        * **Z_STEP** [list[int/float]]: redshift step properties. Values are: redshift step, max redshift, redshift step for redshifts above 6 (coarser sampling).
        * **COSMOLOGY** [list[int/float]]: cosmology parameters. Values are: Hubble constant H0, baryon fraction Omegam0, cosmological constant fraction Omegalambda0.
        * **MOD_EXTINC** [list[int/float]]: minimum and maximum model extinctions
        * **EXTINC_LAW** [str]: extinction law file (in $LEPHAREDIR/ext)
        * **EB_V** [list[int/float]]: color excess E(B-V). It must contain less than 50 values.
        * **EM_LINES** [str]: whether to consider emission lines or not. Accepted values are 'YES' or 'NO'.
        * **ERR_SCALE** [list[int/float]]: magnitude errors per band to add in quadrature
        * **ERR_FACTOR** [int/float]: scaling factor to apply to the errors
        * **ZPHOTLIB** [list[str]]: librairies used to compute the Chi2. Maximum number is 3.
        * **ADD_EMLINES** [str]: whether to add emission lines or not (dupplicate with **EM_LINES** ?). Accepted values are 'YES' or 'NO'.
        
        For the complete list of options, see :py:class:`~.LePhareOutputParam` values (upper case names).

Resolved SED fitting
--------------------

Run the SED fitting
###################

.. tab-set::

    .. tab-item:: Using Cigale_ as backend
        
        `Cigale`_ can now be easily launched as follows
        
        .. code:: python
            
            output = sedobj(catalogue,
                            ncores              = 8,           
                            physical_properties = None,       
                            bands               = ['F435W', 'F606W', 'F775W'],
                            save_best_sed       = False,
                            save_chi2           = False,
                            lim_flag            = False,
                            blocks              = 1
                           )
                           
        The first argument is the :py:class:`~.CigaleCat` object created above. Then, additional keyword arguments can be passed:
        
        * :python:`ncores`: number of threads to use for parallelisation
        * :python:`physical_properties`: a list of physical property names to be computed. Providing :python:`physical_properties = None` will result in all the physical properties being computed.
        * :python:`bands`: the bands for which to estimate the fluxes in the output file
        * :python:`save_best_sed`: whether to save the best-fit SED **for each pixel being fitted**
        * :python:`save_chi2`: whether to save the chi2 **for each pixel being fitted**
        * :python:`lim_flag`: whether to consider upper limits or not
        * :python:`blocks`: number of subdivisions for the data if there are too many pixels to be fitted
    
        This library automatically extracts output parameters and stores them into the :python:`output` variable as a :py:class:`~.CigaleOutput` object.
    
    .. tab-item:: Using LePhare_ as backend
            
        The :py:class:`~.LePhareSED` object can be directly called to run the SED fitting. In order to avoid to load all of LePhare parameters in the output file, a list of required parameter names (see :py:class:`~.LePhareOutputParam` for accepted values) must be passed as follows
        
        .. code:: python
        
            params = ['MASS_INF', 'MASS_MED', 'MASS_SUP', 'SFR_INF', 'SFR_MED', 'SFR_SUP']
            output = sed(catalogue, outputParams=params)        

        The SED fitting code then executes in the background. When running, LePhare_ generates various files: 
        
        * file.in: Input catalogue containing data
        * file.para: Parameter files with all the SED fitting properties
        * file.output_para: List of output parameters given in the output file
        * file.out: Output data file
        
        This library automatically extracts those output parameters and stores them into the :python:`output` variable as a :py:class:`~.LePhareOutput` object.
                
        .. important::
        
            Data given as log values in the LePhare_ output parameter file are converted into physical units.
            
            For instance, :py:attr:`~.LePhareOutputParam.MASS_MED` parameter is given by LePhare_ by default as the decimal logarithm of the median mass in solar masses. But, in the :py:class:`~.LePhareOutput` object it corresponds to the median mass in solar masses.

            
        Before performing the SED fitting, LePhare_ must generate a grid of models for the stars, galaxies and QSO. These models are saved into different files located in LePhare_ directory, so in practice they only need to be generated once, unless one needs a new grids of models.
        
        **By default, calling the** :py:class:`~.LePhareSED` **object always generates all of the SED models and compute their magnitudes**. To disable one or more or the SED generation and/or magnitude computation, optional parameters can be passed as
        
        .. code-block:: python
        
            params     = ['MASS_INF', 'MASS_MED', 'MASS_SUP', 'SFR_INF', 'SFR_MED', 'SFR_SUP']
            
            skipSED    = True # Skip SED generation
            skipFilter = True # Skip filters generations
            skipGal    = True # Skip galaxy magnitude computation
            skipQSO    = True # Skip QSO magnitude computation
            skipStar   = True # Skip stellar magnitude computation
            
            output     = sed(catalogue, outputParams=params, 
                             skipSEDgen    = skipSED, 
                             skipFilterGen = skipFilter, 
                             skipMagQSO    = skipQSO, 
                             skipMagStar   = skipStar, 
                             skipMagGal    = skipGal
                            )

Extract data from a previous run
################################

Alternatively, if the SED fitting was already run beforehand, it is possible to directly load the data without doing the fit again by directly calling :py:class:`~.CigaleOutput` or :py:class:`~.LePhareOutput`:

.. tab-set::

    .. tab-item:: Using Cigale_ as backend
    
        .. code:: python
        
            output = SED.CigaleOutput('example/out/results.fits')

    .. tab-item:: Using Cigale_ as backend
        
        .. code:: python
        
            output = SED.LePhareOutput('example/example.out')

Plot a resolved map
-------------------

Both :py:class:`~.CigaleOutput` and :py:class:`~.LePhareOutput` have a utility class that allows to reconstruct a 2D ndarray_ with the same shape as the input images and with the mask applied.

.. tab-set::

    .. tab-item:: Using Cigale_ as backend
    
        For Cigale_, the only arguments that need to be passed are the parameter name to produce the resolved map for (here :python:`'bayes.stellar.m_star'`) and the shape of the image:

        .. code:: python
        
            image = output.toImage('bayes.stellar.m_star', shape=(100, 100))
    
    .. tab-item:: Using LePhare_ as backend
    
        For LePhare_, more arguments are required in order to scale back the resolved map to the right unit. The first argument is the parameter name to produce the resolved map for (here :python:`'mass_med'`) and then one needs to provide
        
        * the shape of the image,
        * the scale factor used to normalise the data (in this example 100)
        * the mean map used to normalise the data (which is stored in :py:attr:`~.FilterList.meanMap`)
    
        .. code:: python
        
            image = output.toImage('mass_med', 
                                   shape       = (100, 100),
                                   scaleFactor = 100, 
                                   meanMap     = flist.meanMap
                                  )
            
.. note::

    The variable :python:`image` is an `Astropy Quantity`_. Its unit can be recovered with :python:`image.unit` and its values in any unit (e.g. solar masses) as an ndarray_ with :python:`image.to('Msun').value`
    
.. note::
        
    Since :python:`shape`, :python:`scaleFactor` and :python:`meanMap` are not straightforward to find, a utility method can be used to recover them automatically:
    
    .. code:: python
    
        output.link(flist)
        image = output.toImage('bayes.stellar.m_star')
        
    where :python:`output` is the :py:class:`~.CigaleOutput` or :py:class:`~.LePhareOutput` object from above and :python:`flist` is the :py:class:`~.FilterList` object created :ref:`here <referenceToFilterList>`.
    
We can now generate a resolved stellar mass map:

.. code:: python

    from   matplotlib        import rc
    import matplotlib        as     mpl
    import matplotlib.pyplot as     plt
        
    rc('font', **{'family': 'serif', 'serif': ['Times']})
    rc('text', usetex=True)
    mpl.rcParams['text.latex.preamble'] = r'\usepackage{newtxmath}'
    rc('figure', figsize=(5, 4.5))
    
    plt.imshow(np.log10(image.to('Msun').value), origin='lower', cmap='rainbow', vmin=6)
    plt.xlabel('X [pixel]', size=13)
    plt.ylabel('Y [pixel]', size=13)
    
    cbar = plt.colorbar(ret, orientation='vertical', shrink=0.9)
    cbar.set_label(r'$\log_{10}$ M$_{\star}$ [M$_{\odot}$]', size=13)
    plt.show()
    
.. jupyter-execute::
    :hide-code:
    
    import os.path           as     opath
    from   astropy.io        import fits
    import pixSED            as     SED
    import numpy             as     np
    
    from   matplotlib        import rc
    import matplotlib        as     mpl
    import matplotlib.pyplot as     plt
    
    # Define data file names
    galName    = '1'                                                             # Galaxy number
    zeropoints = [25.68, 26.51, 25.69, 25.94, 24.87, 26.27, 26.23, 26.45, 25.94] # HST zeropoints
    redshift   = 0.622                                                           # Redshift of the galaxy
    bands      = ['435', '606', '775', '814', '850', '105', '125', '140', '160'] # Bands
    band_names = ['F435W', 'F606W', 'F775W', 'F814W', 'F850LP', 'F105W', 'F125W', 'F140W', 'F160W']
    
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
    
    flist      = SED.FilterList(filts, mask, code=SED.SEDcode.CIGALE, redshift=redshift)
    
    ###   2. Update data table and add Poisson noise (texpFac != 0)   ###
    flist.genTable(cleanMethod=SED.CleanMethod.ZERO, texpFac=1)
    
    ###   6. Generate a resolved stellar mass map   ###
    output = SED.CigaleOutput(opath.join('example', galName, 'out', 'results.fits'))
    output.link(flist)
    
    mass_star  = np.log10(output.toImage('bayes.stellar.m_star').to('Msun').value)
    
    ###   7. Plot   ###
    from   matplotlib        import rc
    import matplotlib        as     mpl
    import matplotlib.pyplot as     plt
        
    rc('font', **{'family': 'serif', 'serif': ['Times']})
    rc('text', usetex=True)
    mpl.rcParams['text.latex.preamble'] = r'\usepackage{newtxmath}'
    rc('figure', figsize=(5, 4.5))
    
    ret = plt.imshow(mass_star, origin='lower', cmap='rainbow', vmin=6)
    plt.xlabel('X [pixel]', size=13)
    plt.ylabel('Y [pixel]', size=13)
    
    cbar = plt.colorbar(ret, orientation='vertical', shrink=0.9)
    cbar.set_label(r'$\log_{10}$ M$_{\star}$ [M$_{\odot}$]', size=13)
    plt.show()