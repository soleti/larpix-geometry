'''
Generate a YAML file with the pixel layout and chip connections for the
packaged 10x10 pixel tile

Differs from 2.4.1 because it uses chip keys rather than chip ids (different format_version)

'''
import os
import yaml
import importlib.util

format_version = '1.0.0' # use chip keys

spec = importlib.util.spec_from_file_location('layout', os.path.join(os.path.dirname(__file__),'layout-2.4.0.py'))
layout = importlib.util.module_from_spec(spec)
spec.loader.exec_module(layout)

chips = [('1-1-{}'.format(chipid),channels) for chipid,channels in layout.chips]

with open('layout-2.4.1.yaml', 'w') as f:
    yaml.dump({'format_version': format_version, 'pixels': layout.pixels, 'chips': chips, 'x': -layout.width/2, 'y': -layout.height/2,
        'width': layout.width, 'height': layout.height}, f)
