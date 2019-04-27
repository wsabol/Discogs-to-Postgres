DROP FUNCTION IF EXISTS sp_set_setting;

CREATE FUNCTION sp_set_setting (
  _name     VARCHAR(40),
  _value    VARCHAR(255)
)
RETURNS VOID
LANGUAGE PLPGSQL
AS $$
BEGIN
  IF (SELECT COUNT(*) FROM Setting WHERE name = _name) = 0 THEN
    INSERT INTO Setting( name, value )
    VALUES( _name, _value );
  ELSE
    UPDATE SETTING
    SET value = _value
    WHERE name = _name;
  END IF;
END
$$;

DROP FUNCTION IF EXISTS sp_delete_setting;

CREATE FUNCTION sp_delete_setting (
  _name    VARCHAR(40)
)
RETURNS VOID
LANGUAGE PLPGSQL
AS $$
BEGIN
  DELETE FROM Setting
  WHERE name = _name;
END
$$;

DROP FUNCTION IF EXISTS sp_get_setting;

CREATE FUNCTION sp_get_setting (
    _name   VARCHAR(40)
)
RETURNS VARCHAR(255)
LANGUAGE PLPGSQL
AS $$
BEGIN

  RETURN COALESCE((
    SELECT value
    FROM Setting
    WHERE name = _name
  ), '');

END
$$;

DROP FUNCTION IF EXISTS sp_process_artists_insert;

CREATE FUNCTION sp_process_artists_insert() RETURNS VOID
LANGUAGE PLPGSQL
AS $$
BEGIN

  INSERT INTO ArtistGroup(
    artist_id_group,
    artist_id_member,
    active_flag
  )
  SELECT
    grp.artist_id_group,
    grp.artist_id_member,
    max(grp.active_flag)
  FROM (
    SELECT
      artist_id_group,
      artist_id as artist_id_member,
      active_flag
    FROM xgroup
    UNION ALL
    SELECT
      artist_id,
      artist_id_member,
      active_flag
    FROM xmember
  ) grp
  GROUP BY
    grp.artist_id_group,
    grp.artist_id_member;

  DROP TABLE xgroup;
  DROP TABLE xmember;

END
$$;

DROP FUNCTION IF EXISTS sp_process_releases_insert;

CREATE FUNCTION sp_process_releases_insert() RETURNS VOID
LANGUAGE PLPGSQL
AS $$
BEGIN

END
$$;

DROP FUNCTION IF EXISTS sp_process_masters_insert;

CREATE FUNCTION sp_process_masters_insert() RETURNS VOID
LANGUAGE PLPGSQL
AS $$
BEGIN

  UPDATE Master m
  SET artists_sort = r.artists_sort
  FROM MasterRelease r
  WHERE r.id = m.main_release_id
  AND r.artists_sort <> '';

  /* ROLE */
  UPDATE MasterArtist ra
  SET role_id = x.id
  FROM ArtistRole x
  WHERE x.name = ra.xrole;

  INSERT INTO ArtistRole(name)
  select distinct xrole
  from MasterArtist
  WHERE xrole <> ''
  AND role_id = 0;

  UPDATE MasterArtist ra
  SET role_id = x.id
  FROM ArtistRole x
  WHERE x.name = ra.xrole
  and ra.role_id = 0;

  DROP INDEX IF EXISTS IDX_XROLE_1;
  ALTER TABLE MasterArtist DROP COLUMN xrole;

  /* GENRE */
  UPDATE MasterGenre rg
  SET genre_id = x.id
  FROM Genre x
  WHERE x.name = rg.xgenre;

  INSERT INTO Genre(name)
  select distinct xgenre
  from MasterGenre
  WHERE xgenre <> ''
  AND genre_id = 0;

  UPDATE MasterGenre rg
  SET genre_id = x.id
  FROM Genre x
  WHERE x.name = rg.xgenre
  and rg.genre_id = 0;

  DROP INDEX IF EXISTS IDX_XGENRE;
  ALTER TABLE MasterGenre DROP COLUMN xgenre;

  /* STYLE */
  UPDATE MasterStyle rs
  SET style_id = x.id
  FROM Style x
  WHERE x.name = rs.xstyle;

  INSERT INTO Style(name)
  select distinct xstyle
  from MasterStyle
  WHERE xstyle <> ''
  AND style_id = 0;

  UPDATE MasterStyle rs
  SET style_id = x.id
  FROM Style x
  WHERE x.name = rs.xstyle
  AND rs.style_id = 0;

  DROP INDEX IF EXISTS IDX_XSTYLE;
  ALTER TABLE MasterStyle DROP COLUMN xstyle;

  /* COPY TRACKS FROM MAIN RELEASE */
  INSERT INTO MasterTrack(
    master_id,
    xtrack_number_main,
    has_subtracks_flag,
    is_subtrack_flag,
    track_number,
    title,
    subtrack_title,
    position,
    duration_seconds
  )
  select
    m.id,
    rt.xtrack_number_main,
    rt.has_subtracks_flag,
    rt.is_subtrack_flag,
    rt.track_number,
    rt.title,
    rt.subtrack_title,
    rt.position,
    rt.duration_seconds
  FROM Master m
  JOIN MasterRelease mr
  on mr.id = m.main_release_id
  JOIN ReleaseTrack rt
  on rt.release_id = mr.id;

  DROP TABLE ReleaseTrack CASCADE;

  /* track id *
  UPDATE MasterTrack as rt
  SET track_id_main = x.id
  FROM MasterTrack as x
  WHERE x.master_id = rt.master_id
  AND x.track_number = rt.xtrack_number_main;*/

  DROP INDEX IF EXISTS IDX_TRACK_LOOKUP;
  ALTER TABLE MasterTrack DROP COLUMN xtrack_number_main;

  /* COPY TRACKS ARTISTS FROM MAIN RELEASE */
  INSERT INTO MasterTrackArtist(
    track_id,
    artist_id,
    join_char,
    xrole,
    primary_flag
  )
  select
    mt.id,
    rta.artist_id,
    rta.join_char,
    rta.xrole,
    rta.primary_flag
  FROM Master m
  JOIN MasterTrack mt
  on mt.master_id = m.id
  JOIN ReleaseTrackArtist rta
  on rta.xrelease_id = m.main_release_id
  AND rta.xtrack_number = mt.track_number
  WHERE role_id > 0;

  DROP TABLE ReleaseTrackArtist CASCADE;

  /* ROLE (trackartist) */
  UPDATE MasterTrackArtist ra
  SET role_id = x.id
  FROM ArtistRole x
  WHERE x.name = ra.xrole;

  INSERT INTO ArtistRole(name)
  select distinct xrole
  from MasterTrackArtist
  WHERE xrole <> ''
  AND role_id = 0;

  UPDATE MasterTrackArtist ra
  SET role_id = x.id
  FROM ArtistRole x
  WHERE x.name = ra.xrole
  and ra.role_id = 0;

  DROP INDEX IF EXISTS IDX_XROLE_2;
  ALTER TABLE MasterTrackArtist DROP COLUMN xrole;

END
$$;
