from __future__ import unicode_literals

import logging

from mopidy import core

from evdev import ecodes

import pykka

from .input import InputThread, Handler

logger = logging.getLogger(__name__)


class KeyHandler(Handler):
    def __init__(self, device_fn, event_code, actor_ref, longpress=5):
        super(KeyHandler, self).__init__(device_fn, "EV_KEY", event_code)
        self.actor_proxy = actor_ref.proxy()
        self.longpress = longpress
        self.timestamp = None

    def handle(self, event):
        if event.value == 0:
            self.press(self.actor_proxy)

    def press(self, actor_proxy):
        pass


class VolumeUpHandler(KeyHandler):
    def press(self, actor_proxy):
        actor_proxy.change_volume(5)


class VolumeDownHandler(KeyHandler):
    def press(self, actor_proxy):
        actor_proxy.change_volume(-5)


class NextSongHandler(KeyHandler):
    def press(self, actor_proxy):
        actor_proxy.next_song()


class PreviousSongHandler(KeyHandler):
    def press(self, actor_proxy):
        actor_proxy.previous_song()


class NextPlaylistHandler(KeyHandler):
    def press(self, actor_proxy):
        actor_proxy.next_playlist()


class PreviousPlaylistHandler(KeyHandler):
    def press(self, actor_proxy):
        actor_proxy.previous_playlist()


class PlayHandler(KeyHandler):
    def press(self, actor_proxy):
        actor_proxy.play()


class PauseHandler(KeyHandler):
    def press(self, actor_proxy):
        actor_proxy.pause()


class PlayPauseHandler(KeyHandler):
    def press(self, actor_proxy):
        actor_proxy.playpause_toggle()


class MuteHandler(KeyHandler):
    def press(self, actor_proxy):
        actor_proxy.toggle_mute()

class ShuffleHandler(KeyHandler):
    def press(self, actor_proxy):
        actor_proxy.toggle_shuffle()

class PlaylistHandler(KeyHandler):
    def __init__(self, device_fn, actor_ref, longpress=5):
        self.event_keys = ['KEY_0', 'KEY_1', 'KEY_2', 'KEY_3', 'KEY_4', 'KEY_5', 'KEY_6', 'KEY_7', 'KEY_8', 'KEY_9']
        super(PlaylistHandler, self).__init__(device_fn, self.event_keys, actor_ref)

        self.event_codes = [ecodes.ecodes[key] for key in self.event_keys]

    def handle(self, event):
        self.actor_proxy.set_playlist(self.event_codes.index(event.code))


class InputFrontend(pykka.ThreadingActor, core.CoreListener):
    def __init__(self, config, core):
        super(InputFrontend, self).__init__()
        self.config = config['headless']
        self.core = core

        self.selected_playlist = None
        self.playlists = None
        self.inputthread = None

    def on_start(self):
        self.playlists_loaded()
        device = self.config["device"]

        self.inputthread = InputThread()
        self.inputthread.register_handlers([
            PlayHandler(device, self.config["play"], self.actor_ref),
            PauseHandler(device, self.config["pause"], self.actor_ref),
            PlayPauseHandler(device, self.config["playpause"], self.actor_ref),
            VolumeUpHandler(device, self.config["volume_up"], self.actor_ref),
            VolumeDownHandler(device, self.config["volume_down"], self.actor_ref),
            NextSongHandler(device, self.config["next_song"], self.actor_ref),
            PreviousSongHandler(device, self.config["previous_song"], self.actor_ref),
            NextPlaylistHandler(device, self.config["next_playlist"], self.actor_ref),
            PreviousPlaylistHandler(device, self.config["previous_playlist"], self.actor_ref),
            MuteHandler(device, self.config["mute"], self.actor_ref),
            ShuffleHandler(device, self.config["shuffle"], self.actor_ref),
            PlaylistHandler(device, self.actor_ref),
        ])
        self.inputthread.start()

    def on_stop(self):
        self.inputthread.stop()

    def change_volume(self, value):
        volume = self.core.playback.volume.get() + value
        if volume < 0:
            volume = 0
        elif volume > 100:
            volume = 100

        logger.debug("Volume changed: {0}".format(volume))
        self.core.playback.volume = volume

    def next_song(self):
        self.core.playback.next()

    def previous_song(self):
        self.core.playback.previous()

    def change_playlist(self, value):
        self.selected_playlist = (self.selected_playlist + value) % len(self.playlists)
        self.core.tracklist.clear()
        self.core.tracklist.add(uri=self.playlists[self.selected_playlist].uri)
        self.core.playback.play()

    def next_playlist(self):
        self.change_playlist(1)

    def previous_playlist(self):
        self.change_playlist(-1)

    def play(self):
        self.core.playback.play()

    def pause(self):
        self.core.playback.pause()

    def toggle_shuffle(self):
        self.core.playback.set_random(not self.core.playback.get_random())

    def playpause_toggle(self):
        if self.core.playback.state.get() == core.PlaybackState.PLAYING:
            self.core.playback.pause()
        else:
            self.core.playback.play()

    def set_playlist(self, playlist_nr):
        playlist = self.core.playlists.as_list()[playlist_nr]
        self.core.tracklist.clear()
        self.core.tracklist.add(uri=playlist)
        self.core.playback.play()

    def toggle_mute(self):
        mute = not self.core.playback.mute.get()
        logger.debug("Muted: {0}".format(mute))
        self.core.playback.mute = mute

    def playlists_loaded(self):
        self.playlists = []
        for playlist in self.core.playlists.playlists.get():
            self.playlists.append(playlist)
        self.selected_playlist = 0
