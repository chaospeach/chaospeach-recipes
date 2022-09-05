#!/usr/local/autopkg/python
#
# Copyright 2022
#

import re

from autopkglib import ProcessorError
from autopkglib.URLGetter import URLGetter

BASEURL = "https://cdn.azul.com/zulu/bin/"
OS="macosx"

ARCHITECTURES = {
    "arm64": "aarch64",
    "x86_64": "x64"
}

__all__ = ["AzulURLProvider"]

class AzulURLProvider(URLGetter):

    description = __doc__

    input_variables = {
        "ver": {
            "required": True,
            "description": "JRE Version, e.g., '17.0.0' for 17 (LTS)"
        },
        "arch": {
            "reqiured": True,
            "description": "Specify architecture of the JRE"
        }
    }

    output_variables = {
        "downloadURL": {
            "description": "URL for downloading the latest version of JRE"
        }
    }

    def versionToGet(self):
        vers = "%s" % self.env["ver"]
        vers = vers.replace(".", "\.")
        re_arch = ARCHITECTURES[self.env["arch"]]
        re_one = re.compile("(zulu).*(-ca-jre%s-%s_%s).*\.dmg" % ( vers, OS, re_arch ))

        return "zulu17.38.1-ca-jre17.0.0-macoxs_aarch64.dmg"

    def getVersionList(self):
        self.output("Retrieving version page...")


    def getDownloadURL(self):
        fullVers = self.versionToGet()
        jre_dmg = ""
        download_url = "%s/%s" % ( BASEURL, jre_dmg )


    def main(self):
        if "%s" % self.env["arch"] in ARCHITECTURES:
            self.output("Getting JRE %s for %s (%s)" % ( self.env["ver"], self.env["arch"], OS ))
        else:
            raise ProcessorError("%s is an invalid architecture")
    



if __name__ == "__main__":
    PROCESSOR = AzulURLProvider()
    PROCESSOR.execute_shell()
