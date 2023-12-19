#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
.. codeauthor:: Wilfried Mercier - IRAP/LAM <wilfried.mercier@lam.fr>

Load and show a SFR map from an already existing output of a LePhare run.
"""

import os.path           as     opath
from   astropy.io        import fits
import pixSED            as     sed

from   matplotlib        import rc
import matplotlib        as     mpl
import matplotlib.pyplot as     plt

galName    = '1'
zeropoints = [25.68, 26.51, 25.69, 25.94, 24.87, 26.27, 26.23, 26.45, 25.94]
redshift   = 0.622
bands      = ['435', '606', '775', '814', '850', '105', '125', '140', '160']

dataFiles  = [] # flux maps
data2Files = [] # flux maps convolved by the square of the PSF
varFiles   = [] # variance maps

# Get file names
for band in bands:

   file    = opath.abspath(opath.join('data', f'{galName}_{band}.fits'))
   dataFiles.append(file)

   file2   = opath.abspath(opath.join('data', f'{galName}_{band}_PSF2.fits'))
   data2Files.append(file2)

   vfile   = opath.abspath(opath.join('data', f'{galName}_{band}_var.fits'))
   varFiles.append(vfile)

# Get mask
mfile      = opath.abspath(opath.join('data', f'{galName}_mask.fits'))
with fits.open(mfile) as hdul:
   mask    = hdul[0].data == 0

# Generate filters list
filts      = []
for band, data, data2, var, zpt in zip(bands, dataFiles, data2Files, varFiles, zeropoints):
   filts.append(sed.Filter(band, file, var, zpt, file2=file2))

flist      = sed.FilterList(filts, mask, code=sed.SEDcode.LEPHARE, redshift=redshift)
flist.genTable(cleanMethod=sed.CleanMethod.ZERO, scaleFactor=100, texpFac=4)

# Create LePhare output from output file and filters list
output = sed.LePhareOutput('1/1.out')
output.link(flist)

# Show SFR map
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
