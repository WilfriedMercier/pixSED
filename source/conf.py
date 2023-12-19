#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
.. codeauthor:: Hugo Plombat - LUPM <hugo.plombat@umontpellier.fr> & Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>

Configuration script for Sphinx documentation.
"""

def skip(app, what, name, obj, would_skip, options):
    if name == "__init__":
        return False
    return would_skip

###################################################
#               Project information               #
###################################################

project            = 'pixSED'
copyright          = '2023, Wilfried Mercier'
author             = 'Wilfried Mercier'
show_authors       = True

highlight_options  = {'default': {'lexers.python.PythonLexer'},
                     }

extensions         = ['sphinx.ext.autodoc',
                      'sphinx.ext.mathjax',
                      'sphinx.ext.viewcode',
                      'sphinx.ext.autosummary',
                      'sphinx.ext.intersphinx',
                      'jupyter_sphinx',
                      "sphinx_design"
                     ]

# The full version, including alpha/beta/rc tags
release            = '1.0'

# Add any paths that contain templates here, relative to this directory.
templates_path     = ['_templates']
exclude_patterns   = []

#######################################################
#               Options for HTML output               #
#######################################################

#html_theme         = 'karma_sphinx_theme'
#html_theme = "sphinxawesome_theme"
# html_logo          = "path/to/my/logo.png"
html_theme = "pydata_sphinx_theme"


html_title = 'pixSED'

# Force light mode by default
html_context = {"default_mode" : "light"}

html_theme_options = {
    "icon_links": [
        {
            # Label for this link
            "name": "GitHub",
            
            # URL where the link will redirect
            "url": "https://github.com/WilfriedMercier/SED",
            
            # Icon class (if "type": "fontawesome"), or path to local image (if "type": "local")
            "icon": "fa-brands fa-square-github",
            
            # The type of image to be used (see below for details)
            "type": "fontawesome",
        }],
    
    "announcement" : "Support for LePhare is currently deprecated as it relies on the old Fortran version. Please use Cigale instead.",
    "show_nav_level" : 2
}

# Add sypport for custom css file
html_static_path = ["_static"]
html_css_files   = ["mycss.css"]

html_collapsible_definitions = True

rst_prolog = """
.. role:: python(code)
  :language: python
  :class: highlight
  
.. _Astropy Table: https://docs.astropy.org/en/stable/api/astropy.table.Table.html#astropy.table.Table
.. _Astropy Quantity: https://docs.astropy.org/en/stable/units/quantity.html
.. _Astropy Header: https://docs.astropy.org/en/stable/io/fits/api/headers.html
.. _ndarray: https://numpy.org/doc/stable/reference/generated/numpy.array.html
.. _Cigale: https://cigale.lam.fr/
.. _LePhare: https://cesam.lam.fr/lephare/lephare.html
"""

