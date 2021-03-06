# -*- coding: utf-8 -*-
"""
'Python pairwise comparison letter generator'

Github: PhilPlantMan
"""
import pandas as pd
import numpy as np
import string
import random
import statsmodels.stats.multicomp as multi
import scikit_posthocs as sp


def multi_comparisons_letter_df_generator(comparisons_df, letter_ordering_series = None, 
                                          primary_optimisation_parameter = "Number of different letters", 
                                          monte_carlo_cycles = 5, letter_separator = '', ): 
    """
    Function takes a df listing pairwise comparisons with a cols labelled 'group1' and 'group2' for the two groups being compared 
    and another column labelled 'reject' with boolean values corresponding to whether the null hypothesis should be rejected 
    i.e. True: Both treatments are significantly different
    
    letter_ordering_series (default = None): In theory, which letters are assigned to each non-significance grouping is
    arbitrary and therefor the order can be changed. Offering letter_ordering_series a series with the same index as the output
    will make sure that the order that letters are assigned will follow letter_ordering_series from max to min. For boxplots,
    letter_ordering_series with median values is a good choice.
    
    monte_carlo_cycles (default = 5): Function will always return correct letter representation however it may be suboptimal. 
    Within each monte carlo cycle, a random letter is deleted until the representation breaks. The result with the optimum
    number layout of letters after n monte_carlo_cycles is returned. 
    
    The optimum letter layout is set by primary_optimisation_parameter (default = "Number of different letters"):
        'Number of different letter' optimises for fewest different letters
        "Min letters per row" optimises for the fewest letters assigned per treatment
        "Letter total" optimises for the fewest total letters of the treatments combined
        
    letter_separator (default = ''): Separator for each letter in string assigned to each treatment
    
    
    Letter representation is determined by the method described by Piepho 2004: An Algorithm for a Letter-Based Representation
    of All-Pairwise Comparisons
    """
    #'Insert' stage
    #make df with all unique groups as index
    letters_df = comparisons_df['group1'].append(comparisons_df['group2']).drop_duplicates().to_frame().set_index(0)
    
    letters_df[letters_df.shape[1]] = 1
    for pos_result in comparisons_df.loc[comparisons_df['reject']==True].index:
        group1 = comparisons_df.loc[pos_result, 'group1']
        group2 = comparisons_df.loc[pos_result, 'group2']
        for letter_col in letters_df:
            group1_val = letters_df.loc[group1,letter_col]
            group2_val = letters_df.loc[group2,letter_col]
            if group1_val == 1 and group2_val == 1:
                #duplicate column
                new_col = letters_df.shape[1]
                letters_df[new_col] = letters_df[letter_col]
                #del val at group1 first col and at group2 new col
                letters_df.loc[group1,letter_col] = 0
                letters_df.loc[group2,new_col] = 0
    #'Absorb' stage          
    for col in letters_df:
       other_cols_list = list(letters_df)
       other_cols_list.remove(col)
       col_total = letters_df[col].sum()
       for other_col in other_cols_list:
           matched_total = 0
           for row in letters_df.index:
               if letters_df.loc[row, col] == 1 and letters_df.loc[row, other_col]: matched_total +=1
           if col_total == matched_total:
               letters_df.drop(col, axis = 1, inplace = True)  
               break
        
    def check_letters_against_tests(test_df, letters_df):
        if letters_df.sum(axis = 1).min() == 0: return False
        for result_row in test_df.index:
            group1 = test_df.loc[result_row, 'group1']
            group2 = test_df.loc[result_row, 'group2']
            reject = bool(test_df.loc[result_row, 'reject'])
            count_of_true_trues = 0
            count_of_true_falses = 0
            for letter_col in letters_df:
                group1_val = letters_df.loc[group1,letter_col]
                group2_val = letters_df.loc[group2,letter_col]
                if reject:
                    if group1_val != group2_val: count_of_true_trues += 1
                    if group1_val == 1 and group2_val == 1: 
                        return False
                if reject == False:
                    if group1_val == 1 and group2_val == 1: count_of_true_falses += 1
            if reject and count_of_true_trues == 0: 
                return False
            if reject == False and count_of_true_falses == 0: 
                return False
        return True

    #'Sweep stage' with monte carlo optimisation
    for i in range(monte_carlo_cycles):
        num_of_letters = letters_df.sum().sum()
        num_list = list(np.arange(start = 1, stop = 1+ num_of_letters))
        letters_df_monte_order = letters_df.copy()
        for row in letters_df_monte_order.index:
            for col in letters_df_monte_order:
                if letters_df_monte_order.loc[row,col] == 0: continue
                random_num = random.sample(num_list, 1)[0]
                letters_df_monte_order.loc[row,col] = random_num
                num_list.remove(random_num)
        
        current_letters_df = letters_df.copy()
        for pos in range(num_of_letters + 1):     
            mask = letters_df_monte_order.isin([pos])
            zero_df = letters_df.copy().loc[:] = 0
            letters_df_copy = current_letters_df.copy()
            letters_df_copy.mask(mask, other = zero_df, inplace = True)
            if check_letters_against_tests(comparisons_df,letters_df_copy):
                current_letters_df = letters_df_copy
        
        for col in letters_df:
            if current_letters_df[col].sum() == 0: current_letters_df.drop(col, axis = 1, inplace = True)
            
        # determine fitness parameters for optimisation
        current_fitness_parameter_vals = {"Min letters per row":current_letters_df.sum(axis = 1).max(),
                                          "Number of different letters": current_letters_df.shape[1],
                                          "Letter total": current_letters_df.sum().sum()}
        if i == 0: 
            best_fitness_parameter_vals = current_fitness_parameter_vals
            best_letters_df = current_letters_df
            continue
        
        if current_fitness_parameter_vals[primary_optimisation_parameter] > best_fitness_parameter_vals[primary_optimisation_parameter]:
            continue
        if current_fitness_parameter_vals[primary_optimisation_parameter] < best_fitness_parameter_vals[primary_optimisation_parameter]:
            best_letters_df = current_letters_df.copy()
            best_fitness_parameter_vals = current_fitness_parameter_vals
            
        if sum(current_fitness_parameter_vals.values()) < sum(best_fitness_parameter_vals.values()):
            best_letters_df = current_letters_df.copy()
            best_fitness_parameter_vals = current_fitness_parameter_vals
    
    #order cols
    if isinstance(letter_ordering_series, pd.Series):
        scoring_df = pd.DataFrame(index = best_letters_df.index)
        for row in best_letters_df.index:
            for col in best_letters_df:
                scoring_df.loc[row, col] = best_letters_df.loc[row, col] * letter_ordering_series[row]
        scoring_df = scoring_df.replace(0, np.NaN)
        scoring_means = scoring_df.mean(axis = 0).sort_values(ascending = False)
        best_letters_df = best_letters_df[scoring_means.index]
    # letter the cols     
    for col_name, col_num in zip(best_letters_df, range(len(best_letters_df.columns))):
        letter = string.ascii_lowercase[col_num]
        best_letters_df.loc[best_letters_df[col_name] == 1, col_name] = letter
    # make df with strings ready for presentation
    best_string_df = pd.DataFrame(index = best_letters_df.index)
    best_string_df.loc[:,'string'] = ""
    for row in best_letters_df.index:
        for col in best_letters_df:
            if best_letters_df.loc[row, col] != 0:
                letter_string = best_string_df.loc[row, 'string']
                letter = best_letters_df.loc[row, col]
                if letter_string == "": best_string_df.loc[row, 'string'] = letter
                else: best_string_df.loc[row, 'string'] = letter_separator.join((letter_string, letter))
                
    return best_string_df

def stack_correlation_table(df):
    """
    Converts a dataframe correlation table to a stacked comparisons table
    """
    df = df.stack().to_frame()
    for row in df.index:
        if row[0] == row[1]: 
            df = df.drop(row)
            continue
        sorted_row = list(row)
        sorted_row.sort()
        df.loc[row,'A'], df.loc[row,'B'] = sorted_row[0], sorted_row[1]
    df = df.set_index(['A', 'B'], drop = True)
    df = df.loc[~df.index.duplicated(keep='first')]
    return df

def scikit_results_munger(results, alpha):
    results = stack_correlation_table(results)
    results.rename({0:'p'}, axis = 1, inplace = True)
    results.loc[results['p'] <= alpha, 'reject'] = True
    results.loc[results['p'] > alpha, 'reject'] = False
    for row in results.index:
        results.loc[row, 'group1'] = row[0]
        results.loc[row, 'group2'] = row[1]
    return results

def post_hoc_df(df, Y_col, X_col, posthoc = "tukey", alpha = 0.05):
    """
    Returns a df with pairwise comparisons with reject column calculated according to alpha
    
    TODO: Add more posthoc tests to this function
    """
    if posthoc == "Statsmodels_tukey":
        comp = multi.MultiComparison(df[Y_col], df['comb'])
        results = comp.tukeyhsd(alpha=alpha)
        results = pd.DataFrame(data=results._results_table.data[1:], columns=results._results_table.data[0])
    if posthoc == "dunn": results = scikit_results_munger(sp.posthoc_dunn(df, val_col= Y_col, group_col= X_col, p_adjust = 'holm'), alpha)
    if posthoc == "tukey": results = scikit_results_munger(sp.posthoc_tukey(df, val_col= Y_col, group_col= X_col), alpha)
    return results

if __name__ == "__main__":
    data_url = 'http://bit.ly/2cLzoxH'
    df = pd.read_csv(data_url)
    df.rename(columns = {'lifeExp': "Life expectancy (years)"}, inplace = True)                   
    #set Y col                    
    Y_col = 'Life expectancy (years)'
    #Grouping parameters
    X_col = 'continent'
    hue_col = 'year'
    X_order = ['Asia', 'Africa']
    hue_order = [1952, 1957, 1962, 1967, 1987, 2007]
    #Set p threshold for ANOVA and Post hoc tests
    alpha = 0.05 
    #reduce df
    df = df[df[X_col].isin(X_order)]
    df = df[df[hue_col].isin(hue_order)]
    #Combine X and Hue to form a group column
    df['comb'] = df[X_col].map(str) + "│" + df[hue_col].map(str) 
    #generate df with pairwise comparisons
    pairwise_comps_df = post_hoc_df(df, Y_col, 'comb', posthoc = 'tukey', alpha = alpha)
    # make df with median values for each group to order letter allocation 
    #median_needs same index as df
    median_df= df.groupby([X_col, hue_col])[Y_col].median().to_frame()
    for row in median_df.index:
        median_df.loc[row, 'comb'] = str(row[0]) + "│" + str(row[1])
    median_df.set_index('comb', drop = True, inplace = True)
    df['comb'] = df[X_col].map(str) + "│" + df[hue_col].map(str)    
    #Convert pairwise comparisons to letters representation    
    letters_df = multi_comparisons_letter_df_generator(pairwise_comps_df, 
                                                       letter_ordering_series = median_df)




        