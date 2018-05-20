from datetime import datetime, timedelta
from secret import PLAYLIST_ID


def get_in_rotation(sp, user_id):
    """Returns the tracks in your In Rotation playlist."""
    in_rotation = []
    tracks = sp.user_playlist(user_id, PLAYLIST_ID)['tracks']
    for track in tracks['items']:
        added_on = datetime.strptime(track['added_at'], '%Y-%m-%dT%H:%M:%SZ')
        in_rotation.append((track['track']['id'], track['track']['name'], added_on))
    while tracks['next']:
        tracks = sp.next(tracks)
        for track in tracks['items']:
            added_on = datetime.strptime(track['added_at'], '%Y-%m-%dT%H:%M:%SZ')
            in_rotation.append((track['track']['id'], track['track']['name'], added_on))

    return in_rotation

def get_ids(tracks):
    """Returns the ids of the tracks in a list."""
    if tracks:
        return list(zip(*tracks))[0]
    return []

def get_recently_added(sp, at_least_100=False):
    """Returns a list of all tracks added in the last 2 weeks."""
    two_weeks_ago = datetime.now() - timedelta(days=14)
    found_over_2_weeks = False

    recently_added = []
    tracks = sp.current_user_saved_tracks(limit=50)

    for track in tracks['items']:
        added_on = datetime.strptime(track['added_at'], '%Y-%m-%dT%H:%M:%SZ')

        if added_on > two_weeks_ago or (at_least_100 and len(recently_added) < 100):
            recently_added.append((track['track']['id'], track['track']['name'], added_on))
        else:
            found_over_2_weeks = True

    while tracks['next'] and not found_over_2_weeks:
        tracks = sp.next(tracks)

        for track in tracks['items']:
            added_on = datetime.strptime(track['added_at'], '%Y-%m-%dT%H:%M:%SZ')

            if added_on > two_weeks_ago or (at_least_100 and len(recently_added) < 100):
                recently_added.append((track['track']['id'], track['track']['name'], added_on))
            else:
                found_over_2_weeks = True

    return recently_added

