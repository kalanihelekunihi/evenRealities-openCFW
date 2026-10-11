#!/usr/bin/env python3
"""Stock/source public-entry comparison of FlashDB's KV cache lookup."""
from pathlib import Path
import hashlib, itertools, json, struct, subprocess, zlib
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn.arm_const import *
from elftools.elf.elffile import ELFFile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SOURCE = ROOT / 'g2/components/main/flashdb_cache_lookup_candidates_20261010/cache_lookup.c'
BLOB = (ROOT / 'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()
assert hashlib.sha256(BLOB).hexdigest() == '36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863'
CC = subprocess.check_output(['xcrun', '--find', 'clang'], text=True).strip()
ELF = HERE / 'flashdb-cache-lookup.elf'
CMD = [CC, '--target=arm-none-eabi', '-mcpu=cortex-m4', '-mthumb', '-Oz',
       '-std=c11', '-ffreestanding', '-fno-builtin', '-nostdlib',
       '-Wl,-Ttext=0x10001000', '-Wl,-e,g2_flashdb_cache_lookup',
       '-Wl,--defsym=g2_flashdb_crc32=0x585841',
       '-Wl,--defsym=g2_flashdb_flash_read=0x585a13', str(SOURCE), '-o', str(ELF)]
subprocess.run(CMD, check=True, capture_output=True)
with ELF.open('rb') as f:
    e = ELFFile(f)
    ENTRY = next(s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()
                 if s.name == 'g2_flashdb_cache_lookup')
    SEGS = [(s['p_vaddr'], s.data()) for s in e.iter_segments() if s['p_type'] == 'PT_LOAD']

DB, KEY, OUT, SP = 0x20050000, 0x20051000, 0x20052000, 0x200ff000
NAME = b'name'

def key_for(pattern):
    return NAME+b'\0'*64 if pattern == 0 else bytes(65+i%26 for i in range(64))+b'\0'

def fixture(mode, index, activity, length, pattern):
    db = bytearray(b'\xa5' * 2304)
    key_bytes = key_for(pattern)[:length]
    crc = (zlib.crc32(key_bytes) >> 16) & 0xffff
    target_addr = 0x10000 + index
    for i in range(64):
        row_crc = i
        row_addr = 0x10000 + i
        row_active = 5
        if mode in ('hit', 'collision', 'read_error') and i == index:
            row_crc, row_active = crc, activity
        if mode == 'empty' and i == index:
            row_crc, row_addr = crc, 0xffffffff
        if mode == 'two' and i in (0, index):
            row_crc, row_active = crc, activity
        struct.pack_into('<HHI', db, 168 + 8*i, row_crc, row_active, row_addr)
    return bytes(db), target_addr

def run(source, case):
    mode, index, activity, length, pattern = case
    before, target_addr = fixture(*case)
    u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
    u.mem_map(0x437000, ((len(BLOB)+0xfe0+0xfff)//0x1000)*0x1000)
    u.mem_write(0x437fe0, BLOB)
    u.mem_map(0x10000000, 0x100000)
    for a,b in SEGS:u.mem_write(a,b)
    u.mem_map(0x20000000, 0x100000)
    u.mem_write(DB,before)
    u.mem_write(KEY,key_for(pattern))
    u.mem_write(OUT,struct.pack('<I',0xabababab))
    for r,v in zip((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3),
                   (DB,KEY,length,OUT)):u.reg_write(r,v)
    u.reg_write(UC_ARM_REG_SP,SP)
    u.reg_write(UC_ARM_REG_LR,0x10000001)
    calls=[]
    def hook(emu,pc,size,_):
        if pc==0x585a12:
            db,a,b,n=(emu.reg_read(r) for r in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3))
            assert db==DB and n==64 and a>=0x10018,(source,case,hex(pc),db,a,b,n)
            calls.append(a)
            row_addr=a-24
            saved=bytearray(key_for(pattern)[:64])
            if mode=='collision' or (mode=='two' and row_addr==0x10000):
                saved[0]=ord('Z') if saved[0]!=ord('Z') else ord('Q')
            emu.mem_write(b,bytes(saved))
            emu.reg_write(UC_ARM_REG_R0,2 if mode=='read_error' else 0)
            emu.reg_write(UC_ARM_REG_PC,emu.reg_read(UC_ARM_REG_LR))
    u.hook_add(UC_HOOK_CODE,hook)
    u.emu_start(ENTRY if source else 0x543e29,0x10000000,count=100000)
    assert u.reg_read(UC_ARM_REG_PC)==0x10000000
    assert u.reg_read(UC_ARM_REG_SP)==SP
    return {'ret':u.reg_read(UC_ARM_REG_R0),'out':bytes(u.mem_read(OUT,4)).hex(),
            'db':bytes(u.mem_read(DB,len(before))).hex(),'calls':calls}

cases=[]
for case in itertools.product(('miss','empty','hit','collision','read_error','two'),
                              (0,1,31,63),(0,1,0xffbe,0xffbf,0xffff),(0,1,4,63,64),(0,1)):
    a,b=run(False,case),run(True,case)
    if a!=b:
        for key in a:
            if a[key]!=b[key]:
                if key=='db':
                    aa=bytes.fromhex(a[key]);bb=bytes.fromhex(b[key]);i=next(i for i,(x,y) in enumerate(zip(aa,bb)) if x!=y)
                    raise AssertionError((case,key,i,aa[i:i+16].hex(),bb[i:i+16].hex()))
                raise AssertionError((case,key,a[key],b[key]))
    cases.append(case)

receipt={'status':'PASS','cases':len(cases),'stock_address':'0x543e28..0x543ee8',
         'stock_body_sha256':hashlib.sha256(BLOB[0x543e28-0x437fe0:0x543ee8-0x437fe0]).hexdigest(),
         'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
         'elf_sha256':hashlib.sha256(ELF.read_bytes()).hexdigest(),'compile':CMD,
         'limits':'Stock CRC32 and stock strncmp execute from fixed image. Flash read is a coherent shared callback writing 64 name bytes. Key lengths 0,1,4,63,64 with zero-padded and 64-byte nonzero names. Cortex-M4 scalar execution; M55 archive compile separately.'}
(HERE/'cache-lookup-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print('PASS cache_lookup',len(cases))
