#!/usr/bin/env python3
"""Compile and link twenty-four authenticated terminal/settings/UI RAM spans."""
from pathlib import Path
import hashlib,json,struct,subprocess

root=Path(__file__).resolve().parents[3]
srcdir=root/'components/audio/uart_thread_source_candidate'
out=root/'build/c-firmware/terminal-ram-placement-round1002';out.mkdir(parents=True,exist_ok=True)
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
def native_word(a):return struct.unpack_from('<I',blob,a-0x438000)[0]
assert native_word(0x5cf1c0)==0x200f9694
assert native_word(0x5cf1c4)==0x20374378
assert native_word(0x5cf204)==0x20074fff
assert native_word(0x5e5dd8)==0x2006e0d0
assert native_word(0x49bdf0)==0x200725a0
assert native_word(0x49bffc)==0x200706ec
assert native_word(0x49c030)==0x2007486c
assert native_word(0x46c694)==0x200036fc
assert native_word(0x46bee8)==0x20072da8
assert native_word(0x4672f8)==0x20072608
assert native_word(0x469b88)==0x2007501d
assert native_word(0x469b54)==0x2007501e
for literal,address in ((0x4d3444,0x20003bcc),(0x4d3478,0x200749ec),
                        (0x4d347c,0x200749f0),
                        (0x4d3430,0x200749f4),(0x4d34a0,0x200746e0),
                        (0x4d3440,0x20075025)):
    assert native_word(literal)==address
for literal,address in ((0x46c40c,0x20074994),(0x497938,0x2007491c),
                        (0x497d24,0x2007500d),(0x45d068,0x200749cc),
                        (0x45d0c8,0x20074b10)):
    assert native_word(literal)==address
sources={'encode':srcdir/'terminal_encode_send_5ce7c4.c',
         'status':srcdir/'terminal_status_reply.c',
         'tokens':srcdir/'terminal_agent_tokens.c',
         'settings':srcdir/'settings_notify_ram.c',
         'settings_runtime':srcdir/'settings_runtime_cells.c'}
sources.update({'settings_live':srcdir/'settings_live_buffers.c',
                'settings_manager':srcdir/'settings_manager_storage.c',
                'silent_mode':srcdir/'silent_mode_common_data_46949a.c',
                'system_alert':srcdir/'system_alert_ui_event_4d3354.c',
                'system_alert_page':srcdir/'system_alert_page_init_4d2f48.c',
                'system_alert_update':srcdir/'system_alert_page_update_4d30ba.c',
                'system_alert_mode_owner':srcdir/'registry_callback_4d2bce.c'})
objects=[]
for stem,source in sources.items():
    obj=out/(stem+'.o');objects.append(obj)
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb',
                    '-fshort-enums','-fno-builtin','-O2','-Wall','-Wextra','-Werror',
                    '-c',str(source),'-o',str(obj)],check=True)
lines=[]
for obj in objects:lines+=subprocess.check_output(['arm-none-eabi-nm','-g',str(obj)],text=True).splitlines()
needed=set();defined=set()
for line in lines:
    parts=line.split()
    if len(parts)==2 and parts[0]=='U':needed.add(parts[1])
    elif len(parts)==3 and parts[1].upper()!='U':defined.add(parts[2])
needed-=defined
asm=['.syntax unified','.thumb','.section .text.probe_stubs,"ax",%progbits']
for symbol in sorted(needed-{'audio_terminal_tx_pb_descriptor'}):
    asm += [f'.global {symbol}','.thumb_func',f'{symbol}:','  bx lr']
asm += ['.section .rodata.probe_descriptor,"a",%progbits',
        '.global audio_terminal_tx_pb_descriptor','audio_terminal_tx_pb_descriptor:',
        '  .word 0','.section .note.GNU-stack,"",%progbits']
stub=out/'probe_stubs.s';stub.write_text('\n'.join(asm)+'\n')
stubobj=out/'probe_stubs.o'
subprocess.run(['arm-none-eabi-as','-mcpu=cortex-m55','-mthumb',str(stub),'-o',str(stubobj)],check=True)
linker=srcdir/'terminal_ram_placement.ld';elf=out/'probe.elf'
subprocess.run(['arm-none-eabi-ld','-e','audio_terminal_send_message_5ce7c4',
                '-T',str(linker),'-o',str(elf),*[str(o) for o in objects],str(stubobj)],check=True)
symbols={}
for line in subprocess.check_output(['arm-none-eabi-nm','-S',str(elf)],text=True).splitlines():
    parts=line.split()
    if len(parts)==4:symbols[parts[3]]=(int(parts[0],16),int(parts[1],16))
expected={'audio_terminal_agent_session_ptr':(0x2006e0d4,4),
          'audio_system_alert_page_id_20003bcc':(0x20003bcc,4),
          'audio_settings_manager_storage':(0x200036fc,0x20),
          'audio_terminal_agent_special_flag':(0x2006e35c,1),
          'audio_terminal_message_sequence':(0x20074fff,1),
          'audio_settings_notify_encode_buffer':(0x200706ec,0x100),
          'audio_settings_notify_staging':(0x200725a0,0x68),
          'audio_settings_last_message_state':(0x20072608,13),
          'audio_settings_config_live':(0x20072da8,0x50),
          'audio_settings_notify_magic':(0x2007486c,4),
          'audio_settings_ancc_mutex':(0x2007491c,4),
          'audio_settings_left_version_last_request_tick':(0x20074994,4),
          'audio_settings_peer_send_queue':(0x200749cc,4),
          'audio_system_alert_parent_200749ec':(0x200749ec,4),
          'audio_system_alert_child_200749f0':(0x200749f0,4),
          'audio_system_alert_message_notify':(0x200749f4,4),
          'audio_system_alert_font_200746e0':(0x200746e0,4),
          'audio_settings_peer_event':(0x20074b10,4),
          'audio_settings_ancc_count':(0x2007500d,1),
          'audio_silent_mode_ui_status':(0x2007501d,1),
          'audio_silent_mode_change_from_app':(0x2007501e,1),
          'audio_system_alert_active_20075025':(0x20075025,1),
          'audio_terminal_tx_staging':(0x200f9694,0x850),
          'audio_terminal_tx_encoded':(0x20374378,0x878)}
for name,placement in expected.items():assert symbols[name]==placement,(name,symbols.get(name),placement)
spans=sorted((a,a+n,name) for name,(a,n) in expected.items())
assert all(spans[i][1]<=spans[i+1][0] for i in range(len(spans)-1))
selected=root/'build/c-firmware/system-alert-icons-round1034/apollo-main-system-alert-icons.o'
sections=subprocess.check_output(['arm-none-eabi-readelf','-SW',str(selected)],text=True)
for name in expected:
    section='.g2.ram.'+name.removeprefix('audio_')
    if name.startswith('audio_system_alert_'):section=section.rsplit('_200',1)[0]
    if name=='audio_system_alert_message_notify':
        assert '.bss.g2.ram.system_alert_message_notify NOBITS' in sections
        continue
    assert section in sections,section
for alias,offset in {'audio_uart_hand_snapshot_context':0,'g2_audio_log_timezone':0,
                     'audio_settings_config_previous':4,'audio_settings_als_previous':24,
                     'audio_settings_terminal_previous':28}.items():
    assert symbols[alias][0]==0x200036fc+offset,(alias,symbols.get(alias))
selected_imports=subprocess.check_output(['arm-none-eabi-nm','-u',str(selected)],text=True).splitlines()
receipt={'round':1002,'status':'PASS_TERMINAL_RAM_PLACEMENT_FRAGMENT',
         'component':'Apollo terminal/settings/UI source-owned RAM placement for twenty-four spans',
         'source':[str(s.relative_to(root)) for s in sources.values()],
         'source_sha256':{s.name:hashlib.sha256(s.read_bytes()).hexdigest() for s in sources.values()},
         'linker':str(linker.relative_to(root)),'linker_sha256':hashlib.sha256(linker.read_bytes()).hexdigest(),
         'official_image_sha256':hashlib.sha256(blob).hexdigest(),
         'symbols':{k:{'address':hex(a),'size':n} for k,(a,n) in expected.items()},
         'validation':'M55 strict compile, final ELF linker fragment placement and no overlap among twenty-four minimum spans',
         'probe_elf':str(elf.relative_to(root)),'probe_sha256':hashlib.sha256(elf.read_bytes()).hexdigest(),
         'selected_linked_object':str(selected.relative_to(root)),
         'selected_linked_sha256':hashlib.sha256(selected.read_bytes()).hexdigest(),
         'selected_unresolved_imports':len(selected_imports),
         'whole_image_complete':False,'hardware_proof':False,
         'gates':['Probe stubs do not supply firmware behavior',
                  'Manager and two buffer allocation extents are minimum only',
                  'Full RAM map overlap audit and image link remain open']}
(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(receipt['status'],len(expected),receipt['probe_sha256'])
