#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Authenticate SDK interface layout and inventory shipped function pointers."""
import json
import re
import struct
import subprocess
from analyze_gx8002_upstream_objects import IMAGE,IMAGE_SHA,SDK_COMMIT,sha,authenticated_blob
from link_gx8002_uart_console import ROOT

def analyze():
    sdk=ROOT/'build/upstream-nationalchip-lvp-kws';relative='include/driver/gx_flash.h'
    header=sdk/relative
    blob=subprocess.check_output(['git','-C',str(sdk),'rev-parse',SDK_COMMIT+':'+relative],text=True).strip()
    authenticated_blob(header,blob)
    source=header.read_text();body=source.split('typedef struct gx_flash_dev {',1)[1].split('} GX_FLASH_DEV;',1)[0]
    body=re.sub(r'#ifdef CONFIG_MTD_TESTS.*?#endif','',body,flags=re.S)
    fields=re.findall(r'([^;]+);',body)
    names=[re.search(r'\(\*(\w+)\)',f)[1] for f in fields]
    data=IMAGE.read_bytes()
    if sha(data)!=IMAGE_SHA:raise ValueError('stock changed')
    pointers=struct.unpack_from('<'+str(len(names))+'I',data,0x18518)
    rows=[{'index':i,'name':name,'declaration':' '.join(fields[i].split()),'runtime_address':address,
           'package_offset':address-0x1000dfec if address else None} for i,(name,address) in enumerate(zip(names,pointers))]
    if len(rows)!=30 or rows[12]['runtime_address']!=0x10024244 or rows[18]['runtime_address']!=0x10024250:raise ValueError('interface anchors changed')
    report={'sdk_commit':SDK_COMMIT,'header_path':relative,'header_git_blob':blob,'header_sha256':sha(header.read_bytes()),'configuration':'CONFIG_MTD_TESTS disabled',
            'table_package_offset':0x18518,'table_runtime_address':0x20026504,'bytes':120,'stock_sha256':sha(data[0x18518:0x18590]),'slots':rows,
            'source_admitted':False,'limits':['Layout identification supported by gettype and OTP-lock code anchors; each remaining function still requires behavioral/signature qualification.', 'This inventory does not replace the interface or executable bytes with source.']}
    (ROOT/'docs/research/gx8002-flash-interface-inventory.json').write_text(json.dumps(report,indent=2)+'\n')
    print(len(rows),sum(bool(x) for x in pointers));return report

if __name__=='__main__':analyze()
