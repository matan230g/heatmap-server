import rpy2.robjects as robjects
import pandas as pd
from rpy2.robjects import pandas2ri, Formula, FactorVector,r
pandas2ri.activate()
from rpy2.robjects.packages import importr as importr

deseq = importr('DESeq2')
to_dataframe = robjects.r('function(x) data.frame(x)')

class py_DESeq2:

    # count_matrix - pandas dataframe contains id column (gene_column) and samples (sample_A,sample_B,...)
    # design matrix - samples, condition_A, condition_B ....
    # conditions - array of conditions ['condirion_A','condition_B',...]

    def __init__(self, count_matrix, design_matrix, conditions, gene_column='id'):
        self.dds = None
        self.deseq_result = None
        self.resLFC = None
        self.comparison = None
        self.normalized_count_matrix = None
        self.gene_column = gene_column
        self.gene_id = count_matrix[self.gene_column]
        self.count_matrix = pandas2ri.py2rpy(count_matrix.drop(gene_column, axis=1))
        design_formula = "~ "
        for col in conditions:
            levels = design_matrix[col].unique()
            levels = robjects._convert_rpy2py_strvector(levels)
            as_factor = r["as.factor"]
            design_matrix[col] = FactorVector(design_matrix[col],levels=levels)
            design_matrix[col] = as_factor(design_matrix[col])
            design_formula = design_formula + col + " +"
        design_formula = design_formula[:-2]
        self.design_matrix = pandas2ri.py2rpy(design_matrix)
        self.design_formula = Formula(design_formula)

    # run deseq analysis
    def run_deseq(self, **kwargs):
        self.dds = deseq.DESeqDataSetFromMatrix(countData=self.count_matrix,
                                                colData=self.design_matrix,
                                                design=self.design_formula)
        self.dds = deseq.DESeq(self.dds, **kwargs)



    # get deseeq analysis result
    def get_deseq_result(self, **kwargs):
        self.comparison = deseq.resultsNames(self.dds)
        self.deseq_result = deseq.results(self.dds, **kwargs)
        self.deseq_result = to_dataframe(self.deseq_result)
        self.deseq_result[self.gene_column] = self.gene_id.values
