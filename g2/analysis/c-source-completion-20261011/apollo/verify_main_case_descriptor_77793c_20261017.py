#!/usr/bin/env python3
"""Compare compiled C Case nanopb descriptor graph with authenticated stock."""
import hashlib
import json
import subprocess
from pathlib import Path
from elftools.elf.elffile import ELFFile
ROOT=Path(__file__).resolve().parents[4]
G2=ROOT/'g2';BASE=G2/'build/c-firmware/20261017/main-case-descriptor'
SOURCE=G2/'components/audio/uart_thread_source_candidate/display_case_descriptor_77793c_20261017.c'
MAP=BASE/'descriptor-map.json';OBJECT=BASE/'descriptor.o';ELF=BASE/'descriptor.elf';OUT=BASE/'oracle-receipt.json'
STOCK=(G2/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
CONFIG=G2/'config-recovered/nanopb/g2-config';UPSTREAM=ROOT/'third-party/upstream/nanopb'
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def ref(path):return {'path':str(path.relative_to(ROOT)),'sha256':sha(path)}
def main():
    maprec=json.loads(MAP.read_text())
    assert maprec['status']=='PASS_AUTHENTICATED_MAIN_CASE_DESCRIPTOR_GRAPH_77793C'
    assert maprec['source']['sha256']==sha(SOURCE)
    flags=['--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-O2',
           '-Wall','-Wextra','-Werror','-ffreestanding','-fno-builtin',
           '-DPB_SYSTEM_HEADER="pb_g2_system.h"','-include',str(CONFIG/'pb_g2_options.h'),
           '-I',str(CONFIG),'-I',str(UPSTREAM)]
    subprocess.run(['clang',*flags,'-c',str(SOURCE),'-o',str(OBJECT)],check=True)
    subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000','-e',
                    'audio_uart_case_descriptor_77793c',str(OBJECT),'-o',str(ELF)],check=True)
    with ELF.open('rb') as f:
        e=ELFFile(f);segments=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']
        syms={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
    def cbytes(addr,n):
        for base,data in segments:
            if base<=addr and addr+n<=base+len(data):return data[addr-base:addr-base+n]
        raise RuntimeError(f'unmapped C graph {addr:x}')
    def sbytes(addr,n):
        off=addr-0x438000
        if not 0<=off<=len(STOCK)-n:raise RuntimeError(f'unmapped stock graph {addr:x}')
        return STOCK[off:off+n]
    def read_graph(raw,root):
        def word(addr):return int.from_bytes(raw(addr,4),'little')
        def desc(addr):
            d=raw(addr,24);fields,subs,default,callback=[word(addr+i*4) for i in range(4)]
            count=int.from_bytes(d[16:18],'little');required=int.from_bytes(d[18:20],'little')
            largest=int.from_bytes(d[20:22],'little')
            cursor=fields;fieldwords=[];children=0
            for _ in range(count):
                first=word(cursor);width=(1,2,4,8)[first&3]
                fieldwords += [word(cursor+4*i) for i in range(width)]
                cursor+=4*width
                if ((first>>8)&15) in (8,9):children+=1
            fieldwords.append(word(cursor))
            return (default,callback,count,required,largest,fieldwords,
                    [word(subs+4*i) for i in range(children+1)])
        outer=desc(root)
        assert len(outer[6])==2 and outer[6][1]==0
        nested=desc(outer[6][0])
        assert nested[6]==[0]
        return outer[:6],nested[:6]
    actual=read_graph(cbytes,syms['audio_uart_case_descriptor_77793c'])
    expected=read_graph(sbytes,0x77793c)
    assert actual==expected,(actual,expected)
    rec={'status':'PASS_MAIN_CASE_DESCRIPTOR_C_GRAPH','descriptors':2,
         'source':ref(SOURCE),'extraction_map':ref(MAP),'object':ref(OBJECT),
         'linked_elf':ref(ELF),'stock_payload_sha256':hashlib.sha256(STOCK).hexdigest(),
         'scope':'24-byte nanopb descriptor fields, field-info words and nested pointer graph',
         'remaining_gate':'Generated graph does not prove final ROM placement, complete protobuf runtime or hardware behavior.'}
    OUT.write_text(json.dumps(rec,indent=2,sort_keys=True)+'\n')
    print(rec['status'],2,sha(OUT))
if __name__=='__main__':main()
