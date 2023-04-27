# AUTOGENERATED! DO NOT EDIT! File to edit: ../../nbs/03a_utils.config.ipynb.

# %% auto 0
__all__ = ['set_config', 'get_config', 'config']

# %% ../../nbs/03a_utils.config.ipynb 4
from copy import copy
from types import SimpleNamespace
from typing import Optional, Union, Callable, TypeVar
from contextlib import contextmanager
from lovely_numpy import config as np_config

# %% ../../nbs/03a_utils.config.ipynb 5
class Config(SimpleNamespace):
    "Config"
    def __init__(self,
            precision     = 3,    # Digits after `.`
            threshold_max = 3,    # .abs() larger than 1e3 -> Sci mode
            threshold_min = -4,   # .abs() smaller that 1e-4 -> Sci mode
            sci_mode      = None, # Sci mode (2.3e4). None=auto
            show_mem_above= 1024, # Show memory footprint above this threshold
            indent        = 2,    # Indent for .deeper()
            color         = True, # ANSI colors in text
            deeper_width  = 9,    # For .deeper, width per level
            plt_seed      = 42,   # Sampling seed for `plot`
            fig_close     = True, # Close matplotlib Figure
            fig_show      = False,# Call `plt.show()` for `.plt`, `.chans` and `.rgb`

    ):
        super().__init__(**{k:v for k,v in locals().items() if k not in ["self", "__class__"]})

_defaults = Config()
_config = copy(_defaults)

# %% ../../nbs/03a_utils.config.ipynb 8
# Allows passing None as an argument to reset the 
class _Default():
    def __repr__(self):
        return "Ignore"
D = _Default()
Default = TypeVar("Default")

# %% ../../nbs/03a_utils.config.ipynb 9
def set_config( precision       :Optional[Union[Default,int]]  =D,
                threshold_min   :Optional[Union[Default,int]]  =D,
                threshold_max   :Optional[Union[Default,int]]  =D,
                sci_mode        :Optional[Union[Default,bool]] =D,
                show_mem_above  :Optional[Union[Default,bool]] =D,
                indent          :Optional[Union[Default,bool]] =D,
                color           :Optional[Union[Default,bool]] =D,
                deeper_width    :Optional[Union[Default,int]]  =D,
                plt_seed        :Optional[Union[Default,int]]  =D,
                fig_close       :Optional[Union[Default,bool]] =D,
                fig_show        :Optional[Union[Default,bool]] =D
                ) -> None:

    "Set config variables"
    args = locals().copy()
    for k,v in args.items():
        if v != D:
            if v is None:
                setattr(_config, k, getattr(_defaults, k))
            else:
                setattr(_config, k, v)

# %% ../../nbs/03a_utils.config.ipynb 10
def get_config():
    "Get a copy of config variables"
    return copy(_config)

# %% ../../nbs/03a_utils.config.ipynb 11
@contextmanager
def config( precision       :Optional[Union[Default,int]]   =D,
            threshold_min   :Optional[Union[Default,int]]   =D,
            threshold_max   :Optional[Union[Default,int]]   =D,
            sci_mode        :Optional[Union[Default,bool]]  =D,
            show_mem_above  :Optional[Union[Default,bool]]  =D,
            indent          :Optional[Union[Default,bool]]  =D,
            color           :Optional[Union[Default,bool]]  =D,
            deeper_width    :Optional[Union[Default,int]]   =D,
            plt_seed        :Optional[Union[Default,int]]   =D,
            fig_close       :Optional[Union[Default,bool]]  =D,
            fig_show        :Optional[Union[Default,bool]]  =D
            ):


    "Context manager for temporarily setting printting options."
    global _config
    new_opts = { k:v for k, v in locals().items() if v != D }
    old_opts = copy(get_config().__dict__)

    try:
        set_config(**new_opts)
        yield
    finally:
        set_config(**old_opts)
