from pathlib import Path
import json,subprocess,hashlib
H=Path(__file__).resolve().parent;R=H.parents[3];rows=json.loads((H/'source-changes.json').read_text());checks=[]
def nodes(obj):
 if isinstance(obj,dict):
  yield obj
  for child in obj.get('inner',[]):yield from nodes(child)
def ast(p):
 cmd=['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-std=c11','-ffreestanding','-fsyntax-only','-Xclang','-ast-dump=json',str(p)];run=subprocess.run(cmd,capture_output=True,text=True);assert run.returncode==0,run.stderr;return list(nodes(json.loads(run.stdout)))
for row in rows:
 p=R/row['path'];before=H/'before'/p.name;now=ast(p);old=ast(before)
 if p.name=='dma_abort_provider.c':
  def kind(ns):return next(x['type']['qualType'] for x in ns if x.get('kind')=='VarDecl' and x.get('name')=='callback')
  current=kind(now);original=kind(old);assert current=='void (*)(uint8_t *)' and original=='void (*)(void *)'
 else:
  def cast(ns,name):
   f=next(x for x in ns if x.get('kind')=='FunctionDecl' and x.get('name')==name)
   return [x['type']['qualType'] for x in nodes(f) if x.get('kind')=='CStyleCastExpr' and '(*)(uint32_t)' in x.get('type',{}).get('qualType','')]
  current=cast(now,'invoke_cancel');original=cast(old,'invoke');assert current==['uint32_t (*)(uint32_t)'] and original==['void (*)(uint32_t)']
  if p.name=='application_boot_sensor_irq_5f50_candidate.c':assert cast(now,'invoke')==['void (*)(uint32_t)'] # RxISR ABI retained
 checks.append(dict(source=row['path'],corrected_call_type=current,saved_original_call_type=original,old_contract_negative_control=True))
header=H/'slot-contract.c';header.write_text('''#include <stdint.h>
extern void case_uart_dma_abort_callback(uint8_t *);
extern uint32_t case_boot_sensor_cancel_callback(uint32_t);
_Static_assert(__builtin_types_compatible_p(__typeof__(&case_uart_dma_abort_callback),void (*)(uint8_t *)), "DMA target type");
_Static_assert(__builtin_types_compatible_p(__typeof__(&case_boot_sensor_cancel_callback),uint32_t (*)(uint32_t)), "cancel target type");
_Static_assert(!__builtin_types_compatible_p(void (*)(void *),void (*)(uint8_t *)), "original DMA call types differ");
_Static_assert(!__builtin_types_compatible_p(void (*)(uint32_t),uint32_t (*)(uint32_t)), "original cancel return types differ");
''')
run=subprocess.run(['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-std=c11','-Wall','-Wextra','-Werror','-fsyntax-only',str(header)],capture_output=True,text=True);assert run.returncode==0,run.stderr
r=dict(status='PASS_ACTUAL_SOURCE_AST_CALLBACK_TYPES_AND_3_ORIGINAL_NEGATIVE_CONTROLS',checks=checks,static_compiler_type_controls=4,limits=['AST reads actual dynamic call expression/local callback types; saved-original source compiles syntactically but fails slot compatibility contract','Producer-slot identity based on independently reviewed current source writers; other external/assembly writers not closed'])
(H/'type-verification.json').write_text(json.dumps(r,indent=2)+'\n');print(r['status'])
