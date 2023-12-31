# -*- coding: utf-8 -*-
"""modelling_widget

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1GFo_7_A1c7v5aX66F4Y14VC2k6b7H3bl
"""

# Commented out IPython magic to ensure Python compatibility.
# Making all necessary imports.
import ipywidgets as widgets
from IPython.display import display
from google.colab import output
output.enable_custom_widget_manager()
import numpy as np
import matplotlib.pyplot as plt
from astropy.modeling import models, fitting

__all__ = ['modelling_widget']
def modelling_widget(arcspec, silent = False, model = 'gauss'):
    """
    Takes a flattened spectrum 1D object with continuum at 0 and allows you to
    interactively fit a gaussian or voigt curve.

    Each line is roughly identified by the user, then a Gaussian is fit to
    determine the precise line center. The reference value for the line is then
    entered by the user.

    NOTE: Because of the widgets used, this is not well suited for inclusion in
    pipelines and instead is ideal for interactive analysis.

    Parameters:

    arcspec: Spectrum1D
    The 1d spectrum of the arc lamp to be fit.

    silent: bool (optional), default is False
    Set to True to silence the instruction print out each time.

    model: string, "gauss" or "voigt"
    Whether to use a gaussian or voigt fitting.

    Returns:

    model_equation: list
    Modeling function that will be used.

    xvals: list
    Inpts for the modeling function that will be used.

    """

    # the fluxes & pixels within the arc-spectrum
    flux = arcspec.flux.value
    xpixels = arcspec.spectral_axis.value

    msg = '''
    Instructions:
    ------------
    0) This assumes the continuum of your spectra is flattened and at 0. For proper interactive widgets, ensure you're
    using the Notebook backend in the Jupyter notebook, e.g.:
#         %matplotlib notebook,
    or in Google Colab:
#         %matplotlib widget
    1) Click the plot at one endpoint, and click the button when you're satisfied.
    2) Click the plot at the other endpoint and click the button again once you have it where you would like.
    3) Click the plot at the vertical extrema (peak or trough) then click the button.
    4) If all your values look right (they will show up on the plot), click the final button to graph your fitted curve.'''

    if not silent:
        print(msg)

    endpts = []
    amp_cal = []
    mean = []
    pixvals = []
    model_equation = []
    xvals = []

    # Create widgets, two text boxes, and a button.
    xval1 = widgets.BoundedFloatText(
        value = 5555.0,
        min = np.nanmin(xpixels),
        max = np.nanmax(xpixels),
        step = 0.01,
        description = 'Mean Value (from click):',
        style = {'description_width': 'initial'})

    xval2 = widgets.BoundedFloatText(
        value = 5555.0,
        min = np.nanmin(xpixels),
        max = np.nanmax(xpixels),
        step = 0.01,
        description = 'Endpoint 1 (from click):',
        style = {'description_width': 'initial'})

    xval3 = widgets.BoundedFloatText(
        value = 5555.0,
        min = np.nanmin(xpixels),
        max = np.nanmax(xpixels),
        step = 0.01,
        description = 'Endpoint 2 (from click):',
        style = {'description_width': 'initial'})

    xval4 = widgets.BoundedFloatText(
        value = 1.0,
        min = np.nanmin(flux),
        max = np.nanmax(flux),
        step = 0.01,
        description = 'Peak (from click):',
        style = {'description_width': 'initial'})

    linename = widgets.Text(  # value='Enter Wavelength',
        placeholder = 'Enter Continuum Value',
        description = 'Continuum Flux:',
        style = {'description_width': 'initial'})

    button1 = widgets.Button(description = 'Assign Mean')
    button2 = widgets.Button(description = 'Assign Endpoints')
    button3 = widgets.Button(description = "Assign Amplitude")
    if model == 'gauss':
      button4 = widgets.Button(description = 'Graph Gaussian curve')
    elif model == 'voigt':
      button4 = widgets.Button(description = 'Graph Voigt curve')

    fig, ax = plt.subplots(figsize = (11, 5))

    # Handle plot clicks.
    def onplotclick(event):
        if len(mean) < 1:
          xval1.value = event.xdata
        elif len(endpts) < 1:
          xval2.value = event.xdata
        elif len(endpts) < 2:
          xval3.value = event.xdata
        elif len(amp_cal) < 1:
          xval4.value = event.ydata
        return

    fig.canvas.mpl_connect('button_press_event', onplotclick)

    # Handle button clicks.
    def onbuttonclick1(_):
        mean.append(xval1.value)
        print("Mean:", mean)
        ax.axvline(xval1.value, lw = 1, c = 'r', alpha = 0.7)
        return
    def onbuttonclick2(_):
      if len(endpts) < 1:
        endpts.append(xval2.value)
        ax.axvline(xval2.value, lw = 1, c = 'orange', alpha = 0.7)
      elif len(endpts) < 2:
        endpts.append(xval3.value)
        ax.axvline(xval3.value, lw = 1, c = 'orange', alpha = 0.7)
      print("Endpoints:", endpts)
      return

    def onbuttonclick3(_):
      if len(amp_cal) < 1:
        amp_cal.append(xval4.value)
        amp = float(amp_cal[0])
        ax.plot(mean[0],xval4.value, marker = "x")
        print("Amplitude:" + str(amp))
        # for finding the pixel range:
        for wav in endpts:
          if wav % 1 < 0.5:
            wavint = int(wav - wav % 1)
          else:
            wavint = int(wav - wav % 1 + 1)
          wavpos = np.searchsorted(-1 * xpixels, -1 * wavint)
          pixvals.append(wavpos)
        return

    if model == "gauss":
      def onbuttonclick4(_):
          x = xpixels[np.min(pixvals):np.max(pixvals)]
          y = flux[np.min(pixvals):np.max(pixvals)]
          xvals.append(x)
          amp = float(amp_cal[0])
          fit = fitting.LevMarLSQFitter()
          ginit = models.Gaussian1D(amplitude = amp, mean = mean[0], stddev = abs(endpts[0] - endpts[1]) / 8)
          g = fit(ginit, x, y)
          ax.plot(x,g(x), color = 'purple', linestyle = '--')
          model_equation.append(g)
          print(g)
          print('gaussian curve plotted')
          return

    if model == "voigt":
      def onbuttonclick4(_):
          x = xpixels[np.min(pixvals):np.max(pixvals)]
          y = flux[np.min(pixvals):np.max(pixvals)]
          xvals.append(x)
          amp = float(amp_cal[0])
          hmax = amp/2
          if len(y) % 2 == 0:
            half = int(len(y) / 2)
          else:
            half = int((len(y) + 1) / 2)
          diffarray = np.absolute(y - hmax)
          index1 = diffarray[:half].argmin()
          index2 = diffarray[half:].argmin() + half
          fwhm = abs(x[index1] - x[index2])
          fit = fitting.LevMarLSQFitter()
          vinit1 = models.Voigt1D(x_0 = mean[0], amplitude_L = amp, fwhm_G = fwhm, fwhm_L = fwhm)
          v1 = fit(vinit1, x, y)
          ax.plot(x, v1(x), color = 'purple', linestyle = '--')
          model_equation.append(v1)
          print(v1)
          print('voigt curve plotted')
          return

    button1.on_click(onbuttonclick1)
    button2.on_click(onbuttonclick2)
    button3.on_click(onbuttonclick3)
    button4.on_click(onbuttonclick4)

    # Do the plot.
    ax.plot(xpixels, flux)
    plt.draw()
    plt.title("Fitting of Voigt Profiles on CaT")
    plt.xlabel("Wavelength in Angstroms", fontsize = 10)
    plt.ylabel("Flux in ADU/s", fontsize = 10)

    # Display widgets.
    display(widgets.HBox([xval1, button1]))
    display(widgets.HBox([xval2, xval3, button2]))
    display(widgets.HBox([xval4, button3]))
    display(widgets.HBox([button4]))

    return model_equation, xvals
