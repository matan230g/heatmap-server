from fastapi import APIRouter,Header,HTTPException,FastAPI, File,Response,Request
from fastapi.responses import HTMLResponse
import json
import os
import pandas as pd
from typing import List
import shutil
from controller import deseq_controller
from routers.Unicorn_Exception import UnicornException

router = APIRouter()

@router.post('/run_deseq')
async def run_deseq(request :Request):
    data = await request.form()
    # uuid = request.headers['uuid']
    # JUST FOR TEST TO AVOID A LOT OF FILES
    uuid = 'aae10d89-5fed-4fb4-b2d7-1ac709fb9534'
    deseq_result =  deseq_controller.run_deseq_controller(data,uuid)
    return {'deseq_results':deseq_result}


@router.post('/volcano_plot_deseq',response_class=HTMLResponse)
async def deseq_volcano(request :Request):
    data = await request.form()
    # uuid = request.headers['uuid']
    # JUST FOR TEST TO AVOID A LOT OF FILES
    #
    uuid = 'aae10d89-5fed-4fb4-b2d7-1ac709fb9534'
    fig_json = deseq_controller.deseq_volcano_controller(data,uuid)
    return fig_json

@router.post('/upload_data')
async def upload_data(files:List = File(...)):
        #uuid = request.headers['uuid']
        # JUST FOR TEST TO AVOID A LOT OF FILES
        #
        uuid='aae10d89-5fed-4fb4-b2d7-1ac709fb9534'
        locations=[f"upload_data/{uuid}/count_matrix.csv",f"upload_data/{uuid}/design_matrix.csv"]
        i=0
        for file in files:
            if file.filename.endswith('.csv'):
                with open(locations[i], "wb+") as file_object:
                    file_object.write(file.file.read())
                    file_object.close()
            else:
                raise UnicornException(name="Only csv files", status_code=404,
                                       details="User can only upload csv files")
            i+=1
        count_values = get_ids("count_matrix.csv",uuid)
        design_values = get_ids("design_matrix.csv",uuid)
        return {"count_values":count_values,"design_values":design_values}

def get_ids(filename,uuid):
    data = pd.read_csv(f"upload_data/{uuid}/{filename}")
    names = data.columns.tolist()
    return names

@router.get('/get_deseq_result')
async def get_files_names(request: Request):
    # uuid = request.headers['uuid']
    # JUST FOR TEST TO AVOID A LOT OF FILES
    #
    uuid = 'aae10d89-5fed-4fb4-b2d7-1ac709fb9534'
    deseq_result = pd.read_csv(f"upload_data/{uuid}/deseq_result.csv")
    json_data = deseq_result.to_json(orient="records")
    return json_data



# @router.get('/get_files')
# async def get_files_names(request: Request):
#     files=[]
#     for file in os.walk(r"C:\Users\gal\Desktop\ISE\project\data\csv"):
#         files.append(file[2])
#     return {"files": files}

# @router.get('/download/{path}')
# async def download_file(request :Request):
#     file_path = request.query_params['path']
#     with open(file_path,"rb") as file:
#         bytes =await file.read()




