from typing import List
from controller import deseq_controller
from routers.Unicorn_Exception import UnicornException
from fastapi import APIRouter,HTTPException, File, UploadFile,Response,Request
import pandas as pd
import datetime
import shutil
import json
import uuid
from utils import heatmap
import os
from distutils.dir_util import copy_tree

router = APIRouter()


@router.post('/uploadone')
async def upload_file(response: Response,files:List = File(...)):
    try:
        properties = json.loads(files[len(files)-1])
        check_file_type(files[:len(files)-1])

        rand_user_id = uuid.uuid4()
        files_tuple = []
        filenames = []
        locations_of_files = {}

        #PREPARE ALL THE DATA
        prepare_file(rand_user_id) 

        one_heatmap_properties(files_tuple,rand_user_id,files,filenames,locations_of_files,properties) 
        copy_files(files_tuple)
        deseq_normalization = properties['deseq_normalization1']
        if deseq_normalization:
            deseq_controller.deseq_normalization(locations_of_files['heatmap1'])
        #USE INCHLIB LIBRARY
        properties['base'] = properties['base1']
        properties['norm_type'] = properties['norm_type1']
        properties['compress'] = properties['compress1']

        respone_heatmap = create_heat_map(properties,properties,locations_of_files)
        
        #RESPONSE TO CLIENT UUID
        response.headers["uuid"] = str(rand_user_id)

        save_properties(properties,rand_user_id)

        json_map1 = json.loads(respone_heatmap)
        with open(f"upload_data/{str(rand_user_id)}/heatmap1.json", 'w') as fp:
            json.dump(json_map1, fp)

        return respone_heatmap

    except Exception as exc:
        print(exc)
        raise UnicornException(name="Server-Error",status_code=404,
                               details='Something went wrong. Check your data.')



@router.post('/save')
async def save_current(request: Request):
    uuid = request.headers['uuid']
    file_name = create_save_dir(uuid)
    copy_files_to_saved_dir(uuid,file_name)
    return {'uuid':uuid, 'file_name': file_name}


  
@router.post('/upload')
async def upload_two_files(response: Response,files:List = File(...)):
    try:
        properties = json.loads(files[len(files)-1])
        check_file_type(files[:len(files)-1])

        rand_user_id = uuid.uuid4()

        files_tuple = []
        filenames = []
        locations_of_files = {}

        prepare_file(rand_user_id) 
        properties['metadata1']=properties['metadata']
        # print('properties[compressed_value]',properties['compressed_value'])

        properites_first_map = get_prop(properties,'file1','1','metadata1','raw_linkage1','raw_distance1','both1','column_linkage1','column_distance1', 'compress1', 'compressed_number','compressed_value','1')
        properites_first_map['compress'] = properites_first_map['compress1']
        two_heatmap_properties(files_tuple,rand_user_id,files,filenames,locations_of_files,properties)
        copy_files(files_tuple)
        deseq_normalization = properties['deseq_normalization1']
        if deseq_normalization:
            deseq_controller.deseq_normalization(locations_of_files['heatmap1'])

        deseq_normalization = properties['deseq_normalization2']
        if deseq_normalization:
            deseq_controller.deseq_normalization(locations_of_files['heatmap2'])

        save_properties(properties,rand_user_id)

        first_to_second, second_to_first= create_connection_file(files[len(files)-2],rand_user_id)

        respone_first_heatmap = create_heat_map(properties,properites_first_map,locations_of_files)

        properites_second_map = get_prop(properties,'file2','2','metadata2','raw_linkage2','raw_distance2','both2','column_linkage2','column_distance2','compress2','compressed_number2', 'compressed_value2','2')
        properites_second_map['compress'] = properites_second_map['compress2']


        respone_second_heatmap = create_heat_map(properties,properites_second_map,locations_of_files)

        answer = {"first": respone_first_heatmap, "second": respone_second_heatmap,
                  "first_second_connections": first_to_second, "second_first_connections": second_to_first}
        response.headers["uuid"] = str(rand_user_id)


        json_map1 = json.loads(respone_first_heatmap)
        json_map2 = json.loads(respone_second_heatmap)

        with open(f"upload_data/{str(rand_user_id)}/heatmap1.json", 'w') as fp:
            json.dump(json_map1, fp)

        with open(f"upload_data/{str(rand_user_id)}/heatmap2.json", 'w') as fp:
            json.dump(json_map2, fp)

        return answer

    except Exception as exc:
        print(exc)
        raise HTTPException(status_code=400, detail="Something get wrong, check your settings again")
    
@router.post('/upload-saved')
async def upload_two_files(file: UploadFile = File(...)):
    uuid = file.file.readline().strip().decode()
    file_name = file.file.readline().strip().decode()
    copy_from_saved_to_original(uuid,file_name)
    if os.path.exists(f"upload_data/{uuid}/heatmap2.json"):
        f=open(f"upload_data/{uuid}/heatmap1.json")
        first = json.load(f)

        f=open(f"upload_data/{uuid}/heatmap2.json")
        second = json.load(f)
        return {'first': json.dumps(first), 'second': json.dumps(second), 'uuid':uuid}
    else:
        f=open(f"upload_data/{uuid}/heatmap1.json")
        first = json.load(f)
        return {'first': json.dumps(first), 'uuid':uuid}
  
@router.post('/union')
async def union(request: Request):
    try:
        properties = json.loads(await request.body())
        properties['metdata'] = '0'
        properties['compress'] = properties['compress1']
        uuid = request.headers['uuid']
        f = open(f"upload_data/{uuid}/properties.json")
        prop_data = json.load(f)
        if properties['data_work_on'] =='first_second':
            properties['base'] = prop_data['base1']
            properties['norm_type'] = prop_data['norm_type1']
        else:
            properties['base'] = prop_data['base2']
            properties['norm_type'] = prop_data['norm_type2']

        targets = get_targets(properties,uuid)
        if len(targets) < 2:
            raise HTTPException(status_code=400, detail="No " + properties['action'] +'`s found')
        create_new_heatmap_from_targets(properties,targets,properties['data_work_on'],uuid)
        locations = prepar_md_locations(properties,uuid)
        new_data_location = f"upload_data/{uuid}/{properties['action']}.csv"

        md_location = prepar_md_locations(properties,uuid) ##check if there is any metdadata to add
        if md_location != "": 
            properties['metadata'] = '1'
        if properties['both1'] == 0:
            heatmap_res = heatmap.create_heatmap_json(new_data_location,row_distance=properties['raw_distance'],row_linkage=properties['raw_linkage'],properties=properties,metadata=md_location)
        else:
            heatmap_res = heatmap.create_heatmap_json(new_data_location,row_distance=properties['raw_distance'],row_linkage=properties['raw_linkage'],column_distance=properties['column_distance'],column_linkage=properties['column_linkage'],properties=properties,metadata=md_location)
    
        return heatmap_res

    except:
        raise HTTPException(status_code=500, detail="Error! Check your connection file")

@router.post('/intersection')
async def intersection(request: Request):
    properties = json.loads(await request.body())
    properties['metdata'] = '0'
    properties['compress'] = properties['compress1']
    uuid = request.headers['uuid']
    f = open(f"upload_data/{uuid}/properties.json")
    prop_data = json.load(f)
    if properties['data_work_on'] == 'first_second':
        properties['base'] = prop_data['base1']
        properties['norm_type'] = prop_data['norm_type1']
    else:
        properties['base'] = prop_data['base2']
        properties['norm_type'] = prop_data['norm_type2']
    targets = get_targets(properties, uuid)
    if len(targets) < 2:
        raise HTTPException(status_code=400, detail="No " + properties['action'] + '`s found')
    create_new_heatmap_from_targets(properties, targets, properties['data_work_on'], uuid)

    locations = prepar_md_locations(properties,uuid)
    new_data_location = f"upload_data/{uuid}/{properties['action']}.csv"

    md_location = prepar_md_locations(properties,uuid) ##check if there is any metdadata to add
    if md_location != "": 
       properties['metadata'] = '1'

    if properties['both1'] == 0:
        heatmap_res = heatmap.create_heatmap_json(new_data_location,row_distance=properties['raw_distance'],row_linkage=properties['raw_linkage'],properties=properties,metadata=md_location)
    else:
        heatmap_res = heatmap.create_heatmap_json(new_data_location,row_distance=properties['raw_distance'],row_linkage=properties['raw_linkage'],column_distance=properties['column_distance'],column_linkage=properties['column_linkage'],properties=properties,metadata=md_location)
  
    return heatmap_res


@router.get('/reset_default')
async def reset_default(request: Request):
    uuid = request.headers['uuid']
    params = request.query_params
    side = params['side']
    if side=='map1':
        heatmap_file='heatmap1.json'
    else:
        heatmap_file = 'heatmap2.json'
    heatmap_path = f"upload_data/{uuid}/{heatmap_file}"
    with open(heatmap_path) as json_file:
        heatmap = json.load(json_file)
    return {'heatmap' : heatmap}

def prepar_md_locations(propperties,uuid):
    md_location=""
    if propperties['data_work_on'] == 'first_second':
        if os.path.exists(f"upload_data/{uuid}/metadata2.csv"):
            md_location = f"upload_data/{uuid}/metadata2.csv"
    else:
        if os.path.exists(f"upload_data/{uuid}/metadata1.csv"):
            md_location = f"upload_data/{uuid}/metadata1.csv"
    return md_location


def get_targets(properties,uuid):
    data = pd.read_csv(f"upload_data/{uuid}/{properties['data_work_on']}"+"_connections.csv",names=['src','target'])
    targets = []
    map_target= {}
    dic_data =  data.set_index('src').T.to_dict('list')
    for src in properties['values']:
        if src in dic_data.keys():
           val =  dic_data[src][0] #maybe regex better
           val = val.replace("[", "")
           val = val.replace("]", "")
           val = val.replace("'", "")
           if properties['action'] == 'union':
              targets.extend((val.split(',')))
            #   print('targets',targets)
           else:
              val = val.replace("[", "")
              val = val.replace("]", "")
              val = val.replace("'", "")
              all_connections= val.split(',')
              for conn in all_connections:
                if conn.startswith(' '):
                    conn= conn[1:]
                if conn in map_target.keys():
                    map_target[conn]=map_target[conn]+1
                else:
                    map_target[conn] = 1
    if properties['action'] == 'union':    
        return targets
    else:
        for val in map_target.keys():
            if map_target[val]>=2:
                targets.append(val)
                # print('val: ',val)
                # print('map_target[val]: ',map_target[val])
        # print(targets)
        # print(len(targets))        
        return targets        


def create_new_heatmap_from_targets(properties,targets,choise,uuid):
    if choise == "first_second":
        location="heatmap2.csv"
    else:
        location="heatmap1.csv"
    data = pd.read_csv(f"upload_data/{uuid}/{location}")
    data = data.set_index([data[data.columns[0]]])
    new_data_after_action = data.loc[data.index.isin(targets)]
    new_data_after_action.drop(data.columns[0], axis=1, inplace=True)
    new_data_after_action.to_csv(f"upload_data/{uuid}/{properties['action']}.csv")


def one_heatmap_properties(files_tuple,rand_user_id,files,filenames,locations_of_files,properties):

    files_tuple.append((files[0],f"upload_data/{rand_user_id}/heatmap1.csv"))
    locations_of_files['heatmap1']=(f"upload_data/{rand_user_id}/heatmap1.csv")
    filenames.append("heatmap1.csv")

    if(properties['metadata'] == '1'):
        files_tuple.append((files[1],f"upload_data/{rand_user_id}/metadata.csv"))
        filenames.append("metadata.csv")
        locations_of_files['metadata']=(f"upload_data/{rand_user_id}/metadata.csv")


def two_heatmap_properties(files_tuple,rand_user_id,files,filenames,locations_of_files,properties):
    index_for_second_heatmap = False
    files_tuple.append((files[0],f"upload_data/{rand_user_id}/heatmap1.csv"))
    locations_of_files['heatmap1']=(f"upload_data/{rand_user_id}/heatmap1.csv")
    filenames.append("heatmap1.csv")
    if(properties['metadata'] == '1'):
        index_for_second_heatmap = True
        files_tuple.append((files[1],f"upload_data/{rand_user_id}/metadata1.csv"))
        filenames.append("metadata1.csv")
        locations_of_files['metadata1']=(f"upload_data/{rand_user_id}/metadata1.csv")

    if index_for_second_heatmap == True:
        files_tuple.append((files[2],f"upload_data/{rand_user_id}/heatmap2.csv"))
    else:
        files_tuple.append((files[1],f"upload_data/{rand_user_id}/heatmap2.csv"))
        
    locations_of_files['heatmap2']=(f"upload_data/{rand_user_id}/heatmap2.csv")
    filenames.append("heatmap2.csv")

    if properties['metadata2'] == '1' :
        if index_for_second_heatmap == True:
            files_tuple.append((files[3],f"upload_data/{rand_user_id}/metadata2.csv"))
        else:
            files_tuple.append((files[2],f"upload_data/{rand_user_id}/metadata2.csv"))
        filenames.append("metadata2.csv")
        locations_of_files['metadata2']=(f"upload_data/{rand_user_id}/metadata2.csv")



def prepare_file(id):
    if not os.path.exists('upload_data'):
        os.makedirs('upload_data')
    if os.path.exists(f"upload_data/{id}"):
        shutil.rmtree(f"upload_data/{id}")
    os.makedirs(f"upload_data/{id}")
    
def copy_files(files):
    for file in files:
        file_location =  file[1]
        with open(file_location, "wb+") as file_object:
            shutil.copyfileobj(file[0].file, file_object) 

def get_prop(properties,file, file_num,metadata,raw_linkage,raw_distance,both,column_linkage,column_distance, compress, compressed_number, compressed_value,heatmap_num):
    
    properties_edit ={}
    properties_edit['file'] = properties[file]
    properties_edit['file_num'] = file_num
    properties_edit[metadata] = properties[metadata]
    properties_edit['raw_linkage'] = properties[raw_linkage]
    properties_edit['raw_distance'] = properties[raw_distance]

    properties_edit['base'] = properties['base'+heatmap_num]
    properties_edit['norm_type'] = properties['norm_type'+heatmap_num]

    if properties[both] == 1:
        properties_edit[both] = 1
        properties_edit['column_linkage'] = properties[column_linkage]
        properties_edit['column_distance'] = properties[column_distance] 
    else:
        properties_edit[both] = 0
    if properties[compress] == 1:
        properties_edit[compress] = 1

        properties_edit['compressed_number'] = properties[compressed_number]
        properties_edit['compressed_value'] = properties[compressed_value] 
    else:
        properties_edit[compress] = 0
    return properties_edit

def create_heat_map(original_propperties, heatmap_propperties,locations_of_files):

    try:
        map_num= int(heatmap_propperties['file_num']);
        heatmapId= 'heatmap'+str(map_num)
        metadataId= 'metadata'+str(map_num)
        bothId= 'both'+str(map_num)
        compressId= 'compress'+str(map_num)

    except:
        map_num=1
        heatmapId= 'heatmap1'
        metadataId= 'metadata'
        bothId= 'both1'
        compressId= 'compress1'

    if heatmap_propperties[metadataId] =='1':
        if original_propperties[bothId] == 1:
            heatmap_res = heatmap.create_heatmap_json(locations_of_files[heatmapId],metadata=locations_of_files[metadataId],row_distance=heatmap_propperties['raw_distance'],row_linkage=heatmap_propperties['raw_linkage'],column_distance=heatmap_propperties['column_distance'],column_linkage=heatmap_propperties['column_linkage'],properties=heatmap_propperties)
        else:
            heatmap_res = heatmap.create_heatmap_json(locations_of_files[heatmapId],metadata=locations_of_files[metadataId],row_distance=heatmap_propperties['raw_distance'],row_linkage=heatmap_propperties['raw_linkage'],properties=heatmap_propperties)
    else:
        if original_propperties[bothId] == 1:
            heatmap_res = heatmap.create_heatmap_json(locations_of_files[heatmapId],row_distance=heatmap_propperties['raw_distance'],row_linkage=heatmap_propperties['raw_linkage'],column_distance=heatmap_propperties['column_distance'],column_linkage=heatmap_propperties['column_linkage'],properties=heatmap_propperties)
        else:
            heatmap_res = heatmap.create_heatmap_json(locations_of_files[heatmapId],row_distance=heatmap_propperties['raw_distance'],row_linkage=heatmap_propperties['raw_linkage'],properties=heatmap_propperties)
    return heatmap_res


def create_connection_file(file,id):
    import csv

    def create_connection_file(file_path, connection_dict):
        with open(file_path, 'w',newline='') as csv_file:  
            writer = csv.writer(csv_file)
            for key, value in connection_dict.items():
                writer.writerow([key, value])

    def addToDict(dict_to_add, key, val_instance_to_add ):
        val_list=[]
        if key in dict_to_add.keys():
            val_list = dict_to_add.get(key)
        else:
            val_list=[]
        val_list.append(val_instance_to_add)
        dict_to_add[key]=val_list


    location = f"upload_data/{id}/connection.csv"
    with open(location, "wb+") as file_object:
            shutil.copyfileobj(file.file, file_object)

    f = open(location, "r")
    Lines = f.readlines()
    count=0

    first_to_second= {}
    second_to_first= {}

    for line in Lines:
        count=count+1
        data= line.strip().split(',')
        first_instance= data[0];
        second_instance= data[1];
        
        addToDict(first_to_second, first_instance, second_instance)
        addToDict(second_to_first, second_instance, first_instance)

    f.close()

    create_connection_file(f'upload_data/{id}/first_second_connections.csv',first_to_second)
    create_connection_file(f'upload_data/{id}/second_first_connections.csv',second_to_first)
    return first_to_second, second_to_first


def create_save_dir(uuid):
    file_name = str(datetime.datetime.now()).replace(":","_")
    if not os.path.exists('saved_data'):
        os.makedirs('saved_data')
    if not os.path.exists(f"saved_data/{uuid}"):
        os.makedirs(f"saved_data/{uuid}")
    os.makedirs(f'saved_data/{uuid}/{file_name}')    
    return file_name

def  copy_from_saved_to_original(uuid,file_name):
    new_data_saved_location = f"upload_data/{uuid}"
    old_data_saved_location = f'saved_data/{uuid}/{file_name}'
    copy_tree(old_data_saved_location, new_data_saved_location)


def copy_files_to_saved_dir(uuid, file_name):
    old_data_saved_location = f"upload_data/{uuid}"
    new_data_saved_location = f'saved_data/{uuid}/{file_name}'
    copy_tree(old_data_saved_location, new_data_saved_location)


def save_properties(properties,uuid):
    with open(f"upload_data/{uuid}/properties.json", 'w') as f:
        json.dump(properties, f)
        
def check_file_type(files):
    for file in files:
        if file.filename.endswith('.csv') == False:
            raise UnicornException(name="Only csv files", status_code=404,
                               details=f"User can only upload csv files, {file.filename}")
        # seek to the end of the file
        file.file.seek(0,2)
        file_size = file.file.tell()
        # Reset the file position to the beginning
        file.file.seek(0)
        if file_size > 2000000000:
            raise UnicornException(name="File too big", status_code=404,
                                   details=f"File {file.filename} is too big, maximum file size 2GB")

