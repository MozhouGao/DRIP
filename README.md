# Downwind road intersection point (DRIP)

### Overview 
DRIPs are estimated by extending a virtual line downwind of a point source location until it intersects the nearest public road. This virtual line represents the best estimate available of a time-averaged plume centreline emanating from the point source under a constant wind direction. The virtual line can extend downwind by a pre-defined distance threshold. 

### Publication 
- This methodology is published in Journal of the Air & Waste Management Association (<a href= "https://www.tandfonline.com/doi/full/10.1080/10962247.2022.2113182">article</a>)

#### Abstract 
Multi-sensor vehicle systems have been implemented in large-scale field programs to detect, attribute, and estimate emissions rates of methane (CH4) and other compounds from oil and gas wells and facilities. Most vehicle systems use passive sensing; they must be positioned downwind of sources to detect emissions. A major deployment challenge is predicting the best measurement locations and driving routes to sample infrastructure. Here, we present and validate a methodology that incorporates high-resolution weather forecast and geospatial data to predict measurement locations and optimize driving routes. The methodology estimates the downwind road intersection point (DRIP) of theoretical CH4 plumes emitted from each well or facility. DRIPs serve as waypoints for Dijkstra’s shortest path algorithm to determine the optimal driving route. We present a case study to demonstrate the methodology for planning and executing a vehicle-based concentration mapping survey of 50 oil and gas wells near Pecos, Texas. Validation was performed by comparing DRIPs with 174 CH4 plumes measured by vehicle surveys of oil and gas wells and facilities in Alberta, Canada. Results indicate median Manhattan distances of 145.8 m between DRIPs and plume midpoints and 160.3 m between DRIPs and peak plume enhancements. A total of 46 (26%) of the plume segments overlapped DRIPs. Locational errors of DRIPs are related to misattributions of emissions sources and discrepancies between modeled and instantaneous wind direction measured when the vehicle intersects plumes. Although the development of the methodology was motivated by CH4 emissions from oil and gas facilities, it should be applicable to other types of point source air emissions from known facilities.

### Demonstration 
DRIPs are demonstrated by using <a href= "https://github.com/MozhouGao/DRIP/blob/main/DRIP_Live_Wind_outside.py"> DRIP_Live_Wind_outside.py </a>
 - This demo is a fictitious survey of 7 emissions sources (restaurants) in Coquitlam, British Columbia, Canada on 25 November 2021. DRIP locations were automatically updated when the local time transitioned from one hour to the next. The driving route was also automatically updated by applying Dijkstra’s algorithm at 1 second intervals, which accounted for route deviations and changes in DRIP locations.
 - A video showing route updates based on vehicle location, time, and changes in DRIP locations from the survey is presented by <a href= "https://doi.org/10.6084/m9.figshare.17131469.v4"> Gao, 2022</a>
  
