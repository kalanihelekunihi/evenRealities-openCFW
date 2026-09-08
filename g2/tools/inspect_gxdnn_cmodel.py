#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Authenticate and inspect upstream model objects; never emit firmware payload."""
import json,struct,subprocess
from pathlib import Path
from analyze_gx8002_upstream_objects import ROOT,authenticated_blob,sha
COMMIT='0637b47c8fa0031f8f5651a903cd7d14716382fd'
def inspect():
    sdk=ROOT/'build/upstream-nationalchip-gxdnn';out=ROOT/'build/gxdnn-analysis';out.mkdir(exist_ok=True);rel='grus/lib/libcmodel.a'
    blob=subprocess.check_output(['git','-C',str(sdk),'rev-parse',COMMIT+':'+rel],text=True).strip();data=authenticated_blob(sdk/rel,blob)
    if not data.startswith(b'!<arch>\n'):raise ValueError('gxDNN archive magic')
    offset=8;rows=[]
    while offset<len(data):
        header=data[offset:offset+60]
        if len(header)!=60 or header[58:]!=b'`\n':raise ValueError('gxDNN archive header')
        size=int(header[48:58]);name=header[:16].decode('ascii').strip().rstrip('/');payload=data[offset+60:offset+60+size]
        if len(payload)!=size:raise ValueError('gxDNN archive bounds')
        if name:
            if '/' in name or not name.endswith('.o'):raise ValueError('gxDNN member name')
            if payload[:6]!=b'\x7fELF\x02\x01':raise ValueError('gxDNN expected ELF64 little endian')
            machine=struct.unpack_from('<H',payload,18)[0]
            if machine!=62:raise ValueError('gxDNN expected x86-64 reference model')
            path=out/name;path.write_bytes(payload)
            symbols=subprocess.check_output(['xcrun','llvm-objdump','--syms',str(path)],text=True)
            (out/(name+'.symbols.txt')).write_text(symbols)
            (out/(name+'.disassembly.txt')).write_text(subprocess.check_output(['xcrun','llvm-objdump','--disassemble','--reloc',str(path)],text=True))
            rows.append({'name':name,'bytes':size,'sha256':sha(payload),'machine':machine,'functions':[line.split()[-1] for line in symbols.splitlines() if ' F ' in line or '\tF ' in line]})
        offset+=60+size+(size%2)
    report={'repository':'https://github.com/NationalChip/gxDNN','commit':COMMIT,'archive':{'path':rel,'git_blob':blob,'sha256':sha(data)},'members':rows,'source_admitted':False,'limits':['Read-only object inspection. The x86-64 model archive is not linked, executed or copied into firmware. Host pointer width differs from target command storage. Inferred fields require separate firmware validation.']}
    (ROOT/'docs/research/gx8002-gxdnn-cmodel-inventory.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':print(json.dumps(inspect(),indent=2))
