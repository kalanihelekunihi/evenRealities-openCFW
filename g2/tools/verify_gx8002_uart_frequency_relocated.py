# SPDX-License-Identifier: MIT
def verify(elf=None,code=None,register_word=1<<27):
    from link_gx8002_uart_configure_source import build,ROOT
    from build_transparent_image import Elf32
    from verify_gx8002_memcpy_source import decode
    from verify_gx8002_clock_low_frame import execute
    import struct,json
    if elf is None:
        build(include_initialize=True)
        p=ROOT/'build/gx8002-uart-initialize-source/uart.elf';elf=Elf32(p.read_bytes(),str(p));code=decode((p.parent/'uart.disassembly.txt').read_text())
    e=elf;c=code;ss=list(e.symbols());sy={s['name']:s['value'] for s in ss if s['name']}
    f=next(s for s in ss if s['name']=='open_cfw_gx8002_clock_frequency');calls={int(a,0) for pc,(o,a,w) in c.items() if f['value']<=pc<f['value']+f['size'] and o=='bsr'};lookup=next(v for v in calls if v!=sy['open_cfw_gx8002_clock_divider']);ls=next(s for s in ss if s['value']==lookup and s['size'])
    lit={int(a.split(',')[1],0) for pc,(o,a,w) in c.items() if lookup<=pc<lookup+ls['size'] and o=='lrw'};tb=next(s['value'] for s in ss if s['name']=='gx_clock_param_table' and s['value'] in lit)
    d=next(s for s in e.sections if s['name']=='.data');raw=e.contents(d);records=raw[tb-d['address']:tb-d['address']+416]
    ro=next(s for s in e.sections if s['name']=='.rodata');jump=next(int(a.split(',')[1],0) for pc,(o,a,w) in c.items() if f['value']<=pc<f['value']+24 and o=='lrw');table=struct.unpack_from('<19I',e.contents(ro),jump-ro['address'])
    cells={(d['address']+i,w):int.from_bytes(raw[i:i+w],'little') for w in (1,2,4) for i in range(len(raw)-w+1)}
    for bank in (0xa0010000,0xa0300000):
     for off in range(256):cells[bank+off,4]=register_word
    cells[0xa001008c,4]=0
    index=next(i for i in range(26) if struct.unpack_from('<I',records,16*i)[0]==16);cells[0xa0300088,4]=1<<records[16*index+6]
    r=execute(c,table,16,0,0,lookup_records=records,source_cells=cells,entry=f['value'],lookup_entry=lookup,divider_entry=sy['open_cfw_gx8002_clock_divider'],record_base=tb,jump_base=jump)
    divider_pointer,dto_pointer=struct.unpack_from('<II',records,index*16+8)
    expected=24576000
    if dto_pointer and not register_word&(1<<27):expected=((register_word&0x1ffffff)*expected)>>25
    divider=0
    if divider_pointer:
        off,shift,mask=struct.unpack_from('<BBH',raw,divider_pointer-d['address'])
        field=(register_word>>shift)&mask;divider=field+1 if field else 0
    if divider:expected//=divider
    if r!=(expected,[('lookup',16),('divider',divider)]):raise ValueError(('Relocated frequency oracle',register_word,r,expected,divider))
    return {'register_word':register_word,'result_hz':r[0],'helper_trace':r[1],'source_admitted':False,'limits':['Relocated module-16 high-frequency scenario with source DTO/divider records; modeled MMIO, no full initialization or hardware qualification.']}

if __name__=="__main__":
    print(verify())
