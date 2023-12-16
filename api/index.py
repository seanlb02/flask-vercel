from flask import Flask
import os

from flask import flash, request, redirect, url_for
from werkzeug.utils import secure_filename
import zipfile
from flask import render_template
import geopandas as gpd
import io
from fiona.io import ZipMemoryFile
import fiona
import tempfile
from fiona.io import ZipMemoryFile
import zipfile
import copy

app = Flask(__name__)

 @app.route('/', methods=['GET', 'POST'])
    def upload_file():
        full_filename = os.path.join(app.config['UPLOAD_FOLDER'], 'MCGCLOGO.png')
        if request.method == 'POST':
            try:
                warning = ""
                # retrieve the file sent via post request (the 'input' element name is data_zip_file)
                file = request.files['data_zip_file']
                file_like_object = file.stream._file  
                data = file_like_object.getvalue()
                zipfile_ob = zipfile.ZipFile(file_like_object)
                file_names = zipfile_ob.namelist()


                # Sanitize first input (.zip)
                if file and file.filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS:
                    # Sanitize files WITHIN the zip folder
                    for item in file_names: 
                        if item.rsplit('.', 1)[1].lower() not in ALLOWED_EXTENSIONS:
                            raise fiona.errors.DriverError
                        else:
                            with ZipMemoryFile(data) as zip:
                                with zip.open(f'{file.filename[:-4]}.shp') as collection:
                                    gdf = gpd.GeoDataFrame.from_features([feature for feature in collection], crs=collection.crs)
                            gdf.sindex
                            # geom err check:
                            if False in gdf.is_valid.values:
                                geom_error = "Yes"
                            else: 
                                geom_error = "No"
                            # corrupt geometry check:
                            corr_file = ""
                            if True in gdf.is_empty.values:
                                corr_file = "Yes"
                            else:
                                corr_file= "No"
                            # empty attribute table:
                            if gdf.shape[1] >= 4:
                                no_attr = "Present"
                            else:
                                no_attr = "None"
                            # Topology check
                            # We only check Topology/Geometry errors for polygons and multilines
                            if 'Point' in gdf.geom_type:
                                pass
                            else:
                                # new dummy dataframe to host any overlapping layers
                                sdf = gdf.sindex.query(gdf.geometry, predicate='overlaps')
                                # if there are any:
                                if sdf.size != 0:
                                    topo_error = "Yes"
                                else:
                                    topo_error = "No"
                            flav = os.path.join(app.config['UPLOAD_FOLDER'], 'MCGC_AGREEMENT_LOGO-01.jpg')
                            return render_template('result.html', layer_name = file.filename[:-4], Warning = warning, geometry = str(gdf.geom_type[0]), projection = gdf.crs.name, corrupt = corr_file, attributes = no_attr, geo_err = geom_error, overlap = topo_error,  logo = full_filename, list = file_names, flavicon = flav)

                
            except fiona.errors.DriverError: 
                pass
        flav = os.path.join(app.config['UPLOAD_FOLDER'], 'MCGC_AGREEMENT_LOGO-01.jpg')
        return render_template('home.html', logo = full_filename, flavicon = flav)