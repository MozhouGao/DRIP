import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import osmnx as ox
import toolbox as dp
import contextily as cx


# read data - site
df = pd.read_csv(r"Coq_source_wind.csv", sep=',')
site = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.lon, df.lat))

site = site.set_crs("EPSG:4326")
site.geometry = site.geometry.to_crs(epsg=26910)

# Plot facilities points
site_lons = list(site.geometry.x)
site_lats = list(site.geometry.y)

# downloading road data, and project road data
G= ox.graph_from_point(
    [49.281388, -122.797455], dist=1500, dist_type='bbox', network_type='drive',simplify=False)
home_node = ox.distance.nearest_nodes(G, -122.797455,49.281388)
G_proj = ox.project_graph(G)
G_con = ox.project_graph(G_proj, to_crs='epsg:26910')
G = G_con


# Get Edges and Nodes
nodes, edges = ox.graph_to_gdfs(G, nodes=True, edges=True)
site_list = site.copy()
roadline = edges.geometry
lon_min, lon_max, lat_min, lat_max = dp.found_frame(site, site)

# find drips 
A = [11,12]
drips = []
for a in A: 
    length = 0.2
    windstring = 'Wind_{}'.format(a)
    drip = dp.predict_drip(length,site,windstring,roadline)
    drips.append(drip)
    
# grab drips coordiantes
DRIP_Xs = []
DRIP_Ys = [] 
for drip in drips: 
    dpx,dpy = dp.extractxy(drip)
    DRIP_Xs.append(dpx)
    DRIP_Ys.append(dpy)
       
# Find nodes 
DRIP_nodes = [] 
for d in drips: 
    Node = [] 
    for dd in d: 
        xx = dd.x 
        yy = dd.y 
        testnode = ox.distance.nearest_nodes(G,xx,yy)
        Node.append(testnode)
    DRIP_nodes.append(Node)

# Figure Set-up 
fig = plt.figure(figsize=(5, 5))
ax1 = fig.add_subplot(2, 1, 1)
ax2 = fig.add_subplot(2, 1, 2)
###################### static data ##############################
# Plot source points
site.plot(ax=ax1, color='blue', marker='s', markersize=35, zorder=2, label = 'Restaurants')
site.plot(ax=ax2, color='blue', marker='s', markersize=200, zorder=2, label = 'Restaurants')
# Plot road data
edges.plot(ax=ax1, color='black', linewidth=0.5, zorder=1)
edges.plot(ax=ax2, color='black', linewidth=1, zorder=1)

###################### dynamic data ############################# 
veh = ax1.plot([], [], '^', color='orange', label="Vehicle",zorder=3,markersize=10)
veh2 = ax2.plot([], [], '^', color='orange', markersize=20, label="Vehicle",zorder=3)
# plot route 
route_line = ax1.plot([],[],'-',color='green',linewidth=3,zorder = 2,label = 'Route' )
route_line2 = ax2.plot([],[],'-',color='green',linewidth=4,zorder = 2,label = 'Route' )
###################### semi-dynamic data ########################
# wind direction changes over time -> different DRIPs
# DRIPs 
dri = ax1.plot([],[],'P', color='red',markersize=10,zorder =2,  label='DRIPs')
dri2 = ax2.plot([],[],'P', color='red',markersize=13,zorder =2,  label='DRIPs')
# wind lines 
# create a line for each wind lines 

##################### frame ######################################
ax1.legend(loc='best',fontsize=15)

#################### basemap ################################### 
cx.add_basemap(ax1,
               crs=site.crs,
               source=cx.providers.CartoDB.Voyager
              )

cx.add_basemap(ax2,
               crs=site.crs,
               source=cx.providers.CartoDB.Voyager
              )

# frame1 
lon_min,lon_max,lat_min,lat_max = dp.found_frame(site,site)
ax1.set_xlim(lon_min-200,lon_max+200)
ax1.set_ylim(lat_min-200,lat_max+200)

# time 
props = dict(boxstyle='round', facecolor='white', alpha=0.5)
timestr = ax1.text(lon_min-150,lat_max+100,'',fontsize=15, bbox=props)

# ax2's axis limite is decided based on loc of vechicle
ax1.set_axis_off()
ax2.set_axis_off()

# animation function.  This is called sequentially
xar = [] 
yar = [] 
tar = [] 
Route_x = [] 
Route_y = [] 
def animate(i):
    traj =pd.read_csv(r"GPS_receiver.csv",sep=',')
    
    x_vals = traj['lons']
    y_vals = traj['lats']
    t_vals = traj['time']

    x1 = x_vals[-1:].iloc[0]
    y1 = y_vals[-1:].iloc[0]
    t1 = t_vals[-1:].iloc[0]
    
    tsr = t1.split(' ')[1].split(':')[0]
    tsr = int(tsr)
    xar = [x1]
    yar = [y1]
    tar.append(tsr)
    
    
    timestr.set_text(t1)
    veh[0].set_xdata(xar)
    veh[0].set_ydata(yar)
    veh2[0].set_xdata(xar)
    veh2[0].set_ydata(yar)
    
    ### route 
    # obtain correct data  
    if len(tar)>2:
        if tar[-1] == 10:
            tdiff = 0
        else: 
            tdiff = 1
        drip_x = DRIP_Xs[tdiff]
        drip_y = DRIP_Ys[tdiff]
        # find out the passed DRIP/remove it from list (plot)
        num = 0 
        idx = [] 
        for ele in zip(drip_x,drip_y):
            x2 = ele[0]
            y2 = ele[1]
            d = ((x1 - x2)**2 + (y1-y2)**2)**0.5
            if d<=20:
                idx.append(num)
            num += 1 
        if len(idx) > 0:
            for index in sorted(idx, reverse=True):
                for dx in DRIP_Xs: 
                    del dx[index]
                for dy in DRIP_Ys:
                    del dy[index]
                for dn in DRIP_nodes:
                    del dn[index]           
        # re-obtain data 
        drip_node = DRIP_nodes[tdiff]
        drip_x = DRIP_Xs[tdiff]
        drip_y = DRIP_Ys[tdiff]
        # remove site that doesn't have drip 
        drip_x = [xx for xx in drip_x if xx != 0]
        drip_y = [yy for yy in drip_y if yy != 0]
        
        if len(drip_node) > 0:
            #plot drip 
            dri[0].set_xdata(drip_x)
            dri[0].set_ydata(drip_y)
            dri2[0].set_xdata(drip_x)
            dri2[0].set_ydata(drip_y)
        
            # path planning 
            orig_node = ox.distance.nearest_nodes(G, x1,y1)
            node_list = drip_node.copy()
            Routes = dp.build_route (G, orig_node,node_list )
            
            Route_x.clear()
            Route_y.clear()
            
            for l in Routes: 
                x,y = l.coords.xy
                Route_x.append(x[0]) 
                Route_x.append(x[1]) 
                Route_y.append(y[0])
                Route_y.append(y[1])
                
            route_line [0].set_xdata(Route_x)
            route_line [0].set_ydata(Route_y)
            route_line2[0].set_xdata(Route_x)
            route_line2[0].set_ydata(Route_y)
        else:
            dri[0].set_xdata([])
            dri[0].set_ydata([])
            dri2[0].set_xdata([])
            dri2[0].set_ydata([])
            orig_node = ox.distance.nearest_nodes(G, x1,y1)
            Routes = dp.build_route (G, orig_node,[home_node])
            Route_x.clear()
            Route_y.clear()
            
            for l in Routes: 
                x,y = l.coords.xy
                Route_x.append(x[0]) 
                Route_x.append(x[1]) 
                Route_y.append(y[0])
                Route_y.append(y[1])
                
            route_line [0].set_xdata(Route_x)
            route_line [0].set_ydata(Route_y)
            route_line2[0].set_xdata(Route_x)
            route_line2[0].set_ydata(Route_y)
            
            
    ax2.set_xlim(min(xar)-70,max(xar) + 70)
    ax2.set_ylim(min(yar)-70,max(yar) + 70)
    

    return veh,route_line,dri

anim = FuncAnimation(fig, animate,interval=1000)
plt.show()
