#!/usr/bin/env python3
"""Actual send-hook/encoder/response sender/phone operation/header/battery protocol/frame/TX producer/service/voltage/updater/device-fields/low/diagnostic/initial-curve/recovery/cadence/configuration/KV/discharge/filter/statistics/control composition; ADC registry/delay remain fixtures."""
import hashlib,itertools,json,random,struct,subprocess,tempfile,sys
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-battery-runtime';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();D=0x20016b84;B=0x20006890
P={'r1_native_charger_state_get':0x50618,'r1_battery_task_flags_set':0x77240,'r1_native_charger_initialize':0x5079c,'r1_battery_charged_state_refresh':0x3dd0c,'osKernelGetTickCount':0x7d28c,'r1_battery_charging_progress_reset':0x4fe5c,'r1_battery_five_sample_filter_and_conversion':0x91184,'r1_batcfg_word1_signed_get':0x7bb7c,'__aeabi_memclr':0x277aa,'r1_battery_voltage_average':0x3dda0,'r1_battery_stuck_charge_recovery':0x3db70,'r1_battery_discharge_curve':0x50004,'r1_battery_charging_cadence':0x4fe70,'r1_battery_level_average':0x3d834,'r1_battery_diagnostic_cadence_step':0x3d9b8,'r1_battery_low_escalation':0x3d88c,'r1_proto_report_battery_status':0x8345c,'r1_shared_power_client_release':0x50758,'r1_glasses_tag_frame_send':0x913fc}
def main():
 real_control=True;real_statistics=True;providers=dict(P);provider_reports={};executed={'native':{},'source':{}};control_executed={'native':{},'source':{}}
 if real_statistics:
  for name in ('r1_battery_charged_state_refresh','r1_battery_voltage_average','r1_battery_level_average'):del providers[name]
  providers['r1_shared_power_client_acquire']=0x50778
 if real_control:
  for name in ('r1_battery_charging_progress_reset','r1_battery_task_flags_set','r1_shared_power_client_release','r1_shared_power_client_acquire'):del providers[name]
  providers.update(osThreadFlagsSet=0x7d6f4,r1_yhm_register_write_native=0x35760)
 del providers['r1_battery_five_sample_filter_and_conversion']
 providers.update(r1_stock_dispatch_08=0x85d1a,r1_stock_dispatch_0c=0x85cba,r1_stock_dispatch_10=0x85d2c,nrf_delay_ms=0x78550,osDelay=0x7d154)
 del providers['r1_battery_discharge_curve']
 del providers['r1_batcfg_word1_signed_get']
 providers.update(r1_cfg_port_enter=0x1100e00,r1_cfg_port_leave=0x1100e10)
 configuration_counts={'native':{},'source':{}}
 discharge_counts={'native':0,'source':0}
 del providers['r1_battery_charging_cadence']
 providers['osKernelGetTickFreq']=0x7d2a4
 cadence_counts={'native':0,'source':0}
 del providers['r1_battery_stuck_charge_recovery']
 providers.update(r1_battery_charging_initial_curve=0x4ff3c,r1_structured_log_mode_get=0x914ec,r1_structured_log_format=0x91638,nrf_log_frontend_std_4=0x799f8)
 recovery_counts={'native':0,'source':0};recovery_triggers={'native':0,'source':0}
 del providers['r1_battery_charging_initial_curve']
 del providers['r1_battery_diagnostic_cadence_step']
 providers['nrf_log_frontend_std_1']=0x799c8
 diagnostic_counts={'native':0,'source':0}
 del providers['r1_battery_low_escalation']
 providers.update(nrf_log_frontend_std_2=0x799d6,r1_battery_voltage_get=0x91290,time_backend_timestamp_thunk=0x8ada4,r1_kv_dev_info_fields_set=0x73710,r1_event_publish=0x8d8fc)
 low_counts={'native':0,'source':0};low_providers={side:{'record':0,'event':0} for side in ('native','source')};record_high={side:[] for side in ('native','source')}
 del providers['r1_kv_dev_info_fields_set']
 device_field_counts={side:{'setter':0,'read':0,'write':0} for side in ('native','source')}
 del providers['r1_battery_voltage_get']
 providers['r1_advertising_configuration_byte_get']=0x7ba24
 voltage_counts={'native':0,'source':0};service_prefix_nops={'native':0,'source':0}
 del providers['r1_glasses_tag_frame_send']
 providers.update(r1_glasses_connection_handle_get=0x4cb34,r1_ble_tx_queue_dispatch_type0=0x34064)
 frame_counts={'native':0,'source':0};frame_providers={side:{'reads':0,'dispatches':0,'skipped':0} for side in ('native','source')}
 del providers['r1_glasses_connection_handle_get'];del providers['r1_ble_tx_queue_dispatch_type0']
 providers.update(pvPortMalloc=0x855a0,vPortFree=0x95d48,osMessageQueueGetCount=0x7d390,osMessageQueueGetCapacity=0x7d388,osMessageQueuePut=0x7d40c,nrf_log_frontend_std_0=0x799c0,nrf_log_frontend_std_3=0x799e6)
 tx_counts={side:{'dispatch':0,'malloc':0,'put':0,'accepted':0,'free':0,'allocation_failed':0,'queue_missing':0,'connection_rejected':0} for side in ('native','source')}
 del providers['r1_proto_report_battery_status']
 providers['r1_phone_cmd_send_op1']=0x83896
 protocol_counts={'native':0,'source':0};protocol_sends={'native':0,'source':0}
 del providers['r1_phone_cmd_send_op1']
 providers['r1_protocol_send_response']=0x828b4
 operation_counts={side:{'operation':0,'header':0,'phone_getter':0,'lower':0,'lower_zero':0,'lower_nonzero':0} for side in ('native','source')}
 del providers['r1_protocol_send_response']
 providers.update(r1_authenticated_phone_connection_gate=0x4cbb0,r1_peer_channel_b_valid=0x4cb40,r1_model_encode=0x82f9c,r1_protocol_send_hook_call=0x827f8)
 response_counts={side:{'entry':0,'gate_a':0,'gate_b':0,'malloc':0,'allocated':0,'encode':0,'send':0,'free':0} for side in ('native','source')};response_statuses={'native':{},'source':{}}
 del providers['r1_model_encode']
 encoder_counts={side:{'entry':0,'memmove':0,'crc':0} for side in ('native','source')}
 del providers['r1_protocol_send_hook_call'];providers['r1_protocol_send_callback_fixture']=0x1100e20
 send_hook_counts={'native':0,'source':0}
 vp=OUT/'send-hook-integration-verification.json';vp.unlink(missing_ok=True);rp=OUT/'report.json';r=json.loads(rp.read_text());obj=OUT/'native_battery_runtime.o';assert sha(obj)==r['units'][0]['object_sha256']
 for p,h in r['inputs'].items():assert sha(ROOT/p)==h,p
 objects=[obj]
 for module,filename in [('native-protocol-send-hook','native_protocol_send_hook.o'),('native-protocol-encoder','native_protocol_encoder.o'),('runtime-memmove','memmove.o'),('native-protocol-response','native_protocol_response.o'),('native-phone-operation','native_phone_operation.o'),('native-protocol-response-header','native_protocol_response_header.o'),('native-battery-protocol','native_battery_protocol.o'),('native-tx','native_tx.o'),('connection-handle','connection_handle.o'),('native-battery-frame','native_battery_frame.o'),('native-battery-voltage','native_battery_voltage.o'),('native-kv-device-fields','native_kv_device_fields.o'),('native-battery-low','native_battery_low.o'),('native-battery-diagnostic','native_battery_diagnostic.o'),('native-battery-initial-curve','native_battery_initial_curve.o'),('native-battery-recovery','native_battery_recovery.o'),('native-battery-cadence','native_battery_cadence.o'),('native-battery-configuration','native_battery_configuration.o'),('native-kv-class','native_kv_class.o')]:
  path=BASE/module/'report.json';qr=json.loads(path.read_text());qo=path.parent/filename;assert sha(qo)==qr['units'][0]['object_sha256'];objects.append(qo);provider_reports[module+'/report.json']=sha(path)
  for source,digest in qr['inputs'].items():assert sha(ROOT/source)==digest,source
 checksum_report=BASE/'report.json';cr=json.loads(checksum_report.read_text());cu=next(u for u in cr['units'] if u['source']=='r1/source/stock_checksums.c');co=Path(cu['command'][-1]);assert sha(co)==cu['object_sha256'] and sha(ROOT/cu['source'])==cu['source_sha256'];objects.append(co);provider_reports['report.json']=sha(checksum_report)
 memory_report=BASE/'runtime/report.json';mr=json.loads(memory_report.read_text());mu=next(u for u in mr['units'] if u['source'].endswith('/memcpy.c'));mo=memory_report.parent/'memcpy.o';assert sha(mo)==mu['object_sha256'] and sha(ROOT/mu['source'])==mu['source_sha256'];objects.append(mo);provider_reports['runtime/report.json']=sha(memory_report)

 drp=BASE/'native-battery-discharge/report.json';dr=json.loads(drp.read_text());do=drp.parent/'native_battery_discharge.o';assert sha(do)==dr['units'][0]['object_sha256'];objects.append(do);provider_reports['native-battery-discharge/report.json']=sha(drp)
 for path,h in dr['inputs'].items():assert sha(ROOT/path)==h,path
 filter_report=BASE/'native-battery-filter/report.json';fr=json.loads(filter_report.read_text());fo=filter_report.parent/'native_battery_filter.o';assert sha(fo)==fr['units'][0]['object_sha256'];objects.append(fo);provider_reports['native-battery-filter/report.json']=sha(filter_report)
 for path,h in fr['inputs'].items():assert sha(ROOT/path)==h,path
 filter_counts={'native':0,'source':0}
 if real_statistics:
  stats_report=BASE/'native-battery-statistics/report.json';stats=json.loads(stats_report.read_text());stats_object=stats_report.parent/'native_battery_statistics.o';assert sha(stats_object)==stats['units'][0]['object_sha256'];objects.append(stats_object);provider_reports['native-battery-statistics/report.json']=sha(stats_report)
  for path,h in stats['inputs'].items():assert sha(ROOT/path)==h,path
 if real_control:
  control_report=BASE/'native-battery-control/report.json';control=json.loads(control_report.read_text());control_object=control_report.parent/'native_battery_control.o';assert sha(control_object)==control['units'][0]['object_sha256'];objects.append(control_object);provider_reports['native-battery-control/report.json']=sha(control_report)
  for path,h in control['inputs'].items():assert sha(ROOT/path)==h,path
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';socket='/var/folders/mh/nz9vzlpn7kzff18f77pztg880000gn/T/ghidra-mcp-kalani/ghidra-11353.sock';raw=subprocess.check_output(['curl','-fsS','--max-time','20','--unix-socket',socket,'http://localhost/read_memory?program=stock-r1-native-analysis.elf&address=0x31fd0&length=406']);assert bytes(json.loads(raw)['data'])==app.read_bytes()[0x31fd0-0x27000:0x32166-0x27000];(OUT/'ghidra-memory.json').write_bytes(raw)
 consumer_raw=subprocess.check_output(['curl','-fsS','--max-time','20','--unix-socket',socket,'http://localhost/read_memory?program=stock-r1-native-analysis.elf&address=0x73710&length=64']);assert bytes(json.loads(consumer_raw)['data'])==app.read_bytes()[0x73710-0x27000:0x73710-0x27000+64];consumer_file=OUT/'low-kv-consumer-ghidra.json';consumer_file.write_bytes(consumer_raw)
 tx_evidence={}
 for a,z in [(0x34064,12),(0x3e274,536)]:
  file=OUT/f'rea-frame-tx-{a:x}.json';q=json.loads(file.read_text());assert q['subject']['digest']['sha256']=='92c47a5cca2d71f9020e17693a0268c192677f00e3734c47e28f04d1f1b081e8';tx_evidence[file.name]=sha(file)
  if a==0x34064:assert q['normalized_result']['entrypoint']=='0x34064' and q['normalized_result']['body']['total_bytes']==12
  else:assert q['normalized_result']['entrypoint']=='0x34070' and {'start':'0x3e274','end':'0x3e48b'} in q['normalized_result']['body']['ranges']
  raw=subprocess.check_output(['curl','-fsS','--max-time','20','--unix-socket',socket,f'http://localhost/read_memory?program=stock-r1-native-analysis.elf&address=0x{a:x}&length={z}']);assert bytes(json.loads(raw)['data'])==app.read_bytes()[a-0x27000:a-0x27000+z];file=OUT/f'ghidra-frame-tx-{a:x}.json';file.write_bytes(raw);tx_evidence[file.name]=sha(file)
 rea=json.loads((OUT/'rea-pseudocode.json').read_text());assert rea['subject']['digest']['sha256']=='92c47a5cca2d71f9020e17693a0268c192677f00e3734c47e28f04d1f1b081e8';rng=random.Random(0x31fd0);cases=[];rounding_cases=0
 def fixture(**changes):
  f=dict(state=1,charged=1,flags=(0,0),persist=False,filter=True,mutation=False,average=50,sample=3600,offset=0,tick=0,ring=7,level_ring=7,charge=50,previous=50,voltage=3800,rounding=0)
  f.update(changes);return f
 for state,charged,flags,persist,filtered,mutation,average in itertools.product((0,1,2,0xffffffff),(0,1),((0,0),(1,0),(0,1),(255,255)),(False,True),(False,True),(False,True),(0,1,50,94,95,255)):
  cases.append(fixture(state=state,charged=charged,flags=flags,persist=persist,filter=filtered,mutation=mutation,average=average,sample=rng.choice((0,32767,32768,65535,3600)),offset=rng.choice((0,299,300,(-299)&0xffffffff,(-300)&0xffffffff)),tick=rng.choice((0,1,0xffffffff)),charge=rng.choice((0,1,50,94,95,255)),previous=rng.choice((0,1,50,255))))
 for sample,offset,charged,rounding in itertools.product((0,1,32767,32768,65535,0xffff8000),((-300)&0xffffffff,(-299)&0xffffffff,0,299,300,0x7fffffff,0xffffffff),(0,1),range(4)):
  cases.append(fixture(sample=sample,offset=offset,charged=charged,rounding=rounding));rounding_cases+=1
 for _ in range(1024):cases.append(fixture(state=rng.randrange(3),charged=rng.getrandbits(1),sample=rng.getrandbits(32),offset=rng.getrandbits(32),charge=rng.randrange(256),previous=rng.randrange(256),ring=rng.randrange(16),level_ring=rng.randrange(8),average=rng.choice((0,1,94,95,255,256,0xffffffff)),persist=bool(rng.getrandbits(1)),filter=bool(rng.getrandbits(1)),mutation=bool(rng.getrandbits(1)),flags=(rng.randrange(2),rng.randrange(2)),rounding=rng.randrange(4)))
 with tempfile.TemporaryDirectory() as directory:
  d=Path(directory);ld=d/'layout.ld';elf=d/'test.elf';binary=d/'text.bin';bindings={n:0x1100001+i*16 for i,n in enumerate(providers)};ld.write_text('SECTIONS { .protocol_send_hook 0x20006c20 : { *(.r1.protocol.send_hook) } .protocol_sequence 0x20006b88 : { *(.r1.protocol.sequence) } .protocol_versions 0x20006ba0 : { *(.r1.protocol.version_map) } .response_alloc_ring 0x82a28 : { *(.r1.protocol_response.alloc_ring) } .response_alloc_sdk 0x82a54 : { *(.r1.protocol_response.alloc_sdk) } .response_tx_ring 0x82a7c : { *(.r1.protocol_response.tx_ring) } .response_tx_sdk 0x82ab8 : { *(.r1.protocol_response.tx_sdk) } .response_send_ring 0x82aec : { *(.r1.protocol_response.send_ring) } .response_send_sdk 0x82b24 : { *(.r1.protocol_response.send_sdk) } .protocol_ring 0xc0234 : { *(.r1.battery_protocol.ring) } .protocol_sdk 0x834d4 : { *(.r1.battery_protocol.sdk) } .tx_channel1 0x200065bc : { *(.r1.tx.channel1) } .tx_shared 0x200065e0 : { *(.r1.tx.shared) } .connection6 0x200064b8 : { *(.r1.connection.field6) } .connection8 0x200064ba : { *(.r1.connection.field8) } .connection10 0x200064bc : { *(.r1.connection.field10) } .low_ring 0x3d940 : { *(.r1.battery_low.ring) } .low_sdk 0x3d980 : { *(.r1.battery_low.sdk) } .diag_period_ring 0x3dad0 : { *(.r1.battery_diagnostic.period_ring) } .diag_period_sdk 0x3db04 : { *(.r1.battery_diagnostic.period_sdk) } .diag_offset_ring 0x3db30 : { *(.r1.battery_diagnostic.offset_ring) } .diag_offset_sdk 0x3db50 : { *(.r1.battery_diagnostic.offset_sdk) } .diag_charge_ring 0xc00bc : { *(.r1.battery_diagnostic.charge_ring) } .diag_charge_sdk 0xc0108 : { *(.r1.battery_diagnostic.charge_sdk) } .recovery_ring 0x3dc88 : { *(.r1.battery_recovery.ring) } .recovery_sdk 0x3dcd0 : { *(.r1.battery_recovery.sdk) } .initial_tables 0x99ef6 : { *(.r1.battery.initial_charge_tables) } .tables 0x99d16 : { *(.r1.battery.discharge_tables) } .text 0x1000000 : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }');subprocess.run(['arm-none-eabi-ld','-T',str(ld),'--defsym=r1_thread_create_e=0x4509d','--defsym=r1_task_stop_65bc=0x45085','--defsym=r1_thread_create_b=0x44ef1','--defsym=r1_task_stop_65e0=0x44ed9','--defsym=r1_device_info_record_kv_handle=0x20007de8','--defsym=r1_low_battery_thread_handle=0x20006548','--defsym=r1_batcfg_record_kv_handle=0x20007df8','--defsym=r1_health_record_kv_handle=0x20007df4','--defsym=r1_kv_port=0x20006974','--defsym=r1_battery_device_context='+hex(D),'--defsym=r1_battery_runtime_context='+hex(B),*(['--defsym=r1_battery_thread_handle=0x20006638','--defsym=r1_shared_power_clients=0x20006878'] if real_control else []),*['--defsym='+n+'='+hex(a) for n,a in bindings.items()],*map(str,objects),'-o',str(elf)],check=True,capture_output=True);subprocess.run(['arm-none-eabi-objcopy','-j','.text','-O','binary',str(elf),str(binary)],check=True);syms={v[2]:int(v[0],16) for l in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=l.split())==3};image=binary.read_bytes();assert len(image)<0x10000;machines=[];states={};kinds={a:n for n,a in providers.items()};kinds.update({a&~1:n for n,a in bindings.items()})
  for _ in (0,1):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,app.read_bytes());u.mem_map(0x1000000,0x10000);u.mem_write(0x1000000,image);u.mem_map(0x1100000,0x1000);u.mem_map(0x20000000,0x40000);u.mem_map(0xe000e000,4096);u.reg_write(UC_ARM_REG_C1_C0_2,0xf00000);u.reg_write(UC_ARM_REG_FPEXC,0x40000000);machines.append(u)
  tablefile=d/'tables.bin';subprocess.run(['arm-none-eabi-objcopy','-j','.tables','-O','binary',str(elf),str(tablefile)],check=True);tabledata=tablefile.read_bytes();tablehash=sha(tablefile);assert tabledata==app.read_bytes()[0x99d16-0x27000:0x99d16-0x27000+480];machines[1].mem_write(0x99d16,tabledata)
  initial_tablefile=d/'initial-tables.bin';subprocess.run(['arm-none-eabi-objcopy','-j','.initial_tables','-O','binary',str(elf),str(initial_tablefile)],check=True);initial_tabledata=initial_tablefile.read_bytes();initial_tablehash=sha(initial_tablefile);assert initial_tabledata==app.read_bytes()[0x99ef6-0x27000:0x99ef6-0x27000+480];machines[1].mem_write(0x99ef6,initial_tabledata)
  diagnostic_sections={}
  for n,a,z in [('period_ring',0x3dad0,49),('period_sdk',0x3db04,43),('offset_ring',0x3db30,30),('offset_sdk',0x3db50,24),('charge_ring',0xc00bc,73),('charge_sdk',0xc0108,67)]:
   path=d/('diag-'+n+'.bin');subprocess.run(['arm-none-eabi-objcopy','-j','.diag_'+n,'-O','binary',str(elf),str(path)],check=True);contents=path.read_bytes();assert contents==app.read_bytes()[a-0x27000:a-0x27000+z];machines[1].mem_write(a,contents);diagnostic_sections[n]={'address':a,'bytes':z,'sha256':sha(path)}
  low_sections={}
  for n,a,z in [('ring',0x3d940,55),('sdk',0x3d980,49)]:
   path=d/('low-'+n+'.bin');subprocess.run(['arm-none-eabi-objcopy','-j','.low_'+n,'-O','binary',str(elf),str(path)],check=True);contents=path.read_bytes();assert contents==app.read_bytes()[a-0x27000:a-0x27000+z];machines[1].mem_write(a,contents);low_sections[n]={'address':a,'bytes':z,'sha256':sha(path)}
  tx_sections={}
  cold=Uc(UC_ARCH_ARM,UC_MODE_THUMB);cold.mem_map(0x20000,0xc0000);cold.mem_write(0x27000,app.read_bytes());cold.mem_map(0x20000000,0x40000);cold.mem_write(0x20000000,b'\xa5'*0x40000);cold.reg_write(UC_ARM_REG_SP,0x2003f000);cold.emu_start(0x283a1,0x27208,count=2000000);assert cold.reg_read(UC_ARM_REG_PC)==0x27208
  for n,a,z in [('tx_channel1',0x200065bc,16),('tx_shared',0x200065e0,16),('connection6',0x200064b8,2),('connection8',0x200064ba,2),('connection10',0x200064bc,2)]:
   path=d/(n+'.bin');subprocess.run(['arm-none-eabi-objcopy','-j','.'+n,'-O','binary',str(elf),str(path)],check=True);contents=path.read_bytes();assert len(contents)==z and contents==bytes(cold.mem_read(a,z));tx_sections[n]={'address':a,'bytes':z,'sha256':sha(path),'data':contents}
  protocol_sections={}
  for n,a,z in [('ring',0xc0234,66),('sdk',0x834d4,60)]:
   path=d/('protocol-'+n+'.bin');subprocess.run(['arm-none-eabi-objcopy','-j','.protocol_'+n,'-O','binary',str(elf),str(path)],check=True);contents=path.read_bytes();assert contents==app.read_bytes()[a-0x27000:a-0x27000+z];machines[1].mem_write(a,contents);protocol_sections[n]={'address':a,'bytes':z,'sha256':sha(path)}
  response_sections={}
  for n,a,z in [('alloc_ring', 535080, 43), ('alloc_sdk', 535124, 37), ('tx_ring', 535164, 58), ('tx_sdk', 535224, 52), ('send_ring', 535276, 53), ('send_sdk', 535332, 47)]:
   path=d/('response-'+n+'.bin');subprocess.run(['arm-none-eabi-objcopy','-j','.response_'+n,'-O','binary',str(elf),str(path)],check=True);contents=path.read_bytes();assert contents==app.read_bytes()[a-0x27000:a-0x27000+z];machines[1].mem_write(a,contents);response_sections[n]={'address':a,'bytes':z,'sha256':sha(path)}
  encoder_sections={}
  for n,a,z in [('protocol_send_hook',0x20006c20,4),('protocol_sequence',0x20006b88,2),('protocol_versions',0x20006ba0,4)]:
   path=d/(n+'.bin');subprocess.run(['arm-none-eabi-objcopy','-j','.'+n,'-O','binary',str(elf),str(path)],check=True);contents=path.read_bytes();assert len(contents)==z and contents==bytes(cold.mem_read(a,z));encoder_sections[n]={'address':a,'bytes':z,'sha256':sha(path),'data':contents}
  actual_entries={}
  if real_statistics:
   for name,native in [('r1_battery_charged_state_refresh',0x3dd0c),('r1_battery_voltage_average',0x3dda0),('r1_battery_level_average',0x3d834)]:
    actual_entries[native]=name;actual_entries[syms[name]&~1]=name
  control_entries={}
  if real_control:
   for name,native in [('r1_battery_charging_progress_reset',0x4fe5c),('r1_battery_task_flags_set',0x77240),('r1_shared_power_client_acquire',0x50778),('r1_shared_power_client_release',0x50758)]:
    control_entries[native]=name;control_entries[syms[name]&~1]=name
  cfg_entries={0x7bb44:'r1_batcfg_byte0_get',0x7bb7c:'r1_batcfg_word1_signed_get',0x73930:'r1_kv_class_read',syms['r1_batcfg_byte0_get']:'r1_batcfg_byte0_get',syms['r1_batcfg_word1_signed_get']:'r1_batcfg_word1_signed_get',syms['r1_kv_class_read']:'r1_kv_class_read'}
  def hook(u,a,size,_):
   side='native' if u is machines[0] else 'source';f=states[id(u)]
   if a in (0x827f8,syms['r1_protocol_send_hook_call']):send_hook_counts[side]+=1
   if f.get('in_encoder') and a==f['encoder_return']:f['in_encoder']=False
   if a in (0x82f9c,syms['r1_model_encode']):
    f['in_encoder']=True;f['encoder_return']=u.reg_read(UC_ARM_REG_LR)&~1
    r=[u.reg_read(reg) for reg in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)];stack=struct.unpack('<5I',bytes(u.mem_read(u.reg_read(UC_ARM_REG_SP),20)));level,state=f['protocol_input'];assert r==[0x20025100,19,1,0] and stack[:3]==(1,2,0) and stack[4]==7 and bytes(u.mem_read(stack[3],8))==struct.pack('<II',(level&255)|((1 if state else 2)<<8),0);f['encoder_sequence']=struct.unpack('<H',bytes(u.mem_read(0x20006b88,2)))[0];encoder_counts[side]['entry']+=1;response_counts[side]['encode']+=1;f['trace'].append(('actual_encode',19,1,0,1,2,0,bytes(u.mem_read(stack[3],7)).hex(),7))
   if f.get('in_encoder') and a in (0x2775c,syms['memmove']):encoder_counts[side]['memmove']+=1
   if f.get('in_encoder') and a in (0x5d87c,syms['r1_stock_crc16_modbus']):encoder_counts[side]['crc']+=1

   side='native' if u is machines[0] else 'source';f=states[id(u)]
   if f.get('in_response') and a==f['response_return']:
    status=u.reg_read(UC_ARM_REG_R0);response_statuses[side][str(status)]=response_statuses[side].get(str(status),0)+1;operation_counts[side]['lower_zero' if status==0 else 'lower_nonzero']+=1;f['in_response']=False
   if a in (0x828b4,syms['r1_protocol_send_response']):
    response_counts[side]['entry']+=1;operation_counts[side]['lower']+=1;f['in_response']=True;f['response_return']=u.reg_read(UC_ARM_REG_LR)&~1

   side='native' if u is machines[0] else 'source'
   if a in (0x83896,syms['r1_phone_cmd_send_op1']):operation_counts[side]['operation']+=1;protocol_sends[side]+=1
   if a in (0x84c0c,syms['r1_protocol_response_send_0x100']):operation_counts[side]['header']+=1
   if a in (0x4cba4,syms['r1_phone_connection_handle_get']):operation_counts[side]['phone_getter']+=1

   if a in (0x8345c,syms['r1_proto_report_battery_status']):
    side='native' if u is machines[0] else 'source';protocol_counts[side]+=1;states[id(u)]['protocol_input']=(u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_R1))
   side='native' if u is machines[0] else 'source';f=states[id(u)]
   if a in (0x4cb34,syms['r1_glasses_connection_handle_get']):
    index=f['frame_reads'];assert index<3;value=f['frame_handles'][index];f['frame_reads']+=1;u.mem_write(0x200064bc,struct.pack('<H',value));frame_providers[side]['reads']+=1;f['trace'].append(('actual_connection',value))
    if index==0 and value==0xffff:frame_providers[side]['skipped']+=1
   if a in (0x34064,syms['r1_ble_tx_queue_dispatch_type0']):
    level,state=f['frame_input'];packet=bytes(u.mem_read(u.reg_read(UC_ARM_REG_R1),12));assert u.reg_read(UC_ARM_REG_R0)==f['frame_handles'][1] and u.reg_read(UC_ARM_REG_R2)==6 and packet==struct.pack('<III',0x008b0900,(level&255)|((state&255)<<8),0);frame_providers[side]['dispatches']+=1;f['tx_packet']=packet[:6];f['tx_id']=u.reg_read(UC_ARM_REG_R0)
   if a in (0x3e274,syms['dispatch']):
    tx_counts[side]['dispatch']+=1
    if not f['queue_present']:tx_counts[side]['queue_missing']+=1
    elif f['frame_handles'][2]==0xffff:tx_counts[side]['connection_rejected']+=1

   if a in (0x913fc,syms['r1_glasses_tag_frame_send']):
    side='native' if u is machines[0] else 'source';frame_counts[side]+=1;states[id(u)]['frame_input']=(u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_R1))
   if a in (0x91290,syms['r1_battery_voltage_get']):voltage_counts['native' if u is machines[0] else 'source']+=1
   if a in (0x31fcc,syms['r1_battery_runtime_service']):
    assert bytes(u.mem_read(a,4))==bytes.fromhex('aff30080');service_prefix_nops['native' if u is machines[0] else 'source']+=1
   side='native' if u is machines[0] else 'source'
   if a in (0x73710,syms['r1_kv_dev_info_fields_set']):
    f=states[id(u)];words=struct.unpack('<II',bytes(u.mem_read(u.reg_read(UC_ARM_REG_R0),8)));assert words[0]==0x12345678 and (words[1]&65535)==((struct.unpack('<H',bytes(u.mem_read(D+42,2)))[0]&0x3fff)<<2);record_high[side].append(words[1]>>16);device_field_counts[side]['setter']+=1;low_providers[side]['record']+=1;f['trace'].append(('actual_kv_fields',*words))
   if a in (0x73930,syms['r1_kv_class_read']) and u.reg_read(UC_ARM_REG_R0)==0x20001200:device_field_counts[side]['read']+=1
   if a in (0x73968,syms['r1_kv_class_write']) and u.reg_read(UC_ARM_REG_R0)==0x20001200:device_field_counts[side]['write']+=1

   if a in (0x3d88c,syms['r1_battery_low_escalation']):low_counts['native' if u is machines[0] else 'source']+=1
   if a in (0x3d9b8,syms['r1_battery_diagnostic_cadence_step']):diagnostic_counts['native' if u is machines[0] else 'source']+=1
   if a in (0x4ff3c,syms['r1_battery_charging_initial_curve']):recovery_triggers['native' if u is machines[0] else 'source']+=1
   if a in (0x3db70,syms['r1_battery_stuck_charge_recovery']):recovery_counts['native' if u is machines[0] else 'source']+=1
   if a in (0x4fe70,syms['r1_battery_charging_cadence']):cadence_counts['native' if u is machines[0] else 'source']+=1
   if a in cfg_entries:
    side='native' if u is machines[0] else 'source';name=cfg_entries[a];configuration_counts[side][name]=configuration_counts[side].get(name,0)+1

   if a in (0x50004,syms['r1_battery_discharge_curve']):discharge_counts['native' if u is machines[0] else 'source']+=1
   if a in (0x91184,syms['r1_battery_five_sample_filter_and_conversion']):filter_counts['native' if u is machines[0] else 'source']+=1
   if a in actual_entries:
    counts=executed['native' if u is machines[0] else 'source'];name=actual_entries[a];counts[name]=counts.get(name,0)+1
   if a in control_entries:
    counts=control_executed['native' if u is machines[0] else 'source'];name=control_entries[a];counts[name]=counts.get(name,0)+1
   if a not in kinds:return
   f=states[id(u)];n=kinds[a];r=[u.reg_read(x) for x in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)];event=(n,);value=0
   if n=='r1_authenticated_phone_connection_gate':value=f['response_auth'];response_counts[side]['gate_a']+=1
   elif n=='r1_peer_channel_b_valid':value=f['response_peer'];response_counts[side]['gate_b']+=1
   elif n=='r1_protocol_send_callback_fixture':
    assert r[3]==bindings['r1_protocol_send_callback_fixture']
    level,state=f['protocol_input'];expected=bytearray(bytes.fromhex('640164000002000113000000')+bytes([(level&255),(1 if state else 2),0,0,0,0,0]));struct.pack_into('<H',expected,3,f['encoder_sequence']);crc=0xffff
    for byte in expected:
     crc^=byte
     for _ in range(8):crc=(crc>>1)^0xa001 if crc&1 else crc>>1
    struct.pack_into('<H',expected,10,crc);assert r[:3]==[f['phone_handle'],0x20025100,19] and bytes(u.mem_read(0x20025100,19))==bytes(expected);event+=tuple(r[:3]);value=f['response_send'];response_counts[side]['send']+=1
    if f['mutation']:u.mem_write(D+44,b'\xff')
   elif n=='pvPortMalloc' and f.get('in_response'):
    assert r[0]==19;event+=(r[0],);response_counts[side]['malloc']+=1;value=0x20025100 if f['response_malloc'] else 0;response_counts[side]['allocated']+=int(value!=0)
   elif n=='vPortFree' and r[0]==0x20025100:assert f.get('in_response');event+=(r[0],);response_counts[side]['free']+=1
   elif n=='pvPortMalloc':
    assert r[0]==20;event+=(r[0],);tx_counts[side]['malloc']+=1;value=0x20025000 if f['tx_malloc'] else 0
    if not value:tx_counts[side]['allocation_failed']+=1
   elif n=='vPortFree':assert r[0]==0x20025000;event+=(r[0],);tx_counts[side]['free']+=1
   elif n=='osMessageQueueGetCount':
    assert r[0]==struct.unpack('<I',bytes(u.mem_read(0x200065ec,4)))[0];event+=(r[0],);value=f['tx_count']
    if f['mutation']:u.mem_write(0x200065ec,struct.pack('<I',0x20008100))
   elif n=='osMessageQueueGetCapacity':assert r[0]==struct.unpack('<I',bytes(u.mem_read(0x200065ec,4)))[0];event+=(r[0],);value=f['tx_capacity']
   elif n=='osMessageQueuePut':
    pointer=struct.unpack('<I',bytes(u.mem_read(r[1],4)))[0];assert pointer==0x20025000 and r[0]==struct.unpack('<I',bytes(u.mem_read(0x200065ec,4)))[0] and r[2:]==[0,100];header=struct.unpack('<III',bytes(u.mem_read(pointer,12)));payload=bytes(u.mem_read(pointer+12,6));assert header==(f['tx_id'],0,6) and payload==f['tx_packet'];event+=(r[0],header,payload.hex(),0,100);value=f['tx_status'];tx_counts[side]['put']+=1;tx_counts[side]['accepted']+=int(value==0)
    if f['mutation']:u.mem_write(0x200065e8,struct.pack('<I',0x20015200))
   elif n=='r1_advertising_configuration_byte_get':value=0
   elif n=='time_backend_timestamp_thunk':value=0x12345678
   elif n=='r1_event_publish':
    assert r[:3]==[0x100c,0,0];event+=tuple(r[:3]);value=0x80000007;low_providers['native' if u is machines[0] else 'source']['event']+=1
   elif n=='r1_structured_log_mode_get':value=0
   elif n in ('r1_structured_log_format','nrf_log_frontend_std_4','nrf_log_frontend_std_1','nrf_log_frontend_std_2','nrf_log_frontend_std_0','nrf_log_frontend_std_3'):raise AssertionError('unexpected enabled recovery log')
   elif n in ('r1_cfg_port_enter','r1_cfg_port_leave'):pass
   elif n in ('r1_stock_dispatch_08','r1_stock_dispatch_0c'):
    handle=struct.unpack('<I',bytes(u.mem_read(B+16,4)))[0];assert r[0]==handle;event+=(handle,)
   elif n=='r1_stock_dispatch_10':
    handle=struct.unpack('<I',bytes(u.mem_read(B+16,4)))[0];assert r[0]==handle and r[1]==0 and r[3]==1
    before=struct.unpack('<I',bytes(u.mem_read(r[2],4)))[0];assert before&65535==0
    sample=(f['sample']+f['adc_reads']*137)&65535;u.mem_write(r[2],struct.pack('<H',sample));event+=(handle,sample);f['adc_reads']+=1
    if f['mutation']:u.mem_write(B+16,struct.pack('<I',handle+16));u.mem_write(B+1,bytes([f['adc_reads']%2]))
   elif n in ('nrf_delay_ms','osDelay'):
    assert r[0]==2 and n==('osDelay' if bytes(u.mem_read(B+1,1))[0] else 'nrf_delay_ms');event+=(2,)
   elif n=='osThreadFlagsSet':event+=tuple(r[:2]);value=0x80000004
   elif n=='r1_yhm_register_write_native':
    assert r[:2]==[2,1];command=bytes(u.mem_read(r[2],1));assert command in (b'\xa8',b'\x28');event+=(r[0],r[1],command.hex());value=0xffffffff
    if f['mutation']:u.mem_write(0x20006878,struct.pack('<I',0x80))
   elif n=='r1_native_charger_state_get':value=f['state']
   elif n=='r1_battery_task_flags_set':event+=(r[0],)
   elif n=='r1_shared_power_client_acquire':event+=(r[0],);assert r[0]==0
   elif n=='r1_battery_charged_state_refresh':
    extra=struct.unpack('<I',bytes(u.mem_read(u.reg_read(UC_ARM_REG_SP),4)))[0];event+=(*r,extra);assert tuple(r[1:])+ (extra,)==(B+36,B+12,B+40,B+14);value=f['charged']
   elif n=='osKernelGetTickCount':
    value=(f['tick']+f['tick_calls']*f['tick_step'])&0xffffffff;f['tick_calls']+=1
   elif n=='osKernelGetTickFreq':value=f['frequency']
   elif n=='r1_battery_five_sample_filter_and_conversion':value=f['sample']
   elif n=='r1_batcfg_word1_signed_get':value=f['offset']
   elif n=='__aeabi_memclr':
    event+=tuple(r[:2]);assert r[0]==D+2 and r[1]==16;u.mem_write(D+2,bytes(16))
    if f['mutation']:u.mem_write(D,b'\xa5')
   elif n=='r1_battery_voltage_average':
    if f['mutation']:u.mem_write(D+42,struct.pack('<H',0x1234))
   elif n=='r1_battery_level_average':value=f['average']
   elif n=='r1_shared_power_client_release':
    event+=(r[0],)
    if f['mutation']:u.mem_write(D+44,b'\x5a')
   f['trace'].append(event);u.reg_write(UC_ARM_REG_R0,value);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  for u in machines:u.hook_add(UC_HOOK_CODE,hook)
  saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
  for index,f in enumerate(cases):
   results=[]
   for candidate,u in enumerate(machines):
    u.mem_write(0x20007df8,struct.pack('<I',0x20001000));u.mem_write(0x20001000,bytes(32));u.mem_write(0x20001014,struct.pack('<H',4));u.mem_write(0x20001018,struct.pack('<I',((f['offset']&65535)<<16)|(f['sample']%5)));u.mem_write(0x20006974,struct.pack('<I',0x20000800));u.mem_write(0x20000800,bytes(28)+struct.pack('<II',bindings['r1_cfg_port_enter'],bindings['r1_cfg_port_leave']))
    states[id(u)]={**f,'trace':[],'adc_reads':0,'in_response':False,'response_auth':(0,1,0xffffffff)[index%3],'response_peer':(0,1)[(index//3)%2],'response_malloc':index%11!=0,'response_encode':(0,0,7,0xffffffff)[(index//5)%4],'response_send':(0,1,0xffffffff)[(index//7)%3],'phone_handle':0xffff if index%4==0 else 1,'phone_raw':(0,1,0x80000000,0xffffffff)[(index//4)%4],'frame_reads':0,'frame_handles':(0xffff if index%3==0 else 1,0xffff if index%3==1 else 2,0xffff if index%4==0 else 2),'queue_present':index%5!=0,'tx_malloc':index%7!=0,'tx_count':(0,14,15,0xffffffff)[index%4],'tx_capacity':(16,16,16,0xffffffff)[index%4],'tx_status':(0,0xfffffffc,0xffffffff,1)[(index//4)%4],'tick_calls':0,'tick_step':(0,1000,180000,0xffffffff)[index%4],'frequency':(0,1,1000,0xffffffff)[index%4]};u.mem_write(D-8,bytes([0x93])*84);u.mem_write(B-8,bytes([0xa5])*112);u.mem_write(D,bytes([(f['ring']<<4)|13,f['level_ring']]));u.mem_write(D+42,struct.pack('<H',f['voltage']));u.mem_write(D+44,bytes([f['charge'],*f['flags']]));u.mem_write(D+48,bytes([99 if f['persist'] else 0]));u.mem_write(D+49,struct.pack('<H',0x4567 if f['persist'] else 0));u.mem_write(B,bytes([f['previous'],int(f['filter'])]));u.mem_write(B+12,struct.pack('<H',0x2345));u.mem_write(B+14,struct.pack('<H',0x3456));u.mem_write(B+36,struct.pack('<I',123 if f['persist'] else 0));u.mem_write(B+40,struct.pack('<I',0xaabbccdd));u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101);u.reg_write(UC_ARM_REG_FPSCR,f['rounding']<<22)
    u.mem_write(0x20007de8,struct.pack('<I',0x20001200));u.mem_write(0x20001200,b'\x3c'*80);u.mem_write(0x20001214,struct.pack('<H',52))
    u.mem_write(D+18,struct.pack('<8H',*([(3300,3350,3800)[index%3]]*8)));u.mem_write(D+47,bytes([index&255]));u.mem_write(0x20006548,struct.pack('<I',0x20015520))
    u.mem_write(B+5,bytes([index&255]));u.mem_write(B+3,bytes([f['charge'],0]));u.mem_write(B+10,struct.pack('<H',2400));u.mem_write(B+32,struct.pack('<I',0))
    for row in encoder_sections.values():u.mem_write(row['address'],row['data'])
    u.mem_write(0x20006c20,struct.pack('<I',bindings['r1_protocol_send_callback_fixture']))
    for row in tx_sections.values():u.mem_write(row['address'],row['data'])
    u.mem_write(0x200064ba,struct.pack('<H',0xffff if index%4==0 else 1))
    u.mem_write(0x200065e8,struct.pack('<II',0x20015100,0x20008000 if index%5 else 0));u.mem_write(0x20025000,b'\x96'*64);u.mem_write(0x20025100,b'\x69'*64)
    for t,thresholds in enumerate(((1,2,3,4),(10,20,30,40),(180,180,180,180),(0,0,0,0))):u.mem_write(B+44+t*12,struct.pack('<4H',*thresholds))
    if real_control:u.mem_write(0x20006638,struct.pack('<I',0x20014418));u.mem_write(0x20006878,struct.pack('<I',index&7))
    for i,reg in enumerate(saved):u.reg_write(reg,0x12345600+i)
    u.emu_start((syms['r1_battery_runtime_service']|1) if candidate else 0x31fcd,0x20000100,count=10000);assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and [u.reg_read(reg) for reg in saved]==[0x12345600+i for i in range(8)]
    results.append((u.reg_read(UC_ARM_REG_R0),states[id(u)]['trace'],bytes(u.mem_read(D-8,84)),bytes(u.mem_read(B-8,112)),u.reg_read(UC_ARM_REG_FPSCR),bytes(u.mem_read(0x20006878,4)) if real_control else None,bytes(u.mem_read(0x20001200,80)),bytes(u.mem_read(0x20007de8,4)),bytes(u.mem_read(0x200065bc,16)),bytes(u.mem_read(0x200065e0,16)),bytes(u.mem_read(0x200064b8,6)),bytes(u.mem_read(0x20025000,64)),bytes(u.mem_read(0x20025100,64)),bytes(u.mem_read(0x20006b88,2)),bytes(u.mem_read(0x20006ba0,4))))
   assert states[id(machines[0])]['adc_reads']==states[id(machines[1])]['adc_reads']==5
   assert results[0]==results[1],(index,f,[(i,a,b) for i,(a,b) in enumerate(zip(*results)) if a!=b])
 if real_statistics:assert executed['native']==executed['source'] and len(executed['source'])==3 and all(v==len(cases) for v in executed['source'].values()),executed
 if real_control:assert control_executed['native']==control_executed['source'] and len(control_executed['source'])==4 and all(v>0 for v in control_executed['source'].values()),control_executed
 assert filter_counts=={'native':len(cases),'source':len(cases)}
 assert discharge_counts['native']==discharge_counts['source'] and discharge_counts['source']>0
 assert configuration_counts['native']==configuration_counts['source'] and configuration_counts['source']['r1_batcfg_word1_signed_get']==2896
 assert cadence_counts=={'native':1113,'source':1113}
 assert recovery_counts=={'native':2896,'source':2896} and recovery_triggers['native']==recovery_triggers['source'] and recovery_triggers['source']>0
 assert diagnostic_counts=={'native':2896,'source':2896}
 assert record_high['native']==record_high['source']
 assert low_counts=={'native':2896,'source':2896} and low_providers['native']==low_providers['source'] and all(v>0 for v in low_providers['source'].values())
 assert device_field_counts=={side:{'setter':920,'read':920,'write':920} for side in ('native','source')}
 assert voltage_counts=={'native':920,'source':920} and service_prefix_nops=={'native':2896,'source':2896}
 assert frame_counts['native']==frame_counts['source'] and frame_counts['source']>0 and frame_providers['native']==frame_providers['source'] and all(v>0 for v in frame_providers['source'].values())
 assert tx_counts['native']==tx_counts['source'] and all(value>0 for value in tx_counts['source'].values()),tx_counts
 assert protocol_counts==protocol_sends and protocol_counts['native']==protocol_counts['source'] and protocol_counts['source']>0
 assert operation_counts['native']==operation_counts['source'] and all(v>0 for v in operation_counts['source'].values())
 assert response_counts['native']==response_counts['source'] and response_statuses['native']==response_statuses['source'] and all(v>0 for v in response_counts['source'].values())
 assert encoder_counts['native']==encoder_counts['source'] and encoder_counts['source']['entry']==encoder_counts['source']['memmove']==encoder_counts['source']['crc'] and encoder_counts['source']['entry']>0,encoder_counts
 vp.write_text(json.dumps(dict(executed_send_hook_counts=send_hook_counts,executed_encoder_counts=encoder_counts,source_owned_encoder_sections={n:{k:v for k,v in row.items() if k!='data'} for n,row in encoder_sections.items()},executed_response_counts=response_counts,response_status_counts=response_statuses,compiled_response_sections=response_sections,executed_operation_header_counts=operation_counts,executed_protocol_entry_counts=protocol_counts,protocol_dispatch_counts=protocol_sends,compiled_protocol_sections=protocol_sections,tx_evidence=tx_evidence,tx_cold_poison=165,executed_tx_producer_counts=tx_counts,source_owned_tx_sections={n:{k:v for k,v in row.items() if k!='data'} for n,row in tx_sections.items()},executed_frame_entry_counts=frame_counts,frame_provider_counts=frame_providers,executed_voltage_entry_counts=voltage_counts,service_prefix_nops=service_prefix_nops,native_service_entry='0x31fcc',service_ownership_span_bytes=412,executed_device_field_counts=device_field_counts,native_kv_consumer_evidence_sha256=sha(consumer_file),executed_low_entry_counts=low_counts,low_downstream_counts=low_providers,record_high_half_observations={side:{'count':len(values),'distinct':sorted(set(values)),'sha256':hashlib.sha256(b''.join(struct.pack('<H',v) for v in values)).hexdigest()} for side,values in record_high.items()},compiled_low_sections=low_sections,executed_diagnostic_entry_counts=diagnostic_counts,compiled_diagnostic_sections=diagnostic_sections,compiled_initial_charge_table_sha256=initial_tablehash,executed_initial_curve_entry_counts=recovery_triggers,executed_recovery_entry_counts=recovery_counts,recovery_initial_curve_calls=recovery_triggers,executed_cadence_entry_counts=cadence_counts,executed_configuration_entry_counts=configuration_counts,executed_discharge_entry_counts=discharge_counts,compiled_discharge_table_sha256=tablehash,executed_filter_entry_counts=filter_counts,comparisons=len(cases),real_statistics=real_statistics,real_control=real_control,executed_control_entry_counts=control_executed,executed_statistics_entry_counts=executed,provider_reports=provider_reports,explicit_numeric_rounding_cases=rounding_cases,report_sha256=sha(rp),object_sha256=sha(obj),driver_sha256=sha(Path(__file__)),application_sha256=sha(app),ghidra_memory_sha256=sha(OUT/'ghidra-memory.json'),rea_sha256=sha(OUT/'rea-pseudocode.json'),native_entry='0x31fd0',native_size=406,application_linked=False,instruction_identity=False,limitations=['Actual low escalation, diagnostic cadence and recovery with disabled logging, cadence, cached-class/musl copy, configuration, discharge policy, filter, refresh, averages and control execute; cadence threshold rows are fixture RAM with source ownership gated; matched four-byte cached records and port callbacks are fixtures, rejected-size composition remains gated; ADC registry/delay and Connection getters, type0 wrapper and shared TX producer/musl copy execute; allocator/queue/notification endpoints and live connection/queue/thread transitions are modeled; advertising-config (zero), response gates/allocator/send callback target, low event/time/thread and remaining hardware endpoints are fixtures; actual send-hook dispatcher/encoder/musl movement/recovered CRC and lower response sender/phone operation1/header/getter and battery protocol report execute with disabled logging; actual service prefix/updater/getter execute; recursive refresh composition remains gated; actual device-info setter and cached read/write/musl copy execute with matched52-byte records; rejected-size caller composition remains open; full eight-byte KV input records compared, including upper halfword; native consumer reads six bytes; other compiler/caller identity remains gated; initial-charge curve and compiled calibration data execute; opaque read-word high halves are not compared in this graph, and direct filter verification covers them','Raw device/runtime roots are address bindings, not source-owned initialization','All four FPSCR rounding modes and final FPSCR are compared; physical FPU/concurrency not proven','Packed native-width SRAM views preserve unaligned values; physical interrupt ordering/atomicity/concurrency remain gates','Charged-state refresh consumes five semantic arguments; no decompiler scratch sixth argument']),indent=2)+'\n');print('Battery runtime:',len(cases),'native/source comparisons;',rounding_cases,'explicit numeric/FPSCR cases; real statistics:',real_statistics)
if __name__=='__main__':main()
