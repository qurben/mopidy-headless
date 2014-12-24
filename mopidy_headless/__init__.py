from __future__ import unicode_literals

import os

from mopidy import config, ext


__version__ = '0.0.1'


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
        schema['volume_up'] = config.String()
        schema['volume_down'] = config.String()
        schema['next_song'] = config.String()
        schema['previous_song'] = config.String()
        schema['next_playlist'] = config.String()
        schema['previous_playlist'] = config.String()
        schema['play'] = config.String()
        schema['pause'] = config.String()
        schema['mute'] = config.String()
        schema['playpause'] = config.List()
        return schema

    def setup(self, registry):
        from .frontend import InputFrontend
        registry.add('frontend', InputFrontend)
