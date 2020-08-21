import numpy as np
from scipy.integrate import odeint
import matplotlib.pyplot as plt
from matplotlib import gridspec
from matplotlib.figure import Figure
import panel as pn
import panel.widgets as pnw
import param

import matplotlib
matplotlib.rcParams.update({'font.size': 10})

class ParameterToScan:
    def __init__(self, name, start, end, step):
        self.name = name
        if (start%1==0) & (end%1==0) & (step%1==0):
            self.slider = pn.widgets.IntSlider(name=name, start=start, end=end, step=step, value=int((end-start)/2))
        else:
            self.slider = pn.widgets.FloatSlider(name=name, start=start, end=end, step=step, value=(end-start)/2)


class Variable:
    def __init__(self, name, val):
        self.name = name
        self.val  = val
        self.checkbox = pn.widgets.Checkbox(name=' '+name, value=True)


class TimeClass(param.Parameterized):
    t0    = param.Parameter(default=0, doc="t start")
    t_max = param.Parameter(default=50, doc="t stop")
    dt    = param.Parameter(default=0.001, doc="t step")


def get_odesoln(model, variables, t_param, params):
    y0 = tuple([var.val for var in variables])
    t = np.arange(t_param.t0, t_param.t_max, t_param.dt)
    soln = odeint(model, y0, t, args=params)    
    
    fig = Figure()
    ax = fig.add_subplot()

    ylabel = ''
    for num, var in enumerate(variables):
        if var.checkbox.value == True:
            ax.plot(t, soln[:, num], label=var.name)
            ylabel += var.name + ', '
            
    ax.set_xlabel('time')
    ax.set_ylabel(ylabel[:-2])
    ax.legend()
    
    return fig


def interactive_scan(model, variables, params):
        
    param_widgets = [p.slider for p in params]
    variable_widgets = [p.checkbox for p in variables]
    
    adv = pn.widgets.Toggle(name='Advanced options')
    t   = TimeClass()
            
    @pn.depends(adv, watch=True)
    def _reactive_widgets(self):
        if adv.value == True:        
            return pn.Column(
                pn.Row(t.param)
            )
        else:
            return pn.Column()
    
    
    def panel():
        expand_layout = pn.Column()

        return pn.Column(
            pn.panel(_reactive_widgets, expand=True, expand_layout=expand_layout),
            expand_layout
        )
                
    
    @pn.depends(*param_widgets, *variable_widgets, watch=True)
    def reactive_plot(*listening_to):
        return get_odesoln(model, variables, t, listening_to[:-len(variables)])
    
    widgets   = pn.Row(pn.Column(*param_widgets, adv), pn.Column(*variable_widgets))
        
    window = pn.Row(reactive_plot, pn.Column(widgets, panel))
    pn.extension()
    return window