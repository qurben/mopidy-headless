Mopidy Headless
==============

Mopidy headless makes it possible to connect a HID (Human Interface Device), like a remote or a keyboard, to a Mopidy server.

Use ir-keytable from lirc to see which keycodes are supported::

    # ir-keytable -td /dev/input/event<X>
    
Configuration
-------

The default config is the following::

    [headless]
    enabled = true
    
    device = /dev/input/event11
    
    volume_up = KEY_VOLUMEUP
    volume_down = KEY_VOLUMEDOWN
    next_song = KEY_NEXTSONG
    previous_song = KEY_PREVIOUSSONG
    play = KEY_PLAY
    pause = KEY_PAUSE
    mute = KEY_MUTE
    next_playlist = KEY_CHANNELDOWN
    previous_playlist = KEY_CHANNELUP
    
The device is found in /dev/input.

Make sure that the user running mopidy can read from the device you want to use. See http://puredata.info/docs/faq/how-can-i-set-permissions-so-hid-can-read-devices-in-gnu-linux to allow a non-root user to read from input devices.
