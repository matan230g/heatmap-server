import plotly.express as px
import numpy as np
from routers.Unicorn_Exception import UnicornException


class volcano_plot :

    """  This class create a volcano plot using plotly express package,
         the class default use is a DESeq2 analysis data file but it can fit any type of data that contains numbers.

         Attributes
         ----------
         data : dataframe
            the data for the plot
         x_th : number
           threshold to classify the data in the x-axis
         y_th : number
           threshold to classify the data in the y-axis
         x_operation / y_operation : string from { None, Log}
            what operation to take on the data in the appropriate axis
         x_column/y_column : string
            the name of the column in the dataframe for the corresponding axis, the string must be column name in the dataframe
         title: string
            title for the plot

         Methods
         -------
         create_volcano_plot():
           creates a volcano plot based on the data in the object creation,
           return json of the object.
         add color by condition():
            classifies the data in the in axes according to the threshold conditions,
            each group get different color.
         column_operation():
            performs action on the data in one of the axes
    """

    #
    def __init__(self,data,x_th,y_th,x_operation = None,y_operation='Log',y_column="pvalue",x_column="log2FoldChange",title='volcano_plot'):
        if len(data)==0:
            raise UnicornException(name="Empty data", status_code=404,
                                   details="Bad request, the data is empty")
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
        # remove na values from the data
        self.data.dropna(inplace=True)
        # classify the data by the given conditions
        self.add_color_by_condition()
        # create operation on both axes if needed
        if self.y_operation != 'None':
            y_label = self.column_operation(self.y,self.y_operation)
            self.y = y_label
        if self.x_operation != 'None':
            x_label = self.column_operation(self.x,self.x_operation)
            self.x = x_label

        title=self.title + " x threshold : " +str(self.x_th)+", y threshold: "+str(self.y_th)
        # add all dataframe columns to the hover
        hover = self.data.columns
        # create plotly express plot
        fig = px.scatter(self.data, x=self.x, y=self.y, color='color', hover_data=hover,
                         title=title)
        json = fig.to_json()
        return  json

    # Add data for each gen, the gen Significantly high/low or normal- not significantly
    def add_color_by_condition(self):
        self.data.loc[(self.data[self.x] <= -self.x_th) & (self.data[self.y] < self.y_th), 'color'] = 'Low'
        self.data.loc[(self.data[self.x] >= self.x_th) & (self.data[self.y] < self.y_th), 'color'] = 'High'
        self.data['color'].fillna('Normal' , inplace=True)
        return self.data

    # mathematical calculation for a column at the request of a user
    def column_operation(self,column,operation):
        label=column
        if (operation == 'Log'):
            label = "-log10("+column+")"
            self.data[label] = self.data[column].apply(lambda x: -np.log10(x))
        return label


