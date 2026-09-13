# SPDX-License-Identifier: MIT
from verify_gx8002_backup_clock_source_common import verify_part

def verify(prefix=None,sdk=None,output=None):
    return verify_part('lookup',prefix,sdk,output)
