#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Source admission for the device-specific flash configuration."""
import contextlib
import io
import json
import shutil
from compare_gx8002_flash_device import verify as compare
from verify_gx8002_logging import check_paths
from link_gx8002_uart_console import ROOT


def verify(prefix=None, sdk=None, output=None):
    check_paths(prefix, sdk)
    with contextlib.redirect_stdout(io.StringIO()):
        evidence = compare()
    row = evidence['build']
    symbol = 'open_cfw_gx8002_flash_device_config'
    if output:
        output.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT/'build/gx8002-board/device.elf', output/'device.elf')
    return {'functions': [{'symbol': symbol, 'section_name': '.text',
                          'compiled_bytes': row['compiled_bytes'],
                          'compiled_sha256': row['compiled_sha256'],
                          'stock_occurrences': [{'symbol': symbol,
                                                'package_offset': row['package_offset'],
                                                'bytes': row['stock_envelope_bytes'],
                                                'sha256': row['stock_sha256'],
                                                'region': 'image_a_sram_text'}]}],
            'evidence': evidence, 'source_admitted': True, 'hardware_qualified': False,
            'limits': ['Qualified transport/control call contracts; physical flash remains unqualified.']}


if __name__ == '__main__':
    (ROOT/'docs/research/gx8002-flash-device-verification.json').write_text(json.dumps(verify(), indent=2)+'\n')
