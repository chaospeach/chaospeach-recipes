#!/usr/local/autopkg/python
#
# Copyright 2022 Ashe Night
#
# Licensed under the Educational Community License, Version 2.0 (ECL-2.0);
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://opensource.org/licenses/ECL-2.0
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
    """ Retrieves latest version of specified jdk/jre from Azul and returns the link """

    description = __doc__

    input_variables = {
        "base_version": {
            "required": True,
            "description": "Base jdk/jre version to check for. Varying granularity can be used."
        },
        "arch": {
            "reqiured": True,
            "description": "Specify architecture of the the environment"
        },
        "environment": {
            "required": False,
            "description": "Spe",
            "default": "jre"
        }
    }

    output_variables = {
        "download_url": {
            "description": "URL for downloading the latest version of jre/jdk"
        },
        "download_version": {
            "description": "Version of jre/jdk to from the download_url"
        }
    }

    def getDownloadURL(self):
        """ Download the directory listing at BASE_URL"""

        # Use the download feature of URLGetter (yay subclasses)
        version_page = self.download(BASEURL, text=True)

        # Craft regex to scrape for our specified version (returns tuples)
        version_arch = ARCHITECTURES[self.env["arch"]]
        re_basever = "%s".replace(".", "\.") % self.env["base_version"]
        re_match = re.compile("\"zulu(.*)-ca-(%s%s.*)-%s_%s.dmg\"" % ( self.env["environment"], re_basever, OS, version_arch ))
        version_matches = re.findall(re_match, version_page)
        self.output("Looking versions for %s (%s)" % ( self.env["base_version"], version_arch ))

        # Ensure we found something, otherwise there isn't anything available for that base_version
        if not version_matches:
            raise ProcessorError("No versions found with the base version %s and architecture of %s" % ( self.env["base_version"], self.env["arch"] ))
        # Sort and pull latest version
        version_matches = sorted(version_matches, key=lambda tup: tup[1], reverse=True)
        version_latest = version_matches[0]
        self.env["download_version"] = version_latest[0]
        self.output("Latest version of (%s) is %s. zulu-%s" % ( self.env['base_version'], version_latest[1], version_latest[0] ))

        # Assemble latest components into a filename, and set output download_url 
        latest_url = "%szulu%s-ca-%s-%s_%s.dmg" % ( BASEURL, version_latest[0], version_latest[1], OS, version_arch )
        self.env['download_url'] = latest_url
        self.output("download_url: %s" % self.env["download_url"])

    def main(self):
        # Check if we received a valid architecture
        if "%s" % self.env["arch"] in ARCHITECTURES:
            self.output("Getting %s %s for %s (%s)" % ( self.env["environment"], self.env["base_version"], self.env["arch"], OS ))
            try:
                self.getDownloadURL()
            except Exception as err:
                raise ProcessorError(err)
        else:
            raise ProcessorError("%s is an invalid architecture" % self.env["arch"])
    
if __name__ == "__main__":
    PROCESSOR = AzulURLProvider()
    PROCESSOR.execute_shell()
