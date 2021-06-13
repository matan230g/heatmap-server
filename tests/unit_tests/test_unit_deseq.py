import unittest
import pandas as pd
from utils import Deseq, ploty_vp
from routers import deseq_router


class Deseq_Utests(unittest.TestCase):

    def test_2(self):
        ds_path = '../test_data/ds_one_condition.csv'
        cm_path = '../test_data/cm_valid.csv'
        ds = pd.read_csv(ds_path,encoding='utf-8-sig')
        cm = pd.read_csv(cm_path,encoding='utf-8-sig')
        conditions =ds.columns.tolist()
        conditions.remove('id')
        deseq_obj = Deseq.py_DESeq2(cm,ds,conditions)
        self.assertIsInstance(deseq_obj,Deseq.py_DESeq2)

    def test_3(self):
        deseq_result_path ='../test_data/deseq_result.csv'
        deseq_result = pd.read_csv(deseq_result_path ,encoding='utf-8-sig')
        plot_vp = ploty_vp.volcano_plot(deseq_result,x_th=0.05,y_th=1)
        self.assertIsInstance(plot_vp,ploty_vp.volcano_plot)

    def test_4(self):
        ds_path = '../test_data/ds_one_condition.csv'
        cm_path = '../test_data/cm_valid.csv'
        ds = pd.read_csv(ds_path,encoding='utf-8-sig')
        cm = pd.read_csv(cm_path,encoding='utf-8-sig')
        conditions = list(ds.columns.values)
        conditions.remove('id')
        deseq_obj = Deseq.py_DESeq2(cm,ds,conditions)
        deseq_obj.run_deseq()
        self.assertIsNotNone(deseq_obj.dds)

    def test_5(self):
        try:
            ds_path = '../test_data/ds_one_condition.csv'
            cm_path = '../test_data/cm_float_numbers.csv'
            ds = pd.read_csv(ds_path, encoding='utf-8-sig')
            cm = pd.read_csv(cm_path,encoding='utf-8-sig')
            conditions = list(ds.columns.values)
            conditions.remove('id')
            deseq_obj = Deseq.py_DESeq2(cm, ds, conditions)
            deseq_obj.run_deseq()
        except Exception as exc:
            exception_class = exc.__class__.__name__
            if exception_class == 'RRuntimeError':
                self.assertTrue(True)
            else:
                self.fail('unexpected exception raised')


    def test_6(self):
        try:
            ds_path = '../test_data/invalid_ds.csv'
            cm_path = '../test_data/cm_valid.csv'
            ds = pd.read_csv(ds_path,encoding='utf-8-sig')
            cm = pd.read_csv(cm_path,encoding='utf-8-sig')
            conditions = list(ds.columns.values)
            conditions.remove('id')
            deseq_obj = Deseq.py_DESeq2(cm, ds, conditions)
            deseq_obj.run_deseq()
        except Exception as exc:
            exception_class = exc.__class__.__name__
            if exception_class == 'RRuntimeError':
                self.assertTrue(True)
            else:
                self.fail('unexpected exception raised')

    def test_7(self):
        ds_path = '../test_data/ds_one_condition.csv'
        cm_path = '../test_data/cm_valid.csv'
        ds = pd.read_csv(ds_path,encoding='utf-8-sig')
        cm = pd.read_csv(cm_path,encoding='utf-8-sig')
        conditions = list(ds.columns.values)
        conditions.remove('id')
        deseq_obj = Deseq.py_DESeq2(cm,ds,conditions)
        deseq_obj.run_deseq()
        deseq_obj.get_deseq_result()
        self.assertIsNotNone(deseq_obj.deseq_result)

    def test_8(self):
        deseq_result_path = '../test_data/deseq_result.csv'
        deseq_result = pd.read_csv(deseq_result_path, encoding='utf-8-sig')
        plot_vp = ploty_vp.volcano_plot(deseq_result, x_th=0.05, y_th=1)
        plot_vp.column_operation('pvalue','Log')
        self.assertTrue("-log10(pvalue)" in plot_vp.data.columns.tolist())

    def test_9(self):
        deseq_result_path = '../test_data/deseq_result.csv'
        deseq_result = pd.read_csv(deseq_result_path, encoding='utf-8-sig')
        plot_vp = ploty_vp.volcano_plot(deseq_result, x_th=0.05, y_th=1)
        plot_vp.add_color_by_condition()
        self.assertTrue("color" in plot_vp.data.columns.tolist())

    def test_10(self):
        deseq_result_path = '../test_data/deseq_result.csv'
        deseq_result = pd.read_csv(deseq_result_path, encoding='utf-8-sig')
        plot_vp = ploty_vp.volcano_plot(deseq_result, x_th=0.05, y_th=1)
        plot_json = plot_vp.create_volcano_plot()
        self.assertIsNotNone(plot_json)

    def test_11(self):
        try:
            deseq_result_path = '../test_data/deseq_result.csv'
            deseq_result = pd.read_csv(deseq_result_path, encoding='utf-8-sig')
            plot_vp = ploty_vp.volcano_plot(deseq_result, x_th=0.05, y_th=1,x_column="not_column_name")
            plot_json = plot_vp.create_volcano_plot()
        except Exception as exc:
            exception_class = exc.__class__.__name__
            if exception_class == "KeyError":
                self.assertTrue(True)
            else:
                self.fail('unexpected exception raised')

    def test_12(self):
        deseq_result_path = '../test_data/deseq_result.csv'
        r_deseq_results_path = '../test_data/deseq_R_results.csv'
        deseq_result = pd.read_csv(deseq_result_path, encoding='utf-8-sig')
        r_deseq_results = pd.read_csv(r_deseq_results_path, encoding='utf-8-sig')
        py_lfc = deseq_result['log2FoldChange'].values
        py_pvalue = deseq_result['pvalue'].values
        r_lfc = r_deseq_results['log2FoldChange'].values
        r_pvalue =  r_deseq_results['pvalue'].values
        self.assertAlmostEqual(py_pvalue[0],r_pvalue[0],4)
        self.assertAlmostEqual(py_lfc[0],r_lfc[0],4)
        self.assertTrue(len(deseq_result) == len(r_deseq_results))

    def test_13(self):
        path = deseq_router.get_file_by_side("test_file",'2')
        self.assertEqual('test_file2.csv',path)
        path = deseq_router.get_file_by_side("test_file", '1')
        self.assertEqual('test_file1.csv', path)

