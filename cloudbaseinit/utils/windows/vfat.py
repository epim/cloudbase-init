# Copyright 2015 Cloudbase Solutions Srl
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import os

from cloudbaseinit import exception
from cloudbaseinit.openstack.common import log as logging

from oslo.config import cfg


opts = [
    cfg.StrOpt('mtools_path', default=None,
               help='Path to "mtools" program suite, used for interacting '
                    'with VFAT filesystems'),
]

CONF = cfg.CONF
CONF.register_opts(opts)
LOG = logging.getLogger(__name__)


def _check_mtools_path():
    if not CONF.mtools_path:
        raise exception.CloudbaseInitException(
            '"mtools_path" needs to be provided in order '
            'to access VFAT drives')


def is_vfat_drive(osutils, drive_path):
    """Check if the given drive contains a VFAT filesystem."""
    _check_mtools_path()
    mdir = os.path.join(CONF.mtools_path, "mdir.exe")
    args = [mdir, "-/", "-b", "-i", drive_path, "/"]
    _, _, exit_code = osutils.execute_process(args, shell=False)
    if exit_code:
        LOG.warning("%r is not a VFAT location.", drive_path)
        return

    return True


def copy_from_vfat_drive(osutils, drive_path, target_path):
    """Copy everything from the given VFAT drive into the given target."""
    _check_mtools_path()
    cwd = os.getcwd()
    try:
        os.chdir(target_path)

        # A mcopy call looks like this:
        #
        # mcopy -n -i \\.\PHYSICALDRIVEx ::/file/path destination/path
        mcopy = os.path.join(CONF.mtools_path, "mcopy.exe")
        args = [mcopy, "-s", "-n", "-i", drive_path, "::/", "."]
        osutils.execute_process(args, shell=False)
    finally:
        os.chdir(cwd)
