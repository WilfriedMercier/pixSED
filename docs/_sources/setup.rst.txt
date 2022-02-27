Installation and setup
======================

.. _Astropy: https://www.astropy.org/>
.. _colorama: https://pypi.org/project/colorama/
.. _numpy: https://numpy.org/
.. _gfortran: http://gcc.gnu.org/fortran/
.. _LePhare: https://www.cfht.hawaii.edu/~arnouts/LEPHARE/download.html
.. _LePhare documentation: https://www.cfht.hawaii.edu/~arnouts/LEPHARE/install.html
.. _Cigale: https://gitlab.lam.fr/gyang/cigale/tree/xray
.. _Cigale documentation: https://cigale.lam.fr/documentation

.. role:: bash(code)

    :language: bash

This guide is supposed to help the user in setting up the environment for this library to work.

.. important::   
 
    This library has been developed with **Python 3.7**. We list below the version used during developement for each required dependency. 
    
    Note that it is possible that this library still works with older or more recent versions of these dependencies.
    
To install this library, just clone the repository directly into one of your python module paths

.. code:: bash

    git clone https://github.com/WilfriedMercier/SED.git

If you do not know your module path names, you can list them from the terminal with

.. code:: bash

    python -c 'import sys; print(sys.path)'
    
Alternatively, one can clone the repository into another directory and then make a symbolic link of this directory into one of the module paths, or add this directory to the module paths list.

Required dependencies
---------------------

A couple of third party dependencies are required in order for this library to work. See below for how to install them on Linux/Mac OS.

+-----------+---------+------------------------------+--------------------------------------------+
| Library   | Version | Installation (pip)           | Installation (conda)                       |
+===========+=========+==============================+============================================+
| Astropy_  | 4.2     | :bash:`pip install astropy`  | :bash:`conda install astropy`              |
+-----------+---------+------------------------------+--------------------------------------------+
| colorama_ | 0.4.4   | :bash:`pip install colorama` | :bash:`conda install -c anaconda colorama` |
+-----------+---------+------------------------------+--------------------------------------------+
| numpy_    | 1.19.5  | :bash:`pip install numpy`    | :bash:`conda install numpy`                |
+-----------+---------+------------------------------+--------------------------------------------+

SED fitting codes installation
------------------------------

Here we provide links and information on how to properly setup the environment of these codes to work properly with this library.

LePhare_
########

You can download LePhare SED fitting code `LePhare`_ along with other SED libraries. Follow `LePhare documentation`_ to properly install LePhare. 

.. note::

    This SED library uses by default Bruzual and Charlot 2003 SSP library. It is recommended to install it along LePhare in order to run the examples.

In order to compile LePhare, you need to have Fortran installed on your machine (e.g. gfortran_).

.. important::

    In order for this python library to work, you must define **two environment variables**:

    * **LEPHAREDIR** : main LePhare directory
    * **LEPHAREWORK** : working LePhare directory
        
    Easiest way is to edit your :bash:`~/.bashrc` file in your :bash:`$HOME` directory and write:
    
    .. code:: bash
    
        export LEPHAREDIR=pathtoLEPHAREDIR
        export LEPHAREWORK=pathtoLEPHAREWOR
        
    Do not forget to update it once saved
    
    .. code:: bash
    
        . ~/.bashrc

.. note::

    This library uses by default custom HST filters. These are provided in :file:`additional_files/{lephare}/filters` directory. It is recommended to add them into LePhare filters list in order to run the examples. On Linux and MacOS, this can be done using :file:`additional_files/lephare/{addFilters.sh}` with the command lines
    
    .. code:: bash
    
        cd additional_files/lephare
        ./addFilters.sh


Cigale_
#######

You can download the latest version of X-Cigale `Cigale`_. Follow `Cigale documentation`_ to properly install Cigale.
    
.. note::

    This library uses by default custom HST filters. These are provided in :file:`additional_files/{cigale}/filters` directory. It is recommended to add them into LePhare filters list in order to run the examples. On Linux and MacOS, this can be done using :file:`additional_files/cigale/{addFilters.sh}` with the command lines
    
    .. code:: bash
    
        cd additional_files/cigale
        ./addFilters.sh