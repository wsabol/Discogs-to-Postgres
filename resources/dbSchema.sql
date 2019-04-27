DROP TABLE IF EXISTS Artist CASCADE;
DROP TABLE IF EXISTS ArtistAlias CASCADE;
DROP TABLE IF EXISTS ArtistGroup CASCADE;
DROP TABLE IF EXISTS xgroup CASCADE;
DROP TABLE IF EXISTS xmember CASCADE;
DROP TABLE IF EXISTS ArtistNameVariation CASCADE;
DROP TABLE IF EXISTS ArtistURL CASCADE;
DROP TABLE IF EXISTS Master CASCADE;
DROP TABLE IF EXISTS MasterArtist CASCADE;
DROP TABLE IF EXISTS MasterGenre CASCADE;
DROP TABLE IF EXISTS MasterStyle CASCADE;
DROP TABLE IF EXISTS MasterTrack CASCADE;
DROP TABLE IF EXISTS MasterTrackArtist CASCADE;
DROP TABLE IF EXISTS MasterVideo CASCADE;
DROP TABLE IF EXISTS MasterRelease CASCADE;
DROP TABLE IF EXISTS ReleaseTrack CASCADE;
DROP TABLE IF EXISTS ReleaseTrackArtist CASCADE;


/**********************************************************
-- Add table "ARTIST"
***********************************************************/

CREATE TABLE Artist (
  id INT NOT NULL PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  realname VARCHAR(1024),
  /*profile TEXT,*/
  data_quality INTEGER DEFAULT 10
);

/**********************************************************
-- Add table "ArtistAlias"
***********************************************************/

CREATE TABLE ArtistAlias (
  id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  artist_id_main INTEGER NOT NULL,
  artist_id_alias INTEGER NOT NULL
);

/**********************************************************
-- Add table "ArtistGroup"
***********************************************************/

CREATE TABLE ArtistGroup (
  id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  artist_id_group INTEGER NOT NULL,
  artist_id_member INTEGER NOT NULL,
  active_flag INTEGER NOT NULL DEFAULT 1
);

/**********************************************************
-- Add table "xgroup"
***********************************************************/

CREATE TABLE xgroup (
  artist_id_group INTEGER NOT NULL,
  artist_id INTEGER NOT NULL,
  active_flag INTEGER NOT NULL DEFAULT 1
);

/**********************************************************
-- Add table "xmember"
***********************************************************/

CREATE TABLE xmember (
  artist_id INTEGER NOT NULL,
  artist_id_member INTEGER NOT NULL,
  active_flag INTEGER NOT NULL DEFAULT 1
);

/**********************************************************
-- Add table "ArtistImage"
***********************************************************/

CREATE TABLE ArtistNameVariation (
  id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  artist_id INTEGER NOT NULL,
  name VARCHAR(255)
);

/**********************************************************
-- Add table "ArtistURL"
***********************************************************/

CREATE TABLE ArtistURL (
  id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  artist_id INTEGER,
  url VARCHAR(1024) NOT NULL
);

/**********************************************************
-- Add table "Master"
***********************************************************/

CREATE TABLE Master (
  id INT NOT NULL PRIMARY KEY,
  main_release_id INTEGER NOT NULL DEFAULT 0,
  title VARCHAR(255) NOT NULL,
  release_year INT NULL,
  data_quality INTEGER DEFAULT 10,
  artists_sort VARCHAR(255) NULL
);

/**********************************************************
-- Add table "MasterArtist"
***********************************************************/

CREATE TABLE MasterArtist (
  id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  master_id INTEGER NOT NULL,
  artist_id INTEGER NOT NULL,
  join_char VARCHAR(100) NOT NULL DEFAULT '',
  role_id INTEGER NOT NULL DEFAULT 0,
  xrole VARCHAR(255) NOT NULL DEFAULT '',
  primary_flag INTEGER NOT NULL DEFAULT 0
);

/**********************************************************
-- Add table "MasterGenre"
***********************************************************/

CREATE TABLE MasterGenre (
  id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  master_id INTEGER NOT NULL,
  genre_id INTEGER NOT NULL DEFAULT 0,
  xgenre VARCHAR(100) NOT NULL
);

/**********************************************************
-- Add table "MasterStyle"
***********************************************************/

CREATE TABLE MasterStyle (
  id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  master_id INTEGER NOT NULL,
  style_id INTEGER NOT NULL DEFAULT 0,
  xstyle VARCHAR(100) NOT NULL
);

/**********************************************************
-- Add table "MasterTrack"
***********************************************************/

CREATE TABLE MasterTrack (
  id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  master_id INTEGER NOT NULL,
  xtrack_number_main INTEGER NOT NULL DEFAULT 0,
  track_id_main INTEGER NOT NULL DEFAULT 0,
  has_subtracks_flag INTEGER NOT NULL DEFAULT 0,
  is_subtrack_flag INTEGER NOT NULL DEFAULT 0,
  track_number INTEGER NOT NULL DEFAULT 1,
  title VARCHAR(255) NOT NULL,
  subtrack_title VARCHAR(255) NOT NULL,
  position VARCHAR(50) NOT NULL DEFAULT '',
  duration_seconds INTEGER NOT NULL DEFAULT 0
);

/**********************************************************
-- Add table "MasterTrackArtist"
***********************************************************/

CREATE TABLE MasterTrackArtist (
  id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  track_id INTEGER NOT NULL DEFAULT 0,
  artist_id INTEGER NOT NULL,
  join_char VARCHAR(100) NOT NULL DEFAULT '',
  role_id INTEGER NOT NULL DEFAULT 0,
  xrole VARCHAR(100) NOT NULL DEFAULT '',
  primary_flag INTEGER NOT NULL DEFAULT 0
);

/**********************************************************
-- Add table "MasterVideo"
***********************************************************/

CREATE TABLE MasterVideo (
  id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  master_id INTEGER NOT NULL,
  embed INTEGER NOT NULL DEFAULT 0,
  duration_seconds INTEGER NOT NULL DEFAULT 0,
  src VARCHAR(255) NOT NULL,
  title VARCHAR(255) NOT NULL,
  description VARCHAR(255) NOT NULL
);

/**********************************************************
-- Add table "MasterRelease"
***********************************************************/

CREATE TABLE MasterRelease (
  id INT NOT NULL PRIMARY KEY,
  master_id INTEGER NOT NULL,
  data_quality INTEGER DEFAULT 10,
  artists_sort VARCHAR(255)
);

/**********************************************************
-- Add table "ReleaseTrack"
***********************************************************/

CREATE TABLE ReleaseTrack (
  id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  release_id INTEGER NOT NULL,
  xtrack_number_main INTEGER NOT NULL DEFAULT 0,
  has_subtracks_flag INTEGER NOT NULL DEFAULT 0,
  is_subtrack_flag INTEGER NOT NULL DEFAULT 0,
  track_number INTEGER NOT NULL DEFAULT 1,
  title VARCHAR(255) NOT NULL,
  subtrack_title VARCHAR(255) NOT NULL,
  position VARCHAR(50) NOT NULL DEFAULT '',
  duration_seconds INTEGER NOT NULL DEFAULT 0
);

/**********************************************************
-- Add table "ReleaseTrackArtist"
***********************************************************/

CREATE TABLE ReleaseTrackArtist (
  id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  xrelease_id INTEGER NOT NULL,
  xtrack_number INTEGER NOT NULL,
  artist_id INTEGER NOT NULL,
  join_char VARCHAR(100) NOT NULL DEFAULT '',
  role_id INTEGER NOT NULL DEFAULT 0,
  xrole VARCHAR(100) NOT NULL DEFAULT '',
  primary_flag INTEGER NOT NULL DEFAULT 0
);
