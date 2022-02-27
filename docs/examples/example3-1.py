import os.path           as     opath
from   astropy.io        import fits
import SED

from   matplotlib        import rc
import matplotlib        as     mpl
import matplotlib.pyplot as     plt

# Define data file names
galName    = '1'                                                             # Galaxy number
zeropoints = [25.68, 26.51, 25.69, 25.94, 24.87, 26.27, 26.23, 26.45, 25.94] # HST zeropoints
redshift   = 0.622                                                           # Redshift of the galaxy
bands      = ['435', '606', '775', '814', '850', '105', '125', '140', '160'] # Bands
band_names = [f'F{band}LP' if band == '850' else f'F{band}W' for band in bands] # Bands names in Cigale

dataFiles  = [] # Flux maps
data2Files = [] # Flux maps convolved by the PSF squared
varFiles   = [] # Variance maps

for band in bands:

   file    = opath.abspath(opath.join('..', '..', 'example', 'data', f'{galName}_{band}.fits'))
   dataFiles.append(file)

   file2   = opath.abspath(opath.join('..', '..', 'example', 'data', f'{galName}_{band}_PSF2.fits'))
   data2Files.append(file2)

   vfile   = opath.abspath(opath.join('..', '..', 'example', 'data', f'{galName}_{band}_var.fits'))
   varFiles.append(vfile)

# Get mask file
mfile      = opath.abspath(opath.join('..', '..', 'example', 'data', f'{galName}_mask.fits'))
with fits.open(mfile) as hdul:
   mask    = hdul[0].data == 0

filts      = []
for band, data, data2, var, zpt in zip(bands, dataFiles, data2Files, varFiles, zeropoints):
   filts.append(SED.Filter(band, data, data2, var, zpt))

flist      = SED.FilterList(filts, mask,
                            code=SED.SEDcode.LEPHARE,
                            redshift=redshift,
                            cleanMethod=SED.CleanMethod.ZERO,
                            scaleFactor=1,
                            texpFac=4
                           )

output = SED.CigaleOutput(opath.join('..', '..', 'example', galName, 'out', 'results.fits'))
output.link(flist)
mass_star  = output.toImage('best.stellar.m_star')

rc('font', **{'family': 'serif', 'serif': ['Times']})
rc('text', usetex=True)
mpl.rcParams['text.latex.preamble'] = r'\usepackage{newtxmath}'
rc('figure', figsize=(5, 4.5))

ret = plt.imshow(mass_star.data, origin='lower', cmap='rainbow')
plt.xlabel('X [pixel]', size=13)
plt.ylabel('Y [pixel]', size=13)

cbar = plt.colorbar(ret, orientation='vertical', shrink=0.9)
cbar.set_label(r'$M_{\star}$ [M$_{\odot}$]', size=13)
plt.show()