#!/usr/bin/python
########################################################################################################################
#
# Copyright (c) 2014, Regents of the University of California
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the
# following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following
#   disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the
#    following disclaimer in the documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
# INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
########################################################################################################################

"""ADC library
"""
import laygo
import numpy as np
from math import log
import yaml
import os

def create_power_pin_from_inst(laygen, layer, gridname, inst_left, inst_right):
    """create power pin"""
    rvdd0_pin_xy = laygen.get_inst_pin_coord(inst_left.name, 'VDD', gridname, sort=True)
    rvdd1_pin_xy = laygen.get_inst_pin_coord(inst_right.name, 'VDD', gridname, sort=True)
    rvss0_pin_xy = laygen.get_inst_pin_coord(inst_left.name, 'VSS', gridname, sort=True)
    rvss1_pin_xy = laygen.get_inst_pin_coord(inst_right.name, 'VSS', gridname, sort=True)

    laygen.pin(name='VDD', layer=layer, xy=np.vstack((rvdd0_pin_xy[0],rvdd1_pin_xy[1])), gridname=gridname)
    laygen.pin(name='VSS', layer=layer, xy=np.vstack((rvss0_pin_xy[0],rvss1_pin_xy[1])), gridname=gridname)

def generate_samp_wckbuf(laygen, objectname_pfix, templib_logic, 
                         placement_grid='placement_basic',
                         routing_grid_m3m4='route_M3_M4_basic', 
                         samp_cellname='nsw_24x',
                         inbuf_cellname_list=['inv_8x', 'inv_24x'],
                         outbuf_cellname_list=['inv_4x', 'inv_24x'],
                         space_cellname_list=['space_1x', 'space_2x', 'space_4x'],
                         space_left_m_list=[0, 0, 0],
                         space_right_m_list=[0, 0, 0],
                         origin=np.array([0, 0])):
    """generate a sampler with clock buffers. used when AnalogMOS is not available
    """
    #variable/cell namings
    pg = placement_grid
    rg_m3m4 = routing_grid_m3m4
    tap_name='tap'

    # placement
    itapl=[]
    itapr=[]
    ispl=[]
    ispr=[]
    ispinb=[]
    ispoutb=[]
    # sampler row
    # spacing
    refi = None
    tf = 'R0'
    for spn, spm in zip(space_name, m_space_left_list):
        ispl.append([laygen.relplace(name=None, templatename=spn, gridname=pg, refinstname=refi,
            gridname = pg, refinstname = refi, shape=np.array([nfill_buf_4x, 1]),
                                         direction = 'top', template_libname=templib_logic))
                ifill_buf_4x=laygen.relplace(name = "I" + objectname_pfix + 'SLFILL4X'+str(i), templatename = space_4x_name,
                                         gridname = pg, refinstname = refi, shape=np.array([nfill_buf_4x, 1]),
                                         transform=tf, template_libname=templib_logic)
                refi = ifill_buf_4x.name
        refi=itapl[-1].name
    ispl.append([laygen.replace
    for i in range(num_row):
        if i%2==0: tf='R0'
        else: tf='MX'
        if i==0:
            itapl.append(laygen.place(name="I" + objectname_pfix + 'TAPL0', templatename=tap_name,
                                      gridname=pg, xy=origin, template_libname=templib_logic))
        else:
            itapl.append(laygen.relplace(name = "I" + objectname_pfix + 'TAPL'+str(i), templatename = tap_name,
                                         gridname = pg, refinstname = itapl[-1].name, transform=tf,
                                         direction = 'top', template_libname=templib_logic))
        refi=itapl[-1].name
        #ckbuf
        if i==num_row-1:
            ickbuf0=laygen.relplace(name = "I" + objectname_pfix + 'CKBUF0',
                                          templatename = ckbuf0_name, gridname = pg, refinstname = refi,
                                          transform=tf, template_libname=templib_logic)
            refi=ickbuf0.name
            ickbuf1=laygen.relplace(name = "I" + objectname_pfix + 'CKBUF1',
                                          templatename = ckbuf1_name, gridname = pg, refinstname = refi,
                                          transform=tf, template_libname=templib_logic)
            refi=ickbuf1.name
        elif i==num_row-2:
            ickbuf2=laygen.relplace(name = "I" + objectname_pfix + 'CKBUF2',
                                          templatename = ckbuf0_name, gridname = pg, refinstname = refi,
                                          transform=tf, template_libname=templib_logic)
            refi=ickbuf2.name
            ickbuf3=laygen.relplace(name = "I" + objectname_pfix + 'CKBUF3',
                                          templatename = ckbuf1_name, gridname = pg, refinstname = refi,
                                          transform=tf, template_libname=templib_logic)
            refi=ickbuf3.name
        else:
            if nfill_buf_4x>0:
                ifill_buf_4x=laygen.relplace(name = "I" + objectname_pfix + 'SLFILL4X'+str(i), templatename = space_4x_name,
                                         gridname = pg, refinstname = refi, shape=np.array([nfill_buf_4x, 1]),
                                         transform=tf, template_libname=templib_logic)
                refi = ifill_buf_4x.name
            if nfill_buf_2x>0:
                ifill_buf_2x=laygen.relplace(name = "I" + objectname_pfix + 'SLFILL2X'+str(i), templatename = space_2x_name,
                                         gridname = pg, refinstname = refi, shape=np.array([nfill_buf_2x, 1]),
                                         transform=tf, template_libname=templib_logic)
                refi = ifill_buf_2x.name
            if nfill_buf_1x>0:
                ifill_buf_1x=laygen.relplace(name = "I" + objectname_pfix + 'SLFILL1X'+str(i), templatename = space_2x_name,
                                         gridname = pg, refinstname = refi, shape=np.array([nfill_buf_1x, 1]),
                                         transform=tf, template_libname=templib_logic)
        for j in range(num_bits_row):
            if i*num_bits_row+j < num_bits:
                islice.append(laygen.relplace(name = "I" + objectname_pfix + 'SL' + str(i) + '_' + str(j),
                                              templatename = slice_name, gridname = pg, refinstname = refi,
                                              transform=tf, template_libname=workinglib))
                refi = islice[-1].name
            else:
                #last row
                nfill = laygen.get_template_size(name=islice[0].cellname, gridname=pg, libname=workinglib)[0]
                nfill_4x = int(nfill/4)
                nfill_2x = int((nfill-nfill_4x*4)/2)
                nfill_1x = nfill-nfill_4x*4-nfill_2x*2
                if nfill_4x>0:
                    ifill_4x=laygen.relplace(name = "I" + objectname_pfix + 'SLFILL4X'+str(i*num_bits_row+j), templatename = space_4x_name,
                                             gridname = pg, refinstname = refi, shape=np.array([nfill_4x, 1]),
                                             transform=tf, template_libname=templib_logic)
                    refi = ifill_4x.name
                if nfill_2x>0:
                    ifill_2x=laygen.relplace(name = "I" + objectname_pfix + 'SLFILL2X'+str(i*num_bits_row+j), templatename = space_2x_name,
                                             gridname = pg, refinstname = refi, shape=np.array([nfill_2x, 1]),
                                             transform=tf, template_libname=templib_logic)
                    refi = ifill_2x.name
                if nfill_1x>0:
                    ifill_1x=laygen.relplace(name = "I" + objectname_pfix + 'SLFILL1X'+str(i*num_bits_row+j), templatename = space_2x_name,
                                             gridname = pg, refinstname = refi, shape=np.array([nfill_1x, 1]),
                                             transform=tf, template_libname=templib_logic)
                    refi = ifill_1x.name
        if not m_space_4x==0:
            isp4x.append(laygen.relplace(name="I" + objectname_pfix + 'SP4X'+str(i), templatename=space_4x_name,
                         shape = np.array([m_space_4x, 1]), transform=tf, gridname=pg,
                         refinstname=refi, template_libname=templib_logic))
            refi = isp4x[-1].name
        if not m_space_2x==0:
            isp2x.append(laygen.relplace(name="I" + objectname_pfix + 'SP2X'+str(i), templatename=space_2x_name,
                         shape = np.array([m_space_2x, 1]), transform=tf, gridname=pg,
                         refinstname=refi, template_libname=templib_logic))
            refi = isp2x[-1].name
        if not m_space_1x==0:
            isp1x.append(laygen.relplace(name="I" + objectname_pfix + 'SP1X'+str(i), templatename=space_1x_name,
                         shape=np.array([m_space_1x, 1]), transform=tf, gridname=pg,
                         refinstname=refi, template_libname=templib_logic))
            refi = isp1x[-1].name
        itapr.append(laygen.relplace(name = "I" + objectname_pfix + 'TAPR'+str(i), templatename = tap_name,
                                     gridname = pg, refinstname = refi, transform=tf, template_libname = templib_logic))

    #internal pins
    pdict = laygen.get_inst_pin_coord(None, None, rg_m3m4)
    pdict_m4m5 = laygen.get_inst_pin_coord(None, None, rg_m4m5)

    y0 = pdict[islice[0].name]['I'][0][1]+2
    x1 = laygen.get_inst_xy(name=islice[-1].name, gridname=rg_m3m4)[0]\
         +laygen.get_template_size(name=islice[-1].cellname, gridname=rg_m3m4, libname=workinglib)[0] - 1
    y1_m4m5 = laygen.get_inst_xy(name=islice[-1].name, gridname=rg_m4m5)[1] - 2
    if num_row%2==1:
         y1_m4m5 +=laygen.get_template_size(name=islice[-1].cellname, gridname=rg_m3m4, libname=workinglib)[1]
    #ckbuf route
    [rv0, rclk0] = laygen.route_vh(laygen.layers['metal'][3], laygen.layers['metal'][4], pdict[ickbuf0.name]['I'][0],
                                       pdict[ickbuf0.name]['I'][1]+np.array([4, 1]), rg_m3m4)
    [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], pdict[ickbuf0.name]['O'][0],
                                       pdict[ickbuf1.name]['I'][0],
                                       pdict[islice[num_bits_row*(num_row-1)].name]['CLK'][1][1]-2, rg_m3m4)
    [rv0, rclko0, rv1] = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], pdict[ickbuf1.name]['O'][0],
                                       pdict[islice[num_bits_row*(num_row-1)].name]['CLK'][0],
                                       pdict[islice[num_bits_row*(num_row-1)].name]['CLK'][1][1] , rg_m3m4)
    [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], pdict[ickbuf1.name]['O'][0],
                                       pdict[ickbuf2.name]['I'][0], 
                                       pdict[ickbuf1.name]['O'][0][1]-4, rg_m3m4)
    [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], pdict[ickbuf2.name]['O'][0],
                                       pdict[ickbuf3.name]['I'][0], 
                                       pdict[ickbuf2.name]['O'][0][1], rg_m3m4)
    [rv0, rh0] = laygen.route_vh(laygen.layers['metal'][3], laygen.layers['metal'][4], pdict[ickbuf3.name]['O'][0],
                                       pdict[ickbuf3.name]['O'][0]+np.array([-3,-1]), rg_m3m4)
    [rv0, rclko0] = laygen.route_vh(laygen.layers['metal'][3], laygen.layers['metal'][4], pdict[ickbuf3.name]['O'][0],
                                       pdict[ickbuf3.name]['O'][0]+np.array([2,-1]), rg_m3m4)
    #xy=laygen.get_rect_xy(rclk0.name, rg_m4m5, sort=True)
    #rh0, rclk0 = laygen.route_hv(laygen.layers['metal'][4], laygen.layers['metal'][5], xy[0],
    #                             np.array([xy[0][0]+6-6, y1_m4m5]), rg_m4m5)
    #laygen.create_boundary_pin_from_rect(rclk0, rg_m4m5, 'CLK',
    #                                     laygen.layers['pin'][5], size=6, direction='top')
    laygen.create_boundary_pin_from_rect(rclk0, rg_m4m5, 'CLK',
                                         laygen.layers['pin'][4], size=6, direction='left')
    xy=laygen.get_rect_xy(rclko0.name, rg_m4m5, sort=True)
    for i in range(2):
        rh0, rclko0 = laygen.route_hv(laygen.layers['metal'][4], laygen.layers['metal'][5], xy[0],
                                     np.array([xy[0][0]-2+2*i, y1_m4m5]), rg_m4m5)
        laygen.create_boundary_pin_from_rect(rclko0, rg_m4m5, 'CLKO'+str(i),
                                             laygen.layers['pin'][5], size=6, direction='top', netname='CLKO')
    #clk route
    rclk=[]
    for i in range(1, num_row):
        if (i+1)*num_bits_row < num_bits:
            [rh0, rv0, rclk0] = laygen.route_hvh(laygen.layers['metal'][4], laygen.layers['metal'][3],
                                 pdict[islice[num_bits_row-1].name]['CLK'][1], 
                                 pdict[islice[(i+1)*num_bits_row-1].name]['CLK'][1], 
                                 pdict[islice[0].name]['CLK'][0][0], rg_m3m4)
        else:
            [rh0, rv0, rclk0] = laygen.route_hvh(laygen.layers['metal'][4], laygen.layers['metal'][3],
                                 pdict[islice[num_bits_row-1].name]['CLK'][1], 
                                 pdict[islice[-1].name]['CLK'][1], 
                                 pdict[islice[0].name]['CLK'][0][0], rg_m3m4)
    #pins
    for i in range(num_bits):
        rh0, rin0 = laygen.route_hv(laygen.layers['metal'][4], laygen.layers['metal'][5], pdict_m4m5[islice[i].name]['I'][0],
                                    np.array([pdict_m4m5[islice[i].name]['I'][0][0]+2+2*int(i/num_bits_row), y1_m4m5]), rg_m4m5)
        laygen.create_boundary_pin_from_rect(rin0, rg_m4m5, 'IN<' + str(i) + '>',
                                             laygen.layers['pin'][5], size=6, direction='top')
    for i in range(num_bits):
        rh0, rout0 = laygen.route_hv(laygen.layers['metal'][4], laygen.layers['metal'][5], pdict_m4m5[islice[i].name]['O'][0],
                                     np.array([pdict_m4m5[islice[i].name]['O'][0][0]+2+2*int(i/num_bits_row), 2]), rg_m4m5)
        laygen.create_boundary_pin_from_rect(rout0, rg_m4m5, 'OUT<' + str(i) + '>',
                                             laygen.layers['pin'][5], size=6, direction='bottom')
    # power pin
    pwr_dim=laygen.get_template_size(name=itapl[-1].cellname, gridname=rg_m2m3, libname=itapl[-1].libname)
    rvdd = []
    rvss = []
    if num_row%2==0: rp1='VSS'
    else: rp1='VDD'
    for i in range(0, int(pwr_dim[0]/2)):
        rvdd.append(laygen.route(None, laygen.layers['metal'][3], xy0=np.array([2*i, 0]), xy1=np.array([2*i, 0]), gridname0=rg_m2m3,
                     refinstname0=itapl[0].name, refpinname0='VSS', refinstindex0=np.array([0, 0]),
                     refinstname1=itapl[-1].name, refpinname1=rp1, refinstindex1=np.array([0, 0])))
        rvss.append(laygen.route(None, laygen.layers['metal'][3], xy0=np.array([2*i+1, 0]), xy1=np.array([2*i+1, 0]), gridname0=rg_m2m3,
                     refinstname0=itapl[0].name, refpinname0='VSS', refinstindex0=np.array([0, 0]),
                     refinstname1=itapl[-1].name, refpinname1=rp1, refinstindex1=np.array([0, 0])))
        laygen.pin_from_rect('VDD'+str(2*i-2), laygen.layers['pin'][3], rvdd[-1], gridname=rg_m2m3, netname='VDD')
        laygen.pin_from_rect('VSS'+str(2*i-2), laygen.layers['pin'][3], rvss[-1], gridname=rg_m2m3, netname='VSS')
    for i in range(num_row):
        for j in range(0, int(pwr_dim[0]/2)):
            rvdd.append(laygen.route(None, laygen.layers['metal'][3], xy0=np.array([2*j, 0]), xy1=np.array([2*j, 0]), gridname0=rg_m2m3,
                         refinstname0=itapl[i].name, refpinname0='VDD', refinstindex0=np.array([0, 0]), via0=[[0, 0]],
                         refinstname1=itapl[i].name, refpinname1='VSS', refinstindex1=np.array([0, 0])))
            rvss.append(laygen.route(None, laygen.layers['metal'][3], xy0=np.array([2*j+1, 0]), xy1=np.array([2*j+1, 0]), gridname0=rg_m2m3,
                         refinstname0=itapl[i].name, refpinname0='VDD', refinstindex0=np.array([0, 0]),
                         refinstname1=itapl[i].name, refpinname1='VSS', refinstindex1=np.array([0, 0]), via1=[[0, 0]]))
    for i in range(0, int(pwr_dim[0]/2)):
        rvdd.append(laygen.route(None, laygen.layers['metal'][3], xy0=np.array([2*i+2+1, 0]), xy1=np.array([2*i+2+1, 0]), gridname0=rg_m2m3,
                     refinstname0=itapr[0].name, refpinname0='VSS', refinstindex0=np.array([0, 0]),
                     refinstname1=itapr[-1].name, refpinname1=rp1, refinstindex1=np.array([0, 0])))
        rvss.append(laygen.route(None, laygen.layers['metal'][3], xy0=np.array([2*i+2, 0]), xy1=np.array([2*i+2, 0]), gridname0=rg_m2m3,
                     refinstname0=itapr[0].name, refpinname0='VSS', refinstindex0=np.array([0, 0]),
                     refinstname1=itapr[-1].name, refpinname1=rp1, refinstindex1=np.array([0, 0])))
        laygen.pin_from_rect('VDD'+str(2*i-1), laygen.layers['pin'][3], rvdd[-1], gridname=rg_m2m3, netname='VDD')
        laygen.pin_from_rect('VSS'+str(2*i-1), laygen.layers['pin'][3], rvss[-1], gridname=rg_m2m3, netname='VSS')
    for i in range(num_row):
        for j in range(0, int(pwr_dim[0]/2)):
            rvdd.append(laygen.route(None, laygen.layers['metal'][3], xy0=np.array([2*j+2+1, 0]), xy1=np.array([2*j+2+1, 0]), gridname0=rg_m2m3,
                         refinstname0=itapr[i].name, refpinname0='VDD', refinstindex0=np.array([0, 0]), via0=[[0, 0]],
                         refinstname1=itapr[i].name, refpinname1='VSS', refinstindex1=np.array([0, 0])))
            rvss.append(laygen.route(None, laygen.layers['metal'][3], xy0=np.array([2*j+2, 0]), xy1=np.array([2*j+2, 0]), gridname0=rg_m2m3,
                         refinstname0=itapr[i].name, refpinname0='VDD', refinstindex0=np.array([0, 0]),
                         refinstname1=itapr[i].name, refpinname1='VSS', refinstindex1=np.array([0, 0]), via1=[[0, 0]]))


if __name__ == '__main__':
    laygen = laygo.GridLayoutGenerator(config_file="laygo_config.yaml")

    import imp
    try:
        imp.find_module('bag')
        laygen.use_phantom = False
    except ImportError:
        laygen.use_phantom = True

    tech=laygen.tech
    utemplib = tech+'_microtemplates_dense'
    logictemplib = tech+'_logic_templates'
    laygen.load_template(filename=tech+'_microtemplates_dense_templates.yaml', libname=utemplib)
    laygen.load_grid(filename=tech+'_microtemplates_dense_grids.yaml', libname=utemplib)
    laygen.load_template(filename=logictemplib+'.yaml', libname=logictemplib)
    laygen.templates.sel_library(utemplib)
    laygen.grids.sel_library(utemplib)

    #library load or generation
    workinglib = 'adc_sar_generated'
    laygen.add_library(workinglib)
    laygen.sel_library(workinglib)
    if os.path.exists(workinglib+'.yaml'): #generated layout file exists
        laygen.load_template(filename=workinglib+'.yaml', libname=workinglib)
        laygen.templates.sel_library(utemplib)

    #grid
    pg = 'placement_basic' #placement grid
    rg_m1m2 = 'route_M1_M2_cmos'
    rg_m1m2_thick = 'route_M1_M2_thick'
    rg_m2m3 = 'route_M2_M3_cmos'
    rg_m3m4 = 'route_M3_M4_basic'
    rg_m4m5 = 'route_M4_M5_basic'
    rg_m5m6 = 'route_M5_M6_basic'
    rg_m1m2_pin = 'route_M1_M2_basic'
    rg_m2m3_pin = 'route_M2_M3_basic'

    #display
    #laygen.display()
    #laygen.templates.display()
    #laygen.save_template(filename=workinglib+'_templates.yaml', libname=workinglib)

    mycell_list = []
    num_bits=9
    #load from preset
    load_from_file=True
    yamlfile_spec="adc_sar_spec.yaml"
    yamlfile_size="adc_sar_size.yaml"
    if load_from_file==True:
        with open(yamlfile_spec, 'r') as stream:
            specdict = yaml.load(stream)
        with open(yamlfile_size, 'r') as stream:
            sizedict = yaml.load(stream)
        num_bits=specdict['n_bit']
        m_sarret=sizedict['sarret_m']
        fo_sarret=sizedict['sarret_fo']
    #cell generation (slice)
    cellname='sarretslice'
    print(cellname+" generating")
    mycell_list.append(cellname)
    laygen.add_cell(cellname)
    laygen.sel_cell(cellname)
    generate_sarretslice(laygen, objectname_pfix='DSL0', templib_logic=logictemplib, placement_grid=pg, routing_grid_m3m4=rg_m3m4,
                         m=m_sarret, fo=fo_sarret, origin=np.array([0, 0]))
    laygen.add_template_from_cell()
    #array generation (2 step)
    cellname='sarret_wckbuf' #_'+str(num_bits)+'b'
    print(cellname+" generating")
    mycell_list.append(cellname)
    # 1. generate without spacing
    laygen.add_cell(cellname)
    laygen.sel_cell(cellname)
    generate_sarret2_wckbuf(laygen, objectname_pfix='RET0', templib_logic=logictemplib, placement_grid=pg,
                     routing_grid_m3m4=rg_m3m4, num_bits=num_bits, num_bits_row=int(num_bits/2), m_slice=m_sarret, m_space_4x=0, m_space_2x=0,
                     m_space_1x=0, origin=np.array([0, 0]))
    laygen.add_template_from_cell()
    # 2. calculate spacing param and regenerate
    x0 = laygen.templates.get_template('sarafe_nsw', libname=workinglib).xy[1][0] \
         - laygen.templates.get_template(cellname, libname=workinglib).xy[1][0] \
         - laygen.templates.get_template('nmos4_fast_left').xy[1][0] * 2
    m_space = int(round(x0 / laygen.templates.get_template('space_1x', libname=logictemplib).xy[1][0]))
    m_space_4x = int(m_space / 4)
    m_space_2x = int((m_space - m_space_4x * 4) / 2)
    m_space_1x = int(m_space - m_space_4x * 4 - m_space_2x * 2)
    laygen.add_cell(cellname)
    laygen.sel_cell(cellname)
    generate_sarret2_wckbuf(laygen, objectname_pfix='RET0', templib_logic=logictemplib, placement_grid=pg,
                    routing_grid_m3m4=rg_m3m4, num_bits=num_bits, num_bits_row=int(num_bits/2), m_slice=m_sarret, m_space_4x=m_space_4x,
                    m_space_2x=m_space_2x, m_space_1x=m_space_1x, origin=np.array([0, 0]))
    laygen.add_template_from_cell()

    laygen.save_template(filename=workinglib+'.yaml', libname=workinglib)
    #bag export, if bag does not exist, gds export
    import imp
    try:
        imp.find_module('bag')
        import bag
        prj = bag.BagProject()
        for mycell in mycell_list:
            laygen.sel_cell(mycell)
            laygen.export_BAG(prj, array_delimiter=['[', ']'])
    except ImportError:
        laygen.export_GDS('output.gds', cellname=mycell_list, layermapfile=tech+".layermap")  # change layermapfile