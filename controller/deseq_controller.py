import pandas as pd
import json
from routers.Unicorn_Exception import UnicornException
from utils import Deseq
from utils import heatmap
from utils import ploty_vp as vp


def run_deseq_controller(design_matrix, count_matrix,uuid):
    locations = [f"upload_data/{uuid}/{count_matrix}", f"upload_data/{uuid}/{design_matrix}"]
    count_matrix_path = locations[0]
    design_matrix_path = locations[1]
    count_matrix = pd.read_csv(count_matrix_path,index_col=False)
    design_matrix = pd.read_csv(design_matrix_path,index_col=False)
    ds_col=design_matrix.columns.values
    if 'id 'in count_matrix.columns == False:
        raise UnicornException(name="Bad Request",status_code=404,
                               details="Bad request, count matrix must contains column with id name")
    if 'id 'in ds_col == False:
        raise UnicornException(name="Bad Request", status_code=404,
                                details="Bad request, design matrix must contains column with id name")
    conditions =list(design_matrix.columns.values)
    if conditions is None or len(conditions)<=1 :
        raise UnicornException(name="Bad request",status_code=404, details='There are no conditions in the design matrix, please check that the files are edited according to the request format')
    conditions.remove('id')
    deseq = Deseq.py_DESeq2(count_matrix,design_matrix,conditions,'id')
    deseq.run_deseq()
    deseq.get_deseq_result()
    return deseq

def deseq_volcano_controller(json_data,file_path,output_file,uuid):
    data_path = f"upload_data/{uuid}/{file_path}"
    output_path = f"upload_data/{uuid}/{output_file}"
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
    data_dic = dict(json_data)
    with open(output_path, 'w') as outfile:
        json.dump(data_dic, outfile)
    return json_fig


def filter_heatmap_controller(deseq_path,heatmap_path,plot_path,properties_path,side,filtered_heatmap_path,uuid):
    deseq_result = pd.read_csv(deseq_path)
    with open(plot_path) as json_file:
        plot_settings = json.load(json_file)
    x_th = plot_settings['x_th']
    x_column =plot_settings['x_column']
    x_operation = plot_settings['x_operation']
    y_th = plot_settings['y_th']
    y_column = plot_settings['y_column']
    y_operation = plot_settings['y_operation']
    title="deseq volcano plot "
    volcano_plot = vp.volcano_plot(deseq_result,x_th=x_th, y_th=y_th, x_operation=x_operation, y_operation = y_operation,
                                       y_column = y_column,x_column = x_column,title=title)
    deseq_result.dropna(inplace=True)
    deseq_result = volcano_plot.add_color_by_condition()
    deseq_result = deseq_result[deseq_result['color'] != 'Normal']
    volcano_plot.data = deseq_result
    filter_values = deseq_result['id'].values
    heatmap_df = pd.read_csv(heatmap_path)
    heatmap_df = heatmap_df[heatmap_df['id'].isin(filter_values)]

    ## TODO: check here if the heatmap_df is not empty , if empty raise exception
    if heatmap_df.empty:
        raise UnicornException(name="Empty dataframe", status_code=404,
                               details='After filtering the data, the file is empty. Please try filter settings')
    heatmap_df.to_csv(filtered_heatmap_path, index=False)
    heatmap_json = create_heat_map(properties_path,side,filtered_heatmap_path)
    json_fig = volcano_plot.create_volcano_plot()
    return {"plot":json_fig, "heatmap": heatmap_json}


def get_file_by_side(file_name,side,file_type='.csv'):
    if side == '1' or side == '2':
        return file_name+side+file_type
    else:
        return file_name+'1'+file_type

def create_heat_map(properties_path,side,filtered_heatmap_path):
    with open(properties_path) as json_file:
        properties = json.load(json_file)
    if side == '3' or side=='1':
        side="1"
        meta_data_key = "metadata"
    else:
        meta_data_key = "metadata"+side

    new_properties = {
        'raw_distance': properties['raw_distance' + side],
        'raw_linkage': properties['raw_linkage' + side],
        'column_distance': properties['column_distance' + side],
        'column_linkage': properties['column_linkage' + side],
        'both1':properties['both' + side],
        'metadata':properties[meta_data_key]
    }

    # heatmap_res = heatmap.create_heatmap_json(filtered_heatmap_path, metadata=properties[meta_data_key],
    #                                       row_distance=properties['raw_distance'+side],
    #                                       row_linkage=properties['raw_linkage'+side],
    #                                       column_distance=properties['column_distance'+side],
    #                                       column_linkage=properties['column_linkage'+side],
    #                                       properties=properties)
    heatmap_res = heatmap.create_heatmap_json(filtered_heatmap_path, metadata=properties[meta_data_key],
                                          properties=new_properties)
    return heatmap_res
