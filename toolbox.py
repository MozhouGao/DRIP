import geopandas as gpd
import geopy
from geopy.distance import distance
from shapely.geometry import LineString
import networkx as nx

def find_DPRIPs (roadline,windline):
    """
    find all intersection points between roads and virtual wind trajectories 
    roadline - road geodataframe  
    windline - virtual wind trajectory geodataframe
    
    """
    DPRIPs=[]
    ID = []
    i = 0 
    for w in windline:
        int_pt=[]
        for r in roadline:
            if w.intersection(r): 
                int_pt.append(w.intersection(r))
        if len(int_pt)!=0:        
            DPRIPs.append(int_pt)
            ID.append(1)
        else: 
            ID.append(-999)
        i = i + 1
    
    return DPRIPs

def predict_drip(length,site,windstring,roadline):
    drips = []
    for i in range(len(site)): 
        row = site.iloc[i]
        lat = row.lat 
        lon = row.lon
        tar = row.geometry
        sx = tar.x 
        sy = tar.y 
        
        w1 = row[windstring]
        # coordinates of origin 
        origin = geopy.Point(lat,lon)
        # find the end point of the line 
        end_p = distance(kilometers=0.2).destination(origin, w1)
        e_lat, e_lon = end_p.latitude, end_p.longitude
        # build downwind lines geopdataframe 
        line = LineString([[lon, lat], [e_lon, e_lat]])
        # create geodataframe
        line_gdf = gpd.GeoDataFrame([line])
        # rename the column 
        line_gdf.rename(columns ={0:"geometry"},inplace=True)
        line_gdf = line_gdf.set_crs("EPSG:{}".format(4326))
        line_gdf.geometry = line_gdf.geometry.to_crs(epsg=26910)
        drip = find_DPRIPs (roadline,line_gdf.geometry)
        
        if len(drip)>0:
            drip = drip[0]
            if len(drip) > 0: 
                Dist = [] 

                for d in drip:
                    tx = d.x 
                    ty = d.y
                    dist = ((sx - tx)**2 + (sy-ty)**2)**0.5
                    Dist.append(dist)

                ndp = drip[Dist.index(min(Dist))]
                drips.append(ndp)

            else: 
                drips.append(0)
    return drips 

def found_frame(source,DRIPs):
    """
    zoomed map based on correct coordinate system, make
    make sure both geodataframes have same projection system
    Source: source geodataframe 
    DRIPs: Drips geodataaframe 
    """
    All_site_lon = source.geometry.x
    All_site_lat = source.geometry.y

    All_drip_lon = DRIPs.geometry.x
    All_drip_lat = DRIPs.geometry.y
    
    lon_max = 0
    lon_min = 0 
    if max(All_site_lon) >= max(All_drip_lon): 
        lon_max = max(All_site_lon)
    else:
        lon_max = max(All_drip_lon)

    if min(All_site_lon) <= min(All_drip_lon): 
        lon_min = min(All_site_lon)
    else:
        lon_min = min(All_drip_lon)

    lat_max = 0 
    lat_min = 0 
    if max(All_site_lat) >= max(All_drip_lat): 
        lat_max = max(All_site_lat)
    else:
        lat_max = max(All_drip_lat)

    if min(All_site_lat) <= min(All_drip_lat): 
        lat_min = min(All_site_lat)
    else:
        lat_min = min(All_drip_lat)
        
    return lon_min,lon_max,lat_min,lat_max


def extractxy(drips):
    DRIP_x = [] 
    DRIP_y = [] 
    for xy in drips: 
        x = xy.x 
        y = xy.y 
        
        DRIP_x.append(x)
        DRIP_y.append(y)
        
    return DRIP_x,DRIP_y 

    
    
def build_route (G,orig_node,nodes_list,): 
    """
    G: graph 
    orig_node: original nodes 
    nodes_list:list of nodes 
    """
    Routes =[]
    nodes_list = [i for i in nodes_list if i != 0]
    while len(nodes_list) != 0: 
        sidx = find_nearest_site(nodes_list,orig_node,G)
        target_node = nodes_list[sidx]        
        route_node = nx.dijkstra_path(G=G, source=orig_node, target=target_node, weight='travel_time')
        if len(route_node) > 1:          
            # correct geomerty shape of road  
            lines = node_list_to_path(G, route_node)

            for l in lines:
                route_line = LineString(l)
                Routes.append(route_line)
        
        orig_node = target_node
        #print("route created for {}".format(orig_node))
        nodes_list.pop(sidx)
        
    return Routes

def find_nearest_site(site_node_list,orig_node,G): 
    estimeated_arrival_time = [] 
    for site_node in site_node_list:
        if site_node != 0:
            travel_time = nx.shortest_path_length(G, orig_node, site_node, weight='travel_time')
            estimeated_arrival_time.append(travel_time)
    nidx = estimeated_arrival_time.index(min(estimeated_arrival_time))
    return nidx 
    
def node_list_to_path(G, node_list):
    """
    Given a list of nodes, return a list of lines that together
    follow the path
    defined by the list of nodes.
    Parameters
    ----------
    G : networkx multidigraph
    route : list
        the route as a list of nodes
    Returns
    -------
    lines : list of lines given as pairs ( (x_start, y_start), 
    (x_stop, y_stop) )
    """
    edge_nodes = list(zip(node_list[:-1], node_list[1:]))
    lines = []
    for u, v in edge_nodes:
        e = G.get_edge_data(u, v)
        if e != None:
            # if there are parallel edges, select the shortest in length
            data = min(e.values(), 
                       key=lambda x: x['length'])
            # if it has a geometry attribute
            if 'geometry' in data:
                # add them to the list of lines to plot
                xs, ys = data['geometry'].xy
                lines.append(list(zip(xs, ys)))
            else:
                # if it doesn't have a geometry attribute,
                # then the edge is a straight line from node to node
                x1 = G.nodes[u]['x']
                y1 = G.nodes[u]['y']
                x2 = G.nodes[v]['x']
                y2 = G.nodes[v]['y']
                line = [(x1, y1), (x2, y2)]
                lines.append(line)
    return lines
   