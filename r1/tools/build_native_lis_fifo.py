#!/usr/bin/env python3
"""Compile native FIFO ABI glue and attributed pinned ST level-body adaptation."""
import hashlib,json,re,subprocess
from pathlib import Path
from build_source_candidates import undefined_symbols
from audit_source_frontier import functions
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=BASE/'native-lis-fifo';out.mkdir(exist_ok=True);pin='8d4bd522015004a9646102702901ba5a15ec6d39';vendor=ROOT/('vendor-cache/r1/st-lis2dw12-'+pin)
 expected={'lis2dw12_reg.c':'525e5a139e15ece3ee93f583aa4321739cd1960088e56ffe922ec4f646c19f11','lis2dw12_reg.h':'8ec9712080bf855726f764303b0c2f3eb209c51b8fdada86af059a1ee70fa048','LICENSE':'b54f36a43cf9b8f6292c8f0f3b4c267ebd59859587e0152c94305bc81dda68bc'}
 for name,h in expected.items():assert sha(vendor/name)==h,name
 original=(vendor/'lis2dw12_reg.c').read_bytes().decode();match=re.search(r'int32_t lis2dw12_fifo_data_level_get\(.*?\r?\n\}',original,re.S);assert match
 body=match.group();assert body.count('lis2dw12_read_reg')==1 and body.count('lis2dw12_fifo_samples_t reg;')==1
 adapted=body.replace('lis2dw12_fifo_data_level_get(const stmdev_ctx_t *ctx, uint8_t *val)','r1_lis_fifo_level_body(const stmdev_ctx_t *ctx, uint8_t *val, volatile uint8_t *frame)').replace('lis2dw12_fifo_samples_t reg;','lis2dw12_fifo_samples_t *reg=(lis2dw12_fifo_samples_t *)(uintptr_t)frame;').replace('(uint8_t *) &reg','(uint8_t *)reg').replace('reg.diff','reg->diff')
 assert adapted!=body and 'reg.diff' not in adapted and '&reg' not in adapted and 'r1_lis_fifo_level_body' in adapted
 generated=out/'st-level-frame.c';generated.write_text('/* Attributed adaptation: local register byte externalized to native ABI frame.\n'+(vendor/'LICENSE').read_text()+'\n*/\n#include <stdint.h>\n#include "lis2dw12_reg.h"\n_Static_assert(sizeof(lis2dw12_fifo_samples_t)==1,"native level byte");\n'+adapted+'\n')
 inputs={str(Path(__file__).relative_to(ROOT)):sha(Path(__file__)),**{str((vendor/name).relative_to(ROOT)):h for name,h in expected.items()}};rows=[]
 for source,name in [(ROOT/'r1/components/runtime/native_lis_fifo.c','native_lis_fifo.o'),(generated,'st-level-frame.o')]:
  obj=out/name;dep=obj.with_suffix('.d');cmd=['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-munaligned-access','-mfpu=fpv4-sp-d16','-mfloat-abi=hard','-std=c11','-Os','-ffreestanding','-fno-builtin','-fno-strict-aliasing','-fshort-enums','-ffunction-sections','-fdata-sections','-Wall','-Wextra','-Werror','-fno-delete-null-pointer-checks','-I'+str(vendor),'-isystem',str(ROOT/'vendor-cache/r1/gcc-arm-none-eabi-9-2020-q2-update/arm-none-eabi/include'),'-MD','-MF',str(dep),'-c',str(source),'-o',str(obj)];subprocess.run(cmd,check=True)
  for p in dep.read_text().replace('\\\n',' ').split(':',1)[1].split():
   path=Path(p);inputs[str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else p]=sha(path)
  u,d=undefined_symbols(obj);rows.append(dict(source=str(source.relative_to(ROOT)),source_sha256=sha(source),command=cmd,compiled=True,object_sha256=sha(obj),undefined=u,defined=d,emitted_function_count=len(functions(obj))))
 linked=out/'native-lis-fifo.o';subprocess.run(['arm-none-eabi-ld','-r',str(out/'native_lis_fifo.o'),str(out/'st-level-frame.o'),'-o',str(linked)],check=True);u,d=undefined_symbols(linked);assert not u
 r=dict(units=rows,inputs=inputs,linked_sha256=sha(linked),undefined_symbols=u,defined_symbols=d,upstream_component='st-lis2dw12-pid',upstream_pin=pin,upstream_license='BSD-3-Clause',exact_vendor_checkout_proven=False,upstream_function='lis2dw12_fifo_data_level_get',source_slice_start=match.start(),source_slice_end=match.end(),original_slice_sha256=hashlib.sha256(body.encode()).hexdigest(),adaptations=['Rename to internal kernel and add explicit native scratch pointer','Replace local register byte with pointer into external16-byte native frame','Use reg->diff instead of reg.diff; algorithm and status propagation unchanged'],unmodified_upstream_body=False,context_prefix_bytes=16,full_context_size_proven=False,application_linked=False,instruction_identity=False,whole_image_complete=False)
 (out/'report.json').write_text(json.dumps(r,indent=2)+'\n');print('Native LIS FIFO and attributed ST level kernel compiled:zero imports')
if __name__=='__main__':main()
