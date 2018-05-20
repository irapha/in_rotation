import spotipy
import spotipy.util as util

from spotipy.oauth2 import SpotifyClientCredentials
from secret import USER_EMAIL, CLIENT_ID, CLIENT_SECRET


if __name__ == '__main__':
    scope = 'user-library-read'
    token = util.prompt_for_user_token(USER_EMAIL, scope,
            client_id=CLIENT_ID, client_secret=CLIENT_SECRET, redirect_uri='http://localhost/')

    sp = spotipy.Spotify(auth=token)

    user_id = sp.current_user()['id']
    all_playlists = []
    for i, p in enumerate(sp.user_playlists(user_id)['items']):
        print('{0:03d} {1}'.format(i, p['name']))
        all_playlists.append(p)

    p_idx = int(input('Which playlist you want to use? (number in list above) '))
    print('Use playlist id: {}'.format(all_playlists[p_idx]['id']))
