#!/usr/bin/python3.8
# coding=utf-8
import pandas as pd
import geopandas
import matplotlib.pyplot as plt
import contextily as ctx
import sklearn.cluster
import numpy as nppip
# muzeze pridat vlastni knihovny


def make_geo(df: pd.DataFrame) -> geopandas.GeoDataFrame:
    #Konvertovani dataframe do geopandas.GeoDataFrame se spravnym kodovani

    gdf = geopandas.GeoDataFrame(df, geometry=geopandas.points_from_xy(df["d"], df["e"]), crs="EPSG:5514")
    df_c = gdf.drop(gdf[(gdf.e == -1) | (gdf.d == -1)].index)  #odstraneni radku kde je poloha nehody neznama

    return df_c


def plot_geo(gdf: geopandas.GeoDataFrame, fig_location: str = None,
             show_figure: bool = False):

    #Vykresleni grafu s dvemi podgrafy podle lokality nehody

    gdf_olk = gdf[gdf["region"] == "OLK"]
    gdf_obec = gdf_olk[gdf_olk["p5a"] == 1]
    gdf_mimo_obec = gdf_olk[(gdf_olk["p5a"] == 2) & (gdf_olk["d"] < -495000)]  #odstrani jednu specifickou nehodu ktera kazi graf

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9,9))

    gdf_obec.plot(ax=ax1, markersize=0.2)
    gdf_mimo_obec.plot(ax=ax2, color = "tab:green", markersize=0.2)
   
    ax1.axis("off")
    ax2.axis("off")

    ax1.title.set_text("Nehody v OLK kraji: v obci")
    ax2.title.set_text("Nehody v OLK kraji: mimo obec")

    ctx.add_basemap(ax1, crs=gdf.crs.to_string(), source=ctx.providers.Stamen.TonerLite, alpha=0.9)
    ctx.add_basemap(ax2, crs=gdf.crs.to_string(), source=ctx.providers.Stamen.TonerLite, alpha=0.9)

    fig.savefig(fig_location)

    if show_figure:
        plt.show()


def plot_cluster(gdf: geopandas.GeoDataFrame, fig_location: str = None,
                 show_figure: bool = False):

    """ Vykresleni grafu s lokalitou vsech nehod v kraji shlukovanych do clusteru """

    gdf_c = gdf.drop(gdf[gdf.region != "OLK"].index)  #necha jen nehody z OLK kraje
    gdf_c = gdf_c.reset_index()  #nastavi indexovani zpatky od 0

    gdf_c = gdf_c.set_geometry(gdf_c.geometry).to_crs(epsg=3857)

    gdf_c = gdf_c.loc[:, ('p1', 'geometry')] # extrakce potrebnych sloupcu

    for i in nppip.where(gdf_c.geometry.x >= nppip.finfo(nppip.float64).max):  #smaze vsechny radky, ktere maji Inf hodnoty souradnic
        gdf_c = gdf_c.drop(i)

    coords = nppip.dstack([gdf_c.geometry.x, gdf_c.geometry.y]).reshape(-1, 2)  #vytvoreni matice souradnic pro K-means

    db = sklearn.cluster.KMeans(n_clusters=22).fit(coords) # vytvoreni 22 clusteru

    gdf_c["cluster"] = db.labels_ # prida clustery do dataframe

    gdf2 = gdf_c.dissolve(by="cluster", aggfunc={"p1": "count"}).rename(columns=dict(p1="cnt"))  #urceni velikosti clusteru podle poctu nehod, ktere se v nem nachazeji

    gdf_coords = geopandas.GeoDataFrame(geometry=geopandas.points_from_xy(db.cluster_centers_[:, 0], db.cluster_centers_[:, 1]))  #nastaveni stredovych souradnic clusteru
    gdf_final = gdf2.merge(gdf_coords, left_on="cluster", right_index=True).set_geometry("geometry_y")

    plt.figure(figsize=(9, 9)) 
    ax = plt.gca()  
    ax.axis("off")
    gdf_c.plot(ax=ax, markersize=0.2)
    gdf_final.plot(ax=ax, markersize=gdf_final["cnt"] / 5, alpha = 0.5, column="cnt", legend=True)

    ax.title.set_text("Nehody v OLK kraji")
    ctx.add_basemap(ax, source=ctx.providers.Stamen.TonerLite, alpha=1) 

    plt.savefig(fig_location)

    if show_figure:
        plt.show()


if __name__ == "__main__":
    # zde muzete delat libovolne modifikace
    gdf = make_geo(pd.read_pickle('accidents.pkl.gz'))
    #plot_geo(gdf, "geo1.png", True)
    plot_cluster(gdf, "geo2.png", True)

