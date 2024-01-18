#!/usr/local/autopkg/python
#
# Copyright 2024 Ashe Night
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

# https://www.blender.org/download/release/Blender4.0/blender-4.0.2-macos-x64.dmg/
pre_mirror_url = 'https://www.blender.org/download/release/'
os_str = 'macos'
arch_str = ''

archs = {
    'arm64': 'arm64',
    'x86_64': 'x64'
}

__all__ = [ 'BlenderURLProvider' ]

class BlenderURLProvider( URLGetter ):
    description = __doc__

    # autopkg input
    input_variables = {
        'base_version' : {
            'required': True,
            'description': "Base blender version (format: 'x.y')"
        },
        'arch' : {
            'required': True,
            'description': "Specify architecture of the the environment ('x86_64', or 'arm64'))"
        }
    }

    # autopkg output
    output_variables = {
        'download_url': {
            'description': "URL for downloading the latest version of Blender"
        },
        'download_version': {
            'description': "Version of jre/jdk to from the download_url"
        }
    }


    def getDownloadURL( self ):
        # Combine mirror url with version specified from recipe
        release_url = '%s/Blender%s/' % ( pre_mirror_url, self.env['base_version'] )
        # Use the download feature of URLGetter
        release_index_page = self.download(release_url, text=True)

        # Time for regex
        # Grab all subversions available for our os / arch
        re_match_all_macos = re.compile(
            'blender-%s.\d-%s-%s.dmg' % ( self.env['base_version'], os_str,  arch_str )
        )
        matched_vers_for_arch = re.findall( re_match_all_macos, release_index_page )
        # Make sure we actually got something here
        if not matched_vers_for_arch:
            raise ProcessorError( 'No versions found with the base version provided %s and arch of %s' % ( self.env['base_version'], arch_str ) )
        # We've got something
        matched_vers_for_arch = sorted( matched_vers_for_arch, key = lambda tup: tup[1], reverse = True )
        


    def main( self ):
        # Check for valid arch
        if "%s" % self.env['arch'] in archs:
            # Set arch_string for sugar
            arch_str = '%s' % archs[self.env['arch']]
            # Grab URL based on arch
            self.output( 'Getting URL for Blender %s for %s (%s)', ( self.env['base_version'], os_str, self.env['arch'] ) )
            try:
                self.getDownloadURL()
            except Exception as err:
                raise ProcessorError(err)

            
if __name__ == "__main__":
    PROCESSOR = BlenderURLProvider()
    PROCESSOR.execute_shell()