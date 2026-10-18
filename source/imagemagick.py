"""Select the installed ImageMagick 7 or 6 command without installing anything."""
import shutil


def command(*args):
    if shutil.which('magick'):
        return ['magick', *args]
    if args and args[0] == 'identify' and shutil.which('identify'):
        return ['identify', *args[1:]]
    if shutil.which('convert'):
        return ['convert', *args]
    raise RuntimeError('ImageMagick is required: install version 7 or version 6.')
