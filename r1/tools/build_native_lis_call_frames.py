#!/usr/bin/env python3
"""Factor attributed ST bit updates from transport so native call frames are restored."""
import hashlib,json,re,subprocess
from pathlib import Path
from build_source_candidates import undefined_symbols
from build_native_lis_registers import FUNCTIONS
from build_native_dfu_backend_runtime import allocated_sections
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=BASE/'native-lis-call-frames';out.mkdir(exist_ok=True);parent=BASE/'native-lis-configure';pr=parent/'report.json';p=json.loads(pr.read_text());po=parent/'native-lis-configure-runtime.o';assert sha(po)==p['linked_sha256'];inputs=dict(p['inputs'])
 for path,h in inputs.items():assert sha(ROOT/path)==h,path
 vendor=ROOT/'vendor-cache/r1/st-lis2dw12-8d4bd522015004a9646102702901ba5a15ec6d39';raw=(vendor/'lis2dw12_reg.c').read_bytes().decode();helpers=[];slices=[];bridges=['#include <stdint.h>'];replacements=[]
 def wrapper(name,asm):bridges.append('__attribute__((naked)) uint32_t '+name+'(void) { __asm__ volatile('+json.dumps(asm)+'); }');replacements.append(name)
 def field_helper(name,local):
  m=re.search(r'int32_t '+name+r'\(.*?\r?\n\}',raw,re.S);assert m;body=m.group();typ=re.search(r'(lis2dw12_\w+_t) '+local+r';',body)[1];assign=re.findall(r'\b'+local+r'\.\w+\s*=.*?;',body,re.S);assert len(assign)==1,(name,local,assign);helper='r1_field_'+name+'_'+local
  helpers.append('uint32_t '+helper+'(uint32_t byte,uint32_t val) { union {uint8_t byte; '+typ+' reg;} u; _Static_assert(sizeof(u)==1,"native register byte"); u.byte=(uint8_t)byte; '+assign[0].replace(local+'.','u.reg.')+' return u.byte; }');slices.append(dict(function=name,local=local,type=typ,assignment=assign[0],helper=helper,start=m.start(),end=m.end(),original_slice_sha256=hashlib.sha256(body.encode()).hexdigest()));return helper,body
 for a,suffix in FUNCTIONS.items():
  if suffix=='reset_get':continue
  name='lis2dw12_'+suffix;helper,body=field_helper(name,'reg');register=re.search(r'lis2dw12_read_reg\(ctx, (LIS2DW12_\w+)',body)[1];header=(vendor/'lis2dw12_reg.h').read_text();reg=int(re.search(r'#define '+register+r'\s+0x([0-9A-Fa-f]+)',header)[1],16)
  wrapper(name,f'push {{r3,r4,r5,lr}}\nmov r4,r1\nmov r5,r0\nmovs r3,#1\nmov r2,sp\nmovs r1,#{reg}\nbl lis2dw12_read_reg\ncmp r0,#0\nbne 1f\nldrb r0,[sp]\nmov r1,r4\nbl {helper}\nstrb r0,[sp]\nmovs r3,#1\nmov r2,sp\nmovs r1,#{reg}\nmov r0,r5\nbl lis2dw12_write_reg\n1: pop {{r3,r4,r5,pc}}\n')
 for name,reg,mask,shift in [('lis2dw12_reset_get',0x21,1,6),('lis2dw12_fifo_data_level_get',0x2f,63,0)]:
  wrapper(name,f'push {{r3,r4,r5,lr}}\nmov r4,r1\nmovs r3,#1\nmov r2,sp\nmovs r1,#{reg}\nbl lis2dw12_read_reg\nldrb r1,[sp]\nlsrs r1,r1,#{shift}\nand r1,r1,#{mask}\nstrb r1,[r4]\npop {{r3,r4,r5,pc}}\n' if shift else f'push {{r3,r4,r5,lr}}\nmov r4,r1\nmovs r3,#1\nmov r2,sp\nmovs r1,#{reg}\nbl lis2dw12_read_reg\nldrb r1,[sp]\nand r1,r1,#{mask}\nstrb r1,[r4]\npop {{r3,r4,r5,pc}}\n')
 for name,locals_,regs in [('lis2dw12_data_rate_set',['ctrl1','ctrl3'],[0x20,0x22]),('lis2dw12_filter_path_set',['ctrl6','ctrl_reg7'],[0x25,0x3f])]:
  hs=[field_helper(name,l)[0] for l in locals_];asm='push {r2,r3,r4,r5,r6,lr}\nmov r4,r1\nmov r5,r0\n'
  for i,(reg,helper) in enumerate(zip(regs,hs)):
   off=i*4;asm+=f'movs r3,#1\nadd r2,sp,#{off}\nmovs r1,#{reg}\nmov r0,r5\nbl lis2dw12_read_reg\ncmp r0,#0\nbne 1f\nldrb r0,[sp,#{off}]\nmov r1,r4\nbl {helper}\nstrb r0,[sp,#{off}]\nmovs r3,#1\nadd r2,sp,#{off}\nmovs r1,#{reg}\nmov r0,r5\nbl lis2dw12_write_reg\n'
   if i==0:asm+='cmp r0,#0\nbne 1f\n'
  wrapper(name,asm+'1: pop {r2,r3,r4,r5,r6,pc}\n')
 helpers+=['uint32_t r1_native_power_first(uint32_t b,uint32_t v) {return (b&0xf1u)|((v&1u)<<3)|(v&6u);}','uint32_t r1_native_power_second(uint32_t b,uint32_t v) {return (b&0xfbu)|((v&8u)>>1);}','uint32_t r1_native_reg17_update(uint32_t b) {return b|0x40u;}']
 wrapper('r1_lis_native_power_mode_set','push {r2,r3,r4,r5,r6,lr}\nmov r4,r1\nmov r5,r0\nmovs r3,#1\nmov r2,sp\nmovs r1,#32\nbl lis2dw12_read_reg\ncmp r0,#0\nbne 1f\nldrb r0,[sp]\nmov r1,r4\nbl r1_native_power_first\nstrb r0,[sp]\nmovs r3,#1\nmov r2,sp\nmovs r1,#32\nmov r0,r5\nbl lis2dw12_write_reg\ncmp r0,#0\nbne 1f\nmovs r3,#1\nadd r2,sp,#4\nmovs r1,#37\nmov r0,r5\nbl lis2dw12_read_reg\nmov r6,r0\nldrb r0,[sp,#4]\nmov r1,r4\nbl r1_native_power_second\nstrb r0,[sp,#4]\nmovs r3,#1\nadd r2,sp,#4\nmovs r1,#37\nmov r0,r5\nbl lis2dw12_write_reg\nadd r0,r6\n1: pop {r2,r3,r4,r5,r6,pc}\n')
 wrapper('r1_lis_reg17_bit6_enable','push {r3,r4,r5,lr}\nmov r4,r0\nmovs r3,#1\nmov r2,sp\nmovs r1,#23\nbl lis2dw12_read_reg\ncmp r0,#0\nbne 1f\nldrb r0,[sp]\nbl r1_native_reg17_update\nstrb r0,[sp]\nmovs r3,#1\nmov r2,sp\nmovs r1,#23\nmov r0,r4\nbl lis2dw12_write_reg\n1: pop {r3,r4,r5,pc}\n')
 generated=out/'st-field-updates.c';generated.write_text('/* Attributed ST assignments factored into pure byte updates.\n'+(vendor/'LICENSE').read_text()+'\n*/\n#include <stdint.h>\n#include "lis2dw12_reg.h"\n'+'\n'.join(helpers)+'\n');source=ROOT/'r1/components/runtime/native_lis_call_frames.c';source.write_text('/* Transport runs at native caller SP after pure byte helpers return. */\n'+'\n'.join(bridges)+'\n');inputs[str(Path(__file__).relative_to(ROOT))]=sha(Path(__file__));rows=[];objects=[]
 for src,name in [(source,'native_lis_call_frames.o'),(generated,'st-field-updates.o')]:
  obj=out/name;cmd=['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-mfloat-abi=hard','-mfpu=fpv4-sp-d16','-std=c11','-Os','-ffreestanding','-fno-builtin','-fno-strict-aliasing','-fshort-enums','-ffunction-sections','-fdata-sections','-Wall','-Wextra','-Werror','-I'+str(vendor),'-isystem',str(ROOT/'vendor-cache/r1/gcc-arm-none-eabi-9-2020-q2-update/arm-none-eabi/include'),'-c',str(src),'-o',str(obj)];subprocess.run(cmd,check=True);inputs[str(src.relative_to(ROOT))]=sha(src);rows.append(dict(source=str(src.relative_to(ROOT)),source_sha256=sha(src),command=cmd,compiled=True,object_sha256=sha(obj),undefined=undefined_symbols(obj)[0]));objects.append(obj)
 clone=out/'parent-weak.o';subprocess.run(['arm-none-eabi-objcopy',*[f'--weaken-symbol={x}' for x in replacements],str(po),str(clone)],check=True);assert allocated_sections(po)==allocated_sections(clone)
 def nm(path):return {v[2]:(v[0],v[1]) for l in subprocess.check_output(['arm-none-eabi-nm',str(path)],text=True).splitlines() if len(v:=l.split())==3}
 before,after=nm(po),nm(clone);assert set(before)==set(after)
 for name,v in before.items():assert after[name]==(v[0],'W') if name in replacements else after[name]==v
 linked=out/'native-lis-call-frames-runtime.o';subprocess.run(['arm-none-eabi-ld','-r',str(clone),*map(str,objects),'-o',str(linked)],check=True);u=undefined_symbols(linked)[0];assert u==p['undefined_symbols'] and len(u)==28
 graph=out/'configure-source.o';subprocess.run(['arm-none-eabi-ld','-r','--gc-sections','-u','r1_lis2dw12_configure_boundary',str(linked),'-o',str(graph)],check=True)
 r=dict(units=rows,inputs=inputs,parent_report_sha256=sha(pr),parent_object_sha256=sha(po),parent_clone_sha256=sha(clone),parent_allocated_sections_identical=True,only_named_symbol_bindings_weakened=replacements,linked_sha256=sha(linked),graph_object_sha256=sha(graph),undefined_symbols=u,graph_undefined_symbols=undefined_symbols(graph)[0],source_assignments=slices,upstream_pin='8d4bd522015004a9646102702901ba5a15ec6d39',upstream_license='BSD-3-Clause',unmodified_upstream_body=False,exact_vendor_checkout_proven=False,instruction_identity=False,whole_image_complete=False,hardware_write_executed=False)
 (out/'report.json').write_text(json.dumps(r,indent=2)+'\n');print('Native LIS transport call bridges and pure attributed field helpers compiled:28 main imports')
if __name__=='__main__':main()
