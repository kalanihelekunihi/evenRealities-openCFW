# SPDX-License-Identifier: MIT
"""Rebuild and run the upstream header host harness on macOS."""
import json
import subprocess
from analyze_gx8002_upstream_objects import ROOT, sha
from build_gx8002_uart_header_upstream_probe import build


def verify():
    probe = build()
    out = ROOT/'build/gx8002-uart-header-probe'
    harness = ROOT/'tests/gx8002_uart_header_host_check.c'
    executable = out/'host-check'
    subprocess.run(['clang', '-I'+str(ROOT/'build/upstream-nationalchip-lvp-kws/lvp/common'),
                    '-I'+str(out), str(harness), '-o', str(executable)], check=True)
    subprocess.run([str(executable)], check=True)
    return {'probe': probe, 'harness_sha256': sha(harness.read_bytes()),
            'fragmentation_cases': 22, 'trailing_input_crc_cases': 4, 'followup_reset_cases': 4,
            'source_admitted': False, 'hardware_qualified': False,
            'limits': ['Native host execution of upstream helper with scripted CRC result. Does not compare stock target execution or qualify the complete receive callback.']}

if __name__ == '__main__':
    report = verify()
    (ROOT/'docs/research/gx8002-uart-header-host-verification.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Upstream header host checks passed')
