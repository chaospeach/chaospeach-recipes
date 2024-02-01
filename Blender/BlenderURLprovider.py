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

archs = {
    'arm64': 'arm64',
    'x86_64': 'x64'
}

__all__ = [ 'BlenderURLProvider' ]

class BlenderURLProvider( URLGetter ):
    description = __doc__

    # autopkg input
    input_variables = {
        'arch' : {
            'required': True,
            'description': "Specify architecture of the the environment ('x86_64', or 'arm64'))"
        },
        'base_version' : {
            'required': True,
            'description': "Base blender version (format: 'x.y')"
        },
        'mirror_override_url' : {
            'required': True,
            'description': "Use the specified mirror URL (incl. trailing '/', exclude 'BlenderX.Y')"
        }
    }

    # autopkg output
    output_variables = {
        'download_url': {
            'description': "URL for downloading the latest version of Blender"
        },
        'download_version': {
            'description': "Version of jre/jdk to from the download_url"
        },
        'download_file': {
            'description': "Full filename of download"
        }
    }

    def getDownloadURL( self ):
        # Combine mirror url with version specified from recipe
        release_url = '%sBlender%s/' % ( pre_mirror_url, self.env['base_version'] )
        if '%s' % self.env['mirror_override_url']:
            # We're overriding the mirror
            release_override_url = ( '%sBlender%s/' % ( self.env['mirror_override_url'], self.env['base_version'] ) )
            release_index_page = self.download( release_override_url, text=True )
        else:
            # Use the download feature of URLGetter
            release_index_page = self.download( release_url, text=True )
        
        # Time for regex
        # Grab all subversions available for our os / arch
        re_match_all_macos = re.compile(
            '\"blender-%s.\d-%s-%s\.dmg\"' % ( self.env['base_version'], os_str,  archs[self.env['arch']] )
        )
        matched_vers_for_arch = re.findall( re_match_all_macos, release_index_page )

        # Make sure we actually got something here
        if not matched_vers_for_arch:
            raise ProcessorError( 'No versions found with the base version provided %s (%s)' % ( self.env['base_version'], archs[self.env['arch']] ) )
        
        # We've got something, sort for latest (second entry when split by '-')
        matched_vers_for_arch = sorted( matched_vers_for_arch, key = lambda s: s.split('-')[1], reverse = True )
        self.output( 'Found %s versions for %s (%s)' % ( len(matched_vers_for_arch), self.env['base_version'], archs[self.env['arch']] ) )
        matched_latest_vers_item = matched_vers_for_arch[0]
        matched_latest_vers_dmg = matched_latest_vers_item.replace( '\"', '' )
        matched_latest_vers = matched_latest_vers_dmg.split( '-' )[1]
        self.env['download_file'] = matched_latest_vers_dmg
        self.env['download_version'] = matched_latest_vers
        self.output( 'Latest version of (%s) is %s.' % ( self.env['base_version'], matched_latest_vers ) )

        # We have what we need, craft the URL
        if '%s' % self.env['mirror_override_url']:
            # Override if provided
            latest_vers_url = self.env['mirror_override_url'] + 'Blender' + self.env['base_version'] + '/' + matched_latest_vers_dmg
        else:
            # Use Blender URL
            latest_vers_url = pre_mirror_url + 'Blender' + self.env['base_version'] + '/' + matched_latest_vers_dmg
        self.env['download_url'] = latest_vers_url
        self.output( 'URL for %s (%s) is: %s' % ( matched_latest_vers_dmg[1], archs[self.env['arch']], latest_vers_url ) )
        
    def main( self ):
        # Check for valid arch
        if '%s' % self.env['arch'] in archs:
            # Grab URL based on arch
            self.output( 'Getting URL for Blender %s for %s (%s)' % ( self.env['base_version'], os_str, self.env['arch'] ) )
            try:
                self.getDownloadURL()
            except Exception as err:
                raise ProcessorError(err)

            
if __name__ == '__main__':
    PROCESSOR = BlenderURLProvider()
    PROCESSOR.execute_shell()