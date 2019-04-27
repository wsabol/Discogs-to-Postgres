DROP TABLE IF EXISTS Setting CASCADE;
DROP TABLE IF EXISTS ArtistRole CASCADE;
DROP TABLE IF EXISTS Genre CASCADE;
DROP TABLE IF EXISTS Style CASCADE;


/**********************************************************
-- Add table "Setting"
***********************************************************/

CREATE TABLE Setting (
  id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  name VARCHAR(40) NOT NULL,
  value VARCHAR(255) NOT NULL
);

/**********************************************************
-- Add table "ArtistRole"
***********************************************************/

CREATE TABLE ArtistRole (
  id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  name VARCHAR(255) NOT NULL
);

/**********************************************************
-- Add table "GENRE"
***********************************************************/

CREATE TABLE Genre (
  id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  name VARCHAR(100) NOT NULL
);

/**********************************************************
-- Add table "Style"
***********************************************************/

CREATE TABLE Style (
  id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  name VARCHAR(100) NOT NULL
);
