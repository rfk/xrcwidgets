#
#  Distutils Setup Script for XRCWidgets
#

from distutils.core import setup

NAME = "XRCWidgets"

VER_MAJOR = "0"
VER_MINOR = "9"
VER_REL = "b1"
VER_PATCH = ""

DESCRIPTION = "XRCWidgets GUI Development Framework"
AUTHOR = "Ryan Kelly"
AUTHOR_EMAIL = "ryan@rfk.id.au"
URL="http://www.rfk.id.au/"


PACKAGES=['XRCWidgets']


DATA_FILES=[('share/XRCWidgets/examples',
                    ['examples/simple.py',
                     'examples/simple.xrc']),
            ('share/XRCWidgets/docs',
                    ['docs/manual.pdf',
                     'docs/manual.ps']),
           ]


setup(name=NAME,
      version="%s.%s%s%s" % (VER_MAJOR,VER_MINOR,VER_REL,VER_PATCH),
      description=DESCRIPTION,
      author=AUTHOR,
      author_email=AUTHOR_EMAIL,
      url=URL,
      packages=PACKAGES,
      data_files=DATA_FILES,
     )

