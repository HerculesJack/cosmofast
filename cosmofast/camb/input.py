import numpy as np
import bayesfast as bf
from bayesfast.utils.collections import PropertyList
from collections import OrderedDict
import camb

__all__ = []

# TODO: add consistency module to allow different parameterization


_default_input = OrderedDict(
    H0=67.0,
    ombh2=0.022,
    omch2=0.12,
    omk=0.0,
    mnu=0.06,
    nnu=3.046,
    YHe=None,
    meffsterile=0.0,
    tau=None,
    Alens=1.0,
    w=-1.0,
    wa=0.0,
    As=2e-9,
    ns=0.96,
    nrun=0.0,
    nrunrun=0.0,
    r=0.0,
)


_supported_input = list(_default_input.keys())


_set_cosmology_keys = ['H0', 'ombh2', 'omch2', 'omk', 'mnu', 'nnu', 'YHe',
                       'meffsterile', 'tau', 'Alens']


_set_dark_energy_keys = ['w', 'wa']


_set_init_power_keys = ['As', 'ns', 'nrun', 'nrunrun', 'r']


_get_subdict = lambda dic, ks: OrderedDict([(k, dic[k]) for k in ks])


class CInputBase:
    '''Base class for CAMB input model.'''
    def __init__(self, *args, **kwargs):
        raise NotImplementedError('abstract method.')

    def get(self, x):
        raise NotImplementedError('abstract method.')


class CInput(CInputBase):
    '''Default CAMB input model.'''
    def __init__(self, input_vars):
        self.input_vars = input_vars

    @property
    def input_vars(self):
        return self._input_vars

    @input_vars.setter
    def input_vars(self, input_vars):
        self._input_vars = PropertyList(input_vars, self._input_check)

    def _input_check(self, input_vars):
        input_vars = list(input_vars)
        for iv in input_vars:
            if not (iv in _supported_input):
                raise ValueError('unsupported input variable: {}.'.format(iv))
        return input_vars

    def get(self, x):
        try:
            x = np.atleast_1d(x)
            assert x.shape == (len(self.input_vars),)
        except Exception:
            raise ValueError('invalid input x.')
        input_dict = _default_input.copy()
        for i, iv in enumerate(self.input_vars):
            input_dict[iv] = x[i]

        pars = camb.CAMBparams()
        pars.set_cosmology(**_get_subdict(input_dict, _set_cosmology_keys))
        _dark_energy_model = 'fluid' if input_dict['wa'] == 0. else 'ppf'
        pars.set_dark_energy(dark_energy_model=_dark_energy_model,
                             **_get_subdict(input_dict, _set_dark_energy_keys))
        pars.InitPower.set_params(**_get_subdict(input_dict,
                                                 _set_init_power_keys))
        return pars
