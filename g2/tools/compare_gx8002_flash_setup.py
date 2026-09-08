#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Compatibility entry point: qualify the continuous initializer execution.

Supersedes the historical split model, whose independently supplied state and
configuration-output assumption are no longer appropriate to the source path.
"""
import contextlib,io,json
from compare_gx8002_flash_full import verify as verify_full,ROOT,decode

def verify():
    with contextlib.redirect_stdout(io.StringIO()):full=verify_full()
    report={'verification_scope':'complete initializer including setup, selection and return',
            'cases':full['cases'],'full':full,'source_admitted':False,
            'limits':['Use verify_gx8002_flash_initialize for admission; no physical qualification.']}
    (ROOT/'docs/research/gx8002-flash-setup-comparison.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['cases']);return report
if __name__=='__main__':verify()
