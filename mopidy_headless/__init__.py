from __future__ import unicode_literals

import os

from mopidy import config, ext


__version__ = '0.2.0'


class Extension(ext.Extension):
    dist_name = 'Mopidy-Headless'
    ext_name = 'headless'
    version = __version__

    def get_default_config(self):
        conf_file = os.path.join(os.path.dirname(__file__), 'ext.conf')
        return config.read(conf_file)

    def get_config_schema(self):
        schema = super(Extension, self).get_config_schema()
        schema['device'] = config.String()
        schema['enable_numbers'] = config.Boolean()
        schema['volume_up'] = config.List()
        schema['volume_down'] = config.List()
        schema['next_song'] = config.List()
        schema['previous_song'] = config.List()
        schema['next_playlist'] = config.List()
        schema['previous_playlist'] = config.List()
        schema['play'] = config.List()
        schema['pause'] = config.List()
        schema['playpause'] = config.List()
        schema['mute'] = config.List()
        schema['shuffle'] = config.List()
        return schema

    def setup(self, registry):
        from .frontend import InputFrontend
        registry.add('frontend', InputFrontend)
