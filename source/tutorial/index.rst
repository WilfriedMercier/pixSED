Tutorial introduction
=====================

.. _LePhare: lephare.html
.. _Cigale: cigale.html

This page gives a general overview of the behaviour of this library. For using a specific SED fitting code, please visit the following pages

.. toctree::
    :maxdepth: 1

    LePhare <lephare>
    Cigale <cigale>
    
.. important::
    
    This library is built to easily generate resolved maps of SED fitting codes output parameters performing pixel per pixel SED fitting on multi-band images.
    
    The functions and classes provided here are built to work on a **single resolved object**. 
    
    If you need to generate resolved SED-based maps for many galaxies, then you must loop on those objects rather than trying to do them all at once.
    
Nomenclature
------------

We briefly give below a description of the different classes/terms used in the following.

+--------------------------+-------------------------------------------------------------------------------------------------------------+
| Class/term               | Description                                                                                                 |
+==========================+=============================================================================================================+
| :py:class:`~.Catalogue`  | An intermediate object which contains preprocessed data to generate the SED fitting code configuration file |
+--------------------------+-------------------------------------------------------------------------------------------------------------+
| :py:class:`~.Filter`     | Object which stores data and variance map information relative to a **single** filter                       |
+--------------------------+-------------------------------------------------------------------------------------------------------------+
| :py:class:`~.FilterList` | Object which stores all the :py:class:`~.Filter` objects into a single one                                  |
+--------------------------+-------------------------------------------------------------------------------------------------------------+
| :py:class:`~.Output`     | Abstract object which can read output data from the SED fitting codes and produce resolved maps             |
+--------------------------+-------------------------------------------------------------------------------------------------------------+
| :py:class:`~.SED`        | Abstract object which includes methods to run the SED fitting code and read its output data                 |
+--------------------------+-------------------------------------------------------------------------------------------------------------+


Pre-processing step
-------------------

This library **does not apply** any pre-processing step onto the different multi-band images except those required so that the SED fitting codes work properly. Namely, this library assumes the following:

* All images have the same shape. If not, it will raise an Exception
* All images have the same pixel size and the same resolution (PSF)
* All images share the same centre
* All images have a corresponding **variance** map (square of error - similar shape). This map can include or not the noise from Poisson statistics.
* All images are supposed to be in units of :math:`\rm{e^{-}/s}`

Optionally, if one wants to add Poisson noise to the data, then the :code:`TEXPTIME` keyword must be present in the header of the loaded data.


Step 1: Building :py:class:`~.Filter` and :py:class:`~.FilterList` objects
----------------------------------------------------------------------------

To simplify the handling of FITS data files, each single-band image and its associated variance must be loaded into a :py:class:`~.Filter` object. Each :py:class:`~.Filter` object loads the data and variance, as well as their corresponding headers, and perform simple checks on data shape and useful header keywords.

.. code-block:: python

    import SED

    name = '1'
    file = f'example/{name}_105.fits'
    var  = f'example/{name}_105_variance.fits'
    zpt  = 26.27
    
    filt = SED.Filter(name, file, var, zpt, ext=0, extErr=0)
    
Four parameters have to be provided:

* **name** : Name of the filter. This name will be used later on when constructing the data table for the SED fitting code.
* **file** : Data file name
* **var** : Variance map file name
* **zpt** : Zeropoint corresponding to the filter. This zeropoint is used to convert the data and error maps from :math:`\rm{e^{-}/s}` to magnitude or flux values.

Optionally, if the data and/or variance maps have multiple extensions, one can provide the extension number with the :code:`ext` and :code:`extErr` keywords.

Once all the filters have been built, we combine them into a single :py:class:`~.FilterList` object. This object takes as input a list of all the :py:class:`~.Filter` objects, a mask, the redshift of the galaxy and the SED fitting code used:

.. code-block:: python
    
    code  = SED.SEDcode.LEPHARE      # Either SEDcode.LEPHARE or SEDcode.CIGALE
    z     = 0.6
    mask  = np.full(f1.shape, False) # True for bad pixels, False for good ones
    
    # We assume f1, f2, f3 respresent 3 Filter objects built as above
    flist = SED.FilterList([f1, f2, f3], mask, SEDcode=code, redshift=z)

As in the example above, if you do not have a mask, just provide an array with the same shape as the data and filled with False.

.. note::

    The mask must be the same between all filters.
    
By default, when the :py:class:`~.FilterList` object is constructed for the first time, it automatically calls :py:meth:`~.FilterList.setCode` method, which builds an Astropy Table with the data required by the given SED fitting code.

When building a table, a set of actions are performed on the data to process them. These actions depend on the given SED fitting code. In general, these are:

1. Mask bad pixels (including masked pixels and those with negative flux values)
2. Add (nor not) Poisson noise to the variance map
3. Optionally: scale data using a mean map and a scale factor
4. Map data and variance maps to 1D arrays
5. Compute std (square root of variance) map
6. Convert data and std maps into magnitude or flux values
7. Generate additional columns

If needed, the astropy Table can easily be retrieved as follows

.. code-block:: python

    table = flist.table
    
There are a few options one can change to get a different data processing, update the table and also return it:

.. code-block:: python

    newTable = flist.toTable(cleanMethod=CleanMethod.ZERO, scaleFactor=100, texpFac=0)

The different options are:

* **cleanMethod**: CleanMethod.ZERO (to put 0 if data is in flux unit or -99 if in magnitude on bad pixels) or CleanMethod.MIN (to put the minimum value of the good pixels on bad pixels)
* **texpFac**: exposure time factor which divides the exposure time found in the header of the data. This is only used if a Poisson noise is addes to the data. If 0, no Poisson noise is added.

Optionally, one can also pass these arguments when setting a new code:

.. code-block:: python

    flist.setCode(SED.SEDcode.LEPHARE, cleanMethod=CleanMethod.ZERO, scaleFactor=100, texpFac=0)


Step 2: Generate a :py:class:`~.Catalogue` object
-------------------------------------------------

To simplify the generation of the different input files required by the SED fitting code, a :py:class:`~.Catalogue` object must be generated. Each SED fitting code has its own catalogue:

* :py:class:`~.LePhareCat`
* :py:class:`~.CigaleCat`

The general syntax to produce a catalogue is

.. code-block:: python

    cat = flist.toCatalogue(*args, **kwargs) # Replace *args and **kwargs by the arguments and keyword argument specific to the catalogue

See LePhare_ and Cigale_ for SED fitting code specific information.

.. warning::

    Only :py:class:`~.LePhareCat` is implemented for now.


Step 3: Create a :py:class:`~.SED` object
-----------------------------------------

The input file creation, output file extraction and the interface allowing to run the SED fitting codes directly from python are all dealt with by a :py:class:`~.SED` object.

Each SED fitting code has its own :py:class:`~.SED` class which allows to blindly run the code and gather the output data:

* :py:class:`~.LePhareSED`
* :py:class:`~.CigaleSED`

Each SED object requires its own set of parameters (see LePhare_ and Cigale_ for SED fitting code specific information), but the general syntax is

.. code-block:: python

    sed = SED.LePhareSED('ID', *args, **kwargs) # Replace *args and **kwargs by the arguments and keyword argument specific to the SED object

where the first argument is always the idenfitier of the SED.

.. warning::

    Only :py:class:`~.LePhareSED` is implemented for now.
    
Step 4: Run the SED fitting
---------------------------

Once a :py:class:`~.SED` object has been created, one can start the SED fitting. Each SED fitting code has its own set of parameters but the general syntax is

.. code-block:: python

    params = ['MASS_BEST', 'SFR_BEST']
    output = sed(cat, outputParams=params, **kwargs) # Replace **kwargs by the keyword argument specific to the SED object

The first argument is always the catalogue. Additionally, one can pass the names of the output parameters one wants to retrieve from the SED fitting with the :code:`outputParam` keyword.

.. note::

    Running the fitting code will create a directory named after the identifier and generate various input and ouput file into it. All the information printed on screen are saved into a log file as well.
    
Running the SED fitting code returns an :py:class:`~.Output` object. Each code has its own ouput object:

* :py:class:`~.LePhareOutput`
* :py:class:`~.CigaleOutput`

See LePhare_ and Cigale_ for SED fitting code specific information.

.. warning::

    Only :py:class:`~.LePhareOutput` is implemented for now.

Step 5: Produce a resolved map
------------------------------

When the :py:class:`~.Output` object is created, data is loaded from the output file into an Astropy Table object. One can access the entire table or simply a column as follows:

.. code-block:: python

    table = output.table
    mass  = table['mass_best']
    
But, in this format the data are given as a 1D array. To generate a resolved map, one can use the :py:meth:`~.Output.toImage` method. However, one needs to provide the image shape and, depending on the code used (see LePhare_ and Cigale_ for SED fitting code specific information) a scale factor and a mean map.

Thus, a simpler way is to first link the :py:class:`~.Output` object to the :py:class:`~.FilterList` generated at the beginning and then call :py:meth:`~.FilterList.toImage` method. This ensures that all the necessary parameters are passed to recover an output resolved map which has the correct shape and which has been correctly scaled back.

.. code-block:: python

    output.link(flist)
    mass = output.toImage('mass_best')



