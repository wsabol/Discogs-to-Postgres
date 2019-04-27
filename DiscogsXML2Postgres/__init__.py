import requests
import glob
from datetime import datetime
import configparser
import os
import gzip

import xml.etree.ElementTree as ET

def get_system_time():
    return datetime.today().strftime('%Y-%m-%d %H:%M:%S')

data_config = None
def read_ini():
    global data_config

    c = configparser.ConfigParser()
    c.read('DiscogsXML2Postgres.ini')
    data_config = {
        'discogs_data_url': c['DiscogsData']['discogs_data_url'],
        'data_path': c['DiscogsData']['data_path'],
        'bucket_url': '//discogs-data.s3-us-west-2.amazonaws.com',
        's3b_root_dir': 'data/'
    }

def get_config( key ):
    if data_config is None: read_ini()
    return data_config.get(key, '')

log_path = None
def set_log_path(p):
    global log_path
    log_path = p

def log(msg = '', p = None):
    print(msg.strip())
    if p is None: p = log_path
    if not p is None:
        with open(p, 'a') as f:
            f.write("[{}] {}\n".format(get_system_time(), msg.strip()))


has_s3_settings = False
def get_discogs_s3_settings():
    global data_config, has_s3_settings

    try:
        headers = {"user-agent": "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.2; .NET CLR 1.0.3705;)"}
        r = requests.get( get_config('discogs_data_url'), headers=headers )
        if not r is None:
            page_content = str(r.content)

            p = page_content.index("BUCKET_URL")
            if p >= 0:
                p2 = page_content.index("=", p)
                p3 = page_content.index(";", p)
                s = page_content[p2+1:p3]
                s = s.replace(";", "").strip()
                s = s.replace("'", "").strip()
                s = s.replace("\\", "").strip()
                if not s is None:
                    if len(s) >= 0:
                        data_config['bucket_url'] = s

            p = page_content.index("S3B_ROOT_DIR")
            if p >= 0:
                p2 = page_content.index("=", p)
                p3 = page_content.index(";", p)
                s = page_content[p2+1:p3]
                s = s.replace(";", "").strip()
                s = s.replace("'", "").strip()
                s = s.replace("\\", "").strip()
                if not s is None:
                    if len(s) >= 0:
                        data_config['s3b_root_dir'] = s


    except:
        log("Unable to establish connection. Using info from ini")
        has_s3_settings = True

def discogs_latest_local_data():
    dir_length = len(get_config('data_path'))+1
    files = glob.glob("{}/*.xml".format(get_config('data_path')))
    dt_date = None
    local_xml = []
    for f in files:
        f = f[dir_length:]
        if len(f) >= 16:
            local_xml.append(f)
            dt_test = datetime.strptime(f[8:16], '%Y%m%d')
            if dt_date is None: dt_date = dt_test
            elif dt_test.date() > dt_date.date(): dt_date = dt_test

    return ( dt_date, local_xml )

def discogs_latest_remote_data():
    if not has_s3_settings:
        get_discogs_s3_settings()

    try:
        year = datetime.today().year
        year_xml_files = discogs_remote_files(year)
        if len(year_xml_files) == 0:
            year = year - 1
            year_xml_files = discogs_remote_files(year)

        dt_date = None
        for f in year_xml_files:
            dt_test = datetime.strptime(f[8:16], '%Y%m%d')
            if dt_date is None: dt_date = dt_test
            elif dt_test.date() > dt_date.date(): dt_date = dt_test

        xml_files = []
        for f in year_xml_files:
            if f[8:16] == dt_date.strftime('%Y%m%d'):
                xml_files.append(f)

        return ( dt_date, xml_files )
    except:
        return ( None, [] )

def discogs_remote_files(year):
    if not has_s3_settings:
        get_discogs_s3_settings()

    try:
        headers = {
            "user-agent": "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.2; .NET CLR 1.0.3705;)",
            "Accept-Encoding": "gzip, deflate"
        }
        r = requests.get("https:{}/?delimiter=/&prefix=data/{}/".format(get_config('bucket_url'), year), headers=headers);
        s = r.content
        doc = ET.fromstring(s)
        aws_files = []
        prefix = len("data/{}/".format(year))

        for c in [node for node in doc.getchildren() if node.tag.endswith('Contents')]:
            key = [node for node in c.getchildren() if node.tag.endswith('Key')]
            if len(key) > 0:
                file = key[0].text
                aws_files.append( file[prefix:] )

        return aws_files
    except:
        return []

def download_discogs_data( xml_files ):
    if not has_s3_settings:
        get_discogs_s3_settings()

    if len(xml_files) == 0:
        log("ERROR Remote files not found")
        return False

    log("Download xml files from discogs.")
    for file_name in xml_files:
        file_path = get_config('data_path')+"/"+file_name
        try:
            with open(file_path, 'rb') as f_test:
                log("{} already downloaded".format(file_name))
                continue
        except: pass

        try:
            with open(file_path.replace(".gz", ""), 'r') as f_test:
                log("{} already downloaded".format(file_name))
                continue
        except: pass

        log("Downloading {}".format(file_name))
        download_file(file_name)

    log()
    log("Decompressing downloaded gz files.")
    success = True
    for file_name in xml_files:
        file_path = get_config('data_path')+"/"+file_name
        try:
            with open(file_path.replace(".gz", ""), 'r') as f_test:
                log("{} already decompressed.".format(file_name))
                continue
        except: pass

        log("Decompressing {}.".format(file_name))
        success = success and gzip_decompress(file_path)

    log()

    return True;

def download_file(file_name):
    year = file_name[8:12]
    try:
        with open(new_file_path.replace(".gz", ""), 'r') as f_test:
            os.remove(new_file_path)
    except: pass

    headers = {
        "user-agent": "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.2; .NET CLR 1.0.3705;)",
        "Accept-Encoding": "gzip, deflate"
    }
    url = "https:{}/data/{}/{}".format(get_config('bucket_url'), year, file_name)
    r = requests.get(url, allow_redirects=True, headers=headers)
    open(new_file_path, 'wb').write(r.content)

    try:
        with open(new_file_path.replace(".gz", ""), 'r') as f_test:
            return True
    except: return False

def gzip_decompress(file_name):
    ret_val = False
    with open(file_name.replace(".gz", ""), 'wb') as fdeco:
        with gzip.open(file_name, 'rb') as f:
            for line in f:
                fdeco.write(line)

            return True
