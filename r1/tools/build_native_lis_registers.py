#!/usr/bin/env python3
"""Compile attributed ST single-register bodies with native scratch-frame bridges."""
import hashlib,json,re,subprocess
from pathlib import Path
from build_source_candidates import undefined_symbols
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
FUNCTIONS={0x750b8:'block_data_update_set',0x753c6:'fifo_mode_set',0x753f4:'fifo_watermark_set',0x75422:'filter_bandwidth_set',0x754ac:'full_scale_set',0x757ec:'reset_set',0x7581a:'tap_detection_on_x_set',0x75848:'tap_detection_on_y_set',0x75876:'tap_detection_on_z_set',0x758a4:'tap_dur_set',0x758d2:'tap_mode_set',0x75900:'tap_quiet_set',0x7592e:'tap_shock_set',0x7595c:'tap_threshold_x_set',0x7598a:'tap_threshold_y_set',0x759b8:'tap_threshold_z_set',0x757d2:'reset_get'}
def main():
 out=BASE/'native-lis-registers';out.mkdir(exist_ok=True);vendor=ROOT/'vendor-cache/r1/st-lis2dw12-8d4bd522015004a9646102702901ba5a15ec6d39';expected={'lis2dw12_reg.c':'525e5a139e15ece3ee93f583aa4321739cd1960088e56ffe922ec4f646c19f11','lis2dw12_reg.h':'8ec9712080bf855726f764303b0c2f3eb209c51b8fdada86af059a1ee70fa048','LICENSE':'b54f36a43cf9b8f6292c8f0f3b4c267ebd59859587e0152c94305bc81dda68bc'}
 for name,h in expected.items():assert sha(vendor/name)==h
 raw=(vendor/'lis2dw12_reg.c').read_bytes().decode();bodies=[];slices=[];glue=['#include <stdint.h>']
 for address,suffix in FUNCTIONS.items():
  name='lis2dw12_'+suffix;m=re.search(r'int32_t '+name+r'\(.*?\r?\n\}',raw,re.S);assert m,name;body=m.group();local=re.search(r'  (lis2dw12_\w+_t) reg;',body);assert local,name
  adapted=body.replace(name+'(',name+'_body(',1);pos=adapted.index(')');adapted=adapted[:pos]+', volatile uint8_t *frame'+adapted[pos:];adapted=adapted.replace(local.group(),f'  {local[1]} *reg=({local[1]} *)(uintptr_t)frame;').replace('(uint8_t *) &reg','(uint8_t *)reg').replace('reg.','reg->');assert '&reg' not in adapted and 'reg.' not in adapted
  bodies.append(adapted);slices.append(dict(address=hex(address),name=name,start=m.start(),end=m.end(),original_slice_sha256=hashlib.sha256(body.encode()).hexdigest(),adaptations=['Rename internal body and append native scratch pointer','Replace local register with pointer to native saved-r3 byte','Redirect address/member access; retain upstream status and bitfield algorithm']))
  glue.append('__attribute__((naked)) uint32_t '+name+'(void) { __asm__ volatile("push {r3,r4,r5,lr}\\nmov r2,sp\\nbl '+name+'_body\\npop {r3,r4,r5,pc}\\n"); }')
 glue.append('__attribute__((naked)) uint32_t lis2dw12_write_reg(void) { __asm__ volatile("push {r4,r5}\\nldr r4,[r0,#12]\\nldr r5,[r0]\\nmov r0,r4\\nmov r12,r5\\npop {r4,r5}\\nbx r12\\n"); }')
 generated=out/'st-register-frames.c';generated.write_text('/* Attributed ST adaptation: native saved-register byte is explicit.\n'+(vendor/'LICENSE').read_text()+'\n*/\n#include <stdint.h>\n#include "lis2dw12_reg.h"\n'+'\n'.join(bodies)+'\n');source=ROOT/'r1/components/runtime/native_lis_registers.c';source.write_text('/* Register-only entry bridges; r0/r1 and incoming r3 are native ABI inputs. */\n'+'\n'.join(glue)+'\n')
 inputs={str(Path(__file__).relative_to(ROOT)):sha(Path(__file__)),**{str((vendor/name).relative_to(ROOT)):h for name,h in expected.items()}};rows=[];objects=[]
 for src,name in [(source,'native_lis_registers.o'),(generated,'st-register-frames.o')]:
  obj=out/name;cmd=['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-mfloat-abi=hard','-mfpu=fpv4-sp-d16','-std=c11','-Os','-ffreestanding','-fno-builtin','-fno-strict-aliasing','-fshort-enums','-ffunction-sections','-fdata-sections','-Wall','-Wextra','-Werror','-I'+str(vendor),'-isystem',str(ROOT/'vendor-cache/r1/gcc-arm-none-eabi-9-2020-q2-update/arm-none-eabi/include'),'-c',str(src),'-o',str(obj)];subprocess.run(cmd,check=True);inputs[str(src.relative_to(ROOT))]=sha(src);rows.append(dict(source=str(src.relative_to(ROOT)),source_sha256=sha(src),command=cmd,compiled=True,object_sha256=sha(obj),undefined=undefined_symbols(obj)[0]));objects.append(obj)
 parent=BASE/'native-lis-identity';pr=parent/'report.json';p=json.loads(pr.read_text());po=parent/'native-lis-identity-runtime.o';assert sha(po)==p['linked_sha256']
 for path,h in p['inputs'].items():assert sha(ROOT/path)==h,path;inputs[path]=h
 linked=out/'native-lis-registers-runtime.o';subprocess.run(['arm-none-eabi-ld','-r',str(po),*map(str,objects),'-o',str(linked)],check=True);u=undefined_symbols(linked)[0];assert u==p['undefined_symbols'] and len(u)==29
 roots=['lis2dw12_'+x for x in FUNCTIONS.values()]+['lis2dw12_write_reg'];graph=out/'registers-source.o';subprocess.run(['arm-none-eabi-ld','-r','--gc-sections',*[v for x in roots for v in ['-u',x]],str(linked),'-o',str(graph)],check=True);assert not undefined_symbols(graph)[0]
 r=dict(units=rows,inputs=inputs,parent_report_sha256=sha(pr),parent_object_sha256=sha(po),linked_sha256=sha(linked),graph_object_sha256=sha(graph),undefined_symbols=u,graph_undefined_symbols=[],roots=roots,source_slices=slices,upstream_pin=vendor.name.removeprefix('st-lis2dw12-'),upstream_license='BSD-3-Clause',exact_vendor_checkout_proven=False,unmodified_upstream_body=False,whole_image_complete=False,instruction_identity=False,hardware_write_executed=False)
 (out/'report.json').write_text(json.dumps(r,indent=2)+'\n');print('17 attributed ST register bodies + native write proxy compiled; main29 imports')
if __name__=='__main__':main()
