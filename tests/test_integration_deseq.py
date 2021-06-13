from controller import deseq_controller
from utils import Deseq
import unittest
import json


class Deseq_Integration(unittest.TestCase):

    def test_deseq_normalization(self):
        uuid = 'test_data'
        path = f"../upload_data/{uuid}/{'cm_valid.csv'}"
        deseq_controller.deseq_normalization(path,save=False)
        self.assertTrue(True)

    def test_run_deseq2(self):
        cm_name = 'cm_valid.csv'
        ds_name = 'ds_one_condition.csv'
        uuid = 'test_data'
        locations = [f"../upload_data/{uuid}/{cm_name}", f"../upload_data/{uuid}/{ds_name}"]
        deseq = deseq_controller.run_deseq_controller(locations)
        self.assertIsInstance(deseq,Deseq.py_DESeq2)

    def test_run_deseq_missingID(self):
        try:
            cm_name = 'cm_valid.csv'
            ds_name = 'ds_missing_id.csv'
            uuid = 'test_data'
            locations = [f"../upload_data/{uuid}/{cm_name}", f"../upload_data/{uuid}/{ds_name}"]
            deseq = deseq_controller.run_deseq_controller(locations)
            self.fail('Exception not raised')
        except Exception as exc:
            exception_class = exc.__class__.__name__
            if exception_class == 'UnicornException':
                self.assertTrue(True)
            else:
                self.fail('unexpected exception raised')


    def test_run_deseq_missingID2(self):
        try:
            cm_name = 'cm_missing_id_column.csv'
            ds_name = 'ds_one_condition.csv'
            uuid = 'test_data'
            locations = [f"../upload_data/{uuid}/{cm_name}", f"../upload_data/{uuid}/{ds_name}"]
            deseq = deseq_controller.run_deseq_controller(locations)
            self.fail('Exception not raised')
        except Exception as exc:
            exception_class = exc.__class__.__name__
            if exception_class == 'UnicornException':
                self.assertTrue(True)
            else:
                self.fail('unexpected exception raised')

    def test_run_deseq_missing_conditions(self):
        try:
            cm_name = 'cm_valid.csv'
            ds_name = 'ds_no_conditions.csv'
            uuid = 'test_data'
            locations = [f"../upload_data/{uuid}/{cm_name}", f"../upload_data/{uuid}/{ds_name}"]
            deseq = deseq_controller.run_deseq_controller(locations)
            self.fail('Exception not raised')
        except Exception as exc:
            exception_class = exc.__class__.__name__
            if exception_class == 'UnicornException':
                self.assertTrue(True)
            else:
                self.fail('unexpected exception raised')

    def test_run_deseq_multi_conditions(self):
        cm_name = 'cm_valid.csv'
        ds_name = 'ds_multi_conditions.csv'
        uuid = 'test_data'
        locations = [f"../upload_data/{uuid}/{cm_name}", f"../upload_data/{uuid}/{ds_name}"]
        deseq = deseq_controller.run_deseq_controller(locations)
        self.assertIsInstance(deseq,Deseq.py_DESeq2)

    def test_volcano(self):
        deseq_result = 'deseq_result_test.csv'
        uuid = 'test_data'
        locations = [f"../upload_data/{uuid}/{deseq_result}", f"../upload_data/{uuid}/{'plot_setting.json'}"]
        json_data = dict()
        json_data['x_th'] =1
        json_data['x_column']='log2FoldChange'
        json_data['x_operation'] = None
        json_data['y_th'] = 0.05
        json_data['y_column'] = 'pvalue'
        json_data['y_operation'] = 'Log'
        vp = deseq_controller.deseq_volcano_controller(json_data,locations)
        self.assertIsNotNone(vp[0])
        # check if file created
        with open(locations[1]) as json_file:
            plot_settings = json.load(json_file)
            self.assertTrue(plot_settings['x_th'] == json_data['x_th'] )

    def test_volcano_fail(self):
        try:
            deseq_result = 'deseq_result_test.csv'
            uuid = 'test_data'
            locations = [f"../upload_data/{uuid}/{deseq_result}", f"../upload_data/{uuid}/{'plot_setting.json'}"]
            json_data = dict()
            json_data['x_th'] =1
            json_data['x_column']='log2FoldChange'
            json_data['x_operation'] = None
            json_data['y_th'] =0.05
            json_data['y_column'] = 'NotRealColumn'
            json_data['y_operation'] = 'Log'
            vp = deseq_controller.deseq_volcano_controller(json_data,locations)
            self.fail('Exception not raised')
        except Exception as exc:
            exception_class = exc.__class__.__name__
            if exception_class == "KeyError":
                self.assertTrue(True)
            else:
                self.fail('unexpected exception raised')

    def test_filter_heatmap_fail(self):
        uuid = 'test_data'
        deseq_path = f"../upload_data/{uuid}/{'deseq_result_test.csv'}"
        heatmap_path = f"../upload_data/{uuid}/{'heatmap1.csv'}"
        plot_path = f"../upload_data/{uuid}/{'plot_setting.json'}"
        properties_path = f"../upload_data/{uuid}/{'properties.json'}"
        side = "3"
        filtered_heatmap_path = f"../upload_data/{uuid}/{'filtered_heatmap1.csv'}"
        data_dict = deseq_controller.filter_heatmap_controller(deseq_path,heatmap_path,plot_path,properties_path,side,'Low,High',filtered_heatmap_path)
        self.assertTrue(len(data_dict) == 2)

    def test_filter_heatmap_fail(self):
        try:
            uuid = 'test_data'
            deseq_path = f"../upload_data/{uuid}/{'deseq_result_empty.csv'}"
            heatmap_path = f"../upload_data/{uuid}/{'heatmap1.csv'}"
            plot_path = f"../upload_data/{uuid}/{'plot_setting.json'}"
            properties_path = f"../upload_data/{uuid}/{'properties.json'}"
            side = "3"
            filtered_heatmap_path = f"../upload_data/{uuid}/{'filtered_heatmap1.csv'}"
            data_dict = deseq_controller.filter_heatmap_controller(deseq_path, heatmap_path, plot_path, properties_path,
                                                                   side,'Low,High', filtered_heatmap_path)
            self.fail('Exception not raised')
        except Exception as exc:
            exception_class = exc.__class__.__name__
            if exception_class == "UnicornException":
                self.assertTrue(True)
            else:
                self.fail('unexpected exception raised')



    def test_deseq_normalization_missingID(self):
        try:
            uuid = 'test_data'
            path = f"../upload_data/{uuid}/{'cm_missing_id_column.csv'}"
            deseq_controller.deseq_normalization(path, save=False)
            self.assertTrue(False)
        except Exception as exc:
            exception_class = exc.__class__.__name__
            if exception_class == "UnicornException":
                self.assertTrue(True)
            else:
                self.fail('unexpected exception raised')

    def test_filted_heatmap2(self):
        uuid = 'system_test'
        deseq_path = f"../upload_data/{uuid}/{'deseq_result1.csv'}"
        heatmap_path = f"../upload_data/{uuid}/{'heatmap1.csv'}"
        plot_path = f"../upload_data/{uuid}/{'plot_setting1.json'}"
        properties_path = f"../upload_data/{uuid}/{'properties.json'}"
        side = "1"
        filtered_heatmap_path = f"../upload_data/{uuid}/{'filtered_heatmap1.csv'}"
        data_dict = deseq_controller.filter_heatmap_controller(deseq_path, heatmap_path, plot_path, properties_path,
                                                               side, 'Low,High', filtered_heatmap_path)
        self.assertTrue(len(data_dict) == 2)

    def test_filted_heatmap_missing_values(self):
        try:
            uuid = 'system_test'
            deseq_path = f"../upload_data/{uuid}/{'deseq_result1.csv'}"
            heatmap_path = f"../upload_data/{uuid}/{'heatmap1.csv'}"
            plot_path = f"../upload_data/{uuid}/{'plot_setting1.json'}"
            properties_path = f"../upload_data/{uuid}/{'properties.json'}"
            side = "1"
            filtered_heatmap_path = f"../upload_data/{uuid}/{'filtered_heatmap1.csv'}"
            data_dict = deseq_controller.filter_heatmap_controller(deseq_path, heatmap_path, plot_path, properties_path,
                                                               side, ',', filtered_heatmap_path)
            self.assertTrue(len(data_dict) == 2)
        except Exception as exc:
            exception_class = exc.__class__.__name__
            if exception_class == "UnicornException":
                self.assertTrue(True)
            else:
                self.fail('unexpected exception raised')

    def test_create_heatmap1(self):
        uuid = 'system_test'
        properties_path = f"../upload_data/{uuid}/{'properties.json'}"
        side = "1"
        filtered_heatmap_path = f"../upload_data/{uuid}/{'filtered_heatmap1.csv'}"
        data_dict = deseq_controller.create_heat_map(properties_path,side,filtered_heatmap_path)
        self.assertTrue(data_dict!=None)

    def test_create_heatmap2(self):
        uuid = 'system_test'
        properties_path = f"../upload_data/{uuid}/{'properties.json'}"
        side = "2"
        filtered_heatmap_path = f"../upload_data/{uuid}/{'filtered_heatmap2.csv'}"
        data_dict = deseq_controller.create_heat_map(properties_path, side, filtered_heatmap_path)
        self.assertTrue(data_dict!=None)
