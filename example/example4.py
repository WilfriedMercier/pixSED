#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
.. codeauthor:: Wilfried Mercier - IRAP/LAM <wilfried.mercier@lam.fr>

Load and show a resolved stellar mass map using Cigale SED fitting code.
"""

import numpy                as     np
import os.path              as     opath
import pixSED               as     SED
import matplotlib           as     mpl
import matplotlib.pyplot    as     plt
from   astropy.io           import fits
from   matplotlib.gridspec  import GridSpec
from   matplotlib.colors    import Normalize
from   matplotlib           import rc

# Define data file names
galName    = '1'                                                                # Galaxy number
zeropoints = [25.68, 26.51, 25.69, 25.94, 24.87, 26.27, 26.23, 26.45, 25.94]    # HST zeropoints
redshift   = 0.622                                                              # Redshift of the galaxy
bands      = ['435', '606', '775', '814', '850', '105', '125', '140', '160']    # Bands
band_names = [f'F{band}LP' if band == '850' else f'F{band}W' for band in bands] # Bands names in Cigale

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

# Get mask file
mfile      = opath.abspath(opath.join('data', f'{galName}_mask.fits'))
with fits.open(mfile) as hdul:
   mask    = hdul[0].data == 0

###   1. Generate a FilterList object   ###
filts      = []
for band, data, data2, var, zpt in zip(band_names, dataFiles, data2Files, varFiles, zeropoints):
   filts.append(SED.Filter(band, data, data2, var, zpt))

flist      = SED.FilterList(filts, mask, 
                            code        = SED.SEDcode.CIGALE, 
                            redshift    = redshift,
                            cleanMethod = SED.CleanMethod.ZERO,
                            scaleFactor = 1,                    # whatever value is fine: scaleFactor is not used by Cigale
                            texpFac     = 4
                            )

###   2. Convert to CigaleCat   ###
catalogue  = flist.toCatalogue(galName)

###   3. Create SED fitting object   ###

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


sedobj     = SED.CigaleSED(galName, band_names,
                           uncertainties = [True]*len(band_names),
                           SFH           = SFH,
                           SSP           = SSP,
                           nebular       = nebular,
                           attenuation   = attenuation,
                          )

###   5. Generate a resolved stellar mass map   ###
output = SED.CigaleOutput('1/out/results.fits')
output.link(flist)
mass_star  = output.toImage('bayes.stellar.m_star').to('Msun').value
dmass_star = output.toImage('bayes.stellar.m_star_err').to('Msun').value

###   6. Plot   ###
rc('font', **{'family': 'serif', 'serif': ['Times']})
rc('text', usetex=True)
mpl.rcParams['text.latex.preamble'] = r'\usepackage{newtxmath}'
rc('figure', figsize=(5, 4.5))

f   = plt.figure(figsize=(9, 4.5))
gs  = GridSpec(2, 2, height_ratios=[0.95, 0.02])

ax0  = f.add_subplot(gs[0, 0])
ret0 = plt.imshow(np.log10(mass_star), origin='lower', cmap='rainbow',
                  norm=Normalize(vmin=6, vmax=8.5)
                 )

ax1  = f.add_subplot(gs[0, 1])
ret1 = plt.imshow(mass_star/dmass_star, origin='lower', cmap='rainbow',
                  norm=Normalize(vmin=0, vmax=21)
                 )

ax0.tick_params(which='both', direction='in', top=True, bottom=True, left=True, right=True,
                labelbottom=False, labeltop=True, labelleft=True, labelright=False)

ax1.tick_params(which='both', direction='in', top=True, bottom=True, left=True, right=True,
                labelbottom=False, labeltop=True, labelleft=False, labelright=False)
                

ax0.xaxis.set_label_position('top')
ax1.xaxis.set_label_position('top')
ax0.set_xlabel('X [pixel]', size=13)
ax1.set_xlabel('X [pixel]', size=13)
ax0.set_ylabel('Y [pixel]', size=13)

cba0 = plt.colorbar(ret0, cax = f.add_subplot(gs[1, 0]), orientation='horizontal', shrink=0.9)
cba1 = plt.colorbar(ret1, cax = f.add_subplot(gs[1, 1]), orientation='horizontal', shrink=0.9)
cba0.set_label(r'$M_{\star}$ [M$_{\odot}$]', size=13)
cba0.set_label(r'S/N', size=13)
plt.show()
