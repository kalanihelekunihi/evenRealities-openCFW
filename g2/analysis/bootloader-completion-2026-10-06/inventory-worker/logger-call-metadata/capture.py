from pathlib import Path
import importlib.util,sys,json,struct,hashlib
N=Path(__file__).resolve().parent;R=next(p for p in N.parents if (p/'AGENTS.md').exists());P=R/'g2/analysis/bootloader-completion-2026-10-06/inventory-worker/startup-initialize';c=json.loads((P/'runtime-delay-native-integrated/current-candidate.json').read_text());elf=R/c['directory']/'candidate.elf';rows=[]
for name,file in [('allocator','allocator/verify.py'),('dfu_task','dfu_task/verify.py'),('dfu_context','dfu_task/verify_context.py'),('control','platform_control/verify.py')]:
 path=R/'g2/components/bootloader'/file;s=importlib.util.spec_from_file_location('capture_'+name,path);module=importlib.util.module_from_spec(s);s.loader.exec_module(module);v=module.v;original=v.Machine.code
 def code(self,u,pc,size,user,original=original,name=name):
  if not self.source and pc==0x4176ce:
   def string(p):
    if not p:return None
    out=bytearray()
    for k in range(1024):
     b=u.mem_read(p+k,1)[0]
     if not b:return bytes(out).decode('utf-8',errors='backslashreplace')
     out.append(b)
    raise AssertionError('unterminated')
   r=self.args();sp=u.reg_read(v.a.UC_ARM_REG_SP);words=list(struct.unpack('<8I',u.mem_read(sp,32)));row=dict(family=name,return_address=u.reg_read(v.a.UC_ARM_REG_LR),level=r[0],tag=string(r[1]),file=string(r[2]),function=string(r[3]),line=words[0],format=string(words[1]),argument_words=words[2:],header_words=list(struct.unpack('<8I',u.mem_read(0x20026ef8,32))))
   if name=='dfu_task':row['application_vector']=list(struct.unpack('<2I',u.mem_read(0x438000,8)))
   if row not in rows:rows.append(row)
  return original(self,u,pc,size,user)
 v.Machine.code=code
 real_machine=module.Machine
 def original_only(*args,real_machine=real_machine,**kw):return real_machine(**kw)
 module.Machine=original_only
 sys.argv=[str(path),'--elf',str(elf),'--output',str(N/(name+'-original-replay.json'))]
 try:
  module.main()
  out=N/(name+'-original-replay.json');receipt=json.loads(out.read_text());receipt['status']='PASS_ORIGINAL_ONLY_REPLAY_FOR_METADATA_CAPTURE';receipt['execution_mode']='Both instances original only, no source comparison.';receipt.pop('source_sha256',None);receipt.pop('elf_sha256',None);receipt['limits']=['Original-only duplicate replay for metadata, synthetic children, no source comparison.'];out.write_text(json.dumps(receipt,indent=2)+'\n')
 except Exception as e:
  (N/(name+'-failure.txt')).write_text(repr(e)+'\n');print(name,'fixture-stop',repr(e),flush=True)
 (N/'captured-calls.json').write_text(json.dumps(dict(original_sha256=hashlib.sha256(v.BLOB.read_bytes()).hexdigest(),source_candidate_sha256=c['sha256'],calls=rows,limits=['Captured at original logger4176ce entry, before existing synthetic logger return. Words after format are raw ARM32 slots, only actual format consumes meaningful arguments. Both machines deliberately replay original instructions, to gather logger arguments; these receipts are not source equivalence tests. Lower transport/logger implementation not executed.']),indent=2)+'\n')
print('captured',len(rows),'calls',len({(r['family'],r['line']) for r in rows}),'lines')
