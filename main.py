import spotipy
import spotipy.util as util
import os

from pprint import pprint
from datetime import datetime, timedelta
from spotipy.oauth2 import SpotifyClientCredentials
from secret import USER_EMAIL, CLIENT_ID, CLIENT_SECRET, PLAYLIST_ID, LOG_PATH
from util import get_recently_added, get_in_rotation, get_ids


def print_aligned(song1, song2, log):
    song1_name = song1[:45]
    song1_name = ' '*(45 - len(song1_name)) + song1_name
    text = '{} | {}'.format(song1_name, song2[:45])
    print(text)
    log.write(text + '\n')

def print_song1(song1, message, log):
    song1_name = song1[:45]
    song1_name = ' '*(45 - len(song1_name)) + song1_name
    text = '{} | {}'.format(song1_name, message)
    print(text)
    log.write(text + '\n')

def print_song2(message, song2, log):
    song2_name = song2[:45]
    whitespace_len = 45 - len(message)
    assert whitespace_len >= 0
    text = '{} | {}'.format(' '*(whitespace_len) + message, song2_name)
    print(text)
    log.write(text + '\n')


if __name__ == '__main__':
    scope = 'user-library-read playlist-modify-public'
    token = util.prompt_for_user_token(USER_EMAIL, scope,
            client_id=CLIENT_ID, client_secret=CLIENT_SECRET, redirect_uri='http://localhost/')
    sp = spotipy.Spotify(auth=token)
    user_id = sp.current_user()['id']

    log = open(os.path.join(LOG_PATH, 'log.txt'), 'w')

    # First, find an alignment. we want to find the first song in in_rotation
    # that has a match in recently_added. any song before it in recently_added
    # is new and must be added to in_rotation.

    # Then we go song by song. If a song exists in recently_added but not in
    # in_rotation, skip that one in recently_added. If a song exists in
    # in_rotation but not in recently_added, then remove it from in_rotation.
    # Continue this until all recently_added is done.

    # Then prune in_rotation (songs from the bottom that are older than 2
    # weeks, as long as in_rotation remains with 100+ songs)

    in_rotation = get_in_rotation(sp, user_id)
    recently_added = get_recently_added(sp, at_least_100=True)
    assert len(recently_added) >= 100 # if not true, spotify api might be down.

    final_playlist = []

    i0, i1 = 0, 0
    matched = False
    while i0 < len(in_rotation) and i1 < len(recently_added):
        if in_rotation[i0][0] == recently_added[i1][0]:
            print_aligned(in_rotation[i0][1], recently_added[i1][1], log)
            final_playlist.append(in_rotation[i0])
            matched = True
            i0 += 1
            i1 += 1
        else:
            if in_rotation[i0][0] not in get_ids(recently_added):
                print_song1(in_rotation[i0][1], '[WILL BE REMOVED (old and added manually, or removed from library)]', log)
                i0 += 1
            else:
                if not matched:
                    print_song2('[WILL BE ADDED (newly added song)]', recently_added[i1][1], log)
                    final_playlist.append(recently_added[i1])
                    i1 += 1
                else:
                    print_song2('[WILL REMAIN OUT (manually removed)]', recently_added[i1][1], log)
                    i1 += 1

    for i in range(i0, len(in_rotation)):
        if len(final_playlist) < 100:
            final_playlist.append(in_rotation[i])
            print_song1(in_rotation[i][1], '[WILL REMAIN (old but playlist < 100 songs)]', log)
        else:
            print_song1(in_rotation[i][1], '[WILL BE REMOVED (old and playlist >= 100 songs)]', log)
    for i in range(i1, len(recently_added)):
        print_song2('[WILL REMAIN OUT (manually removed)]', recently_added[i][1], log)

    sp.user_playlist_replace_tracks(user_id, PLAYLIST_ID, get_ids(final_playlist))
