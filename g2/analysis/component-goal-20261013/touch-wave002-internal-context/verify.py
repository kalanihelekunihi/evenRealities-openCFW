#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,re,struct,subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS
from unicorn.arm_const import UC_ARM_REG_SP,UC_ARM_REG_LR,UC_ARM_REG_PC
ROOT=Path(__file__).resolve().parents[4];HERE=Path(__file__).resolve().parent
D=ROOT/'g2/components/touch/reset_layout_candidate_20261010';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
source=D/'reset_generated_internal_context.c';obj=HERE/'internal.o';dep=HERE/'internal.d';before=sha(source)
cmd=['clang','-target','armv6m-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Og','-ffreestanding','-Wall','-Wextra','-Werror','-MD','-MF',str(dep),'-c',str(source),'-o',str(obj)]
subprocess.run(cmd,check=True);assert sha(source)==before
ld=HERE/'fixture.ld';ld.write_text('SECTIONS { .internal 0x20000c50 (NOLOAD) : { *(.touch_bss.internal_context) } ASSERT(SIZEOF(.internal)==120,"LP context extent") }\n')
elf=HERE/'internal.elf';subprocess.run(['arm-none-eabi-ld','-T',str(ld),str(obj),'-o',str(elf)],check=True)
with elf.open('rb') as f:
 e=ELFFile(f);s=e.get_section_by_name('.internal');assert s['sh_type']=='SHT_NOBITS' and s['sh_size']==120 and s['sh_addr']==0x20000c50 and s['sh_addralign']==4
 assert next(x['st_value'] for x in e.get_section_by_name('.symtab').iter_symbols() if x.name=='touch_generated_internal_context')==0x20000c50
fw=ROOT/'g2/blobs/official/g2-2.2.6.10/firmware_touch.bin';assert sha(fw)=='0d13d8bb1337bf22989dc16143e3d5eca29a31cc1ed753ff624668750ea9470d';image=fw.read_bytes()[32:]
zbase,zwords=struct.unpack_from('<II',image,0xb584-0x3300);assert (zbase,zwords)==(0x200008a8,428);assert zbase<=0x20000c50 and 0x20000c50+120<=zbase+zwords*4
cases=[]
for seed in [0,17,255]:
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x3000,0x9000);u.mem_write(0x3300,image);u.mem_map(0x20000000,0x10000);u.mem_write(0x20000000,bytes([seed])*0x10000);u.reg_write(UC_ARM_REG_SP,0x20008000);u.reg_write(UC_ARM_REG_LR,0x20000001);u.emu_start(0x4693,0x46d6,count=100000)
 assert u.reg_read(UC_ARM_REG_PC)==0x46d6 and u.reg_read(UC_ARM_REG_SP)==0x20008000
 assert bytes(u.mem_read(zbase,zwords*4))==bytes(zwords*4)
 assert bytes(u.mem_read(0x20000c50,120))==bytes(120)
 assert bytes(u.mem_read(zbase+zwords*4,4))==bytes([seed])*4
 cases.append({'initial_fill':seed,'native_zeroed_context_bytes':120,'adjacent_lock_zeroed':bytes(u.mem_read(0x20000cc8,4))==bytes(4)})
# Independent compile-time field anchors are backed by these existing consumers,
# including native-derived access118 which disambiguates optional HW IIR field.
consumers={}
for name,anchors in [('active_timer_offline/active.c',['i[118]','u16(i,72)']),('base_frame_offline/base.c',['i[99+j]','i[113]','i[116]','i[117]']),('scan_preparation_offline/prepare.c',['i[116]=common[41]','i[117]=common[42]'])]:
 p=ROOT/'g2/components/touch'/name;t=p.read_text();assert all(a in t for a in anchors);consumers[str(p.relative_to(ROOT))]=sha(p)
paths=dep.read_text().replace('\\\n',' ').split(': ',1)[1].split();deps={str(Path(p).relative_to(ROOT)):sha(Path(p)) for p in paths if Path(p).is_relative_to(ROOT)}
r={'status':'PASS_TYPED_LP_INTERNAL_CONTEXT_NOBITS_AND_NATIVE_RESET','source':str(source.relative_to(ROOT)),'source_sha256':sha(source),'object_sha256':sha(obj),'elf_sha256':sha(elf),'compile_command':cmd,'dependencies':deps,'firmware_sha256':sha(fw),'vendor_commit':'247a9a0f79eb976f144f5fbeb29488c1c2606517','vendor_reference_hashes':{n:sha(ROOT/'g2/analysis/c-source-completion-20261011/touch/capsense-v6-reference'/n) for n in ['cy_capsense_structure.h','cy_capsense_common.h','LICENSE']},'section':{'start':'0x20000c50','end_exclusive':'0x20000cc8','size':120,'type':'NOBITS','alignment':4},'reset_descriptor':{'start':hex(zbase),'words':zwords,'end_exclusive':hex(zbase+zwords*4)},'native_reset_cases':cases,'consumer_hashes':consumers,'limits':['Bounded typed storage/zero-reset/field ABI; final whole-firmware scatter, callbacks, behavior and hardware remain unqualified.','Dimension comes from pinned LP14-state/HW-IIR type and native field anchors, not neighboring allocation gap.']}
(HERE/'verification.json').write_text(json.dumps(r,indent=2)+'\n');print(r['status'],len(cases))
