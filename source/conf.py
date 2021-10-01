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

project            = 'Resolved SED-fitting wrapper'
copyright          = '2021, Wilfried Mercier'
author             = 'Wilfried Mercier'
show_authors       = True

highlight_options  = {'default': {'lexers.python.PythonLexer'},
                     }

extensions         = ['sphinx.ext.autodoc',
                      'sphinx.ext.imgmath',
                      'sphinx.ext.viewcode',
                      'sphinx.ext.autosummary',
                      'matplotlib.sphinxext.plot_directive',
                      #'sphinx_copybutton',
                      'sphinx_execute_code',
                      'sphinx.ext.intersphinx'
                     ]

# The full version, including alpha/beta/rc tags
release            = '0.5'

# Add any paths that contain templates here, relative to this directory.
templates_path     = ['_templates']
exclude_patterns   = []

#######################################################
#               Options for HTML output               #
#######################################################

html_theme         = 'karma_sphinx_theme'
# html_logo          = "path/to/my/logo.png"
'''
html_theme_options = {'navigation_depth': 1}
'''
