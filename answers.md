# Aussgnment 2: GRASS GIS

## 1 Create location

Create new location letting GRASS GIS determine the EPSG from the GeoTiff file.

## 2 Import data

### 2.1 Import motorways

```
v.import input=A2_GRASS_GIS\data\motorways.shp
```

### 2.2 Import adminstrative districts

Import the Shapefile.
```
v.in.ogr input=A2_GRASS_GIS\data\gadm28_adm2_germany.shp output=GADM where=""ID_1" = "1"" location=TEMP
```

### 2.2 Import adminstrative districts

Import the Shapefile filtered to Baden-Württemberg into a new location, then project the temporary location to our main location.
```
v.in.ogr input=A2_GRASS_GIS\data\gadm28_adm2_germany.shp output=GADM where=""ID_1" = "1"" location=TEMP
v.proj location=TEMP mapset=PERMANENT input=GADM output=GADM --overwrite
```

### 2.3 Import GHS layer

THe layer was imported during the creation of the location.

## 3 Calculate population

### 3.1 Set the region

```
g.region vector=GADM
```

### 3.2 Rasterize the districts

Rasterize vector layer, assigning the attribute value `OBJECTID` to the cells
```
v.to.rast input=GADM@PERMANENT output=BW use=attr attribute_column=OBJECTID
```

### 3.3 Calculate the population of each district

Using the zones (`base`) from our district layer we sum up the population
```
r.stats.zonal base=BW@PERMANENT cover=GHS_POP_E2015_GLOBE_R2019A_54009_250_V1_0_18_3@PERMANENT method=sum output=EW_BW
```

### 3.4. Evaluate the population estimate

```
r.stats input=EW_BW@PERMANENT
```

Using the `Query raster/vector maps` tool the following values were extracted:


Mannheim 287 745 (official: 309 370)\
Heidelberg 152 837 (official: 160 355)

Which shows that the calculated values are lower than the offical numbers.

## 4 Calculate total population living within 1km of motorways

### 4.1 Buffer the motorway
```
v.buffer input=motorways@PERMANENT output=motorways_buf distance=1000
```

### 4.2 Rasterize the motorway
```
v.to.rast input=motorways_buf@PERMANENT output=motorway_rast use=val
```

### 4.3 Calculate the population
```
r.stats.zonal base=motorway_rast@PERMANENT cover=GHS_POP_E2015_GLOBE_R2019A_54009_250_V1_0_18_3@PERMANENT method=sum output=pop_motorway
```

### 4.4 Extract result
```
r.stats -n input=pop_motorway@PERMANENT
```