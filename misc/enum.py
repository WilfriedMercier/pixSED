#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
.. codeauthor:: Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>

Enumerations used in other parts of the code.
"""

from enum          import Enum
from astropy.units import Unit
from .misc         import NamedColumn

class CleanMethod(Enum):
    r'''An enumeration for the cleaning method used by the filters.'''
     
    ZERO = 'zero'
    MIN  = 'min'
    
class SEDcode(Enum):
    r'''An enumeration for the SED fitting codes available.'''
    
    LEPHARE = 'lephare'
    CIGALE  = 'cigale'
    
###################################
#        LePhare only Enum        #
###################################
    
class ANDOR(Enum):
    r'''An enumeration with AND or OR options for LePhare.'''
    
    AND = 'AND'
    OR  = 'OR'
    
class MagType(Enum):
    r'''An enumeration for valid magnitude types for LePhare.'''
    
    AB   = 'AB'
    VEGA = 'VEGA'
    
class TableFormat(Enum):
    r'''An enumerator for valid table format for LePhare.'''
    
    MEME = 'MEME'
    MMEE = 'MMEE'
    
class TableType(Enum):
    r'''An enumerator for valid table data type for LePhare.'''
    
    LONG  = 'LONG'
    SHORT = 'SHORT'
    
class TableUnit(Enum):
    r'''An enumeration for valid values for table units for LePhare.'''
    
    MAG  = 'M'
    FLUX = 'F'
    
class YESNO(Enum):
    r'''An enumeration with YES or NO options for LePhare.'''
    
    YES = 'YES'
    NO  = 'NO'
   
class LePhareOutputParam(Enum):
    r'''An enumeration for LePhare output parameters with corresponding table name and table unit.'''
    
    Z_BEST           = NamedColumn('z_best',               '')
    Z_BEST68_LOW     = NamedColumn('z_best_l68',           '') 
    Z_BEST68_HIGH    = NamedColumn('z_best_u68',           '') 
    Z_BEST90_LOW     = NamedColumn('z_best_l90',           '') 
    Z_BEST90_HIGH    = NamedColumn('z_best_u90',           '') 
    Z_BEST99_LOW     = NamedColumn('z_best_l99',           '') 
    Z_BEST99_HIGH    = NamedColumn('z_best_u99',           '')
    Z_ML             = NamedColumn('z_ML',                 '') 
    Z_ML68_LOW       = NamedColumn('z_ML_l68',             '') 
    Z_ML68_HIGH      = NamedColumn('z_ML_u68',             '') 
    CHI_BEST         = NamedColumn('chi2',                 '') 
    MOD_BEST         = NamedColumn('Mod_best',             '') 
    EXTLAW_BEST      = NamedColumn('Ext_law_best',         '') 
    EBV_BEST         = NamedColumn('E(B-V)_best',          '') 
    ZF_BEST          = NamedColumn('ZF_BEST',              '') # No idea what this is
    MAG_ABS_BEST     = NamedColumn('mag_abs_best',         'dex') 
    PDZ_BEST         = NamedColumn('pdz_best',             '') 
    SCALE_BEST       = NamedColumn('scale_best',           '') 
    DIST_MOD_BEST    = NamedColumn('dist_mod_best',        '') # No idea
    NBAND_USED       = NamedColumn('nband',                '') 
    NBAND_ULIM       = NamedColumn('nband_ulim',           '') 
    Z_SEC            = NamedColumn('z_second',             '') 
    CHI_SEC          = NamedColumn('chi2_second',          '') 
    MOD_SEC          = NamedColumn('Mod_second',           '') 
    AGE_SEC          = NamedColumn('age_second',           'yr') 
    EBV_SEC          = NamedColumn('E(B-V)_second',        '') 
    ZF_SEC           = NamedColumn('ZF_SEC',               '') # No idea
    MAG_ABS_SEC      = NamedColumn('mag_abs_second',       'dex') 
    PDZ_SEC          = NamedColumn('pdz_second',           '') 
    SCALE_SEC        = NamedColumn('scale_second',         '') 
    Z_QSO            = NamedColumn('z_qso',                '')
    CHI_QSO          = NamedColumn('chi2_qso',             '') 
    MOD_QSO          = NamedColumn('Mod_qso',              '') 
    MAG_ABS_QSO      = NamedColumn('mag_abs_qso',          'dex') 
    DIST_MOD_QSO     = NamedColumn('dist_mod_qso',         '') 
    MOD_STAR         = NamedColumn('Mod_star',             '')
    CHI_STAR         = NamedColumn('chi2_star',            '')
    MAG_OBS_2        = NamedColumn('mag_obs()',            'dex',  end='()')
    ERR_MAG_OBS_2    = NamedColumn('mag_obs_err()',        'dex',  end='()')
    MAG_MOD_2        = NamedColumn('mag_mod()',            'dex',  end='()')
    K_COR_2          = NamedColumn('K_correction()',       'dex',  end='()')
    MAG_ABS_2        = NamedColumn('mag_abs()',            'dex',  end='()')
    MABS_FILT_2      = NamedColumn('MABS_FILT()',          'dex',  end='()') # No idea
    K_COR_QSO_2      = NamedColumn('K_correction_qso()',   'dex',  end='()')
    MAG_ABS_QSO_2    = NamedColumn('mag_abs_qso()',        'dex', end='()') 
    PDZ_2            = NamedColumn('pdz()',                '',    end='()') 
    CONTEXT          = NamedColumn('context',              '') 
    ZSPEC            = NamedColumn('zspec',                '') 
    STRING_INPUT     = NamedColumn('string_input',         '') 
    LUM_TIR_BEST     = NamedColumn('luminosity_tir_best',  'erg/s') # Not sure about unit
    LIB_FIR          = NamedColumn('library_fir',          '') 
    MOD_FIR          = NamedColumn('mod_fir',              '') 
    CHI2_FIR         = NamedColumn('chi2_fir',             '') 
    FSCALE_FIR       = NamedColumn('fscale_fir',           '') 
    NBAND_FIR        = NamedColumn('nband_fir',            '') 
    LUM_TIR_MED      = NamedColumn('luminosity_tir_med',   '') 
    LUM_TIR_INF      = NamedColumn('luminosity_tir_inf',   '') 
    LUM_TIR_SUP      = NamedColumn('luminosity_tir_sup',   '') 
    MAG_MOD_FIR_2    = NamedColumn('mag_mod_fir',          'dex', end='()') 
    MAG_ABS_FIR_2    = NamedColumn('mag_abs_fir',          'dex', end='()') 
    K_COR_FIR_2      = NamedColumn('K_correction_fir',     'dex', end='()') 
    AGE_BEST         = NamedColumn('age_best',             'yr') 
    AGE_INF          = NamedColumn('age_inf',              'yr') 
    AGE_MED          = NamedColumn('age_median',           'yr') 
    AGE_SUP          = NamedColumn('age_sup',              'yr') 
    LDUST_BEST       = NamedColumn('luminosity_dust_best', 'erg/s') # Not sure about unit
    LDUST_INF        = NamedColumn('luminosity_dust_inf',  'erg/s') # Not sure about unit 
    LDUST_MED        = NamedColumn('luminosity_dust_med',  'erg/s') # Not sure about unit, 
    LDUST_SUP        = NamedColumn('luminosity_dust_sup',  'erg/s') # Not sure about unit, 
    MASS_BEST        = NamedColumn('mass_best',            'Msun',    log=True) 
    MASS_INF         = NamedColumn('mass_inf',             'Msun',    log=True) 
    MASS_MED         = NamedColumn('mass_med',             'Msun',    log=True) 
    MASS_SUP         = NamedColumn('mass_sup',             'Msun',    log=True) 
    SFR_BEST         = NamedColumn('sfr_best',             'Msun/yr', log=True) 
    SFR_INF          = NamedColumn('sfr_inf',              'Msun/yr', log=True) 
    SFR_MED          = NamedColumn('sfr_med',              'Msun/yr', log=True) 
    SFR_SUP          = NamedColumn('sfr_sup',              'Msun/yr', log=True) 
    SSFR_BEST        = NamedColumn('ssfr_best',            '1/yr',    log=True) 
    SSFR_INF         = NamedColumn('ssfr_inf',             '1/yr',    log=True) 
    SSFR_MED         = NamedColumn('ssfr_med',             '1/yr',    log=True) 
    SSFR_SUP         = NamedColumn('ssfr_sup',             '1/yr',    log=True) 
    LUM_NUV_BEST     = NamedColumn('luminosity_nuv_best',  'erg/s') # Not sure about unit
    LUM_R_BEST       = NamedColumn('luminosity_R_best',    'erg/s') # Not sure about unit
    LUM_K_BEST       = NamedColumn('luminosity_K_best',    'erg/s') # Not sure about unit
    PHYS_CHI2_BEST   = NamedColumn('phys_chi2_best',       '') 
    PHYS_MOD_BEST    = NamedColumn('phys_mod_best',        '') 
    PHYS_MAG_MOD_2   = NamedColumn('phys_mag_mod',         'dex', end='()') 
    PHYS_MAG_ABS_2   = NamedColumn('phys_mag_abs',         'dex', end='()') 
    PHYS_K_COR_2     = NamedColumn('phys_K_correction',    'dex', end='()') 
    PHYS_PARA1_BEST  = NamedColumn('phys_para1_best',      '') 
    PHYS_PARA2_BEST  = NamedColumn('phys_para2_best',      '') 
    PHYS_PARA3_BEST  = NamedColumn('phys_para3_best',      '') 
    PHYS_PARA4_BEST  = NamedColumn('phys_para4_best',      '') 
    PHYS_PARA5_BEST  = NamedColumn('phys_para5_best',      '') 
    PHYS_PARA6_BEST  = NamedColumn('phys_para6_best',      '') 
    PHYS_PARA7_BEST  = NamedColumn('phys_para7_best',      '') 
    PHYS_PARA8_BEST  = NamedColumn('phys_para8_best',      '') 
    PHYS_PARA9_BEST  = NamedColumn('phys_para9_best',      '') 
    PHYS_PARA10_BEST = NamedColumn('phys_para10_best',     '') 
    PHYS_PARA11_BEST = NamedColumn('phys_para11_best',     '') 
    PHYS_PARA12_BEST = NamedColumn('phys_para12_best',     '') 
    PHYS_PARA13_BEST = NamedColumn('phys_para13_best',     '') 
    PHYS_PARA14_BEST = NamedColumn('phys_para14_best',     '') 
    PHYS_PARA15_BEST = NamedColumn('phys_para15_best',     '') 
    PHYS_PARA16_BEST = NamedColumn('phys_para16_best',     '') 
    PHYS_PARA17_BEST = NamedColumn('phys_para17_best',     '') 
    PHYS_PARA18_BEST = NamedColumn('phys_para18_best',     '') 
    PHYS_PARA19_BEST = NamedColumn('phys_para19_best',     '') 
    PHYS_PARA20_BEST = NamedColumn('phys_para20_best',     '') 
    PHYS_PARA21_BEST = NamedColumn('phys_para21_best',     '') 
    PHYS_PARA22_BEST = NamedColumn('phys_para22_best',     '') 
    PHYS_PARA23_BEST = NamedColumn('phys_para23_best',     '') 
    PHYS_PARA24_BEST = NamedColumn('phys_para24_best',     '') 
    PHYS_PARA25_BEST = NamedColumn('phys_para25_best',     '') 
    PHYS_PARA26_BEST = NamedColumn('phys_para26_best',     '') 
    PHYS_PARA27_BEST = NamedColumn('phys_para27_best',     '') 
    PHYS_PARA1_MED   = NamedColumn('phys_para1_med',       '') 
    PHYS_PARA2_MED   = NamedColumn('phys_para2_med',       '') 
    PHYS_PARA3_MED   = NamedColumn('phys_para3_med',       '') 
    PHYS_PARA4_MED   = NamedColumn('phys_para4_med',       '') 
    PHYS_PARA5_MED   = NamedColumn('phys_para5_med',       '') 
    PHYS_PARA6_MED   = NamedColumn('phys_para6_med',       '') 
    PHYS_PARA7_MED   = NamedColumn('phys_para7_med',       '') 
    PHYS_PARA8_MED   = NamedColumn('phys_para8_med',       '') 
    PHYS_PARA9_MED   = NamedColumn('phys_para9_med',       '') 
    PHYS_PARA10_MED  = NamedColumn('phys_para10_med',      '') 
    PHYS_PARA11_MED  = NamedColumn('phys_para11_med',      '') 
    PHYS_PARA12_MED  = NamedColumn('phys_para12_med',      '') 
    PHYS_PARA13_MED  = NamedColumn('phys_para13_med',      '') 
    PHYS_PARA14_MED  = NamedColumn('phys_para14_med',      '') 
    PHYS_PARA15_MED  = NamedColumn('phys_para15_med',      '') 
    PHYS_PARA16_MED  = NamedColumn('phys_para16_med',      '') 
    PHYS_PARA17_MED  = NamedColumn('phys_para17_med',      '') 
    PHYS_PARA18_MED  = NamedColumn('phys_para18_med',      '') 
    PHYS_PARA19_MED  = NamedColumn('phys_para19_med',      '') 
    PHYS_PARA20_MED  = NamedColumn('phys_para20_med',      '') 
    PHYS_PARA21_MED  = NamedColumn('phys_para21_med',      '') 
    PHYS_PARA22_MED  = NamedColumn('phys_para22_med',      '') 
    PHYS_PARA23_MED  = NamedColumn('phys_para23_med',      '') 
    PHYS_PARA24_MED  = NamedColumn('phys_para24_med',      '') 
    PHYS_PARA25_MED  = NamedColumn('phys_para25_med',      '') 
    PHYS_PARA26_MED  = NamedColumn('phys_para26_med',      '') 
    PHYS_PARA27_MED  = NamedColumn('phys_para27_med',      '') 
    PHYS_PARA1_INF   = NamedColumn('phys_para1_inf',       '') 
    PHYS_PARA2_INF   = NamedColumn('phys_para2_inf',       '') 
    PHYS_PARA3_INF   = NamedColumn('phys_para3_inf',       '') 
    PHYS_PARA4_INF   = NamedColumn('phys_para4_inf',       '') 
    PHYS_PARA5_INF   = NamedColumn('phys_para5_inf',       '') 
    PHYS_PARA6_INF   = NamedColumn('phys_para6_inf',       '') 
    PHYS_PARA7_INF   = NamedColumn('phys_para7_inf',       '') 
    PHYS_PARA8_INF   = NamedColumn('phys_para8_inf',       '') 
    PHYS_PARA9_INF   = NamedColumn('phys_para9_inf',       '') 
    PHYS_PARA10_INF  = NamedColumn('phys_para10_inf',      '') 
    PHYS_PARA11_INF  = NamedColumn('phys_para11_inf',      '') 
    PHYS_PARA12_INF  = NamedColumn('phys_para12_inf',      '') 
    PHYS_PARA13_INF  = NamedColumn('phys_para13_inf',      '') 
    PHYS_PARA14_INF  = NamedColumn('phys_para14_inf',      '') 
    PHYS_PARA15_INF  = NamedColumn('phys_para15_inf',      '') 
    PHYS_PARA16_INF  = NamedColumn('phys_para16_inf',      '') 
    PHYS_PARA17_INF  = NamedColumn('phys_para17_inf',      '') 
    PHYS_PARA18_INF  = NamedColumn('phys_para18_inf',      '') 
    PHYS_PARA19_INF  = NamedColumn('phys_para19_inf',      '') 
    PHYS_PARA20_INF  = NamedColumn('phys_para20_inf',      '') 
    PHYS_PARA21_INF  = NamedColumn('phys_para21_inf',      '') 
    PHYS_PARA22_INF  = NamedColumn('phys_para22_inf',      '') 
    PHYS_PARA23_INF  = NamedColumn('phys_para23_inf',      '') 
    PHYS_PARA24_INF  = NamedColumn('phys_para24_inf',      '') 
    PHYS_PARA25_INF  = NamedColumn('phys_para25_inf',      '') 
    PHYS_PARA26_INF  = NamedColumn('phys_para26_inf',      '') 
    PHYS_PARA27_INF  = NamedColumn('phys_para27_inf',      '') 
    PHYS_PARA1_SUP   = NamedColumn('phys_para1_sup',       '') 
    PHYS_PARA2_SUP   = NamedColumn('phys_para2_sup',       '') 
    PHYS_PARA3_SUP   = NamedColumn('phys_para3_sup',       '') 
    PHYS_PARA4_SUP   = NamedColumn('phys_para4_sup',       '') 
    PHYS_PARA5_SUP   = NamedColumn('phys_para5_sup',       '') 
    PHYS_PARA6_SUP   = NamedColumn('phys_para6_sup',       '') 
    PHYS_PARA7_SUP   = NamedColumn('phys_para7_sup',       '') 
    PHYS_PARA8_SUP   = NamedColumn('phys_para8_sup',       '') 
    PHYS_PARA9_SUP   = NamedColumn('phys_para9_sup',       '') 
    PHYS_PARA10_SUP  = NamedColumn('phys_para10_sup',      '') 
    PHYS_PARA11_SUP  = NamedColumn('phys_para11_sup',      '') 
    PHYS_PARA12_SUP  = NamedColumn('phys_para12_sup',      '') 
    PHYS_PARA13_SUP  = NamedColumn('phys_para13_sup',      '') 
    PHYS_PARA14_SUP  = NamedColumn('phys_para14_sup',      '') 
    PHYS_PARA15_SUP  = NamedColumn('phys_para15_sup',      '') 
    PHYS_PARA16_SUP  = NamedColumn('phys_para16_sup',      '') 
    PHYS_PARA17_SUP  = NamedColumn('phys_para17_sup',      '') 
    PHYS_PARA18_SUP  = NamedColumn('phys_para18_sup',      '') 
    PHYS_PARA19_SUP  = NamedColumn('phys_para19_sup',      '') 
    PHYS_PARA20_SUP  = NamedColumn('phys_para20_sup',      '') 
    PHYS_PARA21_SUP  = NamedColumn('phys_para21_sup',      '') 
    PHYS_PARA22_SUP  = NamedColumn('phys_para22_sup',      '') 
    PHYS_PARA23_SUP  = NamedColumn('phys_para23_sup',      '') 
    PHYS_PARA24_SUP  = NamedColumn('phys_para24_sup',      '') 
    PHYS_PARA25_SUP  = NamedColumn('phys_para25_sup',      '') 
    PHYS_PARA26_SUP  = NamedColumn('phys_para26_sup',      '') 
    PHYS_PARA27_SUP  = NamedColumn('phys_para27_sup',      '')
   
    
    def __str__(self, *args, **kwargs) -> str:
        r'''
        .. codeauthor:: Wilfried Mercier - IRAP <wilfried.mercier@irap.omp.eu>
        
        Formatted string for this enum.
        '''
        
        return f'{self.name}' if self.name[-2:] != '_2' else f'{self.name.replace("_2", self.value.end)}'