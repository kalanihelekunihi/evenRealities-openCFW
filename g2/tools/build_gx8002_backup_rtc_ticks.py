# SPDX-License-Identifier: MIT
"""Compile shared recovered RTC tick primitives at backup addresses."""
import json,subprocess
from analyze_gx8002_upstream_objects import ROOT,IMAGE,IMAGE_SHA,sha
from build_transparent_image import Elf32
from verify_gx8002_memcpy_source import decode


def build():
    out=ROOT/'build/gx8002-backup-rtc-ticks';out.mkdir(exist_ok=True)
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    sources=[]
    for name in ('start','set'):
        path=ROOT/f'components/shared/gx8002/runtime_gx8002_rtc_{name}_tick.c'
        command=[pre+'gcc','-Os','-mcpu=ck804ef','-mhard-float','-ffreestanding','-fno-builtin','-ffunction-sections','-c',str(path),'-o',str(out/(name+'.o'))]
        subprocess.run(command,check=True);sources.append({'path':str(path),'sha256':sha(path.read_bytes()),'command':command})
    script='''SECTIONS {
.rtc_start 0x10008800 : { *(.text.open_cfw_gx8002_rtc_start_tick) }
.rtc_set 0x10008810 : { *(.text.open_cfw_gx8002_rtc_set_tick) }
}
gx_rtc_start_tick = open_cfw_gx8002_rtc_start_tick;
gx_rtc_set_tick = open_cfw_gx8002_rtc_set_tick;
ASSERT(SIZEOF(.rtc_start) <= 16, "RTC start overflow")
ASSERT(SIZEOF(.rtc_set) <= 12, "RTC set overflow")
'''
    (out/'ticks.ld').write_text(script);path=out/'ticks.elf'
    subprocess.run([pre+'ld','-T',str(out/'ticks.ld'),str(out/'start.o'),str(out/'set.o'),'-o',str(path)],check=True)
    elf=Elf32(path.read_bytes(),'ticks');stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    assert not any(s['name'] and s['section']==0 for s in elf.symbols())
    assert not any(elf.relocations(s['index']) for s in elf.sections)
    rows=[]
    for name,offset,size in (('.rtc_start',0x41140,16),('.rtc_set',0x41150,12)):
        sec=next(s for s in elf.sections if s['name']==name);body=elf.contents(sec)
        assert len(body)==size
        if name=='.rtc_set': assert body==stock[offset:offset+size]
        rows.append({'section':name,'address':sec['address'],'bytes':len(body),'stock_byte_exact':body==stock[offset:offset+size]})
    asm=subprocess.check_output([pre+'objdump','-d',str(path)],text=True);(out/'ticks.disassembly.txt').write_text(asm)
    code=decode(asm)
    sequences={0x10008800:[('lrw','r3, 0xa0003000',2),('ld.w','r1, (r3, 0xc)',2),('ori','r2, r1, 4',4),('st.w','r2, (r3, 0xc)',2),('rts','',2)],0x10008810:[('lrw','r3, 0xa0003000',2),('st.w','r0, (r3, 0x8)',2),('rts','',2)]}
    for pc,seq in sequences.items():
        for ins in seq:assert code[pc]==ins;pc+=ins[2]
    wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf'
    original=Elf32(wrapper.read_bytes(),'stock')
    assert sha(original.contents(next(s for s in original.sections if s['name']=='.data')))==IMAGE_SHA
    old=decode(subprocess.check_output([pre+'objdump','-D','--start-address=0x41140','--stop-address=0x41150',str(wrapper)],text=True))
    pc=0x41140
    for ins in [('lrw','r2, 0xa0003000',2),('ld.w','r3, (r2, 0xc)',2),('ori','r3, r3, 4',4),('st.w','r3, (r2, 0xc)',2),('rts','',2)]:
        assert old[pc]==ins;pc+=ins[2]
    report={'sources':sources,'sections':rows,'elf_sha256':sha(path.read_bytes()),'source_admitted':False,'hardware_qualified':False,'limits':['Set is byte-exact; start differs only in scratch-register allocation, with both decoded straight-line contracts checked: start reads control and writes control OR 4; set writes the complete input word to duration. No hardware timer or initialization qualification is implied.']}
    (ROOT/'docs/research/gx8002-backup-rtc-ticks.json').write_text(json.dumps(report,indent=2)+'\n');return report


if __name__=='__main__':print(json.dumps(build(),indent=2))
