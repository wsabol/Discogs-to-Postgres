import re

class XMLArtist:
    quality = {
        'Complete And Correct': '100',
        'Correct': '95',
        'Needs Minor Changes': '90',
        'Needs Vote': '70',
        'Needs Major Changes': '50',
        'Entirely Incorrect': '10',
        'Entirely Incorrect Edit': '1'
    }

    class Group:
        artist_id_group = '0'
        active = '1'

    class Member:
        artist_id_member = '0'
        active = '1'


    #XMLArtist methods
    def __init__(self):
        self.quality_threshold = 70
        self.artist_id = '0'
        self.name = ''
        self.realname = ''
        # self.profile = ''
        self.data_quality = '0'
        self.images = []
        self.urls = []
        self.aliases = []
        self.groups = []
        self.members = []
        self.name_variations = []

    def parse_xml(self, x_artist):
        try:
            self.artist_id = x_artist.find('id').text
            self.name = x_artist.find('name').text
        except: return False

        try:
            self.data_quality = self.quality[ x_artist.find('data_quality').text ]
        except: pass
        try:
            self.realname = x_artist.find('realname').text or ''
        except: pass
        # try:
        #     self.profile = x_artist.find('profile').text or ''
        # except: pass

        x_aliases = x_artist.find('aliases')
        if not x_aliases is None:
            for el in x_aliases.iter('name'):
                self.aliases.append( el.get('id', '0') )

        x_groups = x_artist.find('groups')
        if not x_groups is None:
            for el in x_groups.iter('name'):
                group = self.Group()
                group.artist_id_group = el.get('id', '0')
                group.active = el.get('active', '1')
                self.groups.append(group)

        x_members = x_artist.find('members')
        if not x_members is None:
            for el in x_members.iter('name'):
                mem = self.Member()
                mem.artist_id_member = el.get('id', '0')
                mem.active = el.get('active', '1')
                self.members.append(mem)

        x_anv = x_artist.find('namevariations')
        if not x_anv is None:
            for el in x_anv.iter('name'):
                self.name_variations.append(el.text)

        x_urls = x_artist.find('urls')
        if not x_urls is None:
            for el in x_urls.iter('url'):
                self.urls.append( el.text or '' )

        return True

    def prepstring(self, target):
        c = "'\"\\$\b\f\n\r\t\v"
        return ''.join(["\\"+x if x in c else x for x in (target or '').strip()])

    def write_artist(self, writers):
        if int(self.data_quality) < self.quality_threshold:
            return False

        # write Artist
        row = [
            self.artist_id,
            self.prepstring(self.name),
            self.prepstring(self.realname),
            # self.prepstring(self.profile),
            self.data_quality
        ]
        writers['Artist'].write( "\t".join(row) + "\n" )

        # write aliases
        for el in self.aliases:
            row = [self.artist_id, el]
            writers['ArtistAlias'].write( "\t".join(row) + "\n" )

        # write groups
        for el in self.groups:
            row = [el.artist_id_group, self.artist_id, el.active]
            writers['xgroup'].write( "\t".join(row) + "\n" )

        # write members
        for el in self.members:
            row = [self.artist_id, el.artist_id_member, el.active]
            writers['xmember'].write( "\t".join(row) + "\n" )

        # write name variations
        for el in self.name_variations:
            row = [
                self.artist_id,
                self.prepstring(el)
            ]
            writers['ArtistNameVariation'].write( "\t".join(row) + "\n" )

        # write urls
        for el in self.urls:
            n = self.prepstring(el)
            if n != "":
                row = [self.artist_id, n]
                writers['ArtistURL'].write( "\t".join(row) + "\n" )

        return True
