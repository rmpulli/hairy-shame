-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.
--
-- You can write comments in this file by starting them with two dashes, like
-- these lines here.

-- This table will store the player information
CREATE TABLE IF NOT EXISTS players (
    id      SERIAL PRIMARY KEY,
    name    varchar(50) NOT NULL,
    wins    integer NOT NULL,
    matches integer NOT NULL
);

-- This table will store matches for the tournament
CREATE TABLE IF NOT EXISTS matches (
    player1_id integer REFERENCES players(id),
    player2_id integer REFERENCES players(id)
);