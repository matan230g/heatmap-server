import rpy2.robjects as robjects
import pandas as pd
from rpy2.robjects import pandas2ri, Formula, FactorVector,r
pandas2ri.activate()
from rpy2.robjects.packages import importr as importr

deseq = importr('DESeq2')
to_dataframe = robjects.r('function(x) data.frame(x)')

class py_DESeq2:

    """  This class run DESeq2 analysis using R package DESeq2 ,
            the class use rpy2 to run DESeq2 analysis in R, the computer running the code must have
            R language installed.

             Attributes
             ----------
             count_matrix : dataframe
                dataframe contains integer values and column named id that contains row identifiers
             design matrix : dataframe
                dataframe contains conditions like gender, type and column named id that contains row identifiers
             gene_column : string
                column name contains identifiers for each row
             conditions: array / list
                array contains DESeq2 conditions

             Methods
             -------
             run_deseq():
               run DESeq2 analysis
             get_deseq_result():
                classifies the data in the in axes according to the threshold conditions,
                each group get different color.
             column_operation():
                performs action on the data in one of the axes
        """

    def __init__(self, count_matrix, design_matrix, conditions, gene_column='id'):
        self.dds = None
        self.deseq_result = None
        self.gene_column = gene_column
        self.gene_id = count_matrix[self.gene_column]
        self.count_matrix = pandas2ri.py2rpy(count_matrix.drop(gene_column, axis=1))
        # create design formula for the analysis
        design_formula = "~ "
        for col in conditions:
            levels = design_matrix[col].unique()
            levels = robjects._convert_rpy2py_strvector(levels)
            as_factor = r["as.factor"]
            design_matrix[col] = FactorVector(design_matrix[col],levels=levels)
            design_matrix[col] = as_factor(design_matrix[col])
            design_formula = design_formula + col + " +"
        design_formula = design_formula[:-2]
        # design_formula ="~ gender + type + gender : type"
        # create R dataframe, and create formula that is important for correct result of the DESeq analysis
        self.design_matrix = pandas2ri.py2rpy(design_matrix)
        self.design_formula = Formula(design_formula)

    # run deseq analysis
    def run_deseq(self, **kwargs):
        self.dds = deseq.DESeqDataSetFromMatrix(countData=self.count_matrix,
                                                colData=self.design_matrix,
                                                design=self.design_formula)
        self.dds = deseq.DESeq(self.dds, **kwargs)

    # create a dataframe with the result
    def get_deseq_result(self, **kwargs):
        self.deseq_result = deseq.results(self.dds, **kwargs)
        self.deseq_result = to_dataframe(self.deseq_result)
        self.deseq_result[self.gene_column] = self.gene_id.values
