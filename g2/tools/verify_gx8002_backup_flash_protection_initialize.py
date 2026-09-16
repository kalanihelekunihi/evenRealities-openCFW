#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Qualify the byte-exact profile initializer and its six ordered writes."""
import contextlib,io,json,shutil,struct,subprocess
from build_gx8002_backup_flash_protection_initialize import build,ROOT,IMAGE
from compare_gx8002_flash_otp_region import execute
from verify_gx8002_memcpy_source import decode
from verify_gx8002_logging import check_paths

def verify(prefix=None,sdk=None,output=None):
    check_paths(prefix,sdk)
    with contextlib.redirect_stdout(io.StringIO()):evidence=build()
    row=evidence['functions'][0]
    if not row['byte_exact'] or not row['fits']:raise ValueError('initializer no longer byte exact')
    out=ROOT/'build/gx8002-backup-flash-protection-initialize';pre=ROOT/'build/csky-macos/install/bin/csky-unknown-elf-';wrapper=out/'protection-initialize-stock.elf'
    subprocess.run([str(pre)+'objcopy','-I','binary','-O','elf32-csky-little','-B','csky',str(IMAGE),str(wrapper)],check=True)
    b=bytearray(wrapper.read_bytes());struct.pack_into('<I',b,36,0x21006009);wrapper.write_bytes(b)
    old=decode(subprocess.check_output([str(pre)+'objdump','-D','--start-address=0x408c0','--stop-address=0x408ec',str(wrapper)],text=True))
    new=decode((out/'protection-initialize-linked.disassembly.txt').read_text())
    events=[['write',0x20017644+4*i,v] for i,v in enumerate([0x20016dfc,5,0x20016e24,7,0x20016e5c,9])]
    for argument in (0,0xffffffff):
        execute(old,0x408c0,argument,events)
        execute(new,0x10007f80,argument,events)
    if output:
        output.mkdir(parents=True,exist_ok=True);shutil.copyfile(out/'protection-initialize.elf',output/'protection-initialize.elf')
    return {'functions':[{'symbol':row['symbol'],'section_name':row['section'],'compiled_bytes':row['compiled_bytes'],'compiled_sha256':row['compiled_sha256'],
      'stock_occurrences':[{'symbol':row['symbol'],'package_offset':row['package_offset'],'bytes':row['stock_envelope_bytes'],'sha256':row['stock_sha256'],'region':'backup_sram_text'}]}],
      'evidence':evidence,'ordered_writes':events,'source_admitted':False,'hardware_qualified':False,
      'limits':['No arguments or branches; full instruction bytes and six ordered stores qualified. BSS ownership and startup caller remain separately unqualified.']}
if __name__=='__main__':
    (ROOT/'docs/research/gx8002-backup-flash-protection-initialize-verification.json').write_text(json.dumps(verify(),indent=2)+'\n')
