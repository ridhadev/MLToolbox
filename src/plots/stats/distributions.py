import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

#####################################################################################################################
# Build multiple plots in a grid and show or save result to a file
#####################################################################################################################
def grid_plots(frame, plot_func=lambda serie: plt.plot(serie.dropna()), columns=[], nb_per_row=3, figsize=(6, 9),
               save_file=None):
    '''
    :param frame: Source data
    :param plot_func: Custom plot fuhhnction taking a serie to plot as argument
    :param columns: Columns to plot, or all numeric columns by default if left empty
    :param nb_per_row: Number of plot to display per plot
    :param figsize: Figure size
    :param save_file: File where the plot would be saved (if specified).
    :return: Nothing
    '''
    num_columns = columns
    if not num_columns:
        num_columns = list(frame.select_dtypes(include=[np.number]).columns)

    nb_cols = len(num_columns)
    nplt_row_add = 1 if nb_cols % nb_per_row else 0

    nplt_row = nb_cols // nb_per_row + nplt_row_add

    fig, axis = plt.subplots(nplt_row, nb_per_row, figsize=figsize)

    if nb_per_row == 1:
        axis = axis.reshape(-1, 1)

    if nplt_row == 1:
        axis = axis.reshape(1, -1)

    for ic, c in enumerate(num_columns):
        axis[ic // nb_per_row][ic % nb_per_row].set_title(str(c))
        plt.sca(axis[ic // nb_per_row][ic % nb_per_row])
        plot_func(frame[c])
        # plt.hist(modf[c].dropna())
        # sns.violinplot(frame[c].dropna())

    plt.tight_layout()
    if save_file:
        plt.savefig(save_file)
    else:
        plt.show()

def plot_hist_by_category(frame, column_name, category_column_name):
    frame.hist(column=column_name, by=category_column_name)
    plt.show()

### Todo add: pie, bar plots
def plot_distribution(serie, kind='hist', title='Distribution of {}', orient='h', show=True):
    '''
    :param serie: Serie distribution to plot. No need to dropna() its handled by this function
    :param kind: 'hist' | 'violinplot' | 'boxplot'
    :param title: Title to set. The {}
    :param orient : Plot orientation 'v' | 'h'
    :param show Show the plot or no (in case of grid display of several plots:
        grid_plots(aframe, plot_func= lambda serie: plot_distribution(serie, show=False), figsize=(16,24))
    :return: none
    '''
    if title:
        plt.title('Distribution of {}'.format(serie.name))

    serie_no_nan = serie.dropna()

    if kind == 'hist':
        orientation = 'vertical' if orient == 'v' else 'horizontal'
        plt.hist(serie_no_nan, orientation=orientation)

    if kind == 'violinplot':
        sns.violinplot(serie_no_nan, orient=orient)

    if kind == 'boxplot':
        sns.boxplot(serie_no_nan, orient=orient)
    if show:
        plt.show()



def plot_pie(values, labels, show= True):
    '''
    Pie chart plot
    :param values: Percentage values of the pie
    :param labels: Labels parallel to the values array
    :param show: Show or not the plot
    :return: None
    '''
    plt.pie(values, labels, autopct=lambda x: round(x, 2))
    if show :
        plt.show()

#
def plot_value_counts_pie(aserie, sorted_labels_array, show=True):
    '''
    Get the value counts of a serie as
    :param aserie:
    :param sorted_labels_array:
    :param show:
    :return:
    '''
    pie_plot(aserie.value_counts(sort=True), sorted_labels_array, show= show)

######################################################################################################################
# Todo define 2D plots
## Todo scatter and multi Y scale plots
## Todo jointplot


## Todo Correlation plots: like swarmplot, heatmap, pairplot
### Todo feature importance plot (with cutoff)
### Todo PCA plots (circle , 1D vs 2D)
### Todo diagnogram (hierarchical clustering)
### Todo generate Tree graph(using .dot tool)

######################################################################################################################
# Todo Remove this useless calss
class DistributionPlots :
    def __init__(self, dataframe, y_attribute='Y'):
        self.df = dataframe.copy()
        self.y = y_attribute

    def plot_distribution(self, attribute = 'Y', kind='hist', title = 'Distribution of {}',  orient='h'):
        '''
        :param attribute:
        :param kind: 'hist' | 'violinplot' | 'boxplot'
        :param title:
        :return:
        '''
        plt.title('Distribution of {}'.format('Y'))

        if kind == 'hist':
            orientation = 'vertical' if orient == 'v' else 'horizontal'
            plt.hist(self.df[attribute], orientation= orientation)
            plt.show()

        if kind == 'violinplot':
            sns.violinplot(self.df[attribute], orient = orient)
            plt.show()

        if kind == 'boxplot' :
            sns.boxplot(self.df[attribute],  orient = orient)
            plt.show()