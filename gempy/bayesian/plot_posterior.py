import numpy as np
import pandas as pn
import scipy.stats as stats
from .joyplot import joyplot

from typing import Union
import copy
import matplotlib.pyplot as plt
from matplotlib import cm

import matplotlib.gridspec as gridspect

# Create cmap
from matplotlib.colors import ListedColormap
import matplotlib.colors as colors
import matplotlib.cm as cmx
import seaborn as sns
from arviz.plots.jointplot import *
from arviz.plots.jointplot import _var_names, _scale_fig_size
from arviz.stats import hpd
import arviz


# Seaborn style
sns.set(style="white", rc={"axes.facecolor": (0, 0, 0, 0)})

# Discrete cmap
pal_disc = sns.cubehelix_palette(10, rot=-.25, light=.7)
pal_disc_l = sns.cubehelix_palette(10)
my_cmap = ListedColormap(pal_disc)
my_cmap_l = ListedColormap(pal_disc_l)


# Continuous cmap
pal_cont = sns.cubehelix_palette(250, rot=-.25, light=.7)
pal_cont_l = sns.cubehelix_palette(250)

my_cmap_full = ListedColormap(pal_cont)
my_cmap_full_l = ListedColormap(pal_cont_l)

default_red = '#DA8886'
default_blue = pal_cont.as_hex()[4]
default_l = pal_disc_l.as_hex()[4]


class PlotPosterior:
    def __init__(self, data: arviz.data.inference_data.InferenceData = None):
        self.data = data
        self.iteration = 1
        self.likelihood_axes = None
        self.marginal_axes = None
        self.joy = None

    def create_figure(self, marginal=True, likelihood=True, joyplot=True,
                      figsize=None, textsize=None,
                      n_samples=11):

        figsize, self.ax_labelsize, _, self.xt_labelsize, self.linewidth, _ = _scale_fig_size(figsize, textsize)
        self.fig, axes = plt.subplots(0, 0, figsize=figsize, constrained_layout=False)
        gs_0 = gridspect.GridSpec(2, 6, figure=self.fig, hspace=.1)

        if marginal is True:
            # Testing
            if likelihood is False:
                self.marginal_axes = self._create_joint_axis(figure=self.fig, subplot_spec=gs_0[0:2, 0:4])
            else:
                self.marginal_axes = self._create_joint_axis(figure=self.fig, subplot_spec=gs_0[0:3, 0:3])

        if likelihood is True:
            if marginal is False:
                self.likelihood_axes = self._create_likelihood_axis(figure=self.fig, subplot_spec=gs_0[0:2, 0:4])
            else:
                self.likelihood_axes = self._create_likelihood_axis(figure=self.fig, subplot_spec=gs_0[0:1, 4:])

        if joyplot is True:
            self.n_samples = n_samples
            self.joy = self._create_joy_axis(self.fig, gs_0[1:2, 4:])

    def _create_joint_axis(self, figure=None, subplot_spec=None, figsize=None, textsize=None):
        figsize, ax_labelsize, _, xt_labelsize, linewidth, _ = _scale_fig_size(figsize, textsize)
        # Instantiate figure and grid

        if figure is None:
            fig, _ = plt.subplots(0, 0, figsize=figsize, constrained_layout=True)
        else:
            fig = figure

        if subplot_spec is None:
            grid = plt.GridSpec(4, 4, hspace=0.1, wspace=0.1, figure=fig)
        else:
            grid = gridspect.GridSpecFromSubplotSpec(4, 4, subplot_spec=subplot_spec)

            # Set up main plot
        self.axjoin = fig.add_subplot(grid[1:, :-1])

        # Set up top KDE
        self.ax_hist_x = fig.add_subplot(grid[0, :-1], sharex=self.axjoin)
        self.ax_hist_x.tick_params(labelleft=False, labelbottom=False)

        # Set up right KDE
        self.ax_hist_y = fig.add_subplot(grid[1:, -1], sharey=self.axjoin)
        self.ax_hist_y.tick_params(labelleft=False, labelbottom=False)
        sns.despine(left=True, bottom=True)

        return self.axjoin, self.ax_hist_x, self.ax_hist_y

    def _create_likelihood_axis(self, figure=None, subplot_spec=None, textsize=None, **kwargs):
        # Making the axes:
        if figure is None:
            figsize = kwargs.get('figsize', None)
            fig, _ = plt.subplots(0, 0, figsize=figsize, constrained_layout=False)
        else:
            fig = figure

        if subplot_spec is None:
            grid = plt.GridSpec(1, 1, hspace=0.1, wspace=0.1, figure=fig)
        else:
            grid = gridspect.GridSpecFromSubplotSpec(1, 1, subplot_spec=subplot_spec)

        ax_like = fig.add_subplot(grid[0, 0])
        ax_like.spines['bottom'].set_position(('data', 0.0))
        # ax_like.spines['left'].set_position(('data', -1))
        ax_like.yaxis.tick_right()

        ax_like.spines['right'].set_position(('axes', 1.03))
        ax_like.spines['top'].set_color('none')
        ax_like.spines['left'].set_color('none')
        ax_like.set_xlabel('Thickness Obs.')
        # ax_like.set_ylabel('Likelihood')
        ax_like.set_title('Likelihood')
        return ax_like

    def _create_joy_axis(self, figure=None, subplot_spec=None, n_samples=None, overlap=.85):
        if n_samples is None:
            n_samples = self.n_samples

        grid = gridspect.GridSpecFromSubplotSpec(n_samples, 1, hspace=-overlap, subplot_spec=subplot_spec)
        ax_joy = [figure.add_subplot(grid[i, 0]) for i in range(n_samples)]
        ax_joy[0].set_title('Foo Likelihood')

        return ax_joy

    def create_color_map(self, draw_mu=None, draw_sigma=None, x_range: tuple = None,
                     **kwargs):

        # if x_range is None:
        #     thick_max = draw_mu + 3 * draw_sigma
        #     thick_min = draw_mu - 3 * draw_sigma
        # else:
        #     thick_min, thick_max = x_range
        #
        # thick_vals = np.linspace(self.x_min_like, self.x_max_like, 100)
        #
        # thick_model = draw_mu
        # thick_std = draw_sigma
        #
        # nor_l = stats.norm.pdf(thick_vals, loc=thick_model, scale=thick_std)
      #  likelihood_at_observation = stats.norm.pdf(observation, loc=thick_model, scale=thick_std)
        cNorm = colors.Normalize(0, self.y_max_like)
        scalarMap = cmx.ScalarMappable(norm=cNorm, cmap=my_cmap_full)
       # color_fill = [colors.to_hex(i) for i in scalarMap.to_rgba(np.atleast_1d(likelihood_at_observation))]

        return scalarMap

    def evaluate_cmap(self, cmap, draw_mu, draw_sigma, obs: Union[float, list] = None):
        likelihood_at_observation = stats.norm.pdf(obs, loc=draw_mu, scale=draw_sigma)
        color_fill = colors.to_hex(cmap.to_rgba(np.atleast_1d(likelihood_at_observation)[0]))
        return color_fill

    def plot_marginal_posterior(self, plotters, iteration=-1, **marginal_kwargs):
        marginal_kwargs.setdefault("plot_kwargs", {})
        marginal_kwargs["plot_kwargs"]["linewidth"] = self.linewidth
        marginal_kwargs.setdefault('fill_kwargs', {})

        marginal_kwargs["plot_kwargs"].setdefault('color', default_l)
        marginal_kwargs['fill_kwargs'].setdefault('color', default_l)
        marginal_kwargs['fill_kwargs'].setdefault('alpha', .8)

        # Flatten data
        x = plotters[0][2].flatten()[:iteration]
        y = plotters[1][2].flatten()[:iteration]

        for val, ax, rotate in ((x, self.ax_hist_x, False), (y, self.ax_hist_y, True)):
            plot_dist(val, textsize=self.xt_labelsize, rotated=rotate, ax=ax, **marginal_kwargs)

    def plot_joint_posterior(self, plotters, iteration=-1, kind='kde', **joint_kwargs):

        # Set labels for axes
        x_var_name = make_label(plotters[0][0], plotters[0][1])
        y_var_name = make_label(plotters[1][0], plotters[1][1])

        self.axjoin.set_xlabel(x_var_name, fontsize=self.ax_labelsize)
        self.axjoin.set_ylabel(y_var_name, fontsize=self.ax_labelsize)
        self.axjoin.tick_params(labelsize=self.xt_labelsize)

        # Flatten data
        x = plotters[0][2].flatten()[:iteration]
        y = plotters[1][2].flatten()[:iteration]

        if kind == "scatter":
            self.axjoin.scatter(x, y, **joint_kwargs)
        elif kind == "kde":
            contour = joint_kwargs.get('contour', True)
            fill_last = joint_kwargs.get('fill_last', False)
            try:
                plot_kde(x, y, contour=contour, fill_last=fill_last, ax=self.axjoin, **joint_kwargs)
            except ValueError:
                pass
            except np.linalg.LinAlgError:
                pass
        else:
            gridsize = joint_kwargs.get('grid_size', 'auto')
            if gridsize == "auto":
                gridsize = int(len(x) ** 0.35)
            self.axjoin.hexbin(x, y, mincnt=1, gridsize=gridsize, **joint_kwargs)
            self.axjoin.grid(False)

    def plot_trace(self, plotters, iteration, n_iterations=20):
        # if iteration < 3:
        #     iteration = 3
        i_0 = np.max([0, (iteration - n_iterations)])

        theta1_val_trace = plotters[0][2].flatten()[i_0:iteration+1]
        theta2_val_trace = plotters[1][2].flatten()[i_0:iteration+1]

        theta1_val = theta1_val_trace[-1]
        theta2_val = theta2_val_trace[-1]

        # Plot point of the given iteration
        self.axjoin.plot(theta1_val, theta2_val, 'bo', ms=6, color='k')

        # Plot a trace of n_iterations
        pair_x_array = np.vstack(
            (theta1_val_trace[:-1], theta1_val_trace[1:])).T  # np.tile(x, (2,1)).T # np.reshape(x, (-1, 2))
        pair_y_array = np.vstack((theta2_val_trace[:-1], theta2_val_trace[1:])).T
        for i, pair_x in enumerate(pair_x_array):
            alpha_val = i / pair_x_array.shape[0]
            pair_y = pair_y_array[i]
            self.axjoin.plot(pair_x, pair_y, linewidth=1, alpha=alpha_val, color='k')

    def plot_marginal(self, var_names=None, data=None, iteration=-1,
                      group='both',
                      plot_trace=True, n_iterations=20,
                      kind='kde',
                      coords=None, credible_interval=.98,
                      marginal_kwargs=None, marginal_kwargs_prior=None,
                      joint_kwargs=None, joint_kwargs_prior=None):
        self.axjoin.clear()
        self.ax_hist_x.clear()
        self.ax_hist_y.clear()

        if data is None:
            data = self.data

        valid_kinds = ["scatter", "kde", "hexbin"]
        if kind not in valid_kinds:
            raise ValueError(
                ("Plot type {} not recognized." "Plot type must be in {}").format(kind, valid_kinds)
            )

        if coords is None:
            coords = {}

        if joint_kwargs is None:
            joint_kwargs = {}

        if marginal_kwargs is None:
            marginal_kwargs = {}

        data_0 = convert_to_dataset(data, group="posterior")
        var_names = _var_names(var_names, data_0)

        plotters = list(xarray_var_iter(get_coords(data_0, coords), var_names=var_names, combined=True))

        if len(plotters) != 2:
            raise Exception(
                "Number of variables to be plotted must 2 (you supplied {})".format(len(plotters))
            )

        if kind == 'kde':
            joint_kwargs.setdefault('contourf_kwargs', {})
            joint_kwargs.setdefault('contour_kwargs', {})
            joint_kwargs['contourf_kwargs'].setdefault('cmap', my_cmap_l)
            joint_kwargs['contourf_kwargs'].setdefault('levels', 11)
            joint_kwargs['contourf_kwargs'].setdefault('alpha', .8)
            joint_kwargs['contour_kwargs'].setdefault('alpha', 0)

        marginal_kwargs.setdefault('fill_kwargs', {})
        marginal_kwargs.setdefault("plot_kwargs", {})
        marginal_kwargs["plot_kwargs"]["linewidth"] = self.linewidth

        marginal_kwargs["plot_kwargs"].setdefault('color', default_l)
        marginal_kwargs['fill_kwargs'].setdefault('color', default_l)
        marginal_kwargs['fill_kwargs'].setdefault('alpha', .8)

        if group == 'both' or group == 'posterior':

            self.plot_joint_posterior(plotters, kind=kind, iteration=iteration, **joint_kwargs)
            self.plot_marginal_posterior(plotters, iteration=iteration, **marginal_kwargs)

        if group == 'both' or group == 'prior':
            if joint_kwargs_prior is None:
                joint_kwargs_prior = {}

            if marginal_kwargs_prior is None:
                marginal_kwargs_prior = {}

            joint_kwargs_prior.setdefault('contourf_kwargs', {})
            marginal_kwargs_prior.setdefault('fill_kwargs', {})
            marginal_kwargs_prior.setdefault("plot_kwargs", {})
            marginal_kwargs_prior["plot_kwargs"]["linewidth"] = self.linewidth

            if kind == 'kde':
                joint_kwargs_prior.setdefault('contourf_kwargs', {})
                joint_kwargs_prior.setdefault('contour_kwargs', {})
                joint_kwargs_prior['contourf_kwargs'].setdefault('cmap', my_cmap)
                joint_kwargs_prior['contourf_kwargs'].setdefault('levels', 11)
                alpha_p = .8 if group == 'prior' else .4
                joint_kwargs_prior['contourf_kwargs'].setdefault('alpha', alpha_p)
                joint_kwargs_prior['contour_kwargs'].setdefault('alpha', 0)

            marginal_kwargs_prior["plot_kwargs"].setdefault('color', default_blue)
            marginal_kwargs_prior['fill_kwargs'].setdefault('color', default_blue)
            marginal_kwargs_prior['fill_kwargs'].setdefault('alpha', alpha_p)

            data_1 = convert_to_dataset(data, group="prior")
            plotters_prior = list(xarray_var_iter(get_coords(data_1, coords), var_names=var_names, combined=True))

            self.plot_joint_posterior(plotters_prior, kind=kind, **joint_kwargs_prior)
            self.plot_marginal_posterior(plotters_prior, **marginal_kwargs_prior)

            x_min, x_max, y_min, y_max = self.compute_hpd(plotters_prior, credible_interval=credible_interval)

        else:
            x_min, x_max, y_min, y_max = self.compute_hpd(plotters, iteration=iteration,
                                                          credible_interval=credible_interval)
        if plot_trace is True:
            self.plot_trace(plotters, iteration, n_iterations)

        self.axjoin.set_xlim(x_min, x_max)
        self.axjoin.set_ylim(y_min, y_max)
        self.ax_hist_x.set_xlim(self.axjoin.get_xlim())
        self.ax_hist_y.set_ylim(self.axjoin.get_ylim())

        return self.axjoin, self.ax_hist_x, self.ax_hist_y

    @staticmethod
    def compute_hpd(plotters, iteration=-1, credible_interval=.98):
        x = plotters[0][2].flatten()[:iteration]
        y = plotters[1][2].flatten()[:iteration]
        x_min, x_max = hpd(x, credible_interval=credible_interval)
        y_min, y_max = hpd(y, credible_interval=credible_interval)
        return x_min, x_max, y_min, y_max

    def set_likelihood_limits(self, val, type):
        val = np.repeat(np.atleast_1d(val), 1)

        if type == 'x_max':
            val = val + val * .2

            try:
                self._xma_list = np.append(self._xma_list[:25], val)
                self.x_max_like = np.max(self._xma_list)
            except AttributeError:
                self._xma_list = val
                self.x_max_like = np.max(self._xma_list)

        if type == 'x_min':
            val = val - val * .2

            try:
                self._xmi_list = np.append(self._xmi_list[:25], val)
                self.x_min_like = np.min(self._xmi_list)
            except AttributeError:
                self._xmi_list = val
                self.x_min_like = np.min(self._xmi_list)

        if type == 'y_max':
            try:
                self._yma_list = np.append(self._yma_list[:25], val)
                self.y_max_like = np.max(self._yma_list)
            except AttributeError:
                self._yma_list = val
                self.y_max_like = np.max(self._yma_list)

    def plot_normal_likelihood(self, mean:Union[str, float], std:Union[str, float], obs:Union[str, float],
                               data=None, iteration=-1, x_range=None, color='auto', **kwargs):
        self.likelihood_axes.clear()

        if data is None:
            data = self.data

        draw = data.posterior[{'chain':0, 'draw':iteration}]
        draw_mu = draw[mean] if type(mean) is str else mean
      #  print('like', draw_mu)
        draw_sigma = draw[std] if type(std) is str else std
        obs = data.observed_data[obs] if type(obs) is str else obs

        self.set_likelihood_limits(draw_mu + 4 * draw_sigma, 'x_max')
        self.set_likelihood_limits(draw_mu - 4 * draw_sigma, 'x_min')

        if x_range is not None:
            thick_min = x_range[0]
            thick_max = x_range[1]
        else:
            thick_max = self.x_max_like # draw_mu + 3 * draw_sigma
            thick_min = self.x_min_like # draw_mu - 3 * draw_sigma

        thick_vals = np.linspace(thick_min, thick_max, 100)
        observation = np.asarray(obs)

        thick_model = draw_mu
        thick_std = draw_sigma

        nor_l = stats.norm.pdf(thick_vals, loc=thick_model, scale=thick_std)
        self.set_likelihood_limits(nor_l.max(), 'y_max')

        likelihood_at_observation = stats.norm.pdf(observation, loc=thick_model, scale=thick_std)

        if color == 'auto':
            # # This operations are for getting the same color in the likelihood plot as in the joy plot
            self.cmap_l = self.create_color_map(draw_mu, draw_sigma)
            color_fill = self.evaluate_cmap(self.cmap_l, draw_mu, draw_sigma, obs)

        elif color is None:
            color_fill = default_l

        else:
            color_fill = color
        y_min = (nor_l.min() - nor_l.max()) * .01
        y_max = nor_l.max() + nor_l.max() * .05

        self.likelihood_axes.plot(thick_vals, nor_l, color='#7eb1bc', linewidth=.5)
        self.likelihood_axes.fill_between(thick_vals, nor_l, 0, color=color_fill, alpha=.8)

        self.likelihood_axes.vlines(observation, 0.001, likelihood_at_observation, linestyles='dashdot',
                                    color='#DA8886', alpha=1)

        self.likelihood_axes.hlines(likelihood_at_observation, observation, thick_max,#thick_min - thick_min * .1,
                                     linestyle='dashdot', color='#DA8886', alpha=1)
        self.likelihood_axes.scatter(7, 0, s=50, c='#DA8886')
        self.likelihood_axes.set_ylim(y_min, y_max)
        self.likelihood_axes.set_xlim(thick_min, thick_max)

        self.likelihood_axes.spines['bottom'].set_position(('data', 0.0))
        self.likelihood_axes.yaxis.tick_right()

        self.likelihood_axes.spines['right'].set_position(('axes', 1.03))
        self.likelihood_axes.spines['top'].set_color('none')
        self.likelihood_axes.spines['left'].set_color('none')
        self.likelihood_axes.set_xlabel('Thickness Obs.')
        self.likelihood_axes.set_title('Likelihood')

        self.likelihood_axes.set_xlim(self.x_min_like, self.x_max_like)
        self.likelihood_axes.set_ylim(0, self.y_max_like)

        return self.likelihood_axes, self.cmap_l

    def plot_joy(self, var_names: tuple = None, obs: Union[str, float] = None,
                 data=None, iteration=-1, samples_size=1000, cmap='auto'):
        """

        A0rgs:
            var_names: mu and sigma of the likelihood!
            obs:
            data:
            iteration:
            samples_size:
            cmap:

        Returns:

        """
        [i.clear() for i in self.joy]
        n_iterations = self.n_samples
        iteration_label = [None for i in range(self.n_samples)]
        if iteration < self.n_samples/2:
            l_0 = 0
            l_1 = int(self.n_samples)
            iteration_label[-1] = 0
            iteration_label[0] = l_1
        else:
            l_0 = int(iteration - np.round(self.n_samples / 2))+1
            l_1 = int(iteration + np.round(self.n_samples / 2))
            iteration_label[-1] = l_0
            iteration_label[int(np.round(self.n_samples / 2))-1] = iteration-1
            iteration_label[0] = l_1

        if data is None:
            data = self.data

        obs = data.observed_data[obs] if type(obs) is str else obs

        data = convert_to_dataset(data, group="posterior")
        coords = {}
        var_names = _var_names(var_names, data)

        plotters = list(
            xarray_var_iter(get_coords(data, coords), var_names=var_names, combined=True))
       # print(l_0, l_1)
        x = plotters[0][2].flatten()[l_0:l_1]
        y = plotters[1][2].flatten()[l_0:l_1]
       # print(x - 4 * y)
        self.set_likelihood_limits(x + 4 * y, 'x_max')
        self.set_likelihood_limits(x - 4 * y, 'x_min')

      #  print('joy', x)
        df = pn.DataFrame()

        color = []
        for e in range(l_1-l_0):# mean_val, std_val in zip(x, y):
            e = -e -1
         #   print('e', e)
            num = np.random.normal(loc=x[e], scale=y[e], size=samples_size)
            name = e + (iteration - int(n_iterations / 2))
            df[name] = num

            if obs is not None:
                self.set_likelihood_limits(stats.norm.pdf(obs, loc=x[e], scale=y[e]), 'y_max')

            if cmap is None:
                color = default_blue
          #      print('why am i here', cmap)

            else:
                if cmap == 'auto':
          #          print('agggg', self.y_max_like)
                    if self.likelihood_axes is None:
                        cmap = self.create_color_map()
                    else:
                        cmap = self.cmap_l

                color.append(self.evaluate_cmap(cmap, x[e], y[e], obs))

      #  print(df)
        if self.likelihood_axes is not None:
            x_range = self.likelihood_axes.get_xlim()
        else:
            x_range = (self.x_min_like, self.x_max_like)
        f, axes = joyplot(df, bw_method=1, labels=iteration_label, ax=self.joy,
                          yrot=0,
                          range_style='all', x_range=x_range,
                          color=color,
                          grid='y',
                          fade=False, last_axis=False,
                          linewidth=.1, alpha=1);

        n_axes = len(axes[:-1])
        if int(n_axes / 2) >= iteration:
         #   print('ax', int(n_axes / 2))
            ax_sel = axes[-iteration-1]
            ax_sel.hlines(0, ax_sel.get_xlim()[0], ax_sel.get_xlim()[1], color='#DA8886', linewidth=3)

        else:
            ax_sel = axes[int(n_axes / 2)]
            ax_sel.hlines(0, ax_sel.get_xlim()[0], ax_sel.get_xlim()[1], color='#DA8886', linewidth=3)

        if obs is not None:
            if self.likelihood_axes is None:
                self.joy[0].scatter(obs, np.ones_like(obs) * self.joy[0].get_ylim()[1],
                                    marker='v', s=200, c='#DA8886')
            self.joy[-1].scatter(obs, np.ones_like(obs) * self.joy[-1].get_ylim()[0],
                                 marker='^', s=200, c='#DA8886')

        return axes

    def plot_posterior(self, prior_var, like_var, obs, iteration=-1,
                       marginal_kwargs=None, likelihood_kwargs=None, joy_kwargs = None):
        if marginal_kwargs is None:
            marginal_kwargs = {}
        if likelihood_kwargs is None:
            likelihood_kwargs = {}
        if joy_kwargs is None:
            joy_kwargs = {}

        self.plot_marginal(prior_var, iteration=iteration, **marginal_kwargs)
        _, cmap = self.plot_normal_likelihood(like_var[0], like_var[1], obs, iteration=iteration,
                                                   **likelihood_kwargs)
        self.plot_joy(like_var, obs=obs, iteration=iteration, **joy_kwargs)
