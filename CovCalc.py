# -*- coding: utf-8 -*-
"""
Created on Wed Oct  7 09:12:48 2015

@author: david
"""

import os

import numpy as np

import json

import matplotlib.pyplot as plt

import fractions

class Sensor():
    def __init__(self,
                 indict):                       
        
        self.sensor = indict
        
        self.sensor['xps'] = self.sensor['xs'] / self.sensor['xp']
        
        self.sensor['yps'] = self.sensor['ys'] / self.sensor['yp']
        
        self.sensor['ds'] = np.sqrt(np.power(self.sensor['xs'],2)+np.power(self.sensor['ys'],2))    
    
        print self.sensor

class ViewCalculator():
                         
    def __init__(self,
                 sensor_dict,
                 lens_dict): 
        self.s = sensor_dict
        
        self.l = lens_dict
        
        print 'vc',self.l
        
    def angle(self,
              d,
              m=None):
                  
        print 'ANgle M', m
        
        if m is None:
            angle = 2*np.arctan(d/(2*self.l['fl']))
            
        else:
            
            angle = 2*np.arctan(d/(2*(np.dot(self.l['fl'],1+m))))
            print angle
        
        return angle
    
    def mag(self,
            distance):
                
        #m = self.l['fl']/(distance*1000-self.l['fl'])
                
        m = self.l['fl']/(distance*1000-self.l['fl'])
        
        return m
        
    def ifov(self,
             m=0):
         
        print 'IFOV M',m
                 
        if self.s['xps'] > self.s['yps']:
            ifov = self.angle(self.s['xps'],m=m)
        else:
            ifov = self.angle(self.s['yps'],m=m)
        
        return ifov
     
    def spatial_res(self,
                    distance):
        
        m = self.mag(distance)
        
        print 'MAG',m
        
        ifov_rad = self.ifov(m=m)
        
        
        spatial_res = distance*ifov_rad
        
        return spatial_res
        
    def footprint(self,
                  distance):
                      
        hfov_rad = self.angle(self.s['xs'])
        
        
        vfov_rad = self.angle(self.s['ys'])
        
        print 'FOV',np.degrees(hfov_rad),np.degrees(vfov_rad)
        
        return ((distance*hfov_rad),(distance*vfov_rad))
    
  
class TestCamera():
    def __init__(self):
        self.camera = {'name':'Nikon D5000',
                       'xs':23.6,
                       'ys':15.8,
                       'xp':4928,
                       'yp':3264}

                       
class TestLens():
    def __init__(self):
        
        self.lens = {'fl':18}
        

class CalcFrameSizes():
    def __init__(self,
                 w,
                 h,
                 min_width):

        if h > w:
            width = h
            height = w

        else:
            width = w
            height = h
            
        print (height,width)

        ratio = fractions.Fraction(height,width).limit_denominator()


        ratio_w = ratio._denominator

        ratio_h = ratio._numerator


        print (ratio_w, ratio_h)

        initial_widths = []

        self.frame_sizes = []

        for i in range(min_width, width+1):
            if i % ratio_w == 0:
                initial_widths.append(i)

        for initial_width in initial_widths:
            initial_height = int(initial_width/ratio_w)*ratio_h

            if height % ratio_h == 0:
                print (initial_width, initial_height)
                self.frame_sizes.append((initial_width,initial_height))

        if len(self.frame_sizes)>15:
            selected_frames = []
            step = int(len(self.frame_sizes)/15)

            print ('STEP',step)

            current = 0

            for i in range(0,16):
                if current < len(self.frame_sizes):
                    if i == 0:
                        selected_frames.append(self.frame_sizes[0])

                        current=current+step

                    elif i == 15:
                        selected_frames.append(self.frame_sizes[-1])



                    else:
                        selected_frames.append(self.frame_sizes[current])
                        current = current+step


            self.frame_sizes = selected_frames


        self.frames_mp = []
        for resolution in self.frame_sizes:
            mp = float(resolution[0]*resolution[1])/1000000
            self.frames_mp.append(mp)
            
            
class FramesPerArea():
     def __init__(self,
                 target_area,
                 footprint_area,
                 overlap = 0.8):
                     
      self.n_frames = target_area/(footprint_area*overlap)       
      
      print self.n_frames

if __name__ == '__main__':
    c = TestCamera().camera
    
    frames = CalcFrameSizes(c['xp'],c['yp'],min_width=800)
    
    colours = ['#D39A1D',
               '#C8901F',
               '#BE8622',
               '#B47C25',
               '#AA7228',
               '#A0682B',
               '#965E2D',
               '#8C5430',
               '#824B33',
               '#784136',
               '#6E3739',
               '#643D3B',
               '#5A233E',
               '#501941',
               '#460F44',
               '#3C0647']
    
    count = 0
    
    print len(frames.frame_sizes)
    
    
    fig, axes = plt.subplots(nrows=2, sharex=True)
    
    #ax2 = ax1.twinx()
    
    axes[0].set(xlabel=r'Distance ($m$)')

    axes[1].set(xlabel=r'Distance ($m$)')
    
    axes[0].set_ylabel(r'Ideal Spatial Reolution ($mm$)')
    
    axes[1].set_ylabel(r'Coverage ($m^2$)')
    
    axes[0].set_xlim(left=1, right=20)
    
    for frame in frames.frame_sizes:
        
        
        cam= c
        
        cam['xp']=frame[0]
        cam['yp']=frame[1]
        
        
        print 'CAM',cam
        
        camera = Sensor(cam)    
        
        lens = TestLens().lens
        
        view = ViewCalculator(camera.sensor, lens)
        
        #print view.angle(camera.sensor['ds'])
        
        #print np.degrees(view.angle(camera.sensor['ds']))
        
        spatial_res =[]
        
        for distance in np.linspace(1,20, num=20):
            spatial_res.append((distance,view.spatial_res(distance)))
    
            #¤print distance,np.degrees(view.angle(camera.sensor['ds'], m=view.mag(distance))), np.dot(lens['fl'],1+view.mag(distance))
            
            
        data  = np.asarray(spatial_res)  
    
  
    
        axes[0].plot(data[:,0],data[:,1]*1000, color=colours[count])
        
        count=count+1
    
    areas=[]
    
    for distance in np.linspace(1,20, num=20):
        footprint = ViewCalculator(Sensor(c).sensor, TestLens().lens).footprint(distance)
        
        print footprint[0],footprint[1]        
        
        
        areas.append((distance,footprint[0]*footprint[1]))
    
        
    areas = np.asarray(areas)
    
    axes[1].plot(areas[:,0],areas[:,1])    
    
    
    
    axes[0].set(title='Spatial resolution')
    axes[1].set(title='Areal field of view')    
    
    
    
    fig.show()
    
    for area in areas:
        nframes = FramesPerArea(9, areas[:,1]).n_frames
        
        
        print ('Distance %s Number of frames %s' %(areas[:,0],nframes))
    
    print 
    print frames.frames_mp
        
    #print spatial_res
    