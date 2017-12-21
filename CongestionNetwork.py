# -*- coding: utf-8 -*-
"""
Created on Tue May  2 14:55:06 2017

@author: James
"""


class Network:
    import numpy as np
    import pandas as pd
    import matplotlib.pyplot as plt
    

    
    def __init__(self, query,last_value_file_string='last_values.csv'):
                
        import pandas as pd
        import numpy as np
        
        self.query = query
        self.last_value_file_string = last_value_file_string
        self.last_values_pd  = pd.read_csv(last_value_file_string)
        self.last_values_congestion = self.last_values_pd['congestion'].values
        
        
        usecols = ['segmentid','street','_fromst','_tost','_length','_traffic','start_lon','_lif_lat','_lit_lon','_lit_lat']  
        raw_data = pd.read_csv(query,dtype='str',usecols=usecols)
        length = len(raw_data)

        start_lon = raw_data['start_lon'].values.astype(np.float)
        start_lat = raw_data['_lif_lat'].values.astype(np.float)
        end_lon = raw_data['_lit_lon'].values.astype(np.float)
        end_lat  = raw_data['_lit_lat'].values.astype(np.float)
        self.seg_ids = raw_data['segmentid'].values.astype('str')
        seg_lengths = raw_data['_length'].values.astype(np.float)
        self.congestion = raw_data['_traffic'].values.astype('int')
        
        def getLastValue(idx,val='index'):
            if(val=='segid'):
                index = np.where(self.seg_ids == str(idx))[0][0]
            else:
                index = idx
            cong_value = self.last_values_congestion[index]
            return(cong_value)
        
        start_coor_array = []
        end_coor_array  = []
        self.node_stack = []
        for i in range(length):
           seg_id_temp = self.seg_ids[i]
           start_lon_temp = "{:.3f}".format((start_lon[i]))      
           start_lat_temp = "{:.3f}".format((start_lat[i]))
           end_lon_temp = "{:.3f}".format((end_lon[i]))
           end_lat_temp = "{:.3f}".format((end_lat[i]))
           start_coor_temp = (start_lon_temp,start_lat_temp)
           start_coor_array.append(start_coor_temp)
           end_coor_temp = (end_lon_temp,end_lat_temp)
           end_coor_array.append(end_coor_temp)
           self.node_stack.append([seg_id_temp,start_lon_temp,start_lat_temp,end_lon_temp,end_lat_temp])

        self.node_stack = np.array(self.node_stack)        
        self.all_coor = start_coor_array
        self.all_coor.extend(end_coor_array)
        self.unique = list(set(self.all_coor))

        self.unique_array = np.array(self.unique)
        unique_lon = self.unique_array[:,0]
        unique_lat = self.unique_array[:,1]
        self.connections = []
        self.node_labels = []
        self.missing_idx = []
        self.weight_values = []
        self.congestion_speed_values = []
        self.connections_array = []
     
        for i in range(length):
            self.node_labels.append(i)
            from_lon, from_lat  = start_coor_array[i]
            to_lon, to_lat = end_coor_array[i]
    
            from_node = np.where((unique_lon== from_lon) & (unique_lat == from_lat))[0]
            to_node = np.where((unique_lon== to_lon) & (unique_lat == to_lat))[0]
    
            congestion_temp = self.congestion[i]
            length_temp = seg_lengths[i]
            if ((congestion_temp != -1) and (congestion_temp != 0)):
                weight = (1/congestion_temp)*length_temp*60*60 
                self.weight_values.append(weight)
                self.congestion_speed_values.append(congestion_temp)
            else:
                self.missing_idx.append(i)
                last_value = getLastValue(i)
                if (last_value != -1):
                    weight = last_value
                else:
                    #weight = 1000 #too high to be considered a path
                    #weight = 
                    if(len(self.congestion_speed_values)>0):
                        avg_cong = sum(self.congestion_speed_values)/len(self.congestion_speed_values)
                    else:
                        avg_cong = 15
                    weight = (1/avg_cong)*length_temp*60*60
                    
            self.connections.append((from_node[0],to_node[0],weight))
            self.connections_array.append([from_node[0],to_node[0],weight])
        self.connections_array = np.array(self.connections_array)
            
    def plotNetwork(self,cmap=plt.cm.RdYlGn_r,node_color='k',node_size=50,size_x=18,size_y=18,save=False,fname='network_file.png'): #YlGn_r
        import numpy as np
        import matplotlib.pyplot as plt
        import networkx as nx

        
        scale_min = round(min(self.weight_values))-1
        scale_max = round(max(self.weight_values))-1
                         
        g = nx.Graph()
        for i, coordinate in enumerate(np.asarray(self.unique,float)):
            g.add_node(i, pos = coordinate, label = self.node_labels[i])
        
        pos= nx.get_node_attributes(g,'pos')
        
        g.add_weighted_edges_from(self.connections)
        edges,weights = zip(*nx.get_edge_attributes(g,'weight').items())
        self.weight_array = np.array(weights)
        
        plt.figure(1,figsize=(size_x,size_y))
        nx.draw(g,pos,node_size = node_size, node_color=node_color,edge_color=weights,edgelist=edges,width=5.0, edge_cmap=cmap)#,v_min=scale_min,vmax=scale_max)
        #nx.draw(g,pos,with_labels=True,node_size = 10, font_color='k',font_size=4, node_color='y',edge_color='b',edgelist=edges,width=2.0)#, edge_cmap=cmap)
        #plt.savefig('reference_map.pdf')
        if(save==True):
            plt.savefig(fname)
        
        plt.show()
        
        return(g)
        
    def plotPath(self,path,node_color='k',edge_color='b',node_size=50):
        import numpy as np
        import matplotlib.pyplot as plt
        import networkx as nx

        g = nx.Graph()
        for i, coordinate in enumerate(np.asarray(self.unique,float)):
            g.add_node(i, pos = coordinate, label = self.node_labels[i])
        
        pos= nx.get_node_attributes(g,'pos')
        
        path_len = len(path)
        arr = []
        for n in range(path_len-1):
            temp_ = (path[n],path[n+1])
            arr.append(temp_)
        g.add_edges_from(arr)   
        plt.figure(1,figsize=(18,18))
        nx.draw(g,pos,node_size=node_size,node_color=node_color,edge_color=edge_color,width=5) 
        plt.show()
        return(g)










        
        
     
        