#!/usr/bin/python
# coding:utf-8

import json
import numpy as np
import sys
from sys import argv
import math
import os
import datetime
import time
from modules.hdfoper import HDFOper
from modules.dboper import MySqlOper

def computeuv(inputfile, outfile):
    try:
        with open(inputfile, 'r') as inf:
            inputjson = json.load(inf)
    except:
        print 'open input file error'
        return
    direction, speed = np.array(inputjson[0]['data'], dtype=np.float), np.array(inputjson[1]['data'], dtype=np.float)   
    invalid = np.isnan(direction)
    direction[invalid] = 0
    speed[invalid] = 0
    # print direction
    u = np.cos(direction*np.pi/180) * speed
    v = np.sin(direction*np.pi/180) * speed
    u[invalid], v[invalid] = np.nan, np.nan
    
    inputjson[0]['data'],  inputjson[1]['data']= list(u), list(v)
    with open(outfile, 'w') as outf:
        json.dump(inputjson, outf)

def formatuv(u, v, outfile, infile):
    # 将u、v转成一维数组
    u, v = np.array(u), np.array(v)
    u, v = u.astype(float), v.astype(float)
    u, v = u[::4,::4], v[::4,::4]
    u, v = np.round(u,2), np.round(v,2)
    tmpu, tmpv = u[:,0], v[:,0]
    u, v = np.column_stack((u, tmpu)), np.column_stack((v, tmpv))
    ny, nx = np.array(u).shape   
    u, v = u.reshape(1,nx*ny), v.reshape(1,nx*ny)
    u, v = u[0].tolist(), v[0].tolist()
    # print max(u)
    # print min(u)
    # print max(v)
    # print min(v)
    dx, dy = 180.0 / (ny-1), 360.0 / (nx-1)
    # print u
    data = [{'header':{ 
                    'parameterNumberName':'wind direction', 'lo1':0,'lo2':360,'la1':90,'la2':-90,
                    'nx':nx,'ny':ny,'dx':dx,'dy':dy,
                    'productTypeName':infile
                },
            'data':u},               
        {'header':{
                    'parameterNumberName':'wind speed', 'lo1':0,'lo2':360,'la1':90,'la2':-90,
                    'nx':nx,'ny':ny,'dx':dx,'dy':dy,
                    'productTypeName':infile
                },
        'data':v}
    ]

    with open(outfile, 'w') as outf:
        json.dump(data, outf)

def formatdata(data, outfile, infile, pname):
    # 将数据转成一维数组
    data = np.array(data)
    data = data.astype(float)
    data = data[::4,::4]
    data = np.round(data,2)
    tmp_data = data[:,0]
    data = np.column_stack((data, tmp_data))
    ny, nx = np.array(data).shape   
    data = data.reshape(1,nx*ny)
    data = data[0].tolist()
    # print max(u)
    # print min(u)
    # print max(v)
    # print min(v)
    dx, dy = 180.0 / (ny-1), 360.0 / (nx-1)
    # print u
    data = [{'header':{ 
                    'parameterNumberName':pname, 'lo1':0,'lo2':360,'la1':90,'la2':-90,
                    'nx':nx,'ny':ny,'dx':dx,'dy':dy,
                    'productTypeName':infile
                },
            'data':data}]

    with open(outfile, 'w') as outf:
        json.dump(data, outf)

def getuv(infile, outpath):
    try:
        hdffile = HDFOper(infile)
    except BaseException as e: # 读取源文件失败
        print '读取源文件失败'
        return 13
    # print os.path.dirname(os.path.realpath(__file__))
    with open(os.path.dirname(os.path.realpath(__file__)) + '/resource/config.json') as jsonfile: # 加载配置文件
        config = json.load(jsonfile)
    layerlen, success_count = len(config['layerindex']), 0
    outfile = os.path.basename(infile).split('.')[0]
    outjson = ''
    # 处理风场数据
    try:
        udatas, vdatas = hdffile.get_dataset(config['Wind']['u_dataset']), \
            hdffile.get_dataset(config['Wind']['v_dataset']) # 获取u/v数据集
        for index in range(layerlen):
            print 'process %s mb' % config['layername'][index]
            try:
                u, v = udatas[config['layerindex'][index],...], vdatas[config['layerindex'][index],...]
                outjson = os.path.join(outpath, '{0}_UV_{1}mb.JSON'.format(outfile, config['layername'][index]))
                formatuv(u, v, outjson, infile)
                insertodb(config, outjson, 'Wind')
                success_count = success_count + 1
            except BaseException as e:
                print '处理风场 %s mb 出现异常' % config['layername'][index]
    except BaseException as e: # 读取数据集失败
        print '读取风场数据集失败'

    # # 处理10m风速数据
    if 'u_10m_dataset' in config['Wind'] and 'v_10m_dataset' in config['Wind']:
        try:
            # 获取10m u/v数据集
            udatas, vdatas = hdffile.get_dataset(config['Wind']['u_10m_dataset']), \
                hdffile.get_dataset(config['Wind']['v_10m_dataset']) 
            outjson = os.path.join(outpath, '{0}_UV_10m.JSON'.format(outfile))
            formatuv(udatas, vdatas, outjson, infile)
            insertodb(config, outjson, 'Wind')
            success_count = success_count + 1
        except BaseException as e: # 读取数据集失败
            print '读取10m数据集失败'
    
    # 处理温度数据 Temp
    if 'Temp' in config:
        tlev_data = hdffile.get_dataset(config['Temp'])
        for index in range(layerlen):
            print 'process %s tlev' % config['layername'][index]
            try:
                tlev = tlev_data[config['layerindex'][index],...]
                outjson = os.path.join(outpath, '{0}_Temp_{1}mb.JSON'.format(outfile, config['layername'][index]))
                formatdata(tlev, outjson, infile, 'Temp')
                insertodb(config, outjson, 'Temp')
                success_count = success_count + 1
            except BaseException as e:
                print '处理温度 %s mb 出现异常' % config['layername'][index]
    # 处理湿度数据 TPW
    if 'TPW' in config:
        tpwlev_data = hdffile.get_dataset(config['TPW'])
        for index in range(layerlen):
            print 'process %s tpwlev' % config['layername'][index]
            try:
                tpwlev = tpwlev_data[config['layerindex'][index],...]
                outjson = os.path.join(outpath, '{0}_TPW_{1}mb.JSON'.format(outfile, config['layername'][index]))
                formatdata(tpwlev, outjson, infile, 'TPW')
                insertodb(config, outjson, 'TPW')
                success_count = success_count + 1
            except BaseException as e:
                print '处理湿度 %s mb 出现异常' % config['layername'][index]
    # 处理云总总水量数据 MSLP
    if 'MSLP' in config:
        mslp_data = hdffile.get_dataset(config['MSLP'])
        print 'process mslp'
        try:
            outjson = os.path.join(outpath, '{0}_MSLP.JSON'.format(outfile))
            formatdata(mslp_data, outjson, infile, 'MSLP')
            insertodb(config, outjson, 'MSLP')
            success_count = success_count + 1
        except BaseException as e:
            print '处理云中总水量 %s mb 出现异常' % config['layername'][index]
    print '处理结束'
    if success_count == 0:
        return 17
    return 0

def insertodb(config, infile, prodtype):
    # 暂时不需要入库 2020/7/8 lihy
    return
    try:
        infilename, infilepath = os.path.basename(infile), os.path.dirname(infile)
        print '开始在数据库中插入数据...'
        _db = MySqlOper(config['db']['dbip'],config['db']['user'],config['db']['pwd'],config['db']['dbname'])
        _db.connect()
        tmpsplits = infilename.replace('-','').split('_')
        tmpstart = datetime.datetime.strptime(tmpsplits[2]+tmpsplits[3]+'00','%Y%m%d%H%M%S')
        tmpend = tmpstart+datetime.timedelta(hours=1)
        sql = "REPLACE INTO %s (SatID,InstrumentName,ObserveType,ProductName,ProjectType,Resolution,CreatTime,StartTime,EndTime,FilePath,FileName,IsExitFlag) VALUES ('%s','%s','%s', '%s','%s','%s','%s', '%s','%s','%s','%s', '%s')" % \
                (config['db']['tablename'], 'FY4A', 'AGRIX', 'GBAL', prodtype, 'GLL', tmpsplits[5].replace('mb.JSON',''), datetime.datetime.now().strftime('%Y%m%d%H%M%S'), tmpstart.strftime('%Y%m%d%H%M%S'), tmpend.strftime('%Y%m%d%H%M%S'), infilepath, os.path.join(infilepath,infilename),1)
        print sql
        _db.insert_data(sql)
        _db.commit_data()
        _db.close()
        print '在数据库中插入数据成功...'
        time.sleep(1)
    except BaseException as e:
        print '数据插入失败:' + e.args[1]  

if __name__ == '__main__':
    if len(argv) < 3:
        print '参数错误，参数1:输入文件全路径，参数2:输出目录'
        sys.exit(15)
    else:
        returncode = getuv(argv[1], argv[2])
        print returncode
        sys.exit(returncode)
    # computeuv('E:/Data/AMV/FY4A-_AGRI--_N_DISK_1047E_L2-_AMV-_C009_NUL_20180630060000_20180630061459_064KM_V0001.json', 'test.json')
    # if len(argv) < 3:
    #     print 'error.'
    # else:       
    #     computeuv(argv[1], argv[2])