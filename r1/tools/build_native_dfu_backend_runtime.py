#!/usr/bin/env python3
"""Share the startup-owned SVCI state, preserving all compiled allocated bytes."""
import hashlib,json,struct,subprocess
from pathlib import Path
from build_source_candidates import undefined_symbols
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def allocated_sections(p):
 data=p.read_bytes();assert data[:6]==b'\x7fELF\x01\x01';off=struct.unpack_from('<I',data,32)[0];size,count,strings=struct.unpack_from('<HHH',data,46);headers=[struct.unpack_from('<10I',data,off+i*size) for i in range(count)];table=headers[strings];names=data[table[4]:table[4]+table[5]];result={}
 for h in headers:
  if h[2]&2:
   name=names[h[0]:].split(b'\0',1)[0].decode();payload=b'' if h[1]==8 else data[h[4]:h[4]+h[5]];result[name]=[h[1],h[2],h[5],h[8],hashlib.sha256(payload).hexdigest()]
 return result
def main():
 out=BASE/'native-dfu-backend-runtime';out.mkdir(exist_ok=True);objects=[];reports={};inputs={str(Path(__file__).relative_to(ROOT)):sha(Path(__file__))}
 for directory,name,key in [('native-dfu-backend','native_dfu_backend.o',None),('native-dfu-ble-runtime','native-dfu-ble-runtime.o','linked_sha256')]:
  rp=BASE/directory/'report.json';r=json.loads(rp.read_text());obj=rp.parent/name;assert sha(obj)==(r[key] if key else r['units'][0]['object_sha256']);objects.append(obj);reports[str(rp.relative_to(BASE))]=sha(rp)
  for p,h in r['inputs'].items():assert sha(ROOT/p)==h,p;inputs[p]=h
 exported=out/'parent-shared-svci.o';subprocess.run(['arm-none-eabi-objcopy','--globalize-symbol=nrf_dfu_set_adv_name_svci_async_def',str(objects[1]),str(exported)],check=True);before=allocated_sections(objects[1]);assert before==allocated_sections(exported)
 linked=out/'native-dfu-backend-runtime.o';subprocess.run(['arm-none-eabi-ld','-r','--defsym=ble_dfu_buttonless_on_sys_evt=r1_native_dfu_on_sys_evt',str(objects[0]),str(exported),'-o',str(linked)],check=True);u,d=undefined_symbols(linked);old=json.loads((objects[1].parent/'report.json').read_text())['undefined_symbols'];closed=sorted(set(old)-set(u));assert closed==['ble_dfu_buttonless_on_sys_evt','r1_dfu_bootloader_prepare_boundary','r1_dfu_control_point_write_boundary'] and not(set(u)-set(old)) and len(u)==25
 data=out/'shared-dfu-data-source.o';subprocess.run(['arm-none-eabi-ld','-r','--gc-sections','-u','r1_ble_dfu_context','-u','nrf_dfu_set_adv_name_svci_async_def',str(exported),'-o',str(data)],check=True);assert undefined_symbols(data)[0]==[]
 copy=out/'memory-source.o';subprocess.run(['arm-none-eabi-ld','-r','--gc-sections','-u','memcpy',str(exported),'-o',str(copy)],check=True);assert undefined_symbols(copy)[0]==[]
 graph=out/'dfu-backend-source.o';subprocess.run(['arm-none-eabi-ld','-r',str(objects[0]),str(data),str(copy),'-o',str(graph)],check=True)
 state=out/'shared-svci-source.o';subprocess.run(['arm-none-eabi-ld','-r','--gc-sections','-u','nrf_dfu_set_adv_name_svci_async_def',str(exported),'-o',str(state)],check=True)
 observer=BASE/'native-dfu-ble-runtime/dfu-ble-source.o';obr=json.loads((observer.parent/'report.json').read_text());assert sha(observer)==obr['graph_object_sha256']
 composed=out/'dfu-backend-observer-source.o';subprocess.run(['arm-none-eabi-ld','-r',str(objects[0]),str(state),str(copy),str(observer),'-o',str(composed)],check=True)
 r=dict(inputs=inputs,provider_reports=reports,objects={str(p.relative_to(BASE)):sha(p) for p in objects},linked_sha256=sha(linked),undefined_symbols=u,exported_parent_sha256=sha(exported),export_transform=['arm-none-eabi-objcopy','--globalize-symbol=nrf_dfu_set_adv_name_svci_async_def'],parent_allocated_sections=before,shared_data_object_sha256=sha(data),memory_object_sha256=sha(copy),graph_object_sha256=sha(graph),graph_undefined_symbols=undefined_symbols(graph)[0],state_object_sha256=sha(state),observer_object_sha256=sha(observer),composed_object_sha256=sha(composed),composed_undefined_symbols=undefined_symbols(composed)[0],closed_parent_imports=closed,newly_exposed_imports=[],existing_svci_state_reused=True,new_backend_pointer_bytes=4,new_adv_name_bytes=28,service_initialization_proven=False,physical_dfu_execution_proven=False,instruction_identity=False,whole_image_complete=False,hardware_write_executed=False)
 (out/'report.json').write_text(json.dumps(r,indent=2)+'\n');print('Native DFU backend runtime:',len(u),'imports;shared SDK SVCI state')
if __name__=='__main__':main()
