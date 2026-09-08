#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
import json
from verify_gx8002_rtc_ticks import ROOT,verify_one

def verify(prefix=None,sdk=None,output=None):
    return verify_one('set',prefix,sdk,output)

if __name__=='__main__':
    report=verify()
    (ROOT/'docs/research/gx8002-rtc-set-tick-verification.json').write_text(json.dumps(report,indent=2)+'\n')
    print('RTC set tick source qualification passed')
