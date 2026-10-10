from pathlib import Path
import struct,json,hashlib
root=Path(__file__).resolve().parent;repo=root.parents[3];images={x['id']:x for x in map(json.loads,(repo/'g2/build/pseudocode-first/20260930T190500Z/inventory/images.jsonl').open())}
rec=images['binh_a_stage2_xip'];data=(repo/rec['content_path']).read_bytes();assert hashlib.sha256(data).hexdigest()==rec['content_sha256'];base=0x10203004
def words(addr,count):return list(struct.unpack('<'+'I'*count,data[addr-base:addr-base+count*4]))
ptrs=words(0x1020b1bc,2);rows=[]
for p in ptrs:
 vals=words(p,5);rows.append({'record_runtime':p,'record_child_span':[p-base,p-base+20],'fields':dict(zip(['type','init','done','tick','buffer_init'],vals)),'bytes_sha256':hashlib.sha256(data[p-base:p-base+20]).hexdigest()})
out={'image_sha256':rec['content_sha256'],'conditional_base':base,'mode_list_runtime':0x1020b1bc,'mode_list_child_span':[0x1020b1bc-base,0x1020b1c4-base],'mode_list_words':ptrs,'mode_records':rows,'state_runtime':0x2002e6e4,'state_words':['s_lvp_loop','s_current_index'],'source_struct':'lvp/lvp_mode.h:LVP_MODE_INFO','qualification':'static table inference exact; runtime state may change and physical XIP/DRAM visibility remains conditional'}
(root/'mode-table.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
srec=images['binh_a_stage2_sram'];sd=(repo/srec['content_path']).read_bytes();assert hashlib.sha256(sd).hexdigest()==srec['content_sha256']
off=0x3938;initial_ptr=struct.unpack('<I',sd[off:off+4])[0];assert initial_ptr==0x20026d3c
values=struct.unpack('<8I',sd[off+4:off+36]);names=['app_name','AppInit','AppEventResponse','AppTaskLoop','AppSuspend','suspend_priv','AppResume','resume_priv'];app=dict(zip(names,values));strings={k:data[v-base:].split(b'\0',1)[0].decode() for k,v in app.items() if k in ['app_name','suspend_priv','resume_priv']}
(root/'app-table.json').write_text(json.dumps({'sram_sha256':srec['content_sha256'],'pointer_child_span':[off,off+4],'pointer_field_runtime_declared':0x20026d38,'pointer_value':initial_ptr,'app_record_child_span':[off+4,off+36],'app_record_runtime_declared':initial_ptr,'fields':app,'strings':strings,'source_struct':'lvp/app_core/lvp_app.h:LVP_APP','qualification':'Initialized-source coordinates from SDK stage2_sram_data linker region; actual DRAM/IRAM visibility and subsequent writes remain unverified. This static initializer does not establish all future callback targets.'},indent=2)+'\n')
