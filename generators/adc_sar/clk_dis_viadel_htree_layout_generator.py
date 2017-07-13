
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
import os
import yaml
#import logging;logging.basicConfig(level=logging.DEBUG)

def generate_clkdis_viadel_htree(laygen, objectname_pfix, logictemp_lib, working_lib, grid, pitch_x, num_ways, origin=np.array([0, 0])):
    """generate htree cell """

    pg = grid['pg']
    rg_m1m2 = grid['rg_m1m2']
    rg_m1m2_thick = grid['rg_m1m2_thick']
    rg_m2m3 = grid['rg_m2m3']
    rg_m2m3_basic = grid['rg_m2m3_basic']
    rg_m2m3_thick = grid['rg_m2m3_thick']
    rg_m2m3_thick2 = grid['rg_m2m3_thick2']
    rg_m3m4 = grid['rg_m3m4']
    rg_m3m4_dense = grid['rg_m3m4_dense']
    rg_m3m4_thick2 = grid['rg_m3m4_thick2']
    rg_m4m5 = grid['rg_m4m5']
    rg_m5m6 = grid['rg_m5m6']
    rg_m6m7 = grid['rg_m6m7'] 

    trackm = 12
    #len_h = laygen.grids.get_absgrid_coord_x(gridname=rg_m4m5, x=20.16)
    len_h = laygen.grids.get_absgrid_coord_x(gridname=rg_m4m5, x=pitch_x)
    len_in = laygen.grids.get_absgrid_coord_x(gridname=rg_m4m5, x=2)
    #num_ways = 8
    num_bits = 5
    m_clko = 4
    num_vss_h=4
    num_vdd_h=4

    ##place all viadel and h grids
    viadel = laygen.place(name='I'+objectname_pfix+'VIADEL0', templatename='clk_dis_viadel', gridname=pg, xy=origin, 
            template_libname=working_lib)
    vd_CLKI0_xy = laygen.get_inst_pin_coord(viadel.name, 'CLKI0_'+str(trackm-1), rg_m4m5)[0]
    vd_CLKI1_xy = laygen.get_inst_pin_coord(viadel.name, 'CLKI1_'+str(trackm-1), rg_m4m5)[0]
    htree0 = laygen.place(name='I'+objectname_pfix+'HTREE0', templatename='clk_dis_htree', gridname=pg, xy=origin, 
            template_libname=working_lib)
    ht0_WO_xy = laygen.get_inst_pin_coord(htree0.name, 'WO0_0_0', rg_m4m5)[0]
    ht0_WI_xy = laygen.get_inst_pin_coord(htree0.name, 'WI_0', rg_m4m5)[0]
    #move htree0
    htree0.xy = np.array([(vd_CLKI0_xy[0]-ht0_WO_xy[0])*0.08, (vd_CLKI0_xy[1]-ht0_WO_xy[1])*0.08])
    ht0_WI_xy = np.array([ht0_WI_xy[0]+(vd_CLKI0_xy[0]-ht0_WO_xy[0]), ht0_WI_xy[1]+(vd_CLKI0_xy[1]-ht0_WO_xy[1])])
    htree1 = laygen.place(name='I'+objectname_pfix+'HTREE1', templatename='clk_dis_htree', gridname=pg, xy=origin, 
            template_libname=working_lib)
    ht1_WO_xy = laygen.get_inst_pin_coord(htree1.name, 'WO0_0_0', rg_m4m5)[0]
    ht1_WI_xy = laygen.get_inst_pin_coord(htree1.name, 'WI_0', rg_m4m5)[0]
    #move htree1
    htree1.xy = np.array([(vd_CLKI1_xy[0]-ht1_WO_xy[0])*0.08, (vd_CLKI1_xy[1]-ht1_WO_xy[1])*0.08])
    ht1_WI_xy = np.array([ht1_WI_xy[0]+(vd_CLKI1_xy[0]-ht1_WO_xy[0]), ht1_WI_xy[1]+(vd_CLKI1_xy[1]-ht1_WO_xy[1])])
    #Create input wire
    #ht0_WI_xy = laygen.get_inst_pin_coord(htree0.name, 'WI_0', rg_m4m5)
    #print(ht0_WI_xy)
    #print(ht1_WI_xy)

    ##create input vias and metals
    for i in range(trackm):
        for j in range (trackm):
            laygen.via(None, xy=np.array([ht0_WI_xy[0]+2*i, ht0_WI_xy[1]+2*j]), gridname=rg_m4m5)
            laygen.via(None, xy=np.array([ht1_WI_xy[0]+2*i, ht1_WI_xy[1]+2*j]), gridname=rg_m4m5)

        laygen.route(None, laygen.layers['metal'][5], xy0=np.array([ht0_WI_xy[0]+2*i, ht0_WI_xy[1]]), xy1=np.array([ht0_WI_xy[0]+2*i, ht0_WI_xy[1]+2*(trackm-1)]),
                gridname0=rg_m4m5)
        laygen.route(None, laygen.layers['metal'][5], xy0=np.array([ht1_WI_xy[0]+2*i, ht1_WI_xy[1]]), xy1=np.array([ht1_WI_xy[0]+2*i, ht1_WI_xy[1]+2*(trackm-1)]), 
                gridname0=rg_m4m5)

        laygen.route(None, laygen.layers['metal'][4], xy0=np.array([ht0_WI_xy[0], ht0_WI_xy[1]+2*i]), xy1=np.array([ht0_WI_xy[0]+(len_h*2-2), ht0_WI_xy[1]+2*i]),
                gridname0=rg_m4m5)
        laygen.route(None, laygen.layers['metal'][4], xy0=np.array([ht1_WI_xy[0]+2*(trackm-1), ht1_WI_xy[1]+2*i]), xy1=np.array([ht1_WI_xy[0]-(len_h*2-2), ht1_WI_xy[1]+2*i]), 
                gridname0=rg_m4m5)

        for j in range (trackm):
            laygen.via(None, xy=np.array([ht0_WI_xy[0]+(len_h*2-2)-2*i, ht0_WI_xy[1]+2*j]), gridname=rg_m4m5)
            laygen.via(None, xy=np.array([ht1_WI_xy[0]-(len_h*2-2)+2*i, ht1_WI_xy[1]+2*j]), gridname=rg_m4m5)

        vipx=laygen.route(None, laygen.layers['metal'][5], xy0=np.array([ht0_WI_xy[0]+(len_h*2-2)-2*i, ht0_WI_xy[1]]), xy1=np.array([ht0_WI_xy[0]+(len_h*2-2)-2*i, ht0_WI_xy[1]+len_in]),
                gridname0=rg_m4m5)
        laygen.create_boundary_pin_form_rect(vipx, gridname=rg_m4m5, pinname='CLKIP_'+str(i), layer=laygen.layers['pin'][5], size=2, direction='top', netname='CLKIP')       
        vinx=laygen.route(None, laygen.layers['metal'][5], xy0=np.array([ht1_WI_xy[0]-(len_h*2-2)+2*i, ht1_WI_xy[1]]), xy1=np.array([ht1_WI_xy[0]-(len_h*2-2)+2*i, ht1_WI_xy[1]+len_in]), 
                gridname0=rg_m4m5)
        laygen.create_boundary_pin_form_rect(vinx, gridname=rg_m4m5, pinname='CLKIN_'+str(i), layer=laygen.layers['pin'][5], size=2, direction='top', netname='CLKIN')

    #Create pins
    #set and rst
    RST_xy = laygen.get_inst_pin_coord(viadel.name, pinname='RSTP', gridname=rg_m2m3_basic)
    laygen.pin(name='RSTP', layer=laygen.layers['pin'][2], xy=RST_xy, gridname=rg_m2m3_basic)
    RST_xy = laygen.get_inst_pin_coord(viadel.name, pinname='RSTN', gridname=rg_m2m3_basic)
    laygen.pin(name='RSTN', layer=laygen.layers['pin'][2], xy=RST_xy, gridname=rg_m2m3_basic)

    #CLKCAL
    for i in range(num_ways):
        for j in range(num_bits):
            CAL_xy = laygen.get_inst_pin_coord(viadel.name, pinname='CLKCAL'+str(i)+'<'+str(j)+'>', gridname=rg_m2m3_basic)
            laygen.pin(name='CLKCAL'+str(i)+'<'+str(j)+'>', layer=laygen.layers['pin'][2], xy=CAL_xy, gridname=rg_m2m3_basic)

    #CLKO
    for i in range(num_ways):
        for j in range(m_clko):
            CLKO_xy = laygen.get_inst_pin_coord(viadel.name, pinname='CLKO'+str(i)+'_'+str(j), gridname=rg_m5m6 )
            laygen.pin(name='CLKO'+str(i)+'<'+str(j)+'>', layer=laygen.layers['pin'][5], xy=CLKO_xy, gridname=rg_m5m6, netname='CLKO<'+str(i)+'>')

    #DATAO
    for i in range(num_ways):
        DATAO_xy = laygen.get_inst_pin_coord(viadel.name, pinname='DATAO<'+str(i)+'>', gridname=rg_m3m4 )
        laygen.pin(name='DATAO<'+str(i)+'>', layer=laygen.layers['pin'][3], xy=DATAO_xy, gridname=rg_m3m4, netname='DATAO<'+str(i)+'>')


    ##VDD and VSS pin
    for i in range(num_ways):
        for j in range(num_vss_h):
            vssl_xy = laygen.get_inst_pin_coord(viadel.name, 'VSS0_'+str(i)+'_'+str(j), rg_m3m4_thick2)
            laygen.pin(name='VSS0_'+str(i)+'_'+str(j), layer=laygen.layers['pin'][4], xy=vssl_xy, gridname=rg_m3m4_thick2, netname='VSS')
            vssr_xy = laygen.get_inst_pin_coord(viadel.name, 'VSS1_'+str(i)+'_'+str(j), rg_m3m4_thick2)
            laygen.pin(name='VSS1_'+str(i)+'_'+str(j), layer=laygen.layers['pin'][4], xy=vssr_xy, gridname=rg_m3m4_thick2, netname='VSS')
        for j in range(num_vdd_h):
            vddl_xy = laygen.get_inst_pin_coord(viadel.name, 'VDD0_'+str(i)+'_'+str(j), rg_m3m4_thick2)
            laygen.pin(name='VDD0_'+str(i)+'_'+str(j), layer=laygen.layers['pin'][4], xy=vddl_xy, gridname=rg_m3m4_thick2, netname='VDD')
            vddr_xy = laygen.get_inst_pin_coord(viadel.name, 'VDD1_'+str(i)+'_'+str(j), rg_m3m4_thick2)
            laygen.pin(name='VDD1_'+str(i)+'_'+str(j), layer=laygen.layers['pin'][4], xy=vddr_xy, gridname=rg_m3m4_thick2, netname='VDD') 
    

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

    # library load or generation
    workinglib = 'clk_dis_generated'
    laygen.add_library(workinglib)
    laygen.sel_library(workinglib)
    if os.path.exists(workinglib + '.yaml'):  # generated layout file exists
        laygen.load_template(filename=workinglib + '.yaml', libname=workinglib)
        laygen.templates.sel_library(utemplib)

    #grid
    grid = dict(
        pg = 'placement_basic', #placement grid
        rg_m1m2 = 'route_M1_M2_cmos',
        rg_m1m2_thick = 'route_M1_M2_basic_thick',
        rg_m2m3 = 'route_M2_M3_cmos',
        rg_m2m3_basic = 'route_M2_M3_basic',
        rg_m2m3_thick = 'route_M2_M3_thick',
        rg_m2m3_thick2 = 'route_M2_M3_thick_basic',
        rg_m3m4 = 'route_M3_M4_basic',
        rg_m3m4_dense = 'route_M3_M4_basic',
        rg_m3m4_thick2 = 'route_M3_M4_basic_thick',
        rg_m4m5 = 'route_M4_M5_basic',
        rg_m5m6 = 'route_M5_M6_basic',
        rg_m6m7 = 'route_M6_M7_basic',
        rg_m1m2_pin = 'route_M1_M2_basic',
        rg_m2m3_pin = 'route_M2_M3_basic',
    )
    #parameters
    pitch_x=laygen.get_template_xy(name='clk_dis_viadel_cell', libname=workinglib)[0]
    num_ways=8
    load_from_file=True
    yamlfile_spec="adc_sar_spec.yaml"
    yamlfile_size="adc_sar_size.yaml"
    if load_from_file==True:
        #load parameters
        with open(yamlfile_spec, 'r') as stream:
            specdict = yaml.load(stream)
        with open(yamlfile_size, 'r') as stream:
            sizedict = yaml.load(stream)
        lvl=int(np.log2(specdict['n_interleave']/2))
        num_ways=specdict['n_interleave']

    print(workinglib)

    mycell_list=[]

    cellname='clk_dis_viadel_htree'
    print(cellname+" generating")
    mycell_list.append(cellname)
    laygen.add_cell(cellname)
    laygen.sel_cell(cellname)
    generate_clkdis_viadel_htree(laygen, objectname_pfix='VIADEL_H', logictemp_lib=logictemplib, working_lib=workinglib, grid=grid, pitch_x=pitch_x, num_ways=num_ways)
    laygen.add_template_from_cell()

    print(mycell_list)

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