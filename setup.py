# Copyright 2004, Ryan Kelly
# Released under the terms of the wxWindows Licence, version 3.
# See the file 'lincence/preamble.txt' in the main distribution for details.


#
#  Distutils Setup Script for XRCWidgets
#

from distutils.core import setup
import os

NAME = "XRCWidgets"

VER_MAJOR = "0"
VER_MINOR = "1"
VER_REL = "5"
VER_PATCH = ""

DESCRIPTION = "XRCWidgets GUI Development Framework"
AUTHOR = "Ryan Kelly"
AUTHOR_EMAIL = "ryan@rfk.id.au"
URL="http://www.rfk.id.au/software/projects/XRCWidgets/"


PACKAGES=['XRCWidgets']


DATA_FILES=[('share/XRCWidgets/docs',
                    ['docs/manual.pdf',
                     'docs/manual.ps']),
            ('share/XRCWidgets/docs/licence',
                    ['licence/lgpl.txt',
                     'licence/licence.txt',
                     'licence/licendoc.txt',
                     'licence/preamble.txt']),
           ]
# Locate and include all files in the 'examples' directory
_EXAMPLES = []
for eName in os.listdir("examples"):
    if eName.endswith(".py") or eName.endswith(".xrc"):
        _EXAMPLES.append("examples/%s" % eName)
DATA_FILES.append(("share/XRCWidgets/examples",_EXAMPLES))


setup(name=NAME,
      version="%s.%s.%s%s" % (VER_MAJOR,VER_MINOR,VER_REL,VER_PATCH),
      description=DESCRIPTION,
      author=AUTHOR,
      author_email=AUTHOR_EMAIL,
      url=URL,
      packages=PACKAGES,
      data_files=DATA_FILES,
     )

