# SPDX-License-Identifier: MIT
"""Rebuild authenticated preparation source and run macOS host edge cases."""
import json,subprocess
from analyze_gx8002_upstream_objects import ROOT,sha
from build_gx8002_uart_body_upstream_probe import build


def verify():
    probe=build();out=ROOT/'build/gx8002-uart-body-probe'
    harness=ROOT/'tests/gx8002_uart_prepare_host_check.c';target=out/'prepare-host-check'
    subprocess.run(['clang','-I'+str(ROOT/'build/upstream-nationalchip-lvp-kws/lvp/common'),
                    '-I'+str(out),str(harness),'-o',str(target)],check=True)
    subprocess.run([str(target)],check=True)
    return {'probe':probe,'host_cases':138,'harness_sha256':sha(harness.read_bytes()),
            'source_admitted':False,'hardware_qualified':False,
            'limits':['Native host preparation behavior only; target layout and complete stock execution require separate verification.']}

if __name__=='__main__':
    report=verify();(ROOT/'docs/research/gx8002-uart-prepare-host-verification.json').write_text(json.dumps(report,indent=2)+'\n');print('Preparation host cases:',report['host_cases'])
