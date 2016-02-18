Mopidy Headless
===============

Mopidy headless makes it possible to connect a HID (Human Interface Device), like a remote or a keyboard, to a Mopidy server.

Use ir-keytable from lirc to see which keycodes are supported::

    # ir-keytable -td /dev/input/...

Configuration
-------------

The default config is the following::

    [headless]
    enabled = true

    device = ;needs to be set

    enable_numbers = true

    volume_up = KEY_VOLUMEUP
    volume_down = KEY_VOLUMEDOWN
    next_song = KEY_RIGHT, KEY_NEXTSONG
    previous_song = KEY_PREVIOUSSONG, KEY_LEFT
    play = KEY_PLAY
    pause = KEY_PAUSE
    playpause = KEY_ENTER
    mute = KEY_MUTE
    next_playlist = KEY_CHANNELDOWN, KEY_DOWN
    previous_playlist = KEY_CHANNELUP, KEY_UP
    shuffle = KEY_RECORD

The device is found in /dev/input.

By default the numpad of the remote is bound to the corresponding playlists on your Mopidy installation. Disable this by setting enable_numbers to false.

Make sure that the user running mopidy can read from the device you want to use. See http://puredata.info/docs/faq/how-can-i-set-permissions-so-hid-can-read-devices-in-gnu-linux to allow a non-root user to read from input devices.
