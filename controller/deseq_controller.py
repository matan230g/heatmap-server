import pandas as pd
import json
from routers.Unicorn_Exception import UnicornException
from utils import Deseq
from utils import heatmap
from utils import ploty_vp as vp


# '''
#     This file is controller that connect deseq and plotly classes to deseq router.
# '''
#
# '''
#     params :
#         * locations - array of strings. each string is path to relevent file
#             locations[0] - count matrix path
#             locations[1] - design matrix
#     The function use Deseq to run deseq analysis.
# '''

def run_deseq_controller(locations):
    count_matrix_path = locations[0]
    design_matrix_path = locations[1]
    count_matrix = pd.read_csv(count_matrix_path,index_col=False,encoding='utf-8-sig')
    design_matrix = pd.read_csv(design_matrix_path,index_col=False,encoding='utf-8-sig')
    dm_columns = [str(c) for c in design_matrix.columns.tolist()]
    cm_columns = [str(c) for c in count_matrix.columns.tolist()]
    if cm_columns.count('id') ==0:
        raise UnicornException(name="Bad request",status_code=404,
                               details="count matrix must contains column with id name")
    if dm_columns.count('id') == 0:
        raise UnicornException(name="Bad request", status_code=404,
                                details="design matrix must contains column with id name")
    conditions =list(design_matrix.columns.values)
    if conditions is None or len(conditions)<=1 :
        raise UnicornException(name="Bad request",status_code=404, details='There are no conditions in the design matrix, please check that the files are edited according to the request format')
    conditions.remove('id')
    try:
        deseq = Deseq.py_DESeq2(count_matrix,design_matrix,conditions,'id')
        deseq.run_deseq()
        deseq.get_deseq_result()
    except:
        raise UnicornException(name="Bad request", status_code=404,
                               details='Error in Deseq analysis. please check your files.')
    return deseq

# '''
#     The functions create volcano plot useing plotly express and return json of the plot.
#     params :
#         * json_data - json contains all data to plot.
#             * x_th,y_th - float, x/y column threshold
#             * x_column / y_column - string, x/y column name
#             * x_operation/ y_operation - string, which operation to do on data Log/None.
#         * locations - path to files
#             locations[0] - data path
#             locations[1] - output_path
# '''

def deseq_volcano_controller(json_data,locations):
    try:
        data_path = locations[0]
        output_path = locations[1]
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
    except Exception as exc:
        raise UnicornException(name="Bad request", status_code=404,
                               details='Error in Deseq analysis. please check your files.')

# '''
#     This function filter heatmap by deseq results.
#     The function returns json heatmap, plot heatmap.
#     params:
#         * deseq_path - string path to deseq result file
#         * heatmap_path - string path to heatmap file
#         * plot_path - string path to plot file
#         * properties_path - file to heatmap properties
#         * side - int which side of heatmap
#         * values - array, which values contains in the heatmap
#         * filtered_heatmap_path - path to save the filterd heatmap
# '''

def filter_heatmap_controller(deseq_path,heatmap_path,plot_path,properties_path,side,values,filtered_heatmap_path):
    deseq_result = pd.read_csv(deseq_path,encoding='utf-8-sig')
    with open(plot_path) as json_file:
        plot_settings = json.load(json_file)
    x_th = plot_settings['x_th']
    x_column =plot_settings['x_column']
    x_operation = plot_settings['x_operation']
    y_th = plot_settings['y_th']
    y_column = plot_settings['y_column']
    y_operation = plot_settings['y_operation']
    title="deseq volcano plot "
    # create volcano plot instance
    volcano_plot = vp.volcano_plot(deseq_result,x_th=x_th, y_th=y_th, x_operation=x_operation, y_operation = y_operation,
                                       y_column = y_column,x_column = x_column,title=title)
    deseq_result.dropna(inplace=True)
    # create label to rows which will be used to filter the data
    deseq_result = volcano_plot.add_color_by_condition()

    values = values.split(',')
    values =[val for val in values if val != '']
    if len(values)>=3 or len(values) <=0:
        raise UnicornException(name="Filter dataframe", status_code=404,
                               details=f'The number of filters is not legal, number of filters is {len(values)}')
    # filter data
    boolean_series = deseq_result.color.isin(values)
    deseq_result = deseq_result[boolean_series]
    volcano_plot.data = deseq_result
    filter_values = deseq_result['id'].values
    heatmap_df = pd.read_csv(heatmap_path,encoding='utf-8-sig')
    heatmap_df = heatmap_df[heatmap_df['id'].isin(filter_values)]

    if heatmap_df.empty:
        raise UnicornException(name="Empty dataframe", status_code=404,
                               details='After filtering the data, the file is empty. Please try filter settings')
    # saved filterd data
    heatmap_df.to_csv(filtered_heatmap_path, index=False)
    heatmap_json = create_heat_map(properties_path,side,filtered_heatmap_path)
    # create new volcano plot which filtered data
    json_fig = volcano_plot.create_volcano_plot()
    return {"plot":json_fig, "heatmap": heatmap_json}

# create new heatmap - filterd heatmap
def create_heat_map(properties_path,side,filtered_heatmap_path):
    with open(properties_path) as json_file:
        properties = json.load(json_file)
    if side=='3':
        side=""
        side1 ='1'
        meta_data_key = "metadata"
    elif side=='1':
        side="1"
        side1 ='1'
        meta_data_key = "metadata"
    else:
        meta_data_key = "metadata"+side
        side1 ='2'

    new_properties = {
        'raw_distance': properties['raw_distance' + side],
        'raw_linkage': properties['raw_linkage' + side],
        'column_distance': properties['column_distance' + side],
        'column_linkage': properties['column_linkage' + side],
        'both1':properties['both' + side1],
        'metadata':properties[meta_data_key],
        'base':properties['base'+side1],
        'deseq_normalization':properties['deseq_normalization'+side1],
        'norm_type': properties['norm_type'+side1],
        'compress': int(properties['compress'+side1])
    }
    if new_properties['compress'] == 1:
        if side == '1':
            side=""
        new_properties['compressed_number'] = properties['compressed_number'+side]
        new_properties['compressed_value'] = properties['compressed_value'+side]


    heatmap_res = heatmap.create_heatmap_json(filtered_heatmap_path, metadata=properties[meta_data_key],
                                          properties=new_properties)
    return heatmap_res

# normalize data which deseq
def deseq_normalization(path_data,save=True):
    data = pd.read_csv(path_data)
    columns = data.columns.tolist()
    if columns.count('id') == 0:
        raise UnicornException(name="Bad Request", status_code=404,
                               details="Bad request, count matrix must contains column with id name")
    columns.remove('id')
    design_matrix = pd.DataFrame()
    design_matrix['id'] = columns
    conditions = ['C'for i in range(len(columns))]
    conditions[0] = 'H'
    design_matrix['condition'] = conditions
    conditions =['condition']
    deseq = Deseq.py_DESeq2(data,design_matrix,conditions)
    deseq.run_deseq()
    deseq.get_deseq_result()
    data = deseq.normalized_count_matrix
    if save:
        data.to_csv(path_data,index=False)


