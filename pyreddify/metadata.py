from dataclasses import dataclass
from typing import Optional, Tuple


@dataclass(frozen=True)
class Metadata:
    metadata: dict


@dataclass(frozen=True)
class Base(Metadata):
    "Base Class for Types"

    id: Optional[str] = None
    uri: Optional[str] = None
    name: Optional[str] = None

    def __post_init__(self):
        object.__setattr__(self, 'id', self.metadata['id'])
        object.__setattr__(self, 'uri', self.metadata['uri'])
        object.__setattr__(self, 'name', self.metadata['name'])


@dataclass(frozen=True)
class Album(Base):
    art: Optional[str] = None
    release: Optional[str] = None
    total_tracks: Optional[Tuple[str, int]] = None
    
    def __post_init__(self):
        object.__setattr__(self, 'art', self.metadata['images'][0]['url'])
        object.__setattr__(self, 'released', self.metadata['release_date'])
        object.__setattr__(self, 'total_tracks', self.metadata['total_tracks'])

@dataclass(frozen=True)
class Track(Base):
    pass


@dataclass(frozen=True)
class Artist(Base):
    pass


@dataclass(frozen=True)
class SpotifyTrackItem(Metadata):
    "Builds Dataclass for a Spotify result item."

    artist      : Optional[Artist] = None
    album       : Optional[Album] = None
    track       : Optional[Track] = None

    def __post_init__(self):
        assert self.metadata['type'] == 'track'
        object.__setattr__(self, 'track', Track(metadata=self.metadata))
        object.__setattr__(self, 'artist', Artist(metadata=self.metadata['artists'][0]))
        object.__setattr__(self, 'album', Album(metadata=self.metadata['album']))
