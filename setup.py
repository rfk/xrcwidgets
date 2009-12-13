#
# Copyright 2004-2009, Ryan Kelly
# Released under the terms of the MIT Licence.
# See the file 'LICENSE.txt' in the main distribution for details.


from distutils.core import setup
import os


XRCWidgets = {}
try:
    execfile("XRCWidgets/__init__.py",XRCWidgets)
except ImportError:
    pass


NAME = "XRCWidgets"
VERSION = XRCWidgets["__version__"]
DESCRIPTION = "Rapid GUI Development Framework using wxPython and XRC"
AUTHOR = "Ryan Kelly"
AUTHOR_EMAIL = "ryan@rfk.id.au"
URL="http://www.rfk.id.au/software/XRCWidgets/"
LICENSE="MIT"


PACKAGES=['XRCWidgets']


DATA_FILES=[]

# Locate and include all files in the 'examples' directory
_EXAMPLES = []
for eName in os.listdir("examples"):
    ext = eName.split(".")[-1]
    if ext in (".py",".xrc",".bmp"):
        _EXAMPLES.append("examples/%s" % eName)
DATA_FILES.append(("share/XRCWidgets/examples",_EXAMPLES))


setup(name=NAME,
      version=VERSION,
      description=DESCRIPTION,
      author=AUTHOR,
      author_email=AUTHOR_EMAIL,
      url=URL,
      license=LICENSE,
      packages=PACKAGES,
      data_files=DATA_FILES,
     )

