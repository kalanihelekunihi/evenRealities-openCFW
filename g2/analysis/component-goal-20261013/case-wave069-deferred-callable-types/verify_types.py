from pathlib import Path
import json,subprocess
H=Path(__file__).resolve().parent;R=H.parents[3];changes=json.loads((H/'source-changes.json').read_text());rows=[]
def walk(x):
 if isinstance(x,dict):
  yield x
  for y in x.get('inner',[]):yield from walk(y)
def get(p):
 cmd=['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-std=c11','-ffreestanding','-fsyntax-only','-Xclang','-ast-dump=json','-I',str((R/'g2/components/case/deferred_consumer_offline')),str(p)];run=subprocess.run(cmd,capture_output=True,text=True);assert run.returncode==0,run.stderr;return list(walk(json.loads(run.stdout)))
for row in changes:
 p=R/row['path'];new=get(p);old=get(H/'before'/p.name)
 def callback_types(ns):return [x['type']['qualType'] for x in ns if x.get('kind')=='CStyleCastExpr' and '(*)(void *, uint32_t)' in x.get('type',{}).get('qualType','')]
 def old_types(ns):return [x['type']['qualType'] for x in ns if x.get('kind')=='CStyleCastExpr' and '(*)(uint32_t, uint32_t)' in x.get('type',{}).get('qualType','')]
 assert callback_types(new)==['void (*)(void *, uint32_t)'];assert old_types(old)==['void (*)(uint32_t, uint32_t)'];assert not old_types(new)
 if p.name=='consumer.c':
  current=next(x['type']['qualType'] for x in new if x.get('kind')=='FunctionDecl' and x.get('name')=='case_scheduler_state');previous=next(x['type']['qualType'] for x in old if x.get('kind')=='FunctionDecl' and x.get('name')=='case_scheduler_state');assert current=='uint32_t (void)' and previous=='int32_t (void)'
 rows.append(dict(source=row['path'],callback_type=callback_types(new)[0],saved_original_rejected_by_contract=True))
unit=H/'deferred-type-contract.c';unit.write_text('''#include <stdint.h>
extern void vEventGroupSetBitsCallback(void *,uint32_t);
extern void vEventGroupClearBitsCallback(void *,uint32_t);
_Static_assert(__builtin_types_compatible_p(__typeof__(&vEventGroupSetBitsCallback),void (*)(void *,uint32_t)), "set callback");
_Static_assert(__builtin_types_compatible_p(__typeof__(&vEventGroupClearBitsCallback),void (*)(void *,uint32_t)), "clear callback");
_Static_assert(!__builtin_types_compatible_p(void (*)(uint32_t,uint32_t),void (*)(void *,uint32_t)), "original callback type differs");
_Static_assert(sizeof(void *)==4 && sizeof(uint32_t)==4, "pinned word ABI");
''');run=subprocess.run(['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-std=c11','-Werror','-fsyntax-only',str(unit)],capture_output=True,text=True);assert run.returncode==0,run.stderr
(H/'type-verification.json').write_text(json.dumps(dict(status='PASS_DEFERRED_CONSUMER_C_TYPE_CONTRACTS',actual_source_AST=rows,original_source_negative_controls=2,static_assertions=4,low_consumer_scheduler_return_decl_matches_actual_provider=True,limits=['Known queued event callbacks; arbitrary external callback targets notclosed','Source originals compile syntactically butfail callable-type compatibility contract']),indent=2)+'\n');print('PASS_DEFERRED_CONSUMER_C_TYPE_CONTRACTS')
