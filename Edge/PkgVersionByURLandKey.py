#!/usr/local/autopkg/python
#
# Copyright 2022
# based on MSOfficeMacURLandUpdateInfoProvider.py by Allister Banks and Tim Sutton
#
import plistlib
from typing import Dict, List

from autopkglib import ProcessorError
from autopkglib.URLGetter import URLGetter

__all__ = ["PkgVersionByURLandKey"]

class PkgVersionByURLandKey(URLGetter):
    """
        This is a much simpler version of the OfficeMacURL[...] processor.
        Using prefabbed URLs it will pull plist data, and extract a version 
        from a key you specify.
    """

    description= __doc__

    input_variables = {
        "url": {
            "required": True,
            "description": "URL to query to retrieve update plist."
        },
        "key": {
            "required": True,
            "description": "Specify key to pull version data from."
        },
        "arch": {
            "required": True,
            "description": "Architecture for User-Agent. Not entirely sure this makes a difference."
        }
    }

    output_variables = {
        "version": {
            "description": "Version extracted from MS metadata"
        }
    }

    def pullPlist(self):

        arch = self.env["arch"]

        self.output("Using %s architecture for user agent." % arch)
        headers = {
            "User-Agent": (
                "Microsoft%20AutoUpdate/3.6.16080300 CFNetwork/"
                "760.6.3 Darwin/15.6.0 ("+arch+")"
            )
        }
        plist_url = self.env["url"]
        plist_key = self.env["key"]

        self.output("Downloading plist...")
        plist = self.download(plist_url, headers)
        metadata = plistlib.loads(plist)

        self.output("Parsed plist, determining what we have...")
        if isinstance(metadata, List):
            """ Not ideal, but it works based on the use-case """
            data = metadata[0]
        elif isinstance(metadata, Dict):
            data = metadata
        else:
            raise ProcessorError("Invalid plist loaded")

        self.output("Extracting version using [%s] as key." % plist_key)
        latest = data.get(plist_key)
        self.env["version"] = latest
        self.output("Extracted version is %s" % self.env["version"])

        
    def main(self):
        try: 
            self.output("Searching for plist at URL: %s" % self.env["url"])
            self.pullPlist()
        except Exception as err:
            raise ProcessorError(err)


if __name__ == "__main__":
    PROCESSOR = PkgVersionByURLandKey()
    PROCESSOR.execute_shell()
    