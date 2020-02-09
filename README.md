# Python pairwise comparisons: letter representations

Collection of python functions to generate letter representations of pairwise significance tests using the method described by [Piepho (2004)](http://dx.doi.org/10.1198/1061860043515). This method is applicable to any significance test that returns a table of pairwise comparisons that describe whether to reject the null hypothesis for each pairing or not.

## Purpose
Currently there is no easy way to represent pairwise significance tests in a letter-based system in python. This is possible in R and most other statistics platforms such as SPSS and Minitab. Such a feature makes it much easier for someone to determine pairwise comparisons from figures with more than just a few treatments than a 'line' based representation (see figures below). 
___

Line-based significance representation (http://www.sthda.com/english/articles/24-ggpubr-publication-ready-plots/76-add-p-values-and-significance-levels-to-ggplots/)

![Line based representation](https://github.com/PhilPlantMan/Python-pair-wise-comparison-letter-generator/Life expectency years tukey 0v2 -05.png)




___

##How to use

There are * stages to generate a letter representation of a pairwise significance test.

Step 1: Generate pairwise comparison table
There are a number of libraries that are available that provide statistical tests, the most popular being Statsmodels and Scikit-posthocs. The outputs of these tests differ slightly and the function post_hoc_df() can be used with functions from either of these libraries. A Tukey postdoc test function from both of these libraries have been included in post_hoc_df() to serve as an example of how other tests can be integrated into this function.

Within 



### Prerequisites

Pandas, Statsmodels, Scikit-posthocs, Matplotlib, Seaborn
