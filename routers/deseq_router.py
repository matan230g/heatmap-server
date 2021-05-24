from fastapi import APIRouter,Header,HTTPException,FastAPI, File,Response,Request
from fastapi.responses import HTMLResponse
import pandas as pd
from controller import deseq_controller
from routers.Unicorn_Exception import UnicornException
from routers.actions import check_file_type

router = APIRouter()

@router.post('/run_deseq')
async def run_deseq(request :Request):
    data = await request.form()
    uuid = request.headers['uuid']
    side = data['side']

    design_matrix_file = get_file_by_side('design_matrix',side)
    count_matrix_file = get_file_by_side('heatmap',side)
    locations = [f"upload_data/{uuid}/{count_matrix_file}", f"upload_data/{uuid}/{ design_matrix_file}"]
    deseq = deseq_controller.run_deseq_controller(locations)
    deseq_result = get_file_by_side('deseq_result',side)
    deseq.deseq_result.to_csv(f"upload_data/{uuid}/{deseq_result}",index=False)
    json_result =  deseq.deseq_result.to_json(orient='index')
    return {'deseq_results':json_result}


@router.post('/volcano_plot_deseq',response_class=HTMLResponse)
async def deseq_volcano(request :Request):
    data = await request.form()
    uuid = request.headers['uuid']

    file_path = get_file_by_side('deseq_result',data['side'])
    output_path = get_file_by_side('plot_setting',data['side'],'.json')
    data_path = f"upload_data/{uuid}/{file_path}"
    output_path = f"upload_data/{uuid}/{output_path}"
    locations = [data_path,output_path]
    fig_json = deseq_controller.deseq_volcano_controller(data,locations)
    return fig_json

@router.post('/upload_data')
async def upload_data(request: Request):
        uuid = request.headers['uuid']
        data = await request.form()
        side = data['side']
        file=data['files']
        file_name = get_file_by_side('design_matrix',side)
        check_file_type([file])
        with open(f"upload_data/{uuid}/{file_name}", "wb+") as file_object:
            file_object.write(file.file.read())
            file_object.close()

@router.get('/get_deseq_result')
async def get_files_names(request: Request):
    uuid = request.headers['uuid']
    params = request.query_params
    side =params['side']
    result_path = get_file_by_side('deseq_result',side)
    deseq_result = pd.read_csv(f"upload_data/{uuid}/{result_path}")
    json_data = deseq_result.to_json(orient="records")
    return json_data


@router.get('/filter_heatmap')
async def filter_heatmap(request: Request):
    uuid = request.headers['uuid']
    params = request.query_params
    side = params['side']
    values = params['values']
    deseq_file = get_file_by_side('deseq_result',side)
    heatmap_file = get_file_by_side('heatmap',side)
    plot_setting_file = get_file_by_side('plot_setting',side,'.json')
    deseq_path = f"upload_data/{uuid}/{deseq_file}"
    properties_path = f"upload_data/{uuid}/properties.json"
    filtered_heatmap = f"upload_data/{uuid}/"+get_file_by_side("filtered_heatmap",side)
    heatmap_path = f"upload_data/{uuid}/{heatmap_file}"
    plot_path = f"upload_data/{uuid}/{plot_setting_file}"
    res = deseq_controller.filter_heatmap_controller(deseq_path,heatmap_path,plot_path,properties_path,side,values,filtered_heatmap,uuid)
    return res


def get_ids(filename,uuid):
    data = pd.read_csv(f"upload_data/{uuid}/{filename}")
    names = data.columns.tolist()
    return names

def get_file_by_side(file_name,side,file_type='.csv'):
    if side == '1' or side == '2':
        return file_name+side+file_type
    else:
        return file_name+'1'+file_type




