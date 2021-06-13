from utils import inchlib_clust_dev as inchlib_clust

'''
    create a json file containing the details of the heatmap in order to draw it on client side.
    params:
        * data - path to csv file contains the relevent data
        * properties - dictionary contains all params 
            * raw_distance - string, for clustering 
            * raw_linkage - string, for clustering
            * column_distane - string, for clustering
            * column_linkage - string, for clustering
            * base - int, for log normalization 
            * norm_type - string, which normalization to use
            * compress - int, 0/1 if to do compress
            * compress_number - int, size of the cluster
            * compress_value - string compress type
            * file_num - int, file side
            * metadata - int 0/1 if to use metadata file
'''

def create_heatmap_json(data,**kwargs):
    properties = kwargs.pop('properties')
    try:
        metadataId= 'metadata'+str(properties['file_num'])
        bothId= 'both'+str(properties['file_num'])
    except:
        metadataId= 'metadata'
        bothId= 'both1'

    #instantiate the Cluster object
    c = inchlib_clust.Cluster()
    # read csv data file with specified delimiter, also specify whether there is a header row, the type of the data (numeric/binary) and the string representation of missing/unknown values
    
    c.read_csv(filename=data, delimiter=",", header=True, datatype="numeric")
    
    # c.read_data(data, header=bool, missing_value=str/False, datatype="numeric/binary") use read_data() for list of lists instead of a data file

    # normalize data to (0,1) scale, but after clustering write the original data to the heatmap

    base = int(properties['base'])
    c.normalize_data(feature_range=base, write_original=True,norm_type=properties['norm_type'])

    # cluster data according to the parameters
    if properties[bothId] == 1:
        c.cluster_data(row_distance=properties['raw_distance'].lower(), row_linkage=properties['raw_linkage'].lower(), axis="both", column_distance=properties['column_distance'].lower(), column_linkage=properties['column_linkage'].lower())
    else:
        c.cluster_data(row_distance=properties['raw_distance'].lower(), row_linkage=properties['raw_linkage'].lower(), axis="row",column_distance="euclidean", column_linkage="ward")
    # instantiate the Dendrogram class with the Cluster instance as an input
    d = inchlib_clust.Dendrogram(c)

    # create the cluster heatmap representation and define whether you want to compress the data by defining the maximum number of heatmap rows, the resulted value of compressed (merged) rows and whether you want to write the features

    compress = int(properties['compress'])
    if compress == 1:
        compress = int(properties['compressed_number'])
        compressed_value = properties['compressed_value']
    else:
        compress = len(c.data)
        compressed_value = 'median'

    d.create_cluster_heatmap(compress=compress, compressed_value=compressed_value, write_data=True)
    if properties[metadataId] == '1':
        metadata  = kwargs.pop('metadata')
    # read metadata file with specified delimiter, also specify whether there is a header row
        # d.add_metadata_from_file(metadata_file=metadata, delimiter=",", header=True, metadata_compressed_value="frequency")

    # read column metadata file with specified delimiter, also specify whether there is a 'header' column
        d.add_column_metadata_from_file(column_metadata_file=metadata, delimiter=",", header=True)
    # export the cluster heatmap on the standard output or to the file if filename specified
    return d.export_cluster_heatmap_as_json()

