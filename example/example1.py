import os.path           as     opath
import matplotlib.pyplot as     plt
from   astropy.io        import fits
import SED

# Define data file names
galName    = '1'                                                             # Galaxy number
zeropoints = [25.68, 26.51, 25.69, 25.94, 24.87, 26.27, 26.23, 26.45, 25.94] # HST zeropoints
redshift   = 0.622                                                           # Redshift of the galaxy
bands      = ['435', '606', '775', '814', '850', '105', '125', '140', '160'] # Bands
band_names = ['ACS_WFC.F435W', 'ACS_WFC.F606W', 'ACS_WFC.F775W',             # Names of the band for LePhare
              'ACS_WFC.F814W', 'ACS_WFC.F850LP', 'WFC3_IR.F105W',
              'WFC3_IR.F125W', 'WFC3_IR.F140W', 'WFC3_IR.F160W']

dataFiles  = [] # Data files
varFiles   = [] # Variance maps

for band in bands:

   file    = opath.abspath(opath.join('data', f'{galName}_{band}.fits'))
   dataFiles.append(file)

   vfile   = opath.abspath(opath.join('data', f'{galName}_{band}_var.fits'))
   varFiles.append(vfile)

# Get mask file
mfile      = opath.abspath(opath.join('data', f'{galName}_mask.fits'))
with fits.open(mfile) as hdul:
   mask    = hdul[0].data == 0

###   1. Generate a FilterList object   ###
filts      = []
for band, data, var, zpt in zip(bands, dataFiles, varFiles, zeropoints):
   filts.append(SED.Filter(band, file, var, zpt))

flist      = SED.FilterList(filts, mask, code=SED.SEDcode.LEPHARE, redshift=redshift)

###   2. Update data table and add Poisson noise (texpFac != 0)   ###
flist.genTable(cleanMethod=SED.CleanMethod.ZERO, scaleFactor=100, texpFac=4)

###   3. Convert to LePhareCat   ###
catalogue  = flist.toCatalogue(f'{galName}.in')

###   4. Create SED fitting object   ###
hst_filt   = [] # Filter names for LePhare
err        = [] # Quadratic errors to add to the magnitudes of each band

for band in band_names:
   filt    = opath.join('hst_filters', f'HST_{band}')
   hst_filt.append(filt)
   err.append(0.03)

properties = {'FILTER_LIST' : hst_filt, 'ERR_SCALE' : err}
sed        = SED.LePhareSED(galName, properties=properties)

###   5. Run SED fitting   ###
params     = ['MASS_BEST', 'MASS_INF', 'MASS_MED', 'MASS_SUP']
skip       = {'skipSEDgen' : True, 'skipFilterGen' : True, 'skipMagGal' : True, 'skipMagQSO' : True, 'skipMagStar' : True}
skip       = {'skipSEDgen' : False, 'skipFilterGen' : False, 'skipMagGal' : False, 'skipMagQSO' : False, 'skipMagStar' : False}
output     = sed(catalogue, outputParams=params, **skip)

###   6. Generate a resolved stellar mass map   ###
output.link(flist)
mass_star  = output.toImage('mass_med')

plt.imshow(mass_star.data, origin='lower', cmap='rainbow')
plt.show()
