Installation and setup
======================

.. _Astropy: https://www.astropy.org/>
.. _colorama: https://pypi.org/project/colorama/
.. _numpy: https://numpy.org/
.. _LePhare: https://www.cfht.hawaii.edu/~arnouts/LEPHARE/lephare.html
.. _Cigale: https://cigale.lam.fr/
.. _gfortran: http://gcc.gnu.org/fortran/

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

You can download LePhare SED fitting code `here <https://www.cfht.hawaii.edu/~arnouts/LEPHARE/download.html>`_ along with other SED libraries. Follow the `installation instructions <https://www.cfht.hawaii.edu/~arnouts/LEPHARE/install.html>`_ to properly install LePhare. 

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


Cigale_
#######

.. warning::

    Cigale not implemented yet.
    