# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/00_repr_str.ipynb.

# %% auto 0
__all__ = ['lovely']

# %% ../nbs/00_repr_str.ipynb 3
import warnings

import torch


from lovely_numpy import np_to_str_common, pretty_str, sparse_join, ansi_color
from lovely_numpy import config as lnp_config

from .utils.config import get_config


# %% ../nbs/00_repr_str.ipynb 6
def type_to_dtype(t: str) -> torch.dtype:
    "Convert str, e.g. 'float32' to torch.dtype e.g torch.float32"
    
    dtp = vars(torch)[t]
    assert isinstance(dtp, torch.dtype)
    return dtp

# %% ../nbs/00_repr_str.ipynb 8
dtnames = { type_to_dtype(k): v
                for k,v in {"float32": "",
                            "float16": "f16",
                            "float64": "f64",
                            "uint8": "u8", # torch does not have uint16/32/64
                            "int8": "i8",
                            "int16": "i16",
                            "int32": "i32",
                            "int64": "i64",
                        }.items()
}

def short_dtype(x): return dtnames.get(x.dtype, str(x.dtype)[6:])

# %% ../nbs/00_repr_str.ipynb 10
def plain_repr(x: torch.Tensor):
    "Pick the right function to get a plain repr"
    # assert isinstance(x, np.ndarray), f"expected np.ndarray but got {type(x)}" # Could be a sub-class.
    return x._plain_repr() if hasattr(type(x), "_plain_repr") else repr(x)

def plain_str(x: torch.Tensor):
    "Pick the right function to get a plain str."
    # assert isinstance(x, np.ndarray), f"expected np.ndarray but got {type(x)}"
    return x._plain_str() if hasattr(type(x), "_plain_str") else str(x)

# %% ../nbs/00_repr_str.ipynb 11
def is_nasty(t: torch.Tensor):
    """Return true of any `t` values are inf or nan"""
    
    if t.numel() == 0: return False # amin/amax don't like zero-lenght tensors

    # Unlike .min()/.max(), amin/amax do not allocate extra GPU memory.

    t_min = t.amin().cpu()
    t_max = t.amax().cpu()

    return (t_min.isnan() or t_min.isinf() or t_max.isinf()).item()

# %% ../nbs/00_repr_str.ipynb 13
def torch_to_str_common(t: torch.Tensor,  # Input
                        color=True,       # ANSI color highlighting
                        ) -> str:
    
    if t.numel() == 0: return ansi_color("empty", "grey", color)


    # Note: At the moment the MPS backend does not support isinf or isnan.
    # Move to CPU, as this does not cost us anything.
    amin, amax = t.amin().cpu(), t.amax().cpu()

    zeros = ansi_color("all_zeros", "grey", color) if amin.eq(0) and amax.eq(0) and t.numel() > 1 else None
    pinf = ansi_color("+Inf!", "red", color) if amax.isposinf() else None
    ninf = ansi_color("-Inf!", "red", color) if amin.isneginf() else None
    nan = ansi_color("NaN!", "red", color) if amin.isnan() else None

    attention = sparse_join([zeros,pinf,ninf,nan])
    numel = f"n={t.numel()}" if t.numel() > 5 and max(t.shape) != t.numel() else None

    summary = None
    if not zeros:
        minmax = f"x∈[{pretty_str(amin)}, {pretty_str(amax)}]" if t.numel() > 2 else None
        meanstd = f"μ={pretty_str(t.mean())} σ={pretty_str(t.std())}" if t.numel() >= 2 else None
        summary = sparse_join([numel, minmax, meanstd])

    return sparse_join([ summary, attention])

# %% ../nbs/00_repr_str.ipynb 14
# tensor.is_cpu was only introduced in 1.13.
def is_cpu(t: torch.Tensor):
    return t.device == torch.device("cpu")

# %% ../nbs/00_repr_str.ipynb 15
@torch.no_grad()
def to_str(t: torch.Tensor,
            plain: bool=False,
            verbose: bool=False,
            depth=0,
            lvl=0,
            color=None) -> str:

    if plain:
        return plain_repr(t)

    conf = get_config()

    tname = "tensor" if type(t) is torch.Tensor else type(t).__name__.split(".")[-1]
    shape = str(list(t.shape)) if t.ndim else None
    type_str = sparse_join([tname, shape], sep="")
    
    dev = str(t.device) if t.device.type != "cpu" else None
    dtype = short_dtype(t)
    grad_fn = t.grad_fn.name() if t.grad_fn else None
    # PyTorch does not want you to know, but all `grad_fn``
    # tensors actuall have `requires_grad=True`` too.
    grad = "grad" if t.requires_grad else None 
    

    # For complex tensors, just show the shape / size part for now.
    if not t.is_complex():
        color = conf.color if color is None else color
        # `lovely-numpy` is used to calculate stats when doing so on GPU would require
        # memory allocation (not float tensors, tensors with bad numbers), or if the
        # data is on CPU (because numpy is faster).
        #
        # Temporarily set the numpy config to match our config for consistency.
        with lnp_config(precision=conf.precision,
                        threshold_min=conf.threshold_min,
                        threshold_max=conf.threshold_max,
                        sci_mode=conf.sci_mode):

            if is_cpu(t) or is_nasty(t) or not t.is_floating_point():
                common = np_to_str_common(t.detach().cpu().numpy(), color=color, ddof=1)
            else:
                common = torch_to_str_common(t, color=color)

            vals = pretty_str(t.cpu().numpy()) if 0 < t.numel() <= 10 else None
            res = sparse_join([type_str, dtype, common, grad, grad_fn, dev, vals])
    else:
        res = plain_repr(t)


    if verbose:
        res += "\n" + plain_repr(t)

    if depth and t.dim() > 1:

        deep_width = min((t.shape[0]), conf.deeper_width) # Print at most this many lines
        deep_lines = [ " "*conf.indent*(lvl+1) + to_str(t[i,:], depth=depth-1, lvl=lvl+1)
                            for i in range(deep_width)] 

        # If we were limited by width, print ...
        if deep_width < t.shape[0]: deep_lines.append(" "*conf.indent*(lvl+1) + "...")

        res += "\n" + "\n".join(deep_lines)

    return res

# %% ../nbs/00_repr_str.ipynb 16
def history_warning():
    "Issue a warning (once) ifw e are running in IPYthon with output cache enabled"

    if "get_ipython" in globals() and get_ipython().cache_size > 0:
        warnings.warn("IPYthon has its output cache enabled. See https://xl0.github.io/lovely-tensors/history.html")

# %% ../nbs/00_repr_str.ipynb 19
class StrProxy():
    def __init__(self, t: torch.Tensor, plain=False, verbose=False, depth=0, lvl=0, color=None):
        self.t = t
        self.plain = plain
        self.verbose = verbose
        self.depth=depth
        self.lvl=lvl
        self.color=color
        history_warning()
    
    def __repr__(self):
        return to_str(self.t, plain=self.plain, verbose=self.verbose,
                      depth=self.depth, lvl=self.lvl, color=self.color)

    # This is used for .deeper attribute and .deeper(depth=...).
    # The second onthe results in a __call__.
    def __call__(self, depth=1):
        return StrProxy(self.t, depth=depth)

# %% ../nbs/00_repr_str.ipynb 20
def lovely(t: torch.Tensor, # Tensor of interest
            verbose=False,  # Whether to show the full tensor
            plain=False,    # Just print if exactly as before
            depth=0,        # Show stats in depth
            color=None):    # Force color (True/False) or auto.
    return StrProxy(t, verbose=verbose, plain=plain, depth=depth, color=color)
