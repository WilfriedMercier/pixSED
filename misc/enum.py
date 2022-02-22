#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
.. codeauthor:: Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>

Enumerations used in other parts of the code.
"""

from enum          import Enum
from .misc         import NamedColumn

class CleanMethod(Enum):
    r'''An enumeration for the cleaning method used by the filters.'''
     
    #: Used to clean bad pixels with flux value of 0
    ZERO = 'zero'
    
    #: Used to clean bad pixels with flux value being the minimum of the good pixels
    MIN  = 'min'
    
class SEDcode(Enum):
    r'''An enumeration for the SED fitting codes available.'''
    
    #: Used to set LePhare as the SED fitting code
    LEPHARE = 'lephare'
    
    #: Used to set Cigale as the SED fitting code
    CIGALE  = 'cigale'
    
###################################
#        Cigale only Enum         #
###################################

class Save_chi2(Enum):
    r'''An enumeration with different for saving the chi2 result of Cigale.'''
    
    #: Save all chi2
    ALL        = 'all'
    
    #: Save no chi2
    NONE       = 'none'
    
    #: Save fluxes chi2
    FLUXES     = 'fluxes'
    
    #: Save properties chi2
    PROPERTIES = 'properties'
    
class IMF(Enum):
    r'''An enumeration with accepted IMF in Cigale.'''
    
    #: Chabrier IMF
    CHABRIER = '1'
    
    #: Salpeter IMF
    SALPETER = '0'
    
###################################
#        LePhare only Enum        #
###################################
    
class ANDOR(Enum):
    r'''An enumeration with AND or OR options for LePhare.'''
    
    #: Logical AND
    AND = 'AND'
    
    #: Logical OR
    OR  = 'OR'
    
class MagType(Enum):
    r'''An enumeration for valid magnitude types for LePhare.'''
    
    #: Used to set AB magnitude system
    AB   = 'AB'
    
    #: Used to set VEGA magnitude system
    VEGA = 'VEGA'
    
class TableFormat(Enum):
    r'''An enumerator for valid table format for LePhare.'''
    
    #: Table format being: Mag, Error, Mag, Error, ...
    MEME = 'MEME'
    
    #: Table format being Mag, Mag, Mag, ..., Error, Error, Error, ...
    MMEE = 'MMEE'
    
class TableType(Enum):
    r'''An enumerator for valid table data type for LePhare.'''
    
    #: Table format being long
    LONG  = 'LONG'
    
    #: Table format being short
    SHORT = 'SHORT'
    
class TableUnit(Enum):
    r'''An enumeration for valid values for table units for LePhare.'''
    
    #: Unit of table set to magnitude
    MAG  = 'M'
    
    #: Unit of table set to flux
    FLUX = 'F'
    
class YESNO(Enum):
    r'''An enumeration with YES or NO options for LePhare.'''
    
    #: Used to set a value to YES
    YES = 'YES'
    
    #: Used to set a value to NO
    NO  = 'NO'
   
class LePhareOutputParam(Enum):
    r'''An enumeration for LePhare output parameters with corresponding table name and table unit.'''
    
    #: Best redshift. Z_BEST.name = 'z_best'.
    Z_BEST           = NamedColumn('z_best',               '')
    
    #: Best redshift lower bound 68%. Z_BEST68_LOW.name = 'z_best_l68'.
    Z_BEST68_LOW     = NamedColumn('z_best_l68',           '') 
    
    #: Best redshift upper bound 68%. Z_BEST68_HIGH.name = 'z_best_u68'.
    Z_BEST68_HIGH    = NamedColumn('z_best_u68',           '') 
    
    #: Best redshift lower bound 90%. Z_BEST90_LOW.name = 'z_best_l90'.
    Z_BEST90_LOW     = NamedColumn('z_best_l90',           '') 
    
    #: Best redshift upper bound 90%. Z_BEST90_HIGH.name = 'z_best_u90'.
    Z_BEST90_HIGH    = NamedColumn('z_best_u90',           '') 
    
    #: Best redshift lower bound 99%. Z_BEST99_LOW.name = 'z_best_l99'.
    Z_BEST99_LOW     = NamedColumn('z_best_l99',           '') 
    
    #: Best redshift upper bound 99%. Z_BEST99_HIGH.name = 'z_best_u99'.
    Z_BEST99_HIGH    = NamedColumn('z_best_u99',           '')
    
    #: Best redshift ML. Z_ML.name = 'z_ML'.
    Z_ML             = NamedColumn('z_ML',                 '') 
    
    #: Best redshift ML lower bound 68%. Z_ML68_LOW.name = 'z_ML_l68'.
    Z_ML68_LOW       = NamedColumn('z_ML_l68',             '') 
    
    #: Best reshift ML upper bound 68%. Z_ML68_HIGH.name = 'z_ML_u68'.
    Z_ML68_HIGH      = NamedColumn('z_ML_u68',             '') 
    
    #: Best chi2. CHI_BEST.name = 'chi2'.
    CHI_BEST         = NamedColumn('chi2',                 '') 
    
    #: Best model. MOD_BEST.name = 'Mod_best'.
    MOD_BEST         = NamedColumn('Mod_best',             '') 
    
    #: Best extinction law. EXTLAW_BEST.name = 'Ext_law_best'.
    EXTLAW_BEST      = NamedColumn('Ext_law_best',         '') 
    
    #: Best color excess. EBV_BEST.name = 'E(B-V)_best'.
    EBV_BEST         = NamedColumn('E(B-V)_best',          '') 
    
    #: ???. ZF_BEST.name = 'ZF_BEST'.
    ZF_BEST          = NamedColumn('ZF_BEST',              '') # No idea what this is
    
    #: Best absolute magnitude ? MAG_ABS_BEST.name = 'mag_abs_best'.
    MAG_ABS_BEST     = NamedColumn('mag_abs_best',         'dex') 
    
    #: Best PDZ. PDZ_BEST.name = 'pdz_best'.
    PDZ_BEST         = NamedColumn('pdz_best',             '') 
    
    #: Best scale factor. SCALE_BEST.name = 'scale_best'.
    SCALE_BEST       = NamedColumn('scale_best',           '') 
    
    #: Best dist mod ? DIST_MOD_BEST.name = 'dist_mod_best'.
    DIST_MOD_BEST    = NamedColumn('dist_mod_best',        '') # No idea
    
    #: Number of bands used. NBAND_USED.name = 'nband'.
    NBAND_USED       = NamedColumn('nband',                '') 
    
    #: Upper limit on number of bands used ? NBAND_ULIM.name = 'nband_ulim'.
    NBAND_ULIM       = NamedColumn('nband_ulim',           '') 
    
    #: Best resdhift second galaxy. Z_SEC.name = 'z_second'.
    Z_SEC            = NamedColumn('z_second',             '') 
    
    #: Best chi2 second galaxy. CHI_SEC.name = 'chi2_second'.
    CHI_SEC          = NamedColumn('chi2_second',          '') 
    
    #: Best model second galaxy. MOD_SEC.name = 'Mod_second'.
    MOD_SEC          = NamedColumn('Mod_second',           '') 
    
    #: Best age second galaxy. AGE_SEC.name = 'age_second'.
    AGE_SEC          = NamedColumn('age_second',           'yr') 
    
    #: Best color excess second galaxy. EBV_SEC.name = 'E(B-V)_second'.
    EBV_SEC          = NamedColumn('E(B-V)_second',        '') 
    
    #: ??? second galaxy. ZF_SEC.name = 'ZF_SEC'.
    ZF_SEC           = NamedColumn('ZF_SEC',               '') # No idea
    
    #: Absolute magnitude second galaxy. MAG_ABS_SEC.name = 'mag_abs_second'.
    MAG_ABS_SEC      = NamedColumn('mag_abs_second',       'dex') 
    
    #: Best PDZ second galaxy. PDZ_SEC.name = 'pdz_second'.
    PDZ_SEC          = NamedColumn('pdz_second',           '') 
    
    #: Best scale factor second galaxy. SCALE_SEC.name = 'scale_second'
    SCALE_SEC        = NamedColumn('scale_second',         '') 
    
    #: redshift QSO. Z_QSO.name = 'z_qso'.
    Z_QSO            = NamedColumn('z_qso',                '')
    
    #: chi2 QSO. CHI_QSO.name = 'chi2_qso'.
    CHI_QSO          = NamedColumn('chi2_qso',             '') 
    
    #: model QSO. MOD_QSO.name = 'Mod_qso'.
    MOD_QSO          = NamedColumn('Mod_qso',              '') 
    
    #: absolute magnitude QSO. MAG_ABS_QSO.name = 'mag_abs_qso'.
    MAG_ABS_QSO      = NamedColumn('mag_abs_qso',          'dex') 
    
    #: Model distance QSO ? DIST_MOD_QSO.name = 'dist_mod_qso'.
    DIST_MOD_QSO     = NamedColumn('dist_mod_qso',         '') 
    
    #: Stellar model. MOD_STAR.name = 'Mod_star'.
    MOD_STAR         = NamedColumn('Mod_star',             '')
    
    #: Chi2 stars. CHI_STAR.name = 'chi2_star'.
    CHI_STAR         = NamedColumn('chi2_star',            '')
    
    #: Absolute magnitude 2. MAG_OBS_2.name = 'mag_obs()'.
    MAG_OBS_2        = NamedColumn('mag_obs()',            'dex',  end='()')
    
    #: Error on absolute magnitude 2. ERR_MAG_OBS_2.name = 'mag_obs_err()'.
    ERR_MAG_OBS_2    = NamedColumn('mag_obs_err()',        'dex',  end='()')
    
    #: Model magnitude 2. MAG_MOD_2.name = 'mag_mod()'.
    MAG_MOD_2        = NamedColumn('mag_mod()',            'dex',  end='()')
    
    #: K correction 2. K_COR_2.name = 'K_correction()'.
    K_COR_2          = NamedColumn('K_correction()',       'dex',  end='()')
    
    #: Absolute magnitude 2. MAG_ABS_2.name = 'mag_abs()'.
    MAG_ABS_2        = NamedColumn('mag_abs()',            'dex',  end='()')
    
    #: Absolute magnitude per filter 2 ??? MABS_FILT_2.name = 'MABS_FILT()'.
    MABS_FILT_2      = NamedColumn('MABS_FILT()',          'dex',  end='()') # No idea
    
    #: K correction QSO 2. K_COR_QSO_2.name = 'K_correction_qso()'.
    K_COR_QSO_2      = NamedColumn('K_correction_qso()',   'dex',  end='()')
    
    #: Absolute magnitude QSO 2. MAG_ABS_QSO_2.name = 'mag_abs_qso()'.
    MAG_ABS_QSO_2    = NamedColumn('mag_abs_qso()',        'dex',  end='()') 
    
    #: PDZ 2. PDZ_2.name = 'pdz()'.
    PDZ_2            = NamedColumn('pdz()',                '',     end='()') 
    
    #: Context. CONTEXT.name = 'context'
    CONTEXT          = NamedColumn('context',              '') 
    
    #: Spectroscopic redshift. ZSPEC.name = 'zspec'.
    ZSPEC            = NamedColumn('zspec',                '') 
    
    #: Input string. STRING_INPUT.name = 'string_input'.
    STRING_INPUT     = NamedColumn('string_input',         '') 
    
    #: Best TIR luminosity. LUM_TIR_BEST.name = 'luminosity_tir_best'.
    LUM_TIR_BEST     = NamedColumn('luminosity_tir_best',  'erg/s') # Not sure about unit
    
    #: FIR library. LIB_FIR.name = 'library_fir'.
    LIB_FIR          = NamedColumn('library_fir',          '') 
    
    #: FIR model. MOD_FIR.name = 'mod_fir'.
    MOD_FIR          = NamedColumn('mod_fir',              '') 
    
    #: FIR chi2. CHI2_FIR.name = 'chi2_fir'.
    CHI2_FIR         = NamedColumn('chi2_fir',             '') 
    
    #: FIR scale factor. FSCALE_FIR.name = 'fscale_fir'.
    FSCALE_FIR       = NamedColumn('fscale_fir',           '') 
    
    #: FIR number of bands used. NBAND_FIR.name = 'nband_fir'.
    NBAND_FIR        = NamedColumn('nband_fir',            '') 
    
    #: TIR median luminosity. LUM_TIR_MED.name = 'luminosity_tir_med'.
    LUM_TIR_MED      = NamedColumn('luminosity_tir_med',   '') 
    
    #: TIR lower bound luminosity. LUM_TIR_INF.name = 'luminosity_tir_inf'.
    LUM_TIR_INF      = NamedColumn('luminosity_tir_inf',   '') 
    
    #: TIR upper bound luminosity. LUM_TIR_SUP.name = 'luminosity_tir_sup'.
    LUM_TIR_SUP      = NamedColumn('luminosity_tir_sup',   '') 
    
    #: FIR model magnitude 2. MAG_MOD_FIR_2.name = 'mag_mod_fir'.
    MAG_MOD_FIR_2    = NamedColumn('mag_mod_fir',          'dex', end='()') 
    
    #: FIR absolute magnitude 2. MAG_ABS_FIR_2.name = 'mag_abs_fir'.
    MAG_ABS_FIR_2    = NamedColumn('mag_abs_fir',          'dex', end='()') 
    
    #: FIR K correction 2. K_COR_FIR_2.name = 'K_correction_fir'.
    K_COR_FIR_2      = NamedColumn('K_correction_fir',     'dex', end='()') 
    
    #: Best age. AGE_BEST.name = 'age_best'.
    AGE_BEST         = NamedColumn('age_best',             'yr') 
    
    #: lower bound age. AGE_INF.name = 'age_inf'.
    AGE_INF          = NamedColumn('age_inf',              'yr') 
    
    #: Median age. AGE_MED.name = 'age_median'.
    AGE_MED          = NamedColumn('age_median',           'yr') 
    
    #: Upper bound age. AGE_SUP.name = 'age_sup'.
    AGE_SUP          = NamedColumn('age_sup',              'yr') 
    
    #: Best dust luminosity. LDUST_BEST.name = 'luminosity_dust_best'.
    LDUST_BEST       = NamedColumn('luminosity_dust_best', 'erg/s') # Not sure about unit
    
    #: Lower bound dust luminosity. LDUST_INF.name = 'luminosity_dust_inf'.
    LDUST_INF        = NamedColumn('luminosity_dust_inf',  'erg/s') # Not sure about unit 
    
    #: Median dust luminosity. LDUST_MED.name = 'luminosity_dust_med'.
    LDUST_MED        = NamedColumn('luminosity_dust_med',  'erg/s') # Not sure about unit, 
    
    #: Upper bound dust luminosity. LDUST_SUP.name = 'luminosity_dust_sup'.
    LDUST_SUP        = NamedColumn('luminosity_dust_sup',  'erg/s') # Not sure about unit, 
    
    #: Best stellar mass. MASS_BEST.name = 'mass_best'.
    MASS_BEST        = NamedColumn('mass_best',            'Msun',    log=True) 
    
    #: Lower bound stellar mass. MASS_INF.name = 'mass_inf'.
    MASS_INF         = NamedColumn('mass_inf',             'Msun',    log=True) 
    
    #: Median stellar mass. MASS_MED.name = 'mass_med'.
    MASS_MED         = NamedColumn('mass_med',             'Msun',    log=True) 
    
    #: Upper bound stellar mass. MASS_SUP.name = 'mass_sup'.
    MASS_SUP         = NamedColumn('mass_sup',             'Msun',    log=True) 
    
    #: Best SFR. SFR_BEST.name = 'sfr_best'.
    SFR_BEST         = NamedColumn('sfr_best',             'Msun/yr', log=True) 
    
    #: Lower bound SFR. SFR_INF.name = 'sfr_inf'.
    SFR_INF          = NamedColumn('sfr_inf',              'Msun/yr', log=True) 
    
    #: Median SFR. SFR_MED.name = 'sfr_med'.
    SFR_MED          = NamedColumn('sfr_med',              'Msun/yr', log=True) 
    
    #: Upper bound SFR. SFR_SUP.name = 'sfr_sup'.
    SFR_SUP          = NamedColumn('sfr_sup',              'Msun/yr', log=True) 
    
    #: Best sSFR. SSFR_BEST.name = 'ssfr_best'.
    SSFR_BEST        = NamedColumn('ssfr_best',            '1/yr',    log=True) 
    
    #: Lower bound sSFR. SSFR_INF.name = 'ssfr_inf'.
    SSFR_INF         = NamedColumn('ssfr_inf',             '1/yr',    log=True) 
    
    #: Median sSFR. SSFR_MED.name = 'ssfr_med'.
    SSFR_MED         = NamedColumn('ssfr_med',             '1/yr',    log=True) 
    
    #: Upper bound sSFR. SSFR_SUP.name = 'ssfr_sup'.
    SSFR_SUP         = NamedColumn('ssfr_sup',             '1/yr',    log=True) 
    
    #: Best NUV luminosity. LUM_NUV_BEST.name = 'luminosity_nuv_best'.
    LUM_NUV_BEST     = NamedColumn('luminosity_nuv_best',  'erg/s') # Not sure about unit
    
    #: Best R-band luminosity. LUM_R_BEST.name = 'luminosity_R_best'.
    LUM_R_BEST       = NamedColumn('luminosity_R_best',    'erg/s') # Not sure about unit
    
    #: Best K-band luminosity. LUM_K_BEST.name = 'luminosity_K_best'.
    LUM_K_BEST       = NamedColumn('luminosity_K_best',    'erg/s') # Not sure about unit
    
    #: Best physical chi2. PHYS_CHI2_BEST.name = 'phys_chi2_best'.
    PHYS_CHI2_BEST   = NamedColumn('phys_chi2_best',       '') 
    
    #: Best physical model. PHYS_MOD_BEST.name = 'phys_mod_best'.
    PHYS_MOD_BEST    = NamedColumn('phys_mod_best',        '') 
    
    #: Physical model magnitude 2. PHYS_MAG_MOD_2.name = 'phys_mag_mod'.
    PHYS_MAG_MOD_2   = NamedColumn('phys_mag_mod',         'dex', end='()') 
    
    #: Physical absolute magnitude 2. PHYS_MAG_ABS_2.name = 'phys_mag_abs'.
    PHYS_MAG_ABS_2   = NamedColumn('phys_mag_abs',         'dex', end='()') 
    
    #: Physical K correction 2. PHYS_K_COR_2.name = 'phys_K_correction'.
    PHYS_K_COR_2     = NamedColumn('phys_K_correction',    'dex', end='()') 
    
    #: Physical best PARA1. PHYS_PARA1_BEST.name = 'phys_para1_best'
    PHYS_PARA1_BEST  = NamedColumn('phys_para1_best',      '') 
    
    #: Physical best PARA2. PHYS_PARA2_BEST.name = 'phys_para2_best'.
    PHYS_PARA2_BEST  = NamedColumn('phys_para2_best',      '') 
    
    #: Physical best PARA3. PHYS_PARA3_BEST.name = 'phys_para3_best'.
    PHYS_PARA3_BEST  = NamedColumn('phys_para3_best',      '') 
    
    #: Physical best PARA4. PHYS_PARA4_BEST.name = 'phys_para4_best'.
    PHYS_PARA4_BEST  = NamedColumn('phys_para4_best',      '') 
    
    #: Physical best PARA5. PHYS_PARA5_BEST.name = 'phys_para5_best'.
    PHYS_PARA5_BEST  = NamedColumn('phys_para5_best',      '') 
    
    #: Physical best PARA6. PHYS_PARA6_BEST.name = 'phys_para6_best'.
    PHYS_PARA6_BEST  = NamedColumn('phys_para6_best',      '') 
    
    #: Physical best PARA7. PHYS_PARA7_BEST.name = 'phys_para7_best'.
    PHYS_PARA7_BEST  = NamedColumn('phys_para7_best',      '') 
    
    #: Physical best PARA8. PHYS_PARA8_BEST.name = 'phys_para8_best'.
    PHYS_PARA8_BEST  = NamedColumn('phys_para8_best',      '') 
    
    #: Physical best PARA9. PHYS_PARA9_BEST.name = 'phys_para9_best'.
    PHYS_PARA9_BEST  = NamedColumn('phys_para9_best',      '') 
    
    #: Physical best PARA10. PHYS_PARA10_BEST.name = 'phys_para10_best'.
    PHYS_PARA10_BEST = NamedColumn('phys_para10_best',     '') 
    
    #: Physical best PARA11. PHYS_PARA11_BEST.name = 'phys_para11_best'.
    PHYS_PARA11_BEST = NamedColumn('phys_para11_best',     '') 
    
    #: Physical best PARA12. PHYS_PARA12_BEST.name = 'phys_para12_best'.
    PHYS_PARA12_BEST = NamedColumn('phys_para12_best',     '') 
    
    #: Physical best PARA13. PHYS_PARA13_BEST.name = 'phys_para13_best'.
    PHYS_PARA13_BEST = NamedColumn('phys_para13_best',     '') 
    
    #: Physical best PARA14. PHYS_PARA14_BEST.name = 'phys_para14_best'.
    PHYS_PARA14_BEST = NamedColumn('phys_para14_best',     '') 
    
    #: Physical best PARA15. PHYS_PARA15_BEST.name = 'phys_para15_best'.
    PHYS_PARA15_BEST = NamedColumn('phys_para15_best',     '') 
    
    #: Physical best PARA16. PHYS_PARA16_BEST.name = 'phys_para16_best'.
    PHYS_PARA16_BEST = NamedColumn('phys_para16_best',     '') 
    
    #: Physical best PARA17. PHYS_PARA17_BEST.name = 'phys_para17_best'.
    PHYS_PARA17_BEST = NamedColumn('phys_para17_best',     '') 
    
    #: Physical best PARA18. PHYS_PARA18_BEST.name = 'phys_para18_best'.
    PHYS_PARA18_BEST = NamedColumn('phys_para18_best',     '') 
    
    #: Physical best PARA19. PHYS_PARA19_BEST.name = 'phys_para19_best'.
    PHYS_PARA19_BEST = NamedColumn('phys_para19_best',     '') 
    
    #: Physical best PARA20. PHYS_PARA20_BEST.name = 'phys_para20_best'.
    PHYS_PARA20_BEST = NamedColumn('phys_para20_best',     '') 
    
    #: Physical best PARA21. PHYS_PARA21_BEST.name = 'phys_para21_best'.
    PHYS_PARA21_BEST = NamedColumn('phys_para21_best',     '') 
    
    #: Physical best PARA22. PHYS_PARA22_BEST.name = 'phys_para22_best'.
    PHYS_PARA22_BEST = NamedColumn('phys_para22_best',     '') 
    
    #: Physical best PARA23. PHYS_PARA23_BEST.name = 'phys_para23_best'.
    PHYS_PARA23_BEST = NamedColumn('phys_para23_best',     '') 
    
    #: Physical best PARA24. PHYS_PARA24_BEST.name = 'phys_para24_best'.
    PHYS_PARA24_BEST = NamedColumn('phys_para24_best',     '') 
    
    #: Physical best PARA25. PHYS_PARA25_BEST.name = 'phys_para25_best'.
    PHYS_PARA25_BEST = NamedColumn('phys_para25_best',     '') 
    
    #: Physical best PARA26. PHYS_PARA26_BEST.name = 'phys_para26_best'.
    PHYS_PARA26_BEST = NamedColumn('phys_para26_best',     '') 
    
    #: Physical best PARA27. PHYS_PARA27_BEST.name = 'phys_para27_best'.
    PHYS_PARA27_BEST = NamedColumn('phys_para27_best',     '') 
    
    #: Physical median PARA1. PHYS_PARA1_MED.name = 'phys_para1_med'.
    PHYS_PARA1_MED   = NamedColumn('phys_para1_med',       '') 
    
    #: Physical median PARA2. PHYS_PARA2_MED.name = 'phys_para2_med'.
    PHYS_PARA2_MED   = NamedColumn('phys_para2_med',       '') 
    
    #: Physical median PARA3. PHYS_PARA3_MED.name = 'phys_para3_med'.
    PHYS_PARA3_MED   = NamedColumn('phys_para3_med',       '') 
    
    #: Physical median PARA4. PHYS_PARA4_MED.name = 'phys_para4_med'.
    PHYS_PARA4_MED   = NamedColumn('phys_para4_med',       '') 
    
    #: Physical median PARA5. PHYS_PARA5_MED.name = 'phys_para5_med'.
    PHYS_PARA5_MED   = NamedColumn('phys_para5_med',       '') 
    
    #: Physical median PARA6. PHYS_PARA6_MED.name = 'phys_para6_med'.
    PHYS_PARA6_MED   = NamedColumn('phys_para6_med',       '') 
    
    #: Physical median PARA7. PHYS_PARA7_MED.name = 'phys_para7_med'.
    PHYS_PARA7_MED   = NamedColumn('phys_para7_med',       '') 
    
    #: Physical median PARA8. PHYS_PARA8_MED.name = 'phys_para8_med'.
    PHYS_PARA8_MED   = NamedColumn('phys_para8_med',       '') 
    
    #: Physical median PARA9. PHYS_PARA9_MED.name = 'phys_para9_med'.
    PHYS_PARA9_MED   = NamedColumn('phys_para9_med',       '') 
    
    #: Physical median PARA10. PHYS_PARA10_MED.name = 'phys_para10_med'.
    PHYS_PARA10_MED  = NamedColumn('phys_para10_med',      '') 
    
    #: Physical median PARA11. PHYS_PARA11_MED.name = 'phys_para11_med'.
    PHYS_PARA11_MED  = NamedColumn('phys_para11_med',      '') 
    
    #: Physical median PARA12. PHYS_PARA12_MED.name = 'phys_para12_med'.
    PHYS_PARA12_MED  = NamedColumn('phys_para12_med',      '') 
    
    #: Physical median PARA13. PHYS_PARA13_MED.name = 'phys_para13_med'.
    PHYS_PARA13_MED  = NamedColumn('phys_para13_med',      '') 
    
    #: Physical median PARA14. PHYS_PARA14_MED.name = 'phys_para14_med'.
    PHYS_PARA14_MED  = NamedColumn('phys_para14_med',      '') 
    
    #: Physical median PARA15. PHYS_PARA15_MED.name = 'phys_para15_med'.
    PHYS_PARA15_MED  = NamedColumn('phys_para15_med',      '') 
    
    #: Physical median PARA16. PHYS_PARA16_MED.name = 'phys_para16_med'.
    PHYS_PARA16_MED  = NamedColumn('phys_para16_med',      '') 
    
    #: Physical median PARA17. PHYS_PARA17_MED.name = 'phys_para17_med'.
    PHYS_PARA17_MED  = NamedColumn('phys_para17_med',      '') 
    
    #: Physical median PARA18. PHYS_PARA18_MED.name = 'phys_para18_med'.
    PHYS_PARA18_MED  = NamedColumn('phys_para18_med',      '') 
    
    #: Physical median PARA19. PHYS_PARA19_MED.name = 'phys_para19_med'.
    PHYS_PARA19_MED  = NamedColumn('phys_para19_med',      '') 
    
    #: Physical median PARA20. PHYS_PARA20_MED.name = 'phys_para20_med'.
    PHYS_PARA20_MED  = NamedColumn('phys_para20_med',      '') 
    
    #: Physical median PARA21. PHYS_PARA21_MED.name = 'phys_para21_med'.
    PHYS_PARA21_MED  = NamedColumn('phys_para21_med',      '') 
    
    #: Physical median PARA22. PHYS_PARA22_MED.name = 'phys_para22_med'.
    PHYS_PARA22_MED  = NamedColumn('phys_para22_med',      '') 
    
    #: Physical median PARA23. PHYS_PARA23_MED.name = 'phys_para23_med'.
    PHYS_PARA23_MED  = NamedColumn('phys_para23_med',      '') 
    
    #: Physical median PARA24. PHYS_PARA24_MED.name = 'phys_para24_med'.
    PHYS_PARA24_MED  = NamedColumn('phys_para24_med',      '') 
    
    #: Physical median PARA25. PHYS_PARA25_MED.name = 'phys_para25_med'.
    PHYS_PARA25_MED  = NamedColumn('phys_para25_med',      '') 
    
    #: Physical median PARA26. PHYS_PARA26_MED.name = 'phys_para26_med'.
    PHYS_PARA26_MED  = NamedColumn('phys_para26_med',      '') 
    
    #: Physical median PARA27. PHYS_PARA27_MED.name = 'phys_para27_med'.
    PHYS_PARA27_MED  = NamedColumn('phys_para27_med',      '') 
    
    #: Physical lower bound PARA1. PHYS_PARA1_INF.name = 'phys_para1_inf'
    PHYS_PARA1_INF   = NamedColumn('phys_para1_inf',       '') 
    
    #: Physical lower bound PARA2. PHYS_PARA2_INF.name = 'phys_para2_inf'.
    PHYS_PARA2_INF   = NamedColumn('phys_para2_inf',       '') 
    
    #: Physical lower bound PARA3. PHYS_PARA3_INF.name = 'phys_para3_inf'.
    PHYS_PARA3_INF   = NamedColumn('phys_para3_inf',       '') 
    
    #: Physical lower bound PARA4. PHYS_PARA4_INF.name = 'phys_para4_inf'.
    PHYS_PARA4_INF   = NamedColumn('phys_para4_inf',       '') 

    #: Physical lower bound PARA5. PHYS_PARA5_INF.name = 'phys_para5_inf'.
    PHYS_PARA5_INF   = NamedColumn('phys_para5_inf',       '') 
    
    #: Physical lower bound PARA6. PHYS_PARA6_INF.name = 'phys_para6_inf'.
    PHYS_PARA6_INF   = NamedColumn('phys_para6_inf',       '') 
    
    #: Physical lower bound PARA7. PHYS_PARA7_INF.name = 'phys_para7_inf'.
    PHYS_PARA7_INF   = NamedColumn('phys_para7_inf',       '') 
    
    #: Physical lower bound PARA8. PHYS_PARA8_INF.name = 'phys_para8_inf'.
    PHYS_PARA8_INF   = NamedColumn('phys_para8_inf',       '') 
    
    #: Physical lower bound PARA9. PHYS_PARA9_INF.name = 'phys_para9_inf'.
    PHYS_PARA9_INF   = NamedColumn('phys_para9_inf',       '') 
    
    #: Physical lower bound PARA10. PHYS_PARA10_INF.name = 'phys_para10_inf'.
    PHYS_PARA10_INF  = NamedColumn('phys_para10_inf',      '') 
    
    #: Physical lower bound PARA11. PHYS_PARA11_INF.name = 'phys_para11_inf'.
    PHYS_PARA11_INF  = NamedColumn('phys_para11_inf',      '') 
    
    #: Physical lower bound PARA12. PHYS_PARA12_INF.name = 'phys_para12_inf'.
    PHYS_PARA12_INF  = NamedColumn('phys_para12_inf',      '') 
    
    #: Physical lower bound PARA13. PHYS_PARA13_INF.name = 'phys_para13_inf'.
    PHYS_PARA13_INF  = NamedColumn('phys_para13_inf',      '') 
    
    #: Physical lower bound PARA14. PHYS_PARA14_INF.name = 'phys_para14_inf'.
    PHYS_PARA14_INF  = NamedColumn('phys_para14_inf',      '') 
    
    #: Physical lower bound PARA15. PHYS_PARA15_INF.name = 'phys_para15_inf'.
    PHYS_PARA15_INF  = NamedColumn('phys_para15_inf',      '') 

    #: Physical lower bound PARA16. PHYS_PARA16_INF.name = 'phys_para16_inf'.
    PHYS_PARA16_INF  = NamedColumn('phys_para16_inf',      '') 
    
    #: Physical lower bound PARA17. PHYS_PARA17_INF.name = 'phys_para17_inf'.
    PHYS_PARA17_INF  = NamedColumn('phys_para17_inf',      '') 
    
    #: Physical lower bound PARA18. PHYS_PARA18_INF.name = 'phys_para18_inf'.
    PHYS_PARA18_INF  = NamedColumn('phys_para18_inf',      '') 
    
    #: Physical lower bound PARA19. PHYS_PARA19_INF.name = 'phys_para19_inf'.
    PHYS_PARA19_INF  = NamedColumn('phys_para19_inf',      '') 
    
    #: Physical lower bound PARA20. PHYS_PARA20_INF.name = 'phys_para20_inf'.
    PHYS_PARA20_INF  = NamedColumn('phys_para20_inf',      '') 
    
    #: Physical lower bound PARA21. PHYS_PARA21_INF.name = 'phys_para21_inf'.
    PHYS_PARA21_INF  = NamedColumn('phys_para21_inf',      '') 
    
    #: Physical lower bound PARA22. PHYS_PARA22_INF.name = 'phys_para22_inf'.
    PHYS_PARA22_INF  = NamedColumn('phys_para22_inf',      '') 
    
    #: Physical lower bound PARA23. PHYS_PARA23_INF.name = 'phys_para23_inf'.
    PHYS_PARA23_INF  = NamedColumn('phys_para23_inf',      '') 
    
    #: Physical lower bound PARA24. PHYS_PARA24_INF.name = 'phys_para24_inf'.
    PHYS_PARA24_INF  = NamedColumn('phys_para24_inf',      '') 
    
    #: Physical lower bound PARA25. PHYS_PARA25_INF.name = 'phys_para25_inf'.
    PHYS_PARA25_INF  = NamedColumn('phys_para25_inf',      '') 
    
    #: Physical lower bound PARA26. PHYS_PARA26_INF.name = 'phys_para26_inf'.
    PHYS_PARA26_INF  = NamedColumn('phys_para26_inf',      '') 
    
    #: Physical lower bound PARA27. PHYS_PARA27_INF.name = 'phys_para27_inf'.
    PHYS_PARA27_INF  = NamedColumn('phys_para27_inf',      '') 
    
    #: Physical upper bound PARA1. PHYS_PARA1_SUP.name = 'phys_para1_sup'.
    PHYS_PARA1_SUP   = NamedColumn('phys_para1_sup',       '') 
    
    #: Physical upper bound PARA2. PHYS_PARA2_SUP.name = 'phys_para2_sup'.
    PHYS_PARA2_SUP   = NamedColumn('phys_para2_sup',       '') 
    
    #: Physical upper bound PARA3. PHYS_PARA3_SUP.name = 'phys_para3_sup'.
    PHYS_PARA3_SUP   = NamedColumn('phys_para3_sup',       '') 
    
    #: Physical upper bound PARA4. PHYS_PARA4_SUP.name = 'phys_para4_sup'.
    PHYS_PARA4_SUP   = NamedColumn('phys_para4_sup',       '') 
    
    #: Physical upper bound PARA5. PHYS_PARA5_SUP.name = 'phys_para5_sup'.
    PHYS_PARA5_SUP   = NamedColumn('phys_para5_sup',       '') 
    
    #: Physical upper bound PARA6. PHYS_PARA6_SUP.name = 'phys_para6_sup'.
    PHYS_PARA6_SUP   = NamedColumn('phys_para6_sup',       '') 
    
    #: Physical upper bound PARA7. PHYS_PARA7_SUP.name = 'phys_para7_sup'.
    PHYS_PARA7_SUP   = NamedColumn('phys_para7_sup',       '') 
    
    #: Physical upper bound PARA8. PHYS_PARA8_SUP.name = 'phys_para8_sup'.
    PHYS_PARA8_SUP   = NamedColumn('phys_para8_sup',       '') 
    
    #: Physical upper bound PARA9. PHYS_PARA9_SUP.name = 'phys_para9_sup'.
    PHYS_PARA9_SUP   = NamedColumn('phys_para9_sup',       '') 
    
    #: Physical upper bound PARA10. PHYS_PARA10_SUP.name = 'phys_para10_sup'.
    PHYS_PARA10_SUP  = NamedColumn('phys_para10_sup',      '') 
    
    #: Physical upper bound PARA11. PHYS_PARA11_SUP.name = 'phys_para11_sup'.
    PHYS_PARA11_SUP  = NamedColumn('phys_para11_sup',      '') 
    
    #: Physical upper bound PARA12. PHYS_PARA12_SUP.name = 'phys_para12_sup'.
    PHYS_PARA12_SUP  = NamedColumn('phys_para12_sup',      '') 
    
    #: Physical upper bound PARA13. PHYS_PARA13_SUP.name = 'phys_para13_sup'.
    PHYS_PARA13_SUP  = NamedColumn('phys_para13_sup',      '') 
    
    #: Physical upper bound PARA14. PHYS_PARA14_SUP.name = 'phys_para14_sup'.
    PHYS_PARA14_SUP  = NamedColumn('phys_para14_sup',      '') 
    
    #: Physical upper bound PARA15. PHYS_PARA15_SUP.name = 'phys_para15_sup'.
    PHYS_PARA15_SUP  = NamedColumn('phys_para15_sup',      '') 
    
    #: Physical upper bound PARA16. PHYS_PARA16_SUP.name = 'phys_para16_sup'.
    PHYS_PARA16_SUP  = NamedColumn('phys_para16_sup',      '') 
    
    #: Physical upper bound PARA17. PHYS_PARA17_SUP.name = 'phys_para17_sup'.
    PHYS_PARA17_SUP  = NamedColumn('phys_para17_sup',      '') 
    
    #: Physical upper bound PARA18. PHYS_PARA18_SUP.name = 'phys_para18_sup'.
    PHYS_PARA18_SUP  = NamedColumn('phys_para18_sup',      '') 
    
    #: Physical upper bound PARA19. PHYS_PARA19_SUP.name = 'phys_para19_sup'.
    PHYS_PARA19_SUP  = NamedColumn('phys_para19_sup',      '') 
    
    #: Physical upper bound PAR20. PHYS_PARA20_SUP.name = 'phys_para20_sup'.
    PHYS_PARA20_SUP  = NamedColumn('phys_para20_sup',      '') 
    
    #: Physical upper bound PAR21. PHYS_PARA21_SUP.name = 'phys_para21_sup'.
    PHYS_PARA21_SUP  = NamedColumn('phys_para21_sup',      '') 
    
    #: Physical upper bound PAR22. PHYS_PARA22_SUP.name = 'phys_para22_sup'.
    PHYS_PARA22_SUP  = NamedColumn('phys_para22_sup',      '') 
    
    #: Physical upper bound PAR23. PHYS_PARA23_SUP.name = 'phys_para23_sup'.
    PHYS_PARA23_SUP  = NamedColumn('phys_para23_sup',      '') 
    
    #: Physical upper bound PAR24. PHYS_PARA24_SUP.name = 'phys_para24_sup'.
    PHYS_PARA24_SUP  = NamedColumn('phys_para24_sup',      '') 
    
    #: Physical upper bound PAR25. PHYS_PARA25_SUP.name = 'phys_para25_sup'.
    PHYS_PARA25_SUP  = NamedColumn('phys_para25_sup',      '') 
    
    #: Physical upper bound PAR26. PHYS_PARA26_SUP.name = 'phys_para26_sup'.
    PHYS_PARA26_SUP  = NamedColumn('phys_para26_sup',      '') 
    
    #: Physical upper bound PAR27. PHYS_PARA27_SUP.name = 'phys_para27_sup'.
    PHYS_PARA27_SUP  = NamedColumn('phys_para27_sup',      '')
   
    
    def __str__(self, *args, **kwargs) -> str:
        r'''
        .. codeauthor:: Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>
        
        Formatted string for this enum.
        '''
        
        return f'{self.name}' if self.name[-2:] != '_2' else f'{self.name.replace("_2", self.value.end)}'