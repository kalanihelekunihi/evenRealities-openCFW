#!/usr/bin/env python3
"""Recompose the selected Apollo C objects with the corrected user response body."""
from pathlib import Path
import hashlib,json,subprocess
root=Path(__file__).resolve().parents[3]
build=root/'build/c-firmware'
out=build/'corrected-user-response-round870';out.mkdir(parents=True,exist_ok=True)
def read(path):return json.loads(path.read_text())
def imports(path):
 return {x.split()[-1] for x in subprocess.check_output(['arm-none-eabi-nm','-u',str(path)],text=True).splitlines()}
def selected(folder,report,omit=(),choose=None):
 rows=read(build/folder/report)['results'];objects=[]
 for row in rows:
  if row['status']!='PASS' or any(row['source'].endswith(s) for s in omit):continue
  if choose is not None and not choose(row):continue
  source=root/row['source'];assert source.is_file()
  assert hashlib.sha256(source.read_bytes()).hexdigest()==row['source_sha256'],source
  objects.append(root/row['object'])
 return objects
def stage(label,base,items,aliases=()):
 dest=out/(label+'.o')
 subprocess.run(['arm-none-eabi-ld','-r',*[f'--defsym={a}={b}' for a,b in aliases],
                 *([str(base)] if base else []),*[str(x) for x in items],'-o',str(dest)],check=True)
 return dest
old_user=build/'audio-source-coherence-round855/user_response.o'
corrected=build/'user-response-round869/user_response.o'
assert corrected.is_file()
audio=selected('audio-source-coherence-round855','receipt.json',omit=('/user_response.c',))
assert old_user not in audio and len(audio)==927
current=stage('audio-corrected',None,[*audio,corrected])
ambiq=selected('ambiq-audio-integration-round856','receipt.json')
assert len(ambiq)==64
current=stage('ambiq',current,ambiq)
main_omit=tuple('full_formatter_outer_candidate/'+x+'.c' for x in
                ('float_bridge','float_render','fp_primitives','general_format'))
main=selected('main-source-audit-round857','receipt.json',omit=main_omit)
assert len(main)==165
current=stage('main',current,main)
foundation_omit=('freertos_ready/tasks_subset.c','freertos_resume/tasks_resume.c',
                 'wsf_timer/wsf_timer_stop.c')
foundation=selected('foundation-integration-round858','receipt.json',omit=foundation_omit)
assert len(foundation)==37
current=stage('foundation',current,foundation)
current=stage('ready-event',current,[build/'ready-event-provider-round859/tasks_subset_selected.o'])
current=stage('wsf-timer',current,[build/'wsf-timer-helpers-round860/wsf_timer_selected.o'])
non_uart=selected('audio-non-uart-round861','audit.json',
                  omit=('uart_tx_offline/am_hal_uart.c','transition_producers_offline/producers.c'))
assert len(non_uart)==191
current=stage('audio-non-uart',current,non_uart)
bundle_audit=read(build/'audio-provider-bundle-round862/audit.json')
prior=build/'audio-non-uart-round861/apollo-main-expanded-audio-source.o'
colliding={owner for owners in bundle_audit['strong_provider_collisions'].values()
           for owner in owners if owner!=prior.name}
bundle=selected('audio-provider-bundle-round862','audit.json',
                choose=lambda row:Path(row['object']).name not in colliding)
assert len(bundle)==41
current=stage('provider-bundle',current,bundle)
alias_rows=read(build/'audio-same-entry-aliases-round863/same-entry-map.json')
assert len(alias_rows)==116
current=stage('same-entry-aliases',current,[],
              aliases=[(r['alias'],r['canonical']) for r in alias_rows])
extra=selected('audio-excluded-dirs-round864','audit.json',
               choose=lambda row:Path(row['source']).parent.name not in
               {'power_vendor_candidate','uart_irq_source_candidate'})
assert len(extra)==82
current=stage('extra-selected-audio',current,extra)
strings=[build/folder/name for folder,name in (
 ('send-begin-strings-round865','send_begin_log_strings.o'),
 ('dashboard-load-strings-round866','dashboard_load_log_strings.o'),
 ('mac-role-strings-round867','mac_role_log_strings.o'),
 ('sync-timer-strings-round868','sync_timer_log_strings.o'),
 ('user-response-round869','user_response_log_strings.o'))]
aliases=[(f'audio_uart_{group}_{kind}',f'audio_uart_begin0_{kind}')
         for group in ('role','timer','user') for kind in ('module','source')]
current=stage('apollo-main-corrected-selected-source',current,strings,aliases)
old=build/'user-response-round869/apollo-main-user-response-strings.o'
before=imports(old);after=imports(current)
assert not after-before,(after-before)
assert {'audio_uart_user_missing_module','audio_uart_user_missing_source',
        'audio_uart_user_missing_function','audio_uart_user_dispatch_function'} not in after
assert len(after)<=len(before)
defined=subprocess.check_output(['arm-none-eabi-nm','-g','--defined-only',str(current)],text=True)
for name in ('audio_uart_user_broadcast','audio_uart_user_dispatch','audio_uart_user_response'):
 assert sum(line.endswith(' '+name) for line in defined.splitlines())==1,name
receipt={'round':870,'status':'PASS_CORRECTED_USER_RESPONSE_SELECTED_SOURCE_REBUILD',
         'component':'Apollo Main selected source composition',
         'corrected_body':str(corrected.relative_to(root)),
         'corrected_body_sha256':hashlib.sha256(corrected.read_bytes()).hexdigest(),
         'source_units':len(audio)+1+len(ambiq)+len(main)+len(foundation)+2+
                        len(non_uart)+len(bundle)+len(extra)+len(strings),
         'same_entry_aliases':len(alias_rows)+len(aliases),
         'unresolved_before_stale_composite':len(before),'unresolved_after':len(after),
         'linked_object':str(current.relative_to(root)),
         'linked_sha256':hashlib.sha256(current.read_bytes()).hexdigest(),
         'whole_image_complete':False,'hardware_proof':False,
         'gates':['Product RAM and remaining provider imports remain unresolved',
                  'Final image placement, byte equality, and hardware execution remain open']}
(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print('PASS_CORRECTED_SELECTED_SOURCE',len(after))
