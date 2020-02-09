# Python pairwise comparisons: letter representations

Collection of python functions to generate letter representations of pairwise significance tests using the method described by [Piepho (2004)](http://dx.doi.org/10.1198/1061860043515). This method is applicable to any significance test that returns a table of pairwise comparisons that describe whether to reject the null hypothesis for each pairing or not.

## Purpose
Currently there is no easy way to represent pairwise significance tests in a letter-based system in python. This is possible in R and most other statistics platforms such as SPSS and Minitab. Such a feature makes it much easier for someone to determine pairwise comparisons from figures with more than just a few treatments than a 'line' based representation. 
___
**Figure 1:** Letter based representation of pairwise significance tests. Groups that share at least 1 letter are not significantly different (ANOVA with Tukey posthoc test, p < 0.05). Generated with custom_boxplot_functions.py

<p align="center">
  <img width="520" height="400" src="https://github.com/PhilPlantMan/Python-pair-wise-comparison-letter-generator/blob/master/Life%20expectency%20years%20tukey%200v2%20-05.png">
</p>

___

## How to use

**Step 1:** Generate a pairwise comparison table

There are a number of libraries that that provide statistical tests; the most popular are Statsmodels and Scikit-posthocs. The outputs of the functions from these libraries differ slightly and the function `post_hoc_df()` in `pairwisecomp_letters.py` can be used with functions from either of these libraries. A Tukey postdoc test function from both of these libraries have been included in `post_hoc_df()` to serve as an example of how other tests can be written into this function.

Example taken from `if __name__ == "__main__"` of: `pairwisecomp_letters.py`
```python
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
print(pairwise_comps_df.head(5)
```

Output: 

|           p | reject   | group1      | group2      |
| -----------:|:---------|:------------|:------------|
|  0.9        | False    | Africa│1952 | Africa│1957 |
|  0.216295   | False    | Africa│1952 | Africa│1962 |
|  0.00354515 | True     | Africa│1952 | Africa│1967 |
|  0.001      | True     | Africa│1952 | Africa│1987 |
|  0.001      | True     | Africa│1952 | Africa│2007 |
___

**Step 2:** Convert pairwise comparisons to a letter representation of significance 

The function `multi_comparisons_letter_df_generator()` takes the dataframe of pairwise comparisons (`pairwise_comps_df`) and returns a dataframe with an index of all individual groups and a string of their respective significance letters. The order that letters appear in the output can be controlled by providing a numerical `pd.series` or n x 1 shaped `pd.dataframe` with the same index as the output of `multi_comparisons_letter_df_generator()`. For example, for use with boxplots, it is logical for the group with the largest median to take the letter ‘a’. To achieve this, a dataframe with median values for each group is passed to the `letter_ordering_series`argument of `multi_comparisons_letter_df_generator()`. 

Continuation of the code example above:
```python
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
print(letter_df.head(5)
```

Output:

|  Index          | string   |
| :------------:|:---------:|
|  Africa│1952 | a        |
|  Africa│1957 | ab       |
|  Africa│1962 | ab       |
|  Africa│1967 | bc       |
|  Africa│1987 | d        |


As described by Piepho, the combination of letters and groups can differ depending on the order the letters are ’swept’. The returned set of letters remain accurate but may not be the minimum set of letters. Therefore, to optimise the returned letter set, multiple cycles of calculations are recommended. The number of cycles of letter determination is controlled by the function argument `monte_carlo_cycles` (default = 5). The ‘fitness’ parameter of the optimisation can be controlled by the function argument primary_optimisation_parameter (default = "Number of different letters"):
+ 'Number of different letters' optimises for fewest different letters
+ "Min letters per row" optimises for the fewest letters assigned per treatment
+ "Letter total" optimises for the fewest total letters of the treatments combined

## Annotating a boxplot with letter representations of significance

The dataframe with letter representations of significance (`letters_df`) can be used to annotate many different types of plot. The most useful application for me is with boxplots. In this repository, I have also provided the script `custom_boxplot_functions.py` that I used to generate *Figure 1* in conjunction with `pairwisecomp_letters.py`. The boxplot uses Seaborn grouped-boxplot. 

### Prerequisites

Pandas, Statsmodels, Scikit-posthocs, Matplotlib, Seaborn







