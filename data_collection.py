# -*- coding: utf-8 -*-
"""
Created on Thu Apr 27 16:06:07 2017

@author: James
"""

#loop/update every hour and collect congestion data for all available segments

import pandas as pd
import numpy as np
import time
import CongestionNetwork

query='https://data.cityofchicago.org/resource/8v9j-bter.csv?%24limit=5000&%24%24app_token=1oBcClovBSmSkEGPHggrWWW6x'


backup_file = 'last_values_backup.csv'
backup_data = pd.read_csv(backup_file)
start_over = False #change to true to overwrite data

total_len = 1257
if(start_over == True):
    last_values = [-1]*total_len
else:
    last_values = backup_data['congestion'].values

test = False
hour = 0
while(True):
    print(hour,time.localtime())
    current_day = time.localtime()[2]
    current_hour = time.localtime()[3]
    current_minute = time.localtime()[4]
    query='https://data.cityofchicago.org/resource/8v9j-bter.csv?%24limit=5000&%24%24app_token=1oBcClovBSmSkEGPHggrWWW6x'
    usecols = ['segmentid','_traffic']
    raw_data = pd.read_csv(query,dtype='str',usecols=usecols)
    cong_values = raw_data['_traffic'].values
    seg_ids = raw_data['segmentid'].values
    missing_idx = np.where(cong_values==-1)[0]  

    segment_values = raw_data['segmentid'].values
    missing_segs = segment_values[missing_idx]
    
    temp_cong_array = []
    for i in range(total_len):
        if(cong_values[i] != -1):
            temp_cong_array.append(cong_values[i])
            last_values[i] = cong_values[i]
        else:
            temp_cong_array.append(last_values[i])
    
    print('missing count:',temp_cong_array.count(str(-1)))
    print('available:',(total_len -temp_cong_array.count(str(-1))))
    
    
    Chicago = CongestionNetwork.Network(query=query)
    img_fname = 'img_{0}_{1}_{2}.png'.format(current_day,current_hour,current_minute)
    g = Chicago.plotNetwork(save=True,fname=img_fname)
    
    time_series_file_name = 'output_{0}_{1}_{2}.csv'.format(current_day,current_hour,current_minute)
    file_name = 'last_values.csv'
    output_stack = np.column_stack((seg_ids,temp_cong_array))
    output_df = pd.DataFrame(output_stack,columns=['segment','congestion'])
    out_csv = output_df.to_csv(file_name)
    time.sleep(900) #10 minutes




