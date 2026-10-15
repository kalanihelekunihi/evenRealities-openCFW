#!/usr/bin/env python3
"""Recompose selected Apollo C with distinct timeout text and live RAM state."""
from pathlib import Path
import hashlib,json,struct,subprocess
from elftools.elf.elffile import ELFFile
root=Path(__file__).resolve().parents[3]
build=root/'build/c-firmware'
out=build/'pool-state-round873';out.mkdir(parents=True,exist_ok=True)
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
changed_names=('send_timeout_end.c','timeout_submit.c','pool_live_state.c')
changed=[]
for name in changed_names:
 src=root/'components/audio/uart_thread_source_candidate'/name
 obj=out/(src.stem+'.o')
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb',
                 '-fshort-enums','-std=c11','-ffreestanding','-fno-builtin','-O2',
                 '-Wall','-Wextra','-Werror','-c',str(src),'-o',str(obj)],check=True)
 changed.append(obj)
audio=selected('audio-source-coherence-round855','receipt.json',
               omit=('/user_response.c','/send_timeout_end.c','/timeout_submit.c'))
assert old_user not in audio and len(audio)==925
current=stage('audio-corrected',None,[*audio,corrected,*changed])
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
 ('user-response-round869','user_response_log_strings.o'),
 ('work-submit-round871','work_submit_log_strings.o'))]
timeout_src=root/'components/audio/uart_thread_source_candidate/timeout_end_log_strings.c'
timeout_obj=out/'timeout_end_log_strings.o'
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb',
                '-fshort-enums','-std=c11','-ffreestanding','-fno-builtin','-O2',
                '-Wall','-Wextra','-Werror','-c',str(timeout_src),'-o',str(timeout_obj)],check=True)
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
assert struct.unpack_from('<I',blob,0x491618-0x438000)[0]==0x20074aa0
assert struct.unpack_from('<I',blob,0x491650-0x438000)[0]==0x20074aa4
assert struct.unpack_from('<I',blob,0x491630-0x438000)[0]==0x20075031
assert struct.unpack_from('<I',blob,0x45e004-0x438000)[0]==0x783c80
with timeout_obj.open('rb') as f:
 elf=ELFFile(f);syms={s.name:s for s in elf.get_section_by_name('.symtab').iter_symbols()}
 cells={'name_peer':0x45e000,'name_user':0x45e020,'name_slave':0x45e65c,
        'name_input':0x45e8b0,'name_display':0x45ebb0,'running_text':0x45e004,
        'compact':0x45e008,'submit_failed':0x45dff8,'submit_compact':0x45dffc}
 for suffix,cell in cells.items():
  name='audio_uart_timeout_'+suffix
  addr=struct.unpack_from('<I',blob,cell-0x438000)[0]
  sym=syms[name]
  data=elf.get_section(sym['st_shndx']).data()[sym['st_value']:].split(b'\0',1)[0]+b'\0'
  assert data==blob[addr-0x438000:].split(b'\0',1)[0]+b'\0',(name,hex(addr))
with changed[2].open('rb') as f:
 elf=ELFFile(f);syms={s.name:s for s in elf.get_section_by_name('.symtab').iter_symbols()}
 for name in ('audio_uart_pool_queue','audio_uart_pool_mutex'):
  sym=syms[name]
  assert sym['st_size']==4 and elf.get_section(sym['st_shndx'])['sh_type']=='SHT_NOBITS',name
strings.append(timeout_obj)
aliases=[(f'audio_uart_{group}_{kind}',f'audio_uart_begin0_{kind}')
         for group in ('role','timer','user') for kind in ('module','source')]
aliases += [(f'audio_uart_timeout_{suffix}',f'audio_uart_begin0_{kind}')
            for suffix,kind in (('module','module'),('source','source'),
                                ('module_peer','module'),('source_peer','source'),
                                ('module_display','module'),('source_display','source'))]
aliases += [('audio_uart_timeout_compact_peer','audio_uart_timeout_compact'),
            ('audio_uart_timeout_compact_display','audio_uart_timeout_compact'),
            ('audio_uart_timeout_submit_compact_peer','audio_uart_timeout_submit_compact'),
            ('audio_uart_timeout_queue','audio_uart_pool_queue'),
            ('audio_uart_timeout_mutex','audio_uart_pool_mutex'),
            ('audio_uart_timeout_running_state','audio_uart_pool_initialized')]
current=stage('apollo-main-pool-state-selected-source',current,strings,aliases)
old=build/'timeout-end-round872/apollo-main-timeout-end-source.o'
before=imports(old);after=imports(current)
assert not after-before,(after-before)
assert {'audio_uart_user_missing_module','audio_uart_user_missing_source',
        'audio_uart_user_missing_function','audio_uart_user_dispatch_function'} not in after
assert len(after)<=len(before)
assert not {'audio_uart_timeout_queue','audio_uart_timeout_mutex',
            'audio_uart_timeout_running_state','audio_uart_timeout_running_text',
            'audio_uart_pool_queue','audio_uart_pool_mutex'}&after
defined=subprocess.check_output(['arm-none-eabi-nm','-g','--defined-only',str(current)],text=True)
for name in ('audio_uart_user_broadcast','audio_uart_user_dispatch','audio_uart_user_response'):
 assert sum(line.endswith(' '+name) for line in defined.splitlines())==1,name
symbols={x.split()[-1]:int(x.split()[0],16) for x in subprocess.check_output(['arm-none-eabi-nm','-a',str(current)],text=True).splitlines() if len(x.split())==3 and x.split()[0].strip('0123456789abcdefABCDEF')==''}
for alias,canonical in aliases:assert symbols[alias]==symbols[canonical],(alias,canonical)
assert symbols['audio_uart_timeout_running_state']!=symbols['audio_uart_timeout_running_text']
receipt={'round':873,'status':'PASS_DISTINCT_TIMEOUT_TEXT_AND_LIVE_RAM_STATE',
         'component':'Apollo Main selected source composition',
         'corrected_body':str(corrected.relative_to(root)),
         'corrected_body_sha256':hashlib.sha256(corrected.read_bytes()).hexdigest(),
         'changed_sources_sha256':{name:hashlib.sha256((root/'components/audio/uart_thread_source_candidate'/name).read_bytes()).hexdigest() for name in changed_names},
         'timeout_strings_source_sha256':hashlib.sha256(timeout_src.read_bytes()).hexdigest(),
         'native_timeout_strings_matched':len(cells),
         'source_units':len(audio)+1+len(changed)+len(ambiq)+len(main)+len(foundation)+2+
                        len(non_uart)+len(bundle)+len(extra)+len(strings),
         'same_entry_aliases':len(alias_rows)+len(aliases),
         'unresolved_before_round872':len(before),'unresolved_after':len(after),
         'supersedes':'round872 timeout_running string/state symbol collision',
         'linked_object':str(current.relative_to(root)),
         'linked_sha256':hashlib.sha256(current.read_bytes()).hexdigest(),
         'whole_image_complete':False,'hardware_proof':False,
         'gates':['Final absolute RAM placement and remaining provider imports remain unresolved',
                  'Final image placement, byte equality, and hardware execution remain open']}
(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print('PASS_DISTINCT_TIMEOUT_TEXT_AND_STATE',len(after))
