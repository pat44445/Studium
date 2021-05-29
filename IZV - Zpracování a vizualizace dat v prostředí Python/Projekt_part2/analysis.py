#!/usr/bin/env python3.8
# coding=utf-8

from matplotlib import pyplot as plt
import pandas as pd
import seaborn as sns
import numpy as np
import os, sys
# muzete pridat libovolnou zakladni knihovnu ci knihovnu predstavenou na prednaskach
# dalsi knihovny pak na dotaz
# Ukol 1: nacteni dat
def get_dataframe(filename: str, verbose: bool = False) -> pd.DataFrame:
      
        df = pd.read_pickle(filename, compression= 'gzip')

        orig_size = df.memory_usage(deep = True).sum()

        df.rename(columns={'p2a': 'date'}, inplace=True)
        df['date'] = pd.to_datetime(df['date'])


        # prevod na kategorical krom date a region
        for i in df:
            if i == 'date' or i == 'region': 
                continue
            else:
                df[i] = df[i].astype('category')
             
        new_size = df.memory_usage(deep = True).sum()

        if verbose:
            print('orig_size=' + str(round(orig_size / 1048576, 2)) + ' MB')
            print('new_size=' + str(round(new_size / 1048576, 2)) + ' MB')

       
        return df
        
# Ukol 2: následky nehod v jednotlivých regionech
def plot_conseq(df: pd.DataFrame, fig_location: str = None,
                show_figure: bool = False):
    
    col= df.region.unique()

    dead = []
    heavy_injured = []
    light_injured = []
    total = []

    # prevedeni typu categorical na int aby se dal udelat sum()
    df['p13a'] =  df['p13a'].astype('int')
    df['p13b'] =  df['p13b'].astype('int')
    df['p13c'] =  df['p13c'].astype('int')

    # pro kazdy kraj zjisti pocet mrtvych, tezce zranenych , lehce zranenych a celkovy pocet nehod
    for i in col:
        dead.append(df.loc[df['region'] == i, 'p13a'].sum())
        heavy_injured.append(df.loc[df['region'] == i, 'p13b'].sum())
        light_injured.append(df.loc[df['region'] == i, 'p13c'].sum())
        total.append(df.loc[df['region'] == i, 'p1'].count())

    # podgraf mrtvi
    df_dead = pd.DataFrame({'dead': dead }, col)
    df_dead = df_dead.sort_values(by=['dead']).iloc[::-1]

    # podgraf tezce zraneni
    df_h_injured = pd.DataFrame({'heavy_injured': heavy_injured }, col)
    df_h_injured = df_h_injured.sort_values(by=['heavy_injured']).iloc[::-1]

    # podgraf lehce zraneni
    df_l_injured = pd.DataFrame({'light_injured' : light_injured }, col)
    df_l_injured = df_l_injured.sort_values(by=['light_injured']).iloc[::-1]

    # podgraf celk. pocet nehod
    df_total = pd.DataFrame({'total' : total }, col)
    df_total = df_total.sort_values(by=['total']).iloc[::-1]



    # graf - 4 radky, 1 sloupec, figsize = A4
    fig, ax = plt.subplots(4, 1, figsize=(8,11))

    #vykresleni grafu
    ax_color = df_dead.plot.bar(ax=ax[0])
    ax_color.set_facecolor("#c7f6ff")
    ax_color = df_h_injured.plot.bar(ax=ax[1])
    ax_color.set_facecolor("#c7f6ff")
    ax_color = df_l_injured.plot.bar(ax=ax[2])
    ax_color.set_facecolor("#c7f6ff")
    ax_color = df_total.plot.bar(ax=ax[3])
    ax_color.set_facecolor("#c7f6ff")

    fig.subplots_adjust(hspace=0.3)

    fig.savefig(fig_location)

    if show_figure:
        fig.show()



#p53 - skoda ve stokorunach

# Ukol3: příčina nehody a škoda
def plot_damage(df: pd.DataFrame, fig_location: str = None,
                show_figure: bool = False):

    col = ['PHA', 'OLK', 'KVK', 'JHM'] #vybrane kraje

    df['p12'] =  df['p12'].astype('int')
    df['p53'] =  df['p53'].astype('int')

    pricina = df.p12.unique()
  
    #cenove intervaly
    price = [0, 500, 2000, 5000, 10000, 100000]
   

    fig, ax = plt.subplots(2, 2, figsize=(11,9))


    for region in col:

        df2 = df[df['region'] == region]

        if region == col[0]:
            x = 0
            y = 0
        elif region == col[1]:
            x = 0 
            y = 1
        elif region == col[2]:
            x = 1 
            y = 0
        else:
            x = 1
            y = 1

       
        tmp = [ [], [], [], [], [], []  ]

        # jedna sestice typu nehod pro kazdy cenovy interval
        for i in range(len(price)-1):
            df100 = df2[ (df2['p12'] == 100) & ((df2['p53'] >= price[i]) & (df2['p53'] <= price[i+1]))]
            tmp[0].append(len(df100.index)) 

            df200 = df2[ ((df2['p12'] > 200) & (df2['p12'] < 210)) & ((df2['p53'] >= price[i]) & (df2['p53'] <= price[i+1]))]
            tmp[1].append(len(df200.index)) 
            
            df300 = df2[ ((df2['p12'] > 300) & (df2['p12'] < 312)) & ((df2['p53'] >= price[i]) & (df2['p53'] <= price[i+1]))]
            tmp[2].append(len(df300.index)) 

            df400 = df2[ ((df2['p12'] > 400) & (df2['p12'] < 415)) & ((df2['p53'] >= price[i]) & (df2['p53'] <= price[i+1]))]
            tmp[3].append(len(df400.index)) 

            df500 = df2[ ((df2['p12'] > 500) & (df2['p12'] < 517)) & ((df2['p53'] >= price[i]) & (df2['p53'] <= price[i+1]))]
            tmp[4].append(len(df500.index))

            df600 = df2[ ((df2['p12'] > 600) & (df2['p12'] < 616)) & ((df2['p53'] >= price[i]) & (df2['p53'] <= price[i+1]))]
            tmp[5].append(len(df600.index)) 


        # dataframe pro kazdy podgraf
        df_graph = pd.DataFrame({   'nezavinene ridicem': tmp[0], 
                                    'neprimerena rychlost jizdy': tmp[1],
                                    'nespravne predjizdeni':  tmp[2],
                                    'nedani prednosti v jizde':  tmp[3],
                                    'nespravny zpusob jizdy': tmp[4],
                                    'technicka zavada vozidla': tmp[5]
                                }, index = ['<50', '50-200', '200-500', '500-1000', '>1000'])

        
       
        
        lab = df_graph.plot.bar(ax=ax[x][y], logy = True, title = region, rot=0, legend = False)
        lab.set(xlabel='Škoda [v tis Kč]', ylabel='Počet nehod')


    # jedna legenda pro vsechny podgrafy
    legend_str=['nezavinene ridicem', 'neprimerena rychlost jizdy', 'nespravne predjizdeni',
                'nedani prednosti v jizde', 'nespravny zpusob jizdy', 'technicka zavada vozidla']
    fig.legend(     
                labels=legend_str,   
                loc="center right",   
                borderaxespad=0.2,    
                title="Typy nehod"  )
      
    fig.subplots_adjust(right=0.78, hspace = 0.3)
    fig.savefig(fig_location)

    if show_figure:
        fig.show()



# Ukol 4: povrch vozovky
def plot_surface(df: pd.DataFrame, fig_location: str = None,
                 show_figure: bool = False):
    pass


if __name__ == "__main__":
    
    # zde je ukazka pouziti, tuto cast muzete modifikovat podle libosti
    # skript nebude pri testovani pousten primo, ale budou volany konkreni ¨
    # funkce.
    #df = get_dataframe('D:\\Stazene\\accidents.pkl.gz', True)
    #plot_conseq(df, fig_location="01_nasledky.png", show_figure=True)
    #plot_damage(df, "02_priciny.png", True)
    plot_surface(df, "03_stav.png", True)

