import pandas as pd
from routers.Unicorn_Exception import UnicornException
from utils import Deseq
from utils import ploty_vp as vp

def run_deseq_controller(json_data,uuid):
    locations = [f"upload_data/{uuid}/count_matrix.csv", f"upload_data/{uuid}/design_matrix.csv"]
    count_matrix_path = locations[0]
    design_matrix_path = locations[1]
    count_matrix_id = json_data['count_matrix_id']
    design_matrix_id = json_data['design_matrix_id']
    count_matrix = pd.read_csv(count_matrix_path)
    design_matrix = pd.read_csv(design_matrix_path)
    if not count_matrix_id in count_matrix.columns:
        raise UnicornException(name="Bad Request",status_code=404,
                               details=f"Column {count_matrix_id} not in count matrix columns, please check that the files are edited according to the request format")
    if not design_matrix_id in design_matrix.columns:
        raise UnicornException(name="Bad Request", status_code=404,
                                details=f"Column {design_matrix_id} not in design matrix columns, please check that the files are edited according to the request format")
    conditions =list(design_matrix.columns.values)
    if conditions is None or len(conditions)<=1 :
        raise UnicornException(name="Bad request",status_code=404, details='There are no conditions in the design matrix, please check that the files are edited according to the request format')
    conditions.remove(design_matrix_id)
    deseq = Deseq.py_DESeq2(count_matrix,design_matrix,conditions,count_matrix_id)
    deseq.run_deseq()
    deseq.get_deseq_result()
    deseq.deseq_result.to_csv(f"upload_data/{uuid}/deseq_result.csv",index=False)
    return deseq.deseq_result.to_json(orient='index')

def deseq_volcano_controller(json_data,uuid):
    data_path = f"upload_data/{uuid}/deseq_result.csv"
    x_th = json_data['x_th']
    x_column =json_data['x_column']
    x_operation = json_data['x_operation']
    y_th = json_data['y_th']
    y_column = json_data['y_column']
    y_operation = json_data['y_operation']
    title="deseq volcano plot "
    data =pd.read_csv(data_path)
    volcano_plot = vp.volcano_plot(data, x_th=x_th, y_th=y_th, x_operation=x_operation, y_operation = y_operation,
                                       y_column = y_column,x_column = x_column,title=title)
    json_fig = volcano_plot.create_volcano_plot()
    return json_fig


