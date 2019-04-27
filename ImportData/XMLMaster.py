import re

class XMLMaster:
    quality = {
        'Complete And Correct': '100',
        'Correct': '95',
        'Needs Minor Changes': '90',
        'Needs Vote': '70',
        'Needs Major Changes': '50',
        'Entirely Incorrect': '10',
        'Entirely Incorrect Edit': '1'
    }

    class Artist:
        artist_id = '0'
        join_char = ''
        role = ''
        primary_flag = '1'

    class Video:
        embed = '0'
        dur = '0'
        src = ''
        title = ''
        description = ''

    # XMLMaster methods
    def __init__(self):
        self.quality_threshold = 80
        self.master_id = '0'
        self.title = ''
        self.main_release = '0'
        self.release_year = '0000'
        # self.notes = ''
        self.data_quality = '0'

        self.artists = []
        self.genres = []
        self.styles = []
        self.videos = []

    def parse_xml(self, x_master):
        try:
            self.master_id = x_master.get('id', '0')
            self.title = x_master.find('title').text[0:255]
            self.main_release = x_master.find('main_release').text
        except: return False
        if self.master_id == '0': return False

        try:
            self.release_year = x_master.find('year').text or '0'
        except: pass
        # try:
        #     self.notes = x_master.find('notes').text or ''
        # except: pass
        try:
            self.data_quality = self.quality[ x_master.find('data_quality').text ]
        except: pass

        self.artists = self.parse_artists( x_master )

        x_genres = x_master.find('genres')
        if not x_genres is None:
            for el in x_genres.getchildren():
                self.genres.append( el.text )

        x_styles = x_master.find('styles')
        if not x_styles is None:
            for el in x_styles.getchildren():
                self.styles.append( el.text )

        x_videos = x_master.find('videos')
        if not x_videos is None:
            for el in x_videos.getchildren():
                v = self.Video()
                v.embed =  str(int(bool( el.get('embed', 'false') )))
                v.dur = self.parse_duration(el.get('duration', '0'))
                v.src = el.get('src', '')
                v.description = (el.find('description').text or '')[0:255]
                v.title = (el.find('title').text or '')[0:255]
                self.videos.append(v)

        return True

    def parse_artists(self, xelement):
        artists = []
        parsed_roles = []

        x_artists = xelement.find('artists')
        if not x_artists is None:
            for node in x_artists.getchildren():
                a_artist_id = '0'
                a_join_char = ''
                a_role = ''
                try:
                    a_artist_id = node.find('id').text or '0'
                except: continue
                if a_artist_id != '0':
                    try:
                        a_join_char = node.find('join').text or ''
                    except: pass
                    try:
                        a_role = node.find('role').text or ''
                    except: pass
                    for r in re.sub( r"\[[^\[\]]+\]", "", a_role).split(","):
                        r = r.strip()
                        if (a_artist_id, r) not in parsed_roles:
                            a = self.Artist()
                            a.artist_id = a_artist_id
                            a.join_char = a_join_char
                            a.role = r
                            artists.append(a)
                            parsed_roles.append((a_artist_id, r))

            x_exartists = xelement.find('extraartists')
            if not x_exartists is None:
                for node in x_exartists.getchildren():
                    a_artist_id = '0'
                    a_join_char = ''
                    a_role = ''
                    try:
                        a_artist_id = node.find('id').text or '0'
                    except: continue
                    if a_artist_id != '0':
                        try:
                            a_join_char = node.find('join').text or ''
                        except: pass
                        try:
                            a_role = node.find('role').text or ''
                        except: pass
                        for r in re.sub( r"\[[^\[\]]+\]", "", a_role).split(","):
                            r = r.strip()
                            if (a_artist_id, r) not in parsed_roles and r != '':
                                a = self.Artist()
                                a.primary_flag = '0'
                                a.artist_id = a_artist_id
                                a.join_char = a_join_char
                                a.role = r
                                artists.append(a)
                                parsed_roles.append((a_artist_id, r))

        return artists

    def parse_duration(self, dur):
        mmss = dur.split(':')
        if len(mmss) == 2:
            return str( int(mmss[0] or '0')*60 + int(mmss[1] or '0') )
        elif dur.isdigit():
            return dur
        else:
            return '0'

    def prepstring(self, target):
        c = "'\"\\$\b\f\n\r\t\v"
        return ''.join(["\\"+x if x in c else x for x in (target or '').strip()])

    def write_master(self, writers):
        if int(self.data_quality) < self.quality_threshold:
            return False
        if 'House' in self.genres:
            return False
        if 'Techno' in self.genres:
            return False
        if 'Deep House' in self.styles:
            return False
        if 'House' in self.styles:
            return False
        if 'Dub' in self.styles:
            return False

        # write Master
        row = [
            self.master_id,
            self.main_release,
            self.prepstring(self.title),
            self.release_year,
            # self.prepstring(self.notes),
            self.data_quality
        ]
        writers['Master'].write( "\t".join(row) + "\n" )

        # write artists
        for el in self.artists:
            row = [
                self.master_id,
                el.artist_id,
                self.prepstring(el.join_char),
                self.prepstring(el.role),
                el.primary_flag
            ]
            writers['MasterArtist'].write( "\t".join(row) + "\n" )

        # write genres
        for el in self.genres:
            row = [
                self.master_id,
                self.prepstring(el)
            ]
            writers['MasterGenre'].write( "\t".join(row) + "\n" )

        # write styles
        for el in self.styles:
            row = [
                self.master_id,
                self.prepstring(el)
            ]
            writers['MasterStyle'].write( "\t".join(row) + "\n" )

        # write videos
        for el in self.videos:
            row = [
                self.master_id,
                el.embed,
                el.dur,
                el.src,
                self.prepstring(el.title),
                self.prepstring(el.description)
            ]
            writers['MasterVideo'].write( "\t".join(row) + "\n" )

        return True
