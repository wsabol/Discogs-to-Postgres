import os
import glob
import configparser
from datetime import datetime
from datetime import timedelta
import time

import psycopg2
from lxml import etree

from .XMLArtist import *
from .XMLRelease import *
from .XMLMaster import *

max_count = 0 #100000
db_config = None
def read_ini():
    global db_config

    c = configparser.ConfigParser()
    c.read('DiscogsXML2Postgres.ini')
    db_config = {
        'server': c['DBConnection']['server'],
        'port': c['DBConnection']['port'],
        'db': c['DBConnection']['db'],
        'user': c['DBConnection']['user'],
        'password': c['DBConnection']['password']
    }

def get_config( key ):
    if db_config is None: read_ini()
    return db_config.get(key, '')

def file_exists(file_name):
    try:
        with open(file_name, 'rb') as f:
            return True
    except:
        return False

def clean_files( data_path ):
    files = glob.glob("{}/*.TAB".format(data_path))
    for f in files:
        os.remove(f)

def log(msg = '', p = None):
    print(msg)

def set_log_func(fn_log):
    global log
    log = fn_log

def connect_to_postgres():
    con = psycopg2.connect(
      host=get_config('server'),
      user=get_config('user'),
      port=get_config('port'),
      password=get_config('password'),
      database=get_config('db')
    )
    log("Connected to Postgres.")
    return con

def create_base_tables( db_con ):
    if db_con is None:
        log("No database connection")
        return

    cursor = db_con.cursor();

    with open('resources/dbBaseTables.sql', 'r') as f:
        cursor.execute( f.read() )
        db_con.commit()

    cursor.close()

def build_schema( db_con ):
    if db_con is None:
        log("No database connection")
        return

    cursor = db_con.cursor();

    with open('resources/dbSchema.sql', 'r') as f:
        cursor.execute( f.read() )
        db_con.commit()

    with open('resources/dbIndexes.sql', 'r') as f:
        cursor.execute( f.read() )
        db_con.commit()

    with open('resources/dbStoredFunctions.sql', 'r') as f:
        cursor.execute( f.read() )
        db_con.commit()

    cursor.close()

def set_setting( db_con, name, value ):
    cursor = db_con.cursor();
    cursor.callproc('sp_set_setting', (name, value))
    db_con.commit()
    cursor.close()

def get_setting( db_con, name ):
    cursor = db_con.cursor();
    cursor.callproc("sp_get_setting", (name,))
    row = cursor.fetchone()
    cursor.close()
    return row[0]

def load_data_local_infile( db_con, tab_file, table_name, field_list = "" ):
    log("Inserting {} ...".format(tab_file))

    with open(tab_file, 'r') as f:
        cursor = db_con.cursor()
        cursor.copy_from( f, table_name, columns=field_list.split(',') )
        db_con.commit()
        cursor.close()
        return True

    return False

##############################
# ARTIST FUNCTIONS
##############################

def convert_artists_tab(data_path, file_name):
    if file_name == '':
        return (False, 0, 0)

    counter = 0
    success_count = 0
    writers = {
        'Artist': None,
        'ArtistAlias': None,
        'xgroup': None,
        'xmember': None,
        'ArtistNameVariation': None,
        'ArtistURL': None
    }

    for k in writers.keys():
        writers[k] = open(data_path+"/"+k+".TAB", 'w')

    for event, element in etree.iterparse("{}/{}".format(data_path, file_name), tag="artist"):
        if element.getparent().tag != 'artists': continue
        if counter >= max_count and max_count > 0: break

        xml_artist = XMLArtist()
        parsed = xml_artist.parse_xml(element)
        if parsed:
            if xml_artist.write_artist( writers ):
                success_count = success_count + 1
        else:
            log("Not Parsed")
            print(etree.tostring(element))

        element.clear()
        xml_artist = None
        parsed = False
        counter = counter + 1

    for fp in writers:
        try:
            fp.close()
        except: pass

    else:
        log("Using existing artist TAB files")

    return ( True, counter, success_count )

def insert_artists_tab( db_con, data_path ):
    if db_con is None:
        log("No database connection!")
        return False

    if file_exists(data_path+"/Artist.TAB"):
        load_data_local_infile(db_con, data_path+"/Artist.TAB", "Artist", "id,name,realname,data_quality")
    else: return False

    if file_exists(data_path+"/ArtistAlias.TAB"):
        load_data_local_infile(db_con, data_path+"/ArtistAlias.TAB", "ArtistAlias", "artist_id_main,artist_id_alias")
    else: return False

    if file_exists(data_path+"/xgroup.TAB"):
        load_data_local_infile(db_con, data_path+"/xgroup.TAB", "xgroup", "artist_id_group,artist_id,active_flag")
    else: return False

    if file_exists(data_path+"/xmember.TAB"):
        load_data_local_infile(db_con, data_path+"/xmember.TAB", "xmember", "artist_id,artist_id_member,active_flag")
    else: return False

    if file_exists(data_path+"/ArtistNameVariation.TAB"):
        load_data_local_infile(db_con, data_path+"/ArtistNameVariation.TAB", "ArtistNameVariation", "artist_id,name")
    else: return False

    if file_exists(data_path+"/ArtistURL.TAB"):
        load_data_local_infile(db_con, data_path+"/ArtistURL.TAB", "ArtistURL", "artist_id,url")
    else: return False

    cur = db_con.cursor()
    cur.callproc('sp_process_artists_insert')
    db_con.commit()
    cur.close()

    return True

##############################
# RELEASE FUNCTIONS
##############################

def convert_releases_tab(data_path, file_name):
    if file_name == '':
        return (False, 0, 'empty file string')

    counter = 0
    success_count = 0
    writers = {
        'MasterRelease': None,
        'ReleaseTrack': None,
        'ReleaseTrackArtist': None
    }

    for k in writers.keys():
        writers[k] = open(data_path+"/"+k+".TAB", 'w')

    for event, element in etree.iterparse("{}/{}".format(data_path, file_name), tag="release"):
        if element.getparent().tag != 'releases': continue
        if counter >= max_count and max_count > 0: break

        xml_release = XMLRelease()
        parsed = xml_release.parse_xml(element)
        if parsed:
            if xml_release.write_release( writers ):
                success_count = success_count + 1
        # else:
            # log("Not Parsed")
            # print(etree.tostring(element))

        element.clear()
        xml_release = None
        parsed = False
        counter = counter + 1

    for fp in writers:
        try:
            fp.close()
        except: pass

    else:
        log("Using existing release TAB files")

    return ( True, counter, success_count )

def insert_releases_tab( db_con, data_path ):
    if db_con is None:
        log("No database connection!")
        return False

    if file_exists(data_path+"/MasterRelease.TAB"):
        load_data_local_infile(db_con, data_path+"/MasterRelease.TAB", "MasterRelease", "id,master_id,data_quality,artists_sort")
    else: return False

    if file_exists(data_path+"/ReleaseTrack.TAB"):
        load_data_local_infile(db_con, data_path+"/ReleaseTrack.TAB", "ReleaseTrack", "release_id,xtrack_number_main,has_subtracks_flag,is_subtrack_flag,track_number,title,subtrack_title,position,duration_seconds")
    else: return False

    if file_exists(data_path+"/ReleaseTrackArtist.TAB"):
        load_data_local_infile(db_con, data_path+"/ReleaseTrackArtist.TAB", "ReleaseTrackArtist", "xrelease_id,xtrack_number,artist_id,join_char,xrole,primary_flag")
    else: return False

    cur = db_con.cursor()
    cur.callproc('sp_process_releases_insert')
    db_con.commit()
    cur.close()

    return True

##############################
# MASTER FUNCTIONS
##############################

def convert_masters_tab(data_path, file_name):
    if file_name == '':
        return (False, 0, 'empty file string')

    counter = 0
    success_count = 0
    writers = {
        'Master': None,
        'MasterArtist': None,
        'MasterGenre': None,
        'MasterStyle': None,
        'MasterVideo': None
    }

    for k in writers.keys():
        writers[k] = open(data_path+"/"+k+".TAB", 'w')

    for event, element in etree.iterparse("{}/{}".format(data_path, file_name), tag="master"):
        if element.getparent().tag != 'masters': continue
        if counter >= max_count and max_count > 0: break

        xml_master = XMLMaster()
        parsed = xml_master.parse_xml(element)
        if parsed:
            if xml_master.write_master( writers ):
                success_count = success_count + 1
        else:
            log("Not Parsed")
            print(etree.tostring(element))

        element.clear()
        xml_master = None
        parsed = False
        counter = counter + 1

    for fp in writers:
        try:
            fp.close()
        except: pass

    else:
        log("Using existing release TAB files")

    return ( True, counter, success_count )

def insert_masters_tab( db_con, data_path ):
    if db_con is None:
        log("No database connection!")
        return False

    if file_exists(data_path+"/Master.TAB"):
        load_data_local_infile(db_con, data_path+"/Master.TAB", "Master", "id,main_release_id,title,release_year,data_quality")
    else: return False

    if file_exists(data_path+"/MasterArtist.TAB"):
        load_data_local_infile(db_con, data_path+"/MasterArtist.TAB", "MasterArtist", "master_id,artist_id,join_char,xrole,primary_flag")
    else: return False

    if file_exists(data_path+"/MasterGenre.TAB"):
        load_data_local_infile(db_con, data_path+"/MasterGenre.TAB", "MasterGenre", "master_id,xgenre")
    else: return False

    if file_exists(data_path+"/MasterStyle.TAB"):
        load_data_local_infile(db_con, data_path+"/MasterStyle.TAB", "MasterStyle", "master_id,xstyle")
    else: return False

    if file_exists(data_path+"/MasterVideo.TAB"):
        load_data_local_infile(db_con, data_path+"/MasterVideo.TAB", "MasterVideo", "master_id,embed,duration_seconds,src,title,description")
    else: return False

    cur = db_con.cursor()
    cur.callproc('sp_process_masters_insert')
    db_con.commit()
    cur.close()

    return True

##############################
# MAIN RUN IMPORT TAB FILES
##############################

def run( db_con, data_path, local_xml ):
    t0 = time.time()
    file_name = ''

    log("Exporting ARTISTS.XML data to TAB files.")
    for f in local_xml:
        if 'artists' in f:
            file_name = f
            break

    ( tab_success, parsed_count, success_count ) = convert_artists_tab(data_path, file_name)
    if not tab_success:
        log("convert_artists_tab failure. ")
        log("Exiting...")
        exit();

    if not db_con is None:
        log("Importing ARTISTS TAB files into Postgres.");
        insert_artists_tab( db_con, data_path )
        clean_files( data_path )

    elapsed = time.time() - t0
    dt = timedelta(seconds=int(elapsed))
    log("ARTIST Done")
    log("{} entities processed".format(parsed_count))
    log("{} records inserted".format(success_count))
    log("Elapsed index time {}".format(str(dt)))
    log()


    log("Exporting RELEASES.XML data to TAB files.")
    for f in local_xml:
        if 'releases' in f:
            file_name = f
            break

    ( tab_success, parsed_count, success_count ) = convert_releases_tab(data_path, file_name)
    if not tab_success:
        log("convert_releases_tab failure. ")
        log("Exiting...")
        exit();

    if not db_con is None:
        log("Importing RELEASES TAB files into Postgres.");
        insert_releases_tab( db_con, data_path )
        clean_files( data_path )

    elapsed = time.time() - t0
    dt = timedelta(seconds=int(elapsed))
    log("RELEASE Done")
    log("{} entities processed".format(parsed_count))
    log("{} records inserted".format(success_count))
    log("Elapsed index time {}".format(str(dt)))
    log()


    log("Exporting MASTERS.XML data to TAB files.")
    for f in local_xml:
        if 'masters' in f:
            file_name = f
            break

    ( tab_success, parsed_count, success_count ) = convert_masters_tab(data_path, file_name)
    if not tab_success:
        log("convert_masters_tab failure. ")
        log("Exiting...")
        exit();

    if not db_con is None:
        log("Importing MASTERS TAB files into Postgres.");
        insert_masters_tab( db_con, data_path )
        clean_files( data_path )

    elapsed = time.time() - t0
    dt = timedelta(seconds=int(elapsed))
    log("MASTERS Done")
    log("{} entities processed".format(parsed_count))
    log("{} records inserted".format(success_count))
    log("Elapsed index time {}".format(str(dt)))
    log()

    elapsed = time.time() - t0
    dt = timedelta(seconds=int(elapsed))
    log("Total Elapsed index time {}".format(str(dt)))
