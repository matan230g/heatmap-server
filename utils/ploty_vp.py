import plotly.express as px
import pandas as pd
import numpy as np

class volcano_plot :

    def __init__(self,data,x_th,y_th,x_operation = None,y_operation=None,y_column="pvalue",x_column="log2FoldChange",title='volcano_plot'):
        self.data = data
        self.x_th = float(x_th)
        self.y_th = float(y_th)
        self.x_operation = x_operation
        self.y_operation = y_operation
        self.x = x_column
        self.y = y_column
        self.title = title
        self.volcno_plot = None
        self.result= None

    def create_volcano_plot(self):
        self.data.dropna(inplace=True)
        self.add_color_by_condition()
        if  self.y_operation != 'None':
            y_label = self.column_operation(self.y,self.y_operation)
            self.y = y_label
        if self.x_operation != 'None':
            x_label = self.column_operation(self.x,self.x_operation)
            self.x = x_label
        title=self.title + " x threshold : " +str(self.x_th)+", y threshold: "+str(self.y_th)
        hover = self.data.columns
        fig = px.scatter(self.data, x=self.x, y=self.y, color='color', hover_data=hover,
                         title=title)
        json = fig.to_json()
        return  json

    # Add data for each gen, the gen Signficantly high/low or normal- not significantly
    def add_color_by_condition(self):
        self.data.loc[(self.data[self.x] <= -self.x_th) & (self.data[self.y] < self.y_th), 'color'] = 'Low'
        self.data.loc[(self.data[self.x] >= self.x_th) & (self.data[self.y] < self.y_th), 'color'] = 'High'
        self.data['color'].fillna('Normal' , inplace=True)

    # mathematical calculation for a column at the request of a user
    def column_operation(self,column,operation):
        if (operation == 'Log'):
            label = "-log10("+column+")"
            self.data[label] = self.data[column].apply(lambda x: -np.log10(x))
        return label


