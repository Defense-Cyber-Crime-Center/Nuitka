#     Copyright 2017, Kay Hayen, mailto:kay.hayen@gmail.com
#
#     Part of "Nuitka", an optimizing Python compiler that is compatible and
#     integrates with CPython, but also works on its own.
#
#     Licensed under the Apache License, Version 2.0 (the "License");
#     you may not use this file except in compliance with the License.
#     You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#     Unless required by applicable law or agreed to in writing, software
#     distributed under the License is distributed on an "AS IS" BASIS,
#     WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#     See the License for the specific language governing permissions and
#     limitations under the License.
#
""" Interface to depends.exe on Windows.

We use depends.exe to investigate needed DLLs of Python DLLs.

"""

import os
import sys
from logging import info

from nuitka import Tracing
from nuitka.__past__ import (  # pylint: disable=redefined-builtin
    raw_input,
    urlretrieve
)
from nuitka.utils import Utils
from nuitka.utils.FileOperations import deleteFile, makePath


def getDependsExePath():
    """ Return the path of depends.exe (for Windows).

        Will prompt the user to download if not already cached in AppData
        directory for Nuitka.
    """
    if Utils.getArchitecture() == "x86":
        depends_url = "http://dependencywalker.com/depends22_x86.zip"
    else:
        depends_url = "http://dependencywalker.com/depends22_x64.zip"

    if "APPDATA" not in os.environ:
        sys.exit("Error, standalone mode cannot find 'APPDATA' environment.")

    nuitka_app_dir = os.path.join(os.environ["APPDATA"], "nuitka")
    if not os.path.isdir(nuitka_app_dir):
        makePath(nuitka_app_dir)

    nuitka_depends_zip = os.path.join(
        nuitka_app_dir,
        os.path.basename(depends_url)
    )
    nuitka_depends_dir = os.path.join(
        nuitka_app_dir,
        Utils.getArchitecture()
    )
    depends_exe = os.path.join(
        nuitka_depends_dir,
        "depends.exe"
    )

    if not os.path.isfile(nuitka_depends_zip) and not os.path.isfile(depends_exe):
        Tracing.printLine("""\
Nuitka will make use of Dependency Walker (http://dependencywalker.com) tool
to analyze the dependencies of Python extension modules. Is it OK to download
and put it in APPDATA (no installer needed, cached, one time question).""")

        reply = raw_input("Proceed and download? [Yes]/No ")

        if reply.lower() in ("no", 'n'):
            sys.exit("Nuitka does not work in --standalone on Windows without.")

        info("Downloading '%s'" % depends_url)
        
        try:
            urlretrieve(
                depends_url,
                nuitka_depends_zip
            )
        except:
            sys.exit("Failed to download %s. Contents should manually be extracted to %s" % (depends_url, nuitka_depends_dir))

    if not os.path.isdir(nuitka_depends_dir):
        os.makedirs(nuitka_depends_dir)


    if not os.path.isfile(depends_exe):
        info("Extracting to '%s'" % depends_exe)

        import zipfile

        try:
            depends_zip = zipfile.ZipFile(nuitka_depends_zip)
            depends_zip.extractall(nuitka_depends_dir)
        except Exception: # Catching anything zip throws, pylint:disable=W0703
            info("Problem with the downloaded zip file, deleting it.")

            deleteFile(depends_exe, must_exist = False)
            deleteFile(nuitka_depends_zip, must_exist = True)

            sys.exit(
                "Error, need '%s' as extracted from '%s'." % (
                    depends_exe,
                    depends_url
                )
            )

    assert os.path.isfile(depends_exe)

    return depends_exe
