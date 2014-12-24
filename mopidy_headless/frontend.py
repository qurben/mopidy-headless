
from __future__ import unicode_literals

import logging

from mopidy import core

import pykka

from .input import InputThread, Handler

logger = logging.getLogger(__name__)

class KeyHandler(Handler):
  def __init__(self, device_fn, event_code, actor_ref, longpress=5):
    super(KeyHandler, self).__init__(device_fn, "EV_KEY", event_code)
    self.actor_proxy=actor_ref.proxy()
    self.longpress=longpress

  def handle(self, event):
    if (event.value==1):
      self.timestamp=event.sec
    if (event.value==0):
      diff=event.sec-self.timestamp
      if (diff>self.longpress):
        self.longpress(self.actor_proxy)
      else:
        self.press(self.actor_proxy)

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

  def longpress(self, actor_proxy):
    actor_proxy.halt()

class InputFrontend(pykka.ThreadingActor, core.CoreListener):
    def __init__(self, config, core):
        super(InputFrontend, self).__init__()
        self.config = config['headless']
        self.core=core

        self.selected_playlist = None
        self.playlists = None
        
    def on_start(self):
        self.playlists_loaded()
        device = self.config["device"]
        
        self.inputthread=InputThread()
        self.inputthread.registerHandler(PlayHandler(device, self.config["play"], self.actor_ref))
        self.inputthread.registerHandler(PauseHandler(device, self.config["pause"], self.actor_ref))
        self.inputthread.registerHandler(PlayPauseHandler(device, self.config["playpause"], self.actor_ref))
        self.inputthread.registerHandler(VolumeUpHandler(device, self.config["volume_up"], self.actor_ref))
        self.inputthread.registerHandler(VolumeDownHandler(device, self.config["volume_down"], self.actor_ref))
        self.inputthread.registerHandler(NextSongHandler(device, self.config["next_song"], self.actor_ref))
        self.inputthread.registerHandler(PreviousSongHandler(device, self.config["previous_song"], self.actor_ref))
        self.inputthread.registerHandler(NextPlaylistHandler(device, self.config["next_playlist"], self.actor_ref))
        self.inputthread.registerHandler(PreviousPlaylistHandler(device, self.config["previous_playlist"], self.actor_ref))
        self.inputthread.registerHandler(MuteHandler(device, self.config["mute"], self.actor_ref))
        self.inputthread.start()

    def on_stop(self):
        self.inputthread.stop()

    def halt(self):
        print("Goodbye")

    def change_volume(self, value):
      volume=self.core.playback.volume.get()+value
      if volume<0:
          volume=0
      elif volume>100:
          volume=100
          
      logger.debug("Volume changed: {0}".format(volume))
      self.core.playback.volume=volume
    
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

    def playpause_toggle(self):
        if self.core.playback.state.get()==core.PlaybackState.PLAYING:
            self.core.playback.pause()
        else:
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
