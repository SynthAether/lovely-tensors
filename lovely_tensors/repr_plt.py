# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/02_repr_plt.ipynb.

# %% auto 0
__all__ = ['plot']

# %% ../nbs/02_repr_plt.ipynb 3
import math
from typing import Union, Any, Optional as O
from functools import cached_property
from matplotlib import pyplot as plt, axes, figure, rc_context
from IPython.core.pylabtools import print_figure

import torch

from .repr_str import to_str, pretty_str
from lovely_numpy.repr_plt import fig_plot

# %% ../nbs/02_repr_plt.ipynb 4
# This is here for the monkey-patched tensor use case.
# Gives the ability to call both .plt and .plt(ax=ax).  

class PlotProxy(): 
    """Flexible `PIL.Image.Image` wrapper"""

    def __init__(self, x:torch.Tensor):
        self.x = x
        self.params = dict( center="zero",
                            max_s=10000,
                            plt0=True,
                            ax=None)

    def __call__(   self,
                    center  :O[str] =None,
                    max_s   :O[int] =None,
                    plt0    :Any    =None,
                    ax      :O[axes.Axes]=None):

        self.params.update( { k:v for
                    k,v in locals().items()
                    if k != "self" and v is not None } )
        
        _ = self.fig # Trigger figure generation
        return self

    @cached_property
    def fig(self) -> figure.Figure:
        return fig_plot( self.x.detach().cpu().numpy(),
                        summary=to_str(self.x, color=False),
                        **self.params)

    def _repr_png_(self):
        return print_figure(self.fig, fmt="png",
            metadata={"Software": "Matplotlib, https://matplotlib.org/"})

    def _repr_svg_(self):
        # Metadata and context for a mode deterministic svg generation
        metadata={
            "Date": None,
            "Creator": "Matplotlib, https://matplotlib.org/",
        }
        with rc_context({"svg.hashsalt": "1"}):
            svg_repr = print_figure(self.fig, fmt="svg", metadata=metadata)
        return svg_repr


# %% ../nbs/02_repr_plt.ipynb 5
def plot(   x       : torch.Tensor, # Tensor to explore
            center  :str    ="zero",    # Center plot on  `zero`, `mean`, or `range`
            max_s   :int    =10000,     # Draw up to this many samples. =0 to draw all
            plt0    :Any    =True,      # Take zero values into account
            ax      :O[axes.Axes]=None  # Optionally provide a matplotlib axes.
        ) -> PlotProxy:
    
    args = locals()
    del args["x"]

    return PlotProxy(x)(**args)

