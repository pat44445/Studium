# -*- coding: utf-8 -*-
"""
Created on Sun Nov  1 21:27:16 2020

@author: pat4444
"""

import matplotlib.pyplot as plt
import download as DD
import argparse

data_source = DD.DataDownloader().get_list()

"""
Zpracuje pocet nehod zpracovanych kraju za 1 rok
"""
def parse_year(data_source, yr):

    years = data_source[1][3].tolist()
    regs = data_source[1][64].tolist()
    
    
    reg_vals = {}
    
    for i in range(len(years)):
         if years[i][:4] == str(yr):
            if regs[i] not in reg_vals:
                reg_vals[regs[i]] = 0
            else:
                 reg_vals[regs[i]] += 1 
           
    total=[]
    regs=[]
    
    reg_vals = ({k: v for k, v in sorted(reg_vals.items(), key=lambda item: item[1])})
    
    for reg in reg_vals.keys():
        regs.append(reg)
        total.append(reg_vals[reg])
        
   
    total.reverse()
    regs.reverse()
   
    return regs, total

"""
Vykresleni grafu
"""
def plot_stat(data_source, fig_location = None, show_figure = False):
    
    year = 2016
    
    fig = plt.figure( figsize=(8,11))
    fig.suptitle('Počty nehod v jednotlivých krajích',fontsize = '15')
    i = 1
    for year in range(2016, 2021, 1):
        order = 1
        regs, total = parse_year(data_source, year)
        fig.add_subplot(5, 1, i)
        graph = plt.bar(regs, total)
        for rect in graph:
            height = rect.get_height()
            plt.annotate('{}'.format(order),
                        xy=(rect.get_x() + rect.get_width() / 2, height),
                        ha='center', va='bottom',fontsize = '10')
      
            order += 1
            
        plt.title('Rok {}'.format(str(year)), fontsize = '12')
        plt.ylabel('Počet nehod',fontsize = '12')
        
        i += 1

    fig.subplots_adjust(hspace=0.4)
    
    if show_figure:
        fig.show()
        
    if fig_location:
        plt.savefig(fig_location)

   
   
   
    


if __name__== "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--fig_location", help="folder for saveing graph")
    parser.add_argument("--show_figure")
     
    fig_loc = None
    show = False
    args = parser.parse_args()
    
    if args.fig_location:
        fig_loc = args.fig_location
        
    if args.show_figure:
        show = True

    plot_stat(data_source, fig_loc, show)
    
    
    
    
    
    
    
    
    
