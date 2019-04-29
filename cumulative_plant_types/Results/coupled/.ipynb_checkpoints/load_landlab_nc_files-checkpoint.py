def load_landlab_nc_files(folder_list, name_list, use_means = True,  do_pickle = False, pickle_name = 'data_pickle.p'):
    """
    function that takes all the paths in the provided input list and extracts the netcdf
    files into a dictionary. 
    Requirement for this to work is the "standart-manu-landlab-folder-structure" so, 
    /model_dir/ll_output/NC and the provided input paths are the full paths to the 
    base model_dir. 
    The second input is a list of names that are used as dictionary indizes.
    
    if  use_means = True, the algorithm will just save the overall mean value per timestep and delete the whole
        landform__ID data-field, since its obsolete. If use_means = False, the algorithm will save a complete copy
        of the grid without boundary nodes for each parameter and each timestep. NOTE: This can produce VERY large
        dictionarys that may cause the pickle-serialization to break.
    
    if argument pickle is set to True, the function automatically creates a serialized
    object in the folder where it was run which encompasses the data_dictionary and is named
    data_pickle.p
    
    Extracted Parameters are: 
        -Topographic Elevation
        -Topographic Slope
        -Erosion Rate
        -Vegetation Density (either cumulative or individual)
        -Soil Depth
        -Soil Production Rate
    
    input:
        folder_list - type: list, eg. ['path1', 'path2', ...]
        name_list   = type: list, eg. ['name1', 'name2', ...]
        do_pickle   = boolean, if True then pickle is used for saving a binary file with the data_object
        pickle_name = type: str, eg. 'MyData.p'
        
    output:
        data_dict   - simu1
                    - simu2
                    - ...
        if do_pickle == True, this saves a binary file in the runtime folder
                    
                    
    created by: 
        Manuel Schmid, 09.3.2019
    """
    
    #import the needed modules
    import numpy as np
    import os, glob, pickle
    from netCDF4 import Dataset
    
    
    #first check if folder_list is really a list
    if isinstance(folder_list, list) and isinstance(name_list, list):
        pass
    else:
        raise ValueError('Provided input must be of type list')
        
    #create dictionary
    data_dict = {}
    
    #create parameter list
    parameters = [
    "topographic__elevation",
    "soil__depth",
    "sediment__flux",
    "landform__ID",
    "precipitation",
    "landform__ID",
    "erosion__rate",
    "vegetation__density",
    'slope_degrees',
    'tree_fpc',
    'grass_fpc',
    'shrub_fpc'
    ]

    #create last part of path to /ll_output/NC
    nc_path = 'll_output/NC/'
    
    #populate dictionary with names from name_list
    for name in name_list:
        data_dict[name] = {}
        for p in parameters:
            data_dict[name][p] = []
    
    #data unpacking
    for folder, name in zip(folder_list, name_list):
        #check if last / was provided with path and create full_path string
        if folder[-1] == '/':
            full_path = os.path.join(folder, nc_path)
        else:
            full_path = os.path.join(folder, '/', nc_path)
        
        counter = 0
        
        print('Data loading of ' + str(name) + ' Simulation')
        
        for nc_file in sorted(glob.glob(os.path.join(full_path, "*.nc")), key = os.path.getmtime):
            _dataDump = Dataset(nc_file)
            counter += 1
            #print('DEBUG: - For loop activated')
            if counter % 100 == 0:
                print('100 files done')
                
            if use_means == True:
                parameters.remove('landform__ID')
            else:
                pass
                
            #check if the simulation was run with individual fpcs or cumulative
            if 'tree_fpc' and 'shrub_fpc' and 'grass_fpc' in _dataDump.variables:
          
                for p in parameters:
                    _cutDump = _dataDump.variables[p][:][0]
                    #delete boundary nodes
                    _cutDump = np.delete(_cutDump, 0 , axis = 0) 
                    _cutDump = np.delete(_cutDump,-1 , axis = 0)
                    _cutDump = np.delete(_cutDump, 0 , axis = 1)
                    _cutDump = np.delete(_cutDump,-1 , axis = 1)

                    if use_means == True:
                        data_dict[name][p].append(np.mean(_cutDump))
                    elif use_means == False:
                        data_dict[name][p].append(_cutDump)
                    else:
                        raise ValueError('use_means must be boolean')
                    
            else:
                
                for p in parameters:
                    _cutDump = _dataDump.variables[p][:][0]
                    #delete boundary nodes
                    _cutDump = np.delete(_cutDump, 0 , axis = 0) 
                    _cutDump = np.delete(_cutDump,-1 , axis = 0)
                    _cutDump = np.delete(_cutDump, 0 , axis = 1)
                    _cutDump = np.delete(_cutDump,-1 , axis = 1)
                    
                    if use_means == True:
                        data_dict[name][p].append(np.mean(_cutDump))
                    elif use_means == False:
                        data_dict[name][p].append(_cutDump)
                    else:
                        raise ValueError('use_means must be boolean')
    
    if do_pickle == True:
        print('do_pickle was choosen. Starting serialization...')
        pickle.dump( data_dict, open( pickle_name, "wb" ))
        print('file saved in: ' + str(pickle_name))
    else: 
        print('do_pickle is false. I am not saving a binary file!')
        pass
    
    #returns the data_dictionary
    return data_dict