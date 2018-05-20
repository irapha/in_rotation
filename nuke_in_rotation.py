import spotipy
import spotipy.util as util

from spotipy.oauth2 import SpotifyClientCredentials
from secret import USER_EMAIL, CLIENT_ID, CLIENT_SECRET, PLAYLIST_ID
from pprint import pprint
from util import get_recently_added, get_ids


if __name__ == '__main__':
    print('this script will erase your in rotation and start it over with the ' +
          'latest 100 songs added.')

    scope = 'user-library-read playlist-modify-public'
    token = util.prompt_for_user_token(USER_EMAIL, scope,
            client_id=CLIENT_ID, client_secret=CLIENT_SECRET, redirect_uri='http://localhost/')
    sp = spotipy.Spotify(auth=token)
    user_id = sp.current_user()['id']

    recently_added_ids = get_ids(get_recently_added(sp, at_least_100=True))
    sp.user_playlist_replace_tracks(user_id, PLAYLIST_ID, recently_added_ids)
