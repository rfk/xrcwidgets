# Copyright 2004, Ryan Kelly
# Released under the terms of the wxWindows Licence, version 3.
# See the file 'lincence/preamble.txt' in the main distribution for details.

inherit distutils

DESCRIPTION="XRCWidgets is a rapid GUI development framework for wxPython."
SRC_URI="http://www.rfk.id.au/software/projects/XRCWidgets/rel_0_1_1_alpha1/XRCWidgets-0.1.1_alpha1.tar.gz"
HOMEPAGE="http://www.rfk.id.au/software/projects/XRCWidgets/"

IUSE=""
SLOT="0"
KEYWORDS="~x86"
LICENSE="wxWinLL-3"

DEPEND=">=dev-lang/python-2.3
        >=dev-python/wxPython-2.4.2.4"

src_install() {

	distutils_src_install
	distutils_python_version

}




