#!/usr/bin/python
#coding:utf-8

import os
import json
import numpy as np
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
if __name__ == "__main__":
  wind_data = []
  with open('D:/work/shamo/haiyang/NWP_GBAL_20200804_0300_UV_300mb.JSON', 'r') as windf:
    wind_data = json.load(windf)
  wind_direction, wind_speed = wind_data[0], wind_data[1]
  img_width, img_height = int(wind_speed['header']['nx']), int(wind_speed['header']['ny'])
  wind_direction, wind_speed = np.array(wind_direction['data']).reshape((img_height,img_width)),\
    np.array(wind_speed['data']).reshape((img_height,img_width))
  wind_direction, wind_speed = wind_direction **2, wind_speed**2
  img_data = wind_direction+wind_speed
  img_data = np.sqrt(img_data)
  # img_data = np.array(wind_speed['data']).reshape((img_height,img_width))
  img_data = np.abs(img_data) * 3.6
  # img_data = img_data.T
  print img_width, img_height
  print np.max(img_data)
  fig = plt.figure(figsize=(img_width/100.0,img_height/100.0))
  ax = fig.add_subplot()
  plt.subplots_adjust(top=1,bottom=0,left=0,right=1,hspace=0,wspace=0)
  colors = [[0,11,254],[0,148,207],[9,254,0],[197,161,0],[254,5,0],[181,3,181],[211,106,211],[255,255,255]]
  colors = np.array(colors) / 255.0
  minvalue, maxvalue = 0, 360
  cmap = LinearSegmentedColormap.from_list('mycolor', colors, N=256)
  norm = mpl.colors.Normalize(vmin=minvalue, vmax=maxvalue)
  plt.imshow(img_data,cmap=cmap,norm=norm)       
  # plt.imshow(data,cmap=plt.cm.get_cmap('jet'),norm=cnorm)
  plt.axis('off')  
  plt.savefig('D:/work/shamo/haiyang/NWP_GBAL_20200804_0300_UV_300mb.jpg')