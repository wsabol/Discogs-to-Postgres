import re

class XMLRelease:
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

    class Track:
        track_number_main = '0'
        has_subtracks = '0'
        is_subtrack = '0'
        track_number = '1'
        title = ''
        subtrack_title = ''
        position = ''
        dur = '0'
        artists = []


    # XMLRelease methods
    def __init__(self):
        self.release_id = '0'
        self.master_id = '0'
        self.data_quality = '0'
        self.artists_sort = ''
        self.tracklist = []


    def parse_xml(self, x_release):
        self.release_id = x_release.get('id', '0')
        if self.release_id == '0': return False

        try:
            self.master_id = x_release.find('master_id').text or '0'
        except: pass
        try:
            self.data_quality = self.quality[ x_release.find('data_quality').text ]
        except: pass
        try:
            self.artists_sort = x_release.find('notes').artists_sort or ''
        except: pass

        self.artists = self.parse_artists( x_release )

        x_tracks = x_release.find('tracklist')
        if not x_tracks is None:
            cnt = 1
            for el in x_tracks.getchildren():
                if (el.find('title').text or '') != '':
                    tr = self.Track()
                    tr.title = el.find('title').text[0:255]
                    tr.track_number = str(cnt)
                    tr.position = str(cnt)
                    try:
                        tr.position = el.find('position').text or tr.position
                    except: pass
                    tr.position = tr.position.strip()[0:50]
                    tr.dur = self.parse_duration(el.find('duration').text or '0')

                    tr.artists = self.parse_artists( el )
                    if len(tr.artists) == 0:
                        tr.artists = self.artists

                    self.tracklist.append(tr)
                    cnt = cnt + 1
        else: return False

                    # x_subs = el.find('subtracks')
                    # if not x_subs is None:
                    #     tr.has_subtracks = '1'
                    #     for sub_el in x_subs:
                    #         if (sub_el.find('title').text or '') != '':
                    #             subtr = self.Track()
                    #             subtr.is_subtrack = '1'
                    #             subtr.track_number_main = tr.track_number
                    #             subtr.track_number_main = tr.track_number
                    #             subtr.subtrack_title = (sub_el.find('title').text or '')[0:255]
                    #             subtr.title = (tr.title + " / " + subtr.title)[0:255]
                    #             subtr.track_number = str(cnt)
                    #             subtr.position = str(cnt)
                    #             try:
                    #                 subtr.position = sub_el.find('position').text
                    #             except: pass
                    #             subtr.dur = self.parse_duration(sub_el.find('duration').text or '0')
                    #
                    #             subtr.artists = self.parse_artists( sub_el )
                    #             if len(subtr.artists) == 0:
                    #                 subtr.artists = tr.artists
                    #
                    #             self.tracklist.append(subtr)
                    #             cnt = cnt + 1

        return True

    def parse_duration(self, dur):
        mmss = dur.split(':')
        if len(mmss) == 2:
            dur = str( int(mmss[0] or '0')*60 + int(mmss[1] or '0') )
        elif not dur.isdigit():
            dur = '0'

        if int(dur) > 2147483647:
            dur = '-1'

        return dur

    def parse_role(self, role):
        role = role.strip()
        irole = role.lower()

        if not re.search("[a-z]", irole):
            role = ''
        elif irole.find('art') > -1 and irole.find('part') == -1 and irole.find('quart') == -1:
            role = ''
        elif irole.find('other') == 0 and irole != 'other':
            role = ''

        return role

    def parse_artists(self, xtrack):
        artists = []
        parsed_roles = []

        x_artists = xtrack.find('artists')
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
                    for r0 in re.sub( r"\[[^\[\]]+\]", "", a_role).split(","):
                        for r in r0.split(";"):
                            r = self.parse_role(r)
                            if (a_artist_id, r) not in parsed_roles:
                                a = self.Artist()
                                a.artist_id = a_artist_id
                                a.join_char = a_join_char
                                a.role = r
                                artists.append(a)
                                parsed_roles.append((a_artist_id, r))

            x_exartists = xtrack.find('extraartists')
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
                        for r0 in re.sub( r"\[[^\[\]]+\]", "", a_role).split(","):
                            for r in r0.split(";"):
                                r = self.parse_role(r)
                                if (a_artist_id, r) not in parsed_roles and r != '':
                                    a = self.Artist()
                                    a.primary_flag = '0'
                                    a.artist_id = a_artist_id
                                    a.join_char = a_join_char
                                    a.role = r
                                    artists.append(a)
                                    parsed_roles.append((a_artist_id, r))

        return artists

    def prepstring(self, target):
        c = "'\"\\$\b\f\n\r\t\v"
        return ''.join(["\\"+x if x in c else x for x in (target or '').strip()])

    def write_release(self, writers):
        if len(self.tracklist) == 0:
            return False

        # write Release
        row = [
            self.release_id,
            self.master_id,
            self.data_quality,
            self.prepstring(self.artists_sort)
        ]
        writers['MasterRelease'].write( "\t".join(row) + "\n" )

        # write tracklist
        for el in self.tracklist:
            row = [
                self.release_id,
                el.track_number_main,
                el.has_subtracks,
                el.is_subtrack,
                el.track_number,
                self.prepstring(el.title),
                self.prepstring(el.subtrack_title),
                self.prepstring(el.position),
                el.dur
            ]
            writers['ReleaseTrack'].write( "\t".join(row) + "\n" )

            for trel in el.artists:
                row = [
                    self.release_id,
                    el.track_number,
                    trel.artist_id,
                    self.prepstring(trel.join_char),
                    self.prepstring(trel.role)[0:100],
                    trel.primary_flag
                ]
                writers['ReleaseTrackArtist'].write( "\t".join(row) + "\n" )

        return True
