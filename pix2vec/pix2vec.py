"""Main module."""

import kalasiris as isis
import csv
import tempfile, os, sys
from osgeo import ogr,osr
import csv
import argparse
import string
import logging

from . import CPT_FIELDS, GCS_DICT

log = logging.getLogger('test')
log.setLevel(logging.DEBUG)

class Cube:
    def __init__(self,isis_cube):
        InsID = isis.getkey_k(isis_cube, 'Instrument', 'InstrumentId')
        samples = isis.getkey_k(isis_cube,'Dimensions','Samples')
        lines = isis.getkey_k(isis_cube,'Dimensions','Lines')
        target = isis.getkey_k(isis_cube,'Instrument','TargetName')
        self.id = InsID
        self.lines = int(lines)
        self.samples = int(samples)
        self.fname = isis_cube
        self.target = target

class GndPixels:
    '''
    a single ground pixel object
    '''
    def __init__(self,cube,vect_out,s0,s1,l0,l1):
        self.file = tempfile.NamedTemporaryFile()
        self.cptfname =  os.path.join(tempfile.mkdtemp(), 'cpt.csv')
        #self.cptfname =  'cpt.csv'
        self.coordlistfname =  os.path.join(tempfile.mkdtemp(), 'coords.lst')
        #self.coordlistfname = 'coords_tmp.lst'
        self.s0 = s0
        self.s1 = s1 + 1
        self.l0 = l0
        self.l1 = l1 + 1
        self.cube = cube
        #
        self.ds = None          # Datasource
        self.layer = None       # Layer
        self.layername =  "spectrometer" # Layer
        self.srs = osr.SpatialReference()
        self.srs.SetFromUserInput(GCS_DICT[cube.target])

        #self.write_all()
        #self.poly = self.get_poly()
        self.write_coordlist()
        self.write_vertex()

        self._open_ds(vect_out)
        self._layer_out()
        self.add_gndpixel_features()
        self._write_ds()
        #self.get_poly()
    def write_coordlist(self):
        with open(self.coordlistfname, 'w', newline='') as csvfile:
            clwriter = csv.writer(csvfile, delimiter=',')
            for i in range(self.l0,self.l1):
                for j in range(self.s0,self.s1):
                    clwriter.writerow((j-0.5,i-0.5)) # 1
                    clwriter.writerow((j+0.5,i-0.5)) # 2
                    clwriter.writerow((j+0.5,i+0.5)) # 3
                    clwriter.writerow((j-0.5,i+0.5)) # 4
                    clwriter.writerow((j-0.5,i-0.5)) # 5 -> 1
                    clwriter.writerow((j,i))         # 6 center
        sys.stdout.write("wrote coordlist %s\n"%self.coordlistfname)
    def write_vertex(self):
        '''
        write the vales for the vertices
        '''
        sys.stdout.write("computing campt from %s\n"%self.coordlistfname)
        p = isis.campt(self.cube.fname,usecoordlist=True,coordlist=self.coordlistfname,format='FLAT',to=self.cptfname,coordtype='image')
        sys.stdout.write("campt done!\n")

    def _open_ds(self,vect_output):
        # Create the output Layer
        #mp = ogr.Geometry(ogr.wkbMultiPolygon)
        # Add an ID field

        outDriver = ogr.GetDriverByName("GPKG")
        outDataSource = outDriver.CreateDataSource(vect_output)
        self.ds = outDataSource

    def _layer_out(self):

        # create the spatial reference system, WGS84
        


        self.layer = self.ds.CreateLayer( self.layername , self.srs, geom_type=ogr.wkbPolygon)

        for k in CPT_FIELDS.keys():
            this_field = ogr.FieldDefn(k, CPT_FIELDS[k])
            self.layer.CreateField(this_field)




    def add_gndpixel_features(self):
        '''
		Adds the features
		'''
        with open(self.cptfname, 'r') as fp:
            row_count = len(fp.readlines()) - 1
        fp.close()
        with open( self.cptfname , newline='') as f:
            reader = csv.DictReader(f,delimiter=',')

            featureDefn = self.layer.GetLayerDefn()
            for row in reader:
            # Create the feature and set values
                feature = ogr.Feature(featureDefn)

                if reader.line_num <= row_count-4:
                    ring = ogr.Geometry(ogr.wkbLinearRing)
                    for r in range(5):
                    #print("line %d of %d\n"%(reader.line_num,row_count))
                        log.debug('This message should appear on the console')
                        lat=float(row['PlanetocentricLatitude'])
                        lng=float(row['PositiveEast360Longitude'])
                        ring.AddPoint(lng,lat)
                        row = next(reader)

                    #for f in FIELDS:
                    #       v = float(row[f['field']])
                    #       #feature.SetField(f,v)

                    ''' 
                    sample_no = float(row['Sample'])
                    line_no = float(row['Line'])
                    if row['LocalRadius'] != 'Null':
                        radius = float(row['LocalRadius'])
                    else: radius = None
                    if row['PixelValue'] != 'Null':
                        value = float(row['PixelValue'])
                    else: value = None

                    feature.SetField("sample", sample_no)
                    feature.SetField("line", line_no)
                    feature.SetField("radius", radius)
                    feature.SetField("value", value)
                    '''
                    row['Sample'] = int(round(float(row['Sample'])))
                    row['Line'] = int(round(float(row['Line'])))
                    for k in CPT_FIELDS.keys():
                        val = row[ k ]
                        feature.SetField( k , val)

                    poly = ogr.Geometry(ogr.wkbPolygon)
                    poly.AddGeometry(ring)
                    del ring
                    feature.SetGeometry(poly)


                    self.layer.CreateFeature(feature)
                    feature = None
        self._write_ds()

    def _write_ds(self):
        self.ds = None

class Footprint:
    def __init__(self,GndPixels,out_filename):
        self.gndpx = GndPixels
        self._write()
        #self._do_fp()


    def _do_fp(self):
        pass
        #print(self.cube.lines)
        #p = self.gndpx.get_poly()
        #self.mp.AddGeometry(p)

    def _write(self):
        # Create the output Layer
        #mp = ogr.Geometry(ogr.wkbMultiPolygon)
        # Add an ID field
        idField = ogr.FieldDefn("id", ogr.OFTInteger)
        mp = self.gndpx.get_poly()
        outShapefile = "states_centroids.shp"
        outDriver = ogr.GetDriverByName("ESRI Shapefile")
        outDataSource = outDriver.CreateDataSource(outShapefile)
        outLayer = outDataSource.CreateLayer("states_centroids", geom_type=ogr.wkbMultiPolygon)

        # Create the feature and set values
        featureDefn = outLayer.GetLayerDefn()
        feature = ogr.Feature(featureDefn)
        feature.SetGeometry(mp)
        feature.SetField("id", 1)

        outLayer.CreateFeature(feature)
        feature = None
