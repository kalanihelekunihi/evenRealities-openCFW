# SPDX-License-Identifier: MIT
"""Authenticate UART defaults without claiming unexplained words as source."""
import json,struct,subprocess,re
from analyze_gx8002_upstream_objects import ROOT,IMAGE,IMAGE_SHA,SDK_COMMIT,authenticated_blob,sha

def analyze():
    image=IMAGE.read_bytes()
    if sha(image)!=IMAGE_SHA:raise ValueError('Firmware identity')
    sdk=ROOT/'build/upstream-nationalchip-lvp-kws';dependencies=[];headers={}
    for name in ('arch/soc/grus/include/base_addr.h','arch/soc/grus/include/soc.h','include/driver/gx_uart.h'):
        blob=subprocess.check_output(['git','-C',str(sdk),'rev-parse',SDK_COMMIT+':'+name],text=True).strip()
        raw=authenticated_blob(sdk/name,blob);headers[name]=raw.decode();dependencies.append({'path':name,'blob':blob,'sha256':sha(raw)})
    bases=headers['arch/soc/grus/include/base_addr.h'];soc=headers['arch/soc/grus/include/soc.h']
    rows=[]
    for port in range(2):
        offset=0x18aa8+port*128;words=struct.unpack_from('<32I',image,offset)
        base=int(re.search(r'#define\s+GX_REG_BASE_UART'+str(port)+r'\s+(0x[0-9A-Fa-f]+)',bases)[1],16)
        irq=int(re.search(r'#define\s+IRQ_NUM_DW_UART'+str(port+1)+r'\s+\((\d+)\)',soc)[1])
        if words[0]!=port or words[1]!=base or words[15]!=irq:raise ValueError('Upstream UART identity mismatch')
        rows.append({'port':port,'package_offset':offset,'runtime_address':0x20026a94+port*128,'sha256':sha(image[offset:offset+128]),'known_identity_fields':{'port':{'offset':0,'value':port},'device':{'offset':4,'value':base},'irq':{'offset':60,'value':irq}},'nonzero_defaults_requiring_consumer_trace':[{'offset':i*4,'value':value} for i,value in enumerate(words) if value and i not in (0,1,15)],'zero_word_offsets':[i*4 for i,v in enumerate(words) if v==0]})
    from verify_gx8002_memcpy_source import decode
    from build_transparent_image import Elf32
    wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf'
    elf=Elf32(wrapper.read_bytes(),str(wrapper))
    if sha(elf.contents(next(section for section in elf.sections if section['name']=='.data')))!=IMAGE_SHA:raise ValueError('Disassembly wrapper identity')
    code=decode(subprocess.check_output([str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump'),'-D','--start-address=0xc954','--stop-address=0xca36',str(wrapper)],text=True))
    expected={0xc958:('ld.w','r3, (r0, 0x1c)'),0xc95c:('bnez','r3, 0xc964'),0xc960:('movi','r3, 8'),0xc962:('st.w','r3, (r0, 0x1c)'),0xc964:('ld.w','r3, (r4, 0x20)'),0xc966:('bnez','r3, 0xc96e'),0xc96a:('movi','r3, 1'),0xc96c:('st.w','r3, (r4, 0x20)'),0xc99a:('ld.w','r7, (r4, 0x10)'),0xc9a0:('ld.w','r3, (r4, 0xc)'),0xc9a2:('lsli','r7, r7, 4'),0xc9a4:('divu','r6, r3, r7'),0xc9ae:('st.w','r6, (r4, 0x14)'),0xca1a:('and','r3, r2'),0xca1c:('ori','r3, r3, 3'),0xca20:('st.w','r3, (r5, 0xc)')}
    for pc,wanted in expected.items():
        if code[pc][:2]!=wanted:raise ValueError(('UART consumer instruction',hex(pc),code[pc],wanted))
    consumers={'baud_offset':16,'input_clock_offset':12,'integer_divisor_offset':20,'divisor_rule':'input_clock / (baud << 4), unsigned 32-bit arithmetic; subsequent fractional calculation not qualified here','default_normalization':[{'offset':28,'zero_replacement':8},{'offset':32,'zero_replacement':1}],'line_control':'At ca14..ca20, low five LCR bits are replaced with 3 independently of the normalized fields.','verified_instruction_count':len(expected),'configuration_package_offset':0xc954}
    return {'image_sha256':IMAGE_SHA,'sdk_commit':SDK_COMMIT,'upstream_dependencies':dependencies,'descriptors':rows,'consumer_evidence':consumers,'source_admitted':False,'limits':['Offset 16 feeds baud-divisor arithmetic. Offsets 28 and 32 have verified normalization but field names are not established. Full configuration behavior remains unqualified. Zero words include mutable runtime fields, not proven unused storage. This report is evidence, not source-owned UART initialization.']}

if __name__=='__main__':
    report=analyze();(ROOT/'docs/research/gx8002-uart-descriptor-defaults.json').write_text(json.dumps(report,indent=2)+'\n');print('Authenticated UART descriptors:',len(report['descriptors']))
