#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Boxplot extenstion for 'Python pairwise comparison letter generator'

Github: PhilPlantMan
"""
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.ticker import AutoMinorLocator
from pairwisecomp_letters import multi_comparisons_letter_df_generator, post_hoc_df

def grouped_boxplot_with_overlay(df, Y_col, X_col, hue_col, X_order, hue_order, 
                                 hue_palette = "YlGn", xtick_kwargs = {}, ytick_kwargs = {}):
    """
    Returns custom Seaborn grouped boxplot objects as a tuple (fig, ax, df)
    """
    # reduce df
    plt.close('all')
    df = df[df[X_col].isin(X_order)]
    Ymax = df[Y_col].max()
    groups = df[X_col].nunique()
    boxs_per_group = 1
    if hue_col != None:
          df = df[df[hue_col].isin(hue_order)]
          boxs_per_group = df[hue_col].nunique()
    # parameters for layout       
    boxs =  boxs_per_group * groups
    fig_width = 1.5+ (.4*boxs) + (.1 * groups)
    # plt settings
    plt.rcParams['figure.constrained_layout.use'] = True
    plt.rc('font', size=12)          # controls default text sizes
    plt.rc('axes', titlesize=12)     # fontsize of the axes title
    plt.rc('axes', labelsize=12)     # fontsize of the x and y labels
    plt.rc('xtick', labelsize=12)    # fontsize of the tick labels
    plt.rc('ytick', labelsize=12)    # fontsize of the tick labels
    plt.rc('legend', fontsize=12)    # legend fontsize
    # make figure and ax objects
    fig, ax = plt.subplots(1, 1, figsize=(fig_width,5))
    # make grouped boxplot 
    ax = sns.boxplot(y=Y_col, x=X_col, 
                     data=df, 
                     palette= hue_palette,
                     saturation = 0.5,
                     hue= hue_col,
                     order = X_order,
                     fliersize = 0,
                     linewidth = 1.75,
                     hue_order = hue_order)
    white_palette = sns.color_palette(['white'])
    # make grouped stripplot 
    ax = sns.stripplot(y=Y_col, x=X_col, 
                       data=df, 
                       jitter=True,
                       dodge=True, 
                       marker='o', 
                       alpha=0.9,
                       hue=hue_col,
                       color='white',
                       palette = white_palette,
                       size = 4,
                       order = X_order,
                       hue_order = hue_order,
                       linewidth=1,
                       edgecolor='black')
    # appearance of axes
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.spines['bottom'].set_linewidth(1.5)
    ax.spines['left'].set_linewidth(1.5)
    ax.yaxis.set_minor_locator(AutoMinorLocator())
    ax.tick_params(which='both', width=1.5)
    ax.tick_params(which='major', length=7)
    ax.tick_params(which='minor', length=4)
    ax.axes.set_ylim(bottom=None, top= Ymax + (Ymax/10))
    plt.xlabel("")
    plt.xticks(**xtick_kwargs)
    plt.yticks(**ytick_kwargs)
    # get legend information from the plot object and plot
    if hue_col != None:
        handles, labels = ax.axes.get_legend_handles_labels()
        plt.legend(handles[0:int(len(handles)/2)], labels[0:int(len(handles)/2)],bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)

    return (fig, ax, df)

def annotate_above_box(df, ax, X_col, Y_col, X_order, text_series, hue_col = None, 
                       hue_order = None,  annotation_kwargs = {}, **kwargs):
    """
    This function draws strings from a pandas series (text_series) at the X centre and Y max
    for each box ontop of the mathplotlib.axes object.
    
    Each 'bar' is 0.8 wide by default in Seaborn. This width is shared by each box 
    within each bar (i.e. the number 'hues')
    """
    number_of_hues = len(hue_order)
    if hue_col == None: number_of_hues = 1
    box_interval = .8 / number_of_hues
    box_centre_X_list = []
    for group in range(len(X_order)):
        position = group -.4 + (.5* box_interval)
        box_centre_X_list.append(position)
        for box in range(1 , number_of_hues):
            position += box_interval
            box_centre_X_list.append(position) # list X positions of each box for annotation
    # calculate maximum values for each box
    if hue_col is not None: box_maxs_series = df.groupby([X_col,hue_col])[Y_col].max()
    else: box_maxs_series = df.groupby([X_col])[Y_col].max()
    # determine text allignment
    ha, va = 'center', 'bottom'
    if 'rotation' in kwargs:
        if kwargs['rotation'] == 'vertical': ha, va = 'left', 'center'
    if 'rotation' in annotation_kwargs:
        if annotation_kwargs['rotation'] == 'vertical': ha, va = 'left', 'center'
    # annotate above each box
    i = 0
    if hue_col is not None: 
        for group in X_order:
            for hue in hue_order:
                y = box_maxs_series.loc[(group,hue)] + (df[Y_col].max()/50) #offset slighly above the max value
                x = box_centre_X_list[i]
                text = text_series.loc[(group,hue)]
                ax.annotate(s = text, xy = (x,y), ha=ha, va=va, **kwargs, **annotation_kwargs)
                i +=1
    else:
        for group in X_order:
            y = box_maxs_series.loc[(group)] + (df[Y_col].max()/50) #offset slighly above the max value
            x = box_centre_X_list[i]
            text = text_series.loc[(group)]
            ax.annotate(s = text, xy = (x,y), ha=ha, va=va, **kwargs, **annotation_kwargs)
            i +=1

def posthoc_letter_boxplot(df, Y_col, X_col, hue_col, X_order, hue_order, post_hoc = "tukey", alpha = 0.05, 
                           fig_path = None, hue_palette = "YlGn", xtick_kwargs = {}, ytick_kwargs = {}, 
                           annotation_kwargs = {}, savefig_kwargs = {}):
    """
    Function draws a grouped custom boxplot with significance caluclaed for a given posthoc test. Significance is 
    represented as letters where boxes sharing the same letter are not significant
    """
    grouping_cols = [X_col]
    if hue_col is not None: grouping_cols.append(hue_col)
    fig, ax, df1 = grouped_boxplot_with_overlay(df, Y_col, X_col, hue_col, X_order, hue_order, 
                                               xtick_kwargs = xtick_kwargs, ytick_kwargs = ytick_kwargs)       
    median_df= df1.groupby(grouping_cols)[Y_col].median().to_frame()
    if hue_col != None:
        for row in median_df.index:
            median_df.loc[row, 'comb'] = str(row[0]) + "│" + str(row[1])
        median_df.set_index('comb', drop = True, inplace = True)
        df1['comb'] = df1[X_col].map(str) + "│" + df1[hue_col].map(str)
        results_df = post_hoc_df(df1, Y_col, 'comb', posthoc = post_hoc, alpha = alpha)
    else: results_df = post_hoc_df(df1, Y_col, X_col, posthoc = post_hoc, alpha = alpha)
    
    letters_df = multi_comparisons_letter_df_generator(results_df, letter_ordering_series = median_df[Y_col])
    if hue_col != None:
        for row in letters_df.index:
                X_group, Hue_group = row.split("│")
                letters_df.loc[row,'Hue group'] = type(hue_order[0])(Hue_group)
                letters_df.loc[row,'X group'] = type(X_order[0])(X_group)
        letters_df.set_index(['X group', 'Hue group'], inplace = True, drop = True)
    
    annotate_above_box(df1, ax, X_col, Y_col, X_order, text_series = letters_df['string'], hue_col = hue_col, hue_order = hue_order, 
                       fontsize = 12, fontweight = 'bold', wrap = True, annotation_kwargs = annotation_kwargs)
    #plot figure
    if fig_path is not None: plt.savefig(fig_path, **savefig_kwargs)
    else: plt.show() 

if __name__ == "__main__":

    import string
    from pathlib import Path 
    
    data_url = 'http://bit.ly/2cLzoxH'
    df = pd.read_csv(data_url)
    df.rename(columns = {'lifeExp': "Life expectancy (years)", 'pop':'Population'}, inplace = True)
                         
    #list column names in appropiate test list                     
    tukey_Y_cols = ['Life expectancy (years)']
    dunn_Y_cols = ['Population']
    
    #set grouped boxplot parameters. Hue refers to sub-grouping within each X group
    X_col = 'continent'
    hue_col = 'year'
    X_order = ['Asia', 'Africa']
    hue_order = [1952, 1957, 1962, 1967, 1987, 2007]
    
    #Set p threshhold for ANOVA and Post hoc tests
    alpha = 0.05 
    
    def custom_boxplot(df, Y_col_list, post_hoc, X_col = X_col, hue_col = hue_col, X_order = X_order, hue_order = hue_order, alpha = alpha, xtick_kwargs = {'rotation' : 'vertical'}, annotation_kwargs = {'rotation' : 'vertical'}, fig_directory = Path.cwd()):
        for Y_col in Y_col_list:
            post_hoc = post_hoc
            remove_punctuation_map = dict((ord(char), None) for char in string.punctuation) #ensures filename does not contain illegal characters
            filename = "{} {} {}.png".format(Y_col.translate(remove_punctuation_map),post_hoc,str(alpha).replace(".", "v2 -"))
            fig_path = fig_directory / filename
            posthoc_letter_boxplot(df, Y_col, X_col, hue_col, X_order, hue_order, post_hoc = post_hoc, alpha = alpha, xtick_kwargs = xtick_kwargs, annotation_kwargs = annotation_kwargs, fig_path = fig_path )
        
    custom_boxplot(df, tukey_Y_cols, 'tukey')
    custom_boxplot(df, dunn_Y_cols, 'dunn')
