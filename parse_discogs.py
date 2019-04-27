import sys
from pprint import pprint
from datetime import datetime

import DiscogsXML2Postgres as app
import ImportData

rebuildSchema = False
forceUpdate = False
onlyTab = False
useExistingXML = False
db_con = None

def file_exists(file_name):
    try:
        with open(file_name, 'rb') as f:
            return True
    except:
        return False


if __name__ == '__main__':
    app.set_log_path( 'logs/log_{}.log'.format(app.get_system_time()) )
    ImportData.set_log_func(app.log)

    app.log('Starting ...')

    # read ini
    # sync config between submodules
    app.read_ini()

    app.log("Parameters:");
    app.log("/useexistingxml   - use the xml files in the data directory (use this for old versions)");
    app.log("/rebuildschema    - create or replace all tables and functions");
    app.log("/onlytab          - don't import data into database only create tab seperated files");
    app.log("/forceupdate      - import database even when database is already up to date. /onlyTab must be off");

    app.log();

    for param in sys.argv:
        param = param.lower()
        if param == '/rebuildschema': rebuildSchema = True
        elif param == '/forceupdate': forceUpdate = True
        elif param == '/useexistingxml': useExistingXML = True
        elif param == '/onlytab': onlyTab = True


    app.log("Using (xml) data stored in '{}'.".format( app.get_config('data_path') ));
    app.log();

    # download data
    ( local_date, local_xml ) = app.discogs_latest_local_data()
    ( remote_date, remote_xml ) = app.discogs_latest_remote_data()

    if useExistingXML and len(local_xml) == 0:
        app.log("No local files found.")
        app.log("Try running without /useExistingXML")
        app.log("Exiting...")
        exit()

    elif useExistingXML and len(local_xml) > 0:
        app.log("Using existing local files")

    elif len(remote_xml) == 0:
        app.log("Could not get remote xml files list")
        app.log("Exiting...")
        exit()

    elif remote_date != local_date:
        new_download_success = app.download_discogs_data( xml_files )
        if not new_download_success:
            app.log("Discogs download failed.")
            app.log("Exiting...")
            exit()

    else:
        app.log("Local Discogs is up to date!")
        app.log()

    # xml should be available at this point.
    # get local xml data
    # --------------------------------------
    ( local_date, local_xml ) = app.discogs_latest_local_data()
    last_db_date = None

    if not onlyTab:
        db_con = ImportData.connect_to_postgres()

        try:
            last_db_date = datetime.strptime(ImportData.get_setting( db_con, 'last_db_date' ), '%Y-%m-%d')
        except: pass
        if type(last_db_date) == datetime:
            if last_db_date == local_date and not forceUpdate:
                app.log("The last discogs export ({}) is already in the database.".format(local_date.strftime('%Y-%m-%d')));
                app.log("Done")
                exit()

        if rebuildSchema:
            app.log("Create or replace base tables.")
            ImportData.create_base_tables( db_con )

        app.log("Create or replace schema.")
        ImportData.build_schema( db_con )


    if len(local_xml) > 0:
        ImportData.run( db_con, app.get_config('data_path'), local_xml )

        if not db_con is None:
            # save db date processed
            ImportData.set_setting( db_con, "last_db_date", local_date.strftime("%Y-%m-%d") )

    else:
        # No local files available, we can't do anything
        app.log("Local files unavailable");
        app.log("Exiting...");
        exit()


    if not onlyTab:
        db_con.close()

    app.log("Done")
