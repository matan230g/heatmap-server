from fastapi import APIRouter,Header,HTTPException,FastAPI, File,Response,Request
from fastapi.responses import HTMLResponse
import pandas as pd
from controller import deseq_controller
from routers.Unicorn_Exception import UnicornException

router = APIRouter()

@router.post('/run_deseq')
async def run_deseq(request :Request):
    data = await request.form()
    # uuid = request.headers['uuid']
    # JUST FOR TEST TO AVOID A LOT OF FILES
    uuid = 'aae10d89-5fed-4fb4-b2d7-1ac709fb9534'
    side = data['side']
    design_matrix_file = get_file_by_side('design_matrix',side)
    count_matrix_file = get_file_by_side('heatmap',side)
    deseq = deseq_controller.run_deseq_controller(design_matrix_file,count_matrix_file,uuid)
    deseq_result = get_file_by_side('deseq_result',side)
    deseq.deseq_result.to_csv(f"upload_data/{uuid}/{deseq_result}",index=False)
    json_result =  deseq.deseq_result.to_json(orient='index')
    return {'deseq_results':json_result}


@router.post('/volcano_plot_deseq',response_class=HTMLResponse)
async def deseq_volcano(request :Request):
    data = await request.form()
    # uuid = request.headers['uuid']
    # JUST FOR TEST TO AVOID A LOT OF FILES
    #

    file_path = get_file_by_side('deseq_result',data['side'])
    output_path = get_file_by_side('plot_setting',data['side'],'.json')
    uuid = 'aae10d89-5fed-4fb4-b2d7-1ac709fb9534'
    fig_json = deseq_controller.deseq_volcano_controller(data,file_path,output_path,uuid)
    return fig_json

@router.post('/upload_data')
async def upload_data(request: Request):
        #uuid = request.headers['uuid']
        # JUST FOR TEST TO AVOID A LOT OF FILES
        #
        data = await request.form()
        side = data['side']
        file=data['files']
        file_name = get_file_by_side('design_matrix',side)
        uuid='aae10d89-5fed-4fb4-b2d7-1ac709fb9534'
        if file.filename.endswith('.csv'):
            with open(f"upload_data/{uuid}/{file_name}", "wb+") as file_object:
                file_object.write(file.file.read())
                file_object.close()
        else:
            raise UnicornException(name="Only csv files", status_code=404,
                                    details="User can only upload csv files")

@router.get('/get_deseq_result')
async def get_files_names(request: Request):
    # uuid = request.headers['uuid']
    # JUST FOR TEST TO AVOID A LOT OF FILES
    #
    params = request.query_params
    side =params['side']
    uuid = 'aae10d89-5fed-4fb4-b2d7-1ac709fb9534'
    result_path = get_file_by_side('deseq_result',side)
    deseq_result = pd.read_csv(f"upload_data/{uuid}/{result_path}")
    json_data = deseq_result.to_json(orient="records")
    return json_data


@router.get('/filter_heatmap')
async def filter_heatmap(request: Request):
    # uuid = request.headers['uuid']
    # JUST FOR TEST TO AVOID A LOT OF FILES
    #
    params = request.query_params
    side = params['side']
    uuid = 'aae10d89-5fed-4fb4-b2d7-1ac709fb9534'
    deseq_file = get_file_by_side('deseq_result',side)
    heatmap_file = get_file_by_side('heatmap',side)
    plot_setting_file = get_file_by_side('plot_setting',side,'.json')
    deseq_path = f"upload_data/{uuid}/{deseq_file}"
    properties_path = f"upload_data/{uuid}/properties.json"
    filtered_heatmap = f"upload_data/{uuid}/filtered-heatmap.csv"
    heatmap_path = f"upload_data/{uuid}/{heatmap_file}"
    plot_path = f"upload_data/{uuid}/{plot_setting_file}"
    res = deseq_controller.filter_heatmap_controller(deseq_path,heatmap_path,plot_path,properties_path,side,filtered_heatmap,uuid)
    return res;


def get_ids(filename,uuid):
    data = pd.read_csv(f"upload_data/{uuid}/{filename}")
    names = data.columns.tolist()
    return names

def get_file_by_side(file_name,side,file_type='.csv'):
    if side == '1' or side == '2':
        return file_name+side+file_type
    else:
        return file_name+file_type




