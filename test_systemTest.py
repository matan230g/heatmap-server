from fastapi.testclient import TestClient
from main import app
import unittest
from routers import actions
import os
from fastapi import File,UploadFile
import json
class system_test(unittest.TestCase):

    client = TestClient(app)

    # deseq tests
    def test_run_deseq(self):
        response = self.client.post('deseq/run_deseq',
                                headers={'uuid':'system_test'},
                                data ={'side':'1'})
        self.assertTrue(response.status_code == 200)

    def test_volcano_plot(self):
        response = self.client.post('/deseq/volcano_plot_deseq',
                               headers = {'uuid': 'system_test'},
                               data={'side':'1','x_th':1, 'y_th':0.05, 'x_operation':'None', 'y_operation':'Log',
                                     'x_column':'log2FoldChange','y_column':'pvalue'})

        self.assertTrue(response.status_code == 200)

    def test_volcano_plot_missing_column(self):
        try:
            response = self.client.post('/deseq/volcano_plot_deseq',
                               headers = {'uuid': 'system_test'},
                               data={'side':'1','x_th':1, 'y_th':0.05, 'x_operation':'None', 'y_operation':'Log',
                                     'x_column':'','y_column':'pvalue'})
        except Exception as exc:
            exception_class = exc.__class__.__name__
            if exception_class == 'UnicornException':
                self.assertTrue(True)
            else:
                self.assertTrue (False)

    def test_get_results(self):
        response = self.client.get('/deseq/get_deseq_result',
                                headers={'uuid':'system_test'},
                                params ={'side':'1'})
        self.assertTrue(response.status_code == 200)

    def test_filter_heatmap(self):
        response = self.client.get('/deseq/filter_heatmap',
                              headers={'uuid': 'system_test'},
                              params={'side': '1','values':'Low,High'})
        self.assertTrue(response.status_code == 200)

    def test_filter_heatmap_no_values(self):
        try:
            response = self.client.get('/deseq/filter_heatmap',
                              headers={'uuid': 'system_test'},
                              params={'side': '1','values':','})
            self.assertTrue(False)
        except Exception as exc:
            exception_class = exc.__class__.__name__
            if exception_class == 'UnicornException':
                self.assertTrue(True)
            else:
                self.assertTrue (False)

    def test_filter_heatmap2(self):
        response = self.client.get('/deseq/filter_heatmap',
                              headers={'uuid': 'system_test'},
                              params={'side': '2','values':'Low,High'})
        self.assertTrue(response.status_code == 200)

    def test_get_results2(self):
        response = self.client.get('/deseq/get_deseq_result',
                                headers={'uuid':'system_test'},
                                params ={'side':'2'})
        self.assertTrue(response.status_code == 200)

    def test_upload_data(self):
        with open('upload_data/system_test/design_matrix1.csv','rb') as file:
            body = file.read()
            response = self.client.post('deseq/upload_data',
                                    headers = {'uuid': 'system_test'},
                                    data = {'side':'1'},
                                    files ={'files': ('design_matrix1.csv',body)})
            self.assertTrue(response.status_code == 200)

    # actions_test ------------------------------------------------------------------

    def test_reset_default(self):
        response = self.client.get('/actions/reset_default',
                              headers={'uuid': 'system_test'},
                              params={'side': '1'})
        self.assertTrue(response.status_code == 200)

    def test_union(self):
        response = self.client.post('/actions/union',
                              headers={'uuid': 'system_test'},
                              json ={'data_work_on': 'first_second','metadata':0,'action':'union','raw_linkage':'Single','raw_distance':'Canberra',
                                    'both1':0,'compress1':1,'compressed_number':100,'compressed_value':'median',
                                    'values':['hsa-miR-1305-3p', 'hsa-miR-3679-5p', 'hsa-miR-4524a-3p', 'hsa-miR-18b-5p']})
        self.assertTrue(response.status_code == 200)

    def test_intersection(self):
        response = self.client.post('/actions/intersection',
                              headers={'uuid': 'system_test'},
                              json ={'data_work_on': 'first_second','metadata':0,'action':'intersection','raw_linkage':'Single','raw_distance':'Canberra',
                                    'both1':0,'compress1':0,'compressed_number':100,'compressed_value':'median',
                                    'values':['hsa-miR-99b-5p','hsa-miR-99a-3p','hsa-miR-99a-5p''hsa-miR-99b-3p']})
        self.assertTrue(response.status_code == 200)

    def test_intersection_empty(self):
        response = self.client.post('/actions/intersection',
                              headers={'uuid': 'system_test'},
                              json ={'data_work_on': 'first_second','metadata':0,'action':'intersection','raw_linkage':'Single','raw_distance':'Canberra',
                                    'both1':0,'compress1':0,'compressed_number':100,'compressed_value':'median',
                                    'values':[]})
        self.assertTrue(response.status_code == 400)

    def test_save(self):
        response = self.client.post('/actions/save',
                                    headers={'uuid': 'test_save'})
        self.assertTrue(response.status_code == 200)

    def test_prepare_file(self):
        id = 'test_id12345'
        actions.prepare_file(id)
        if os.path.exists(f"upload_data/{id}"):
            self.assertTrue(True)
            os.rmdir(f"upload_data/{id}")

    def test_uploadone(self):
        with open('upload_data/system_test/properties.json', 'rb') as file1:
            json_file = json.load(file1)
        with open('upload_data/system_test/heatmap1.csv', 'rb') as file:
            body = file.read()
            response = self.client.post('/actions/uploadone',
                                        files={'files':('design_matrix1.csv', body),'json':('prop.json', json.dumps(json_file))})
            self.assertTrue(response.status_code == 200)


sy = system_test()
sy.test_uploadone()