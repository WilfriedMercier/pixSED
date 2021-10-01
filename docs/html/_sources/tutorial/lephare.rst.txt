LePhare tutorial
================

This tutorial is specific to using LePhare SED fitting code. 


Step 1: Building :py:class:`~.Filter` and :py:class:`~.FilterList` objects
----------------------------------------------------------------------------

Creating :py:class:`~.Filter` and :py:class:`~.FilterList` objects for Lephare is similar to the general example. When creating the :py:class:`~.FilterList`, the following actions are performed:

1. Mask bad pixels (including masked pixels and those with negative flux values)
2. Add Poisson noise to the variance map
3. Compute a mean 2D map (spectral average)
4. Scale data dividing by the mean map and multiplying by a scale factor. This ensures the input magnitudes in LePhare have the correct order of magnitude for every pixel.
5. Map data and variance maps to 1D arrays
6. Compute std (square root of variance) map
7. Convert data and std maps into magnitudes
8. Generate additional columns for LePhare


If needed, the astropy Table can easily be retrieved as follows

.. code-block:: python

    table = flist.table
    
There are a few options one can change to get a different data processing, update the table and also return it:

.. code-block:: python

    newTable = flist.toTable(cleanMethod=CleanMethod.ZERO, scaleFactor=100, texpFac=0)

The different options are:

* **cleanMethod**: CleanMethod.ZERO (to put 0 if data is in flux unit or -99 if in magnitude on bad pixels) or CleanMethod.MIN (to put the minimum value of the good pixels on bad pixels)
* **scaleFactor**: Factor by which to multiply the data and std maps when scaling with the mean map
* **texpFac**: Exposure time factor which divides the exposure time found in the header of the data. This is only used if a Poisson noise is added to the data. If 0, no Poisson noise is added.


Optionally, one can also pass these arguments when setting a new code:

.. code-block:: python

    flist.setCode(SED.SEDcode.LEPHARE, cleanMethod=CleanMethod.ZERO, scaleFactor=100, texpFac=0)


Step 2: Generate a :py:class:`~.LePhareCat` object
--------------------------------------------------

The :py:class:`~.LePhareCat` object is used to easily save the input data to the correct format and write a formatted string used when generating LePhare parameter file. Assuming :code:`flist` is the :py:class:`~.FilterList` object:

.. code-block:: python

    gal        = '1'
    catalogue  = flist.toCatalogue(f'{gal}.in')

The first parameter is the name of the file where the catalogue will be saved. Optional parameters can be passed:

* **tunit**: TableUnit.MAG (data in magnitude) or TableUnit.FLUX (data in flux values)
* **magtype**: MagType.AB (AB magnitudes) or SED.MagType.VEGA (VEGA magnitudes)
* **tformat**: TableFormat.MEME (data and error columns intertwined), TableFormat.MMMEE (data and then error columns)
* **ttype**: TableType.LONG or TableType.SHORT

.. warning::

    **tunit**, **magtype**, **tformat** and **ttype** keyword arguments default values are sufficient when using :py:meth:`~.FilterList.toCatalogue` method.
    
    If needed, only modify them if you create your own :py:class:`~.LePhareCat` through the :py:meth:`~.LePhareCat.__init__` method.
    
    
Step 3: Create a :py:class:`~.LePhareSED` object
------------------------------------------------



.. code-block:: python

    prop = {'FILTER_LIST' : ['HST_ACS_WFC.F435W', 'HST_ACS_WFC.F606W', 'HST_ACS_WFC.F775W'],
            'ERR_SCALE'   : [0.03, 0.03, 0.03]
           }
    
    sed  = SED.LePhareSED('Gal1', properties=prop)
    
The first parameter is the name of the object. This is used to name the associated files and directories. The second parameter is a dictionary where the user can provide all the different SED parameters for LePhare. We give a brief list of the most useful ones below:

* **STAR_SED** [str]: stellar library list file (full path)
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

Step 4: Run the SED fitting
---------------------------

The :py:class:`~.LePhareSED` object can be directly called to run the SED fitting. In order to avoid to load all of LePhare parameters in the output file, a list of required parameter names (see :py:class:`~.LePhareOutputParam` for accepted values) must be passed as follows

.. code-block:: python

    params = ['MASS_INF', 'MASS_MED', 'MASS_SUP', 'SFR_INF', 'SFR_MED', 'SFR_SUP']
    output = sed(catalogue, outputParams=params)
    
When running the code, the output parameter values are extracted from the output parameters file and are stored into a :py:class:`~.LePhareOutput` object.

.. note::

    In order to perform the SED fitting, LePhare  generates a few files:

    * file.in: Input catalogue containing data
    * file.para: Parameter files with all the SED fitting properties
    * file.output_para: List of output parameters given in the output file
    * file.out: Output data file

The different values are stored in an Astropy table, with column names given by the :code:`.name` attribute of the :py:class:`~.LePhareOutputParam` values (e.g. the column name for :py:attr:`~.LePhareOutputParam.Z_BEST` parameter is given by :code:`LePhareOutputParam.Z_BEST.name` which is :code:`'z_best'`), and with the physical units stored.

.. important::

    Data given as log values in the output parameters file are converted into physical units.
    
    For instance, :py:attr:`~.LePhareOutputParam.MASS_MED` parameter is given as the decimal logarithm of the median mass in the output file, but the Astropy table gives the median mass.

    
Before performing the SED fitting, LePhare must generate a grid of models for the stars, galaxies and QSO. These models are saved into different files located in LePhare directory, so in practice they only need to be generated once, unless one needs a new grids of models.

**By default, calling the** :py:class:`~.LePhareSED` **object always generates all of the SED models and compute their magnitudes**. To disable one or more or the SED generation and/or magnitude computation, optional parameters can be passed as

.. code-block:: python

    params     = ['MASS_INF', 'MASS_MED', 'MASS_SUP', 'SFR_INF', 'SFR_MED', 'SFR_SUP']
    skipSED    = True # Skip SED generation
    skipFilter = True # Skip filters generations
    skipGal    = True # Skip galaxy magnitude computation
    skipQSO    = True # Skip QSO magnitude computation
    skipStar   = True # Skip stellar magnitude computation
    output     = sed(catalogue, outputParams=params, skipSEDgen=skipSED, skipFilterGen=skipFilter, skipMagQSO=skipQSO, skipMagStar=skipStar, skipMagGal=skipGal)

Step 4-bis: Extract output data from output file
------------------------------------------------

If you had already performed the SED fitting with this library or directly with LePhare and want to load the output parameters again, you can skip the SED fitting step and directly do instead

.. code-block:: python

    output = SED.LePhareOutput('file.out')

Step 5: Generate a resolved map
-------------------------------

Now that we have a :py:class:`~.LePhareOutputParam` object, we can produce a resolved map of any parameter in the Astropy table. The most general way to do this is as follows

.. code:: python

    shape = (100, 100)    # Shape of the image
    sfac  = 100           # Scale factor used when normalising the input data in FilterList
    param = 'mass_med'    # Column name in the Astropy table (output.table)
    mm    = flist.meanMap # Mean map used when normalising the input data in FilterList
    
    image = output.toImage('mass_med', shape=shape, scaleFactor=sfac, meanMap=mm)
    
    data  = image.data    # Data array
    unit  = image.unit    # Data Astropy unit

The first parameter is always the column name one wants to generate an image from. The keyword parameters are:

* **shape**: shape of the input and output image
* **scaleFactor**: scaling factor used to multiply the data when normalising them
* **meanMap**: mean map (spectral average) use to divide the data when normalising

Since **shape**, **scaleFactor** and **meanMap** are not straightforward to extract from the different objects created above, one can blindly provide them to the :py:class:`~.LePhareOutputParam` object beforehand and then easily call :py:meth:`~.LePhareOutputParam.toImage` method as follows

.. code:: python

    output.link(filterList)
    image = output.toImage('mass_med')
    data  = image.data
    unit  = image.unit
    
.. note::

    The generated output image is an Astropy Quantity, which means it is an array with a physical unit. To only get the data (e.g. for plotting) or the unit one can use the :code:`.data` and :code:`.unit` attributes as shown in the examples above.

