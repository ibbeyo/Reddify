from dataclasses import dataclass, field


@dataclass(frozen=True)
class TrackItem:
    id: str
    uri: str
    name: str


@dataclass(frozen=True)
class ArtistItem(TrackItem):
    pass


@dataclass(frozen=True)
class AlbumItem(TrackItem):
    art: str
    release_date: str
    total_tracks: str


@dataclass(frozen=True)
class TrackType:
    item    : dict
    artist  : ArtistItem = field(default=None)
    album   : AlbumItem = field(default=None)
    track   : TrackItem = field(default=None)

    def __post_init__(self):
        assert self.item['type'] == 'track'

        _track  = self.item
        _album  = self.item['album']
        _artist = self.item['artists'][0]

        object.__setattr__(
            self, 'track', TrackItem(_track['id'], _track['uri'], _track['name'])
        )
        object.__setattr__(
            self, 'artist', ArtistItem(_artist['id'], _artist['uri'], _artist['name'])
        )
        object.__setattr__(
            self, 'album', AlbumItem(
                _album['id'], _album['uri'], _album['name'],
                _album['images'][0]['url'], _album['release_date'], _album['total_tracks']
            )
        )
