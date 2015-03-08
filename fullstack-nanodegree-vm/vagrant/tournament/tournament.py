#!/usr/bin/env python
# 
# tournament.py -- implementation of a Swiss-system tournament
#

import sys
from collections import deque

import psycopg2


def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    return psycopg2.connect("dbname=tournament")


def deleteMatches():
    """Remove all the match records from the database."""
    db = connect()
    c = db.cursor()

    try:
        c.execute("update players set wins = 0")
        c.execute("update players set matches = 0")
        c.execute("TRUNCATE matches")
        db.commit()
    except:
        print "Unexpected error: ", sys.exc_info()[0]
        raise
    finally:
        db.close()


def deletePlayers():
    """Remove all the player records from the database."""
    db = connect()
    c = db.cursor()

    try:
        c.execute("TRUNCATE players CASCADE")
        db.commit()
    except:
        print "Unexpected error: ", sys.exc_info()[0]
        raise
    finally:
        db.close()


def countPlayers():
    """Returns the number of players currently registered."""
    db = connect()
    c = db.cursor()

    c.execute("select count(*) from players")
    result = c.fetchone()
    db.close()

    return result[0]


def registerPlayer(name):
    """Adds a player to the tournament database.
  
    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)
  
    Args:
      name: the player's full name (need not be unique).
    """

    db = connect()
    c = db.cursor()

    try:
        c.execute("INSERT INTO players (name, wins, matches) VALUES (%s, %s, %s)", (name, 0, 0))
        db.commit()
    except:
        print "Unexpected error: ", sys.exc_info()[0]
        raise
    finally:
        db.close()


def playerStandings():
    """Returns a list of the players and their win records, sorted by wins.

    The first entry in the list should be the player in first place, or a player
    tied for first place if there is currently a tie.

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played
    """
    db = connect()
    c = db.cursor()

    c.execute("select * from players order by wins")

    result = c.fetchall()
    db.close()
    return result


def reportMatch(winner, loser):
    """Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
    """

    db = connect()
    c = db.cursor()

    try:
        # update the winner
        updateWins(c, winner)
        updateMatches(c, winner)

        # update the loser
        updateMatches(c, loser)

        db.commit()
    except:
        print "Unexpected error:", sys.exc_info()[0]
        raise
    finally:
        db.close()


def updateWins(c, winner):
    c.execute("update players set wins = wins + 1 where id = (%s)", (winner,))


def updateMatches(c, player_id):
    c.execute("update players set (matches) = (matches + 1) where id = (%s)", (player_id,))


def addMatch(c, player1_id, player2_id):
    c.execute("insert into matches (player1_id, player2_id) values (%s, %s)",
              (player1_id, player2_id,))


def swissPairings():
    """Returns a list of pairs of players for the next round of a match.
  
    Assuming that there are an even number of players registered, each player
    appears exactly once in the pairings.  Each player is paired with another
    player with an equal or nearly-equal win record, that is, a player adjacent
    to him or her in the standings.
  
    Returns:
      A list of tuples, each of which contains (id1, name1, id2, name2)
        id1: the first player's unique id
        name1: the first player's name
        id2: the second player's unique id
        name2: the second player's name
    """

    db = connect()
    c = db.cursor()

    try:
        c.execute("select id, name from players order by wins desc")
        d_results = deque(c.fetchall())
        matches = []

        # If we have an uneven amount of players,
        # last player in list will not be paired
        if countPlayers() % 2 != 0:
            d_results.pop()

        while len(d_results) > 0:
            player = d_results.popleft()

            # need to determine if the match is valid
            for x in xrange(len(d_results)):
                opponent = d_results[x]
                c.execute(
                    "select player1_id, player2_id from matches where "
                    "player1_id = (%s::int) and player2_id = (%s::int) or "
                    "player1_id = (%s::int) and player2_id = (%s::int)",
                    (player[0], opponent[0], opponent[0], player[0]))
                result = c.fetchone()

                # if no results were found then this pairing for a match has not occurred and
                # we can create this match
                if result is None:
                    del d_results[x]
                    addMatch(c, player[0], opponent[0])
                    matches.append((player[0], player[1], opponent[0], opponent[1]))
                    break

        db.commit()

    except:
        print "Unexpected error:", sys.exc_info()[0]
        raise
    finally:
        db.close()

    return matches