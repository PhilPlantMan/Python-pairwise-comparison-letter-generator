# Python-pair-wise-comparison-letter-generator

Collection of python functions to generate letter representations of pairwise significance tests using the method described by [Piepho (2004)](http://dx.doi.org/10.1198/1061860043515). This method is applicable to any significance test that returns a table of pairwise comparisons that describe whether to reject the null hypothesis for each pairing or not.

## Why and how
Currently there is no easy way to represent pairwise significance tests in a letter based system in python. This is possible in R and most other statistics platforms such as SPSS and Minitab. Such a feature makes it much easier for someone to determine pairwise comparisons from figures with more than just a few treatments than a 'line' based representation. 

![Line based representation](http://www.sthda.com/english/sthda-upload/images/ggpubr/add-pvalues-to-ggplots.png)


Download custom_boxplot_functions.py and pairwisecomp_letters.py to the same directory. 



### Prerequisites

Pandas, Statsmodels, Scikit-posthocs, Matplotlib, Seaborn






