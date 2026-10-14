from pathlib import Path
p=Path(__file__).resolve().parent.parent/'case-wave056-timer-trampoline-binding/check.py';ns={'__file__':str(p)};exec(p.read_text().split('rows=[]')[0],ns);globals().update({k:v for k,v in ns.items() if k!='__file__'});OUT=Path(__file__).resolve().parent
rows=[]
for cb in callbacks:
 for mode in [0,1]:
  for static in [False,True]:
   results=[]
   for source in [False,True]:
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0);u.mem_map(0x8000000,0x20000);u.mem_map(0x20000000,0x10000);u.mem_map(0xe000e000,0x2000)
    if source:
     for a,d in segs:u.mem_write(a,d)
    else:u.mem_write(0x8000000,raw)
    low=[0x20002c88];called=[]
    def hook(uc,pc,size,data):
     low[0]=min(low[0],uc.reg_read(UC_ARM_REG_SP))
     if pc==0x801ff00:uc.emu_stop()
     if pc==(syms[cb[1]]&~1 if source else 0x8000000+cb[0]):called.append(pc)
    u.hook_add(UC_HOOK_CODE,hook)
    def invoke(native,symbol,args):
     for reg,v in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],args+[0]*4):u.reg_write(reg,v)
     u.reg_write(UC_ARM_REG_SP,0x20002c88);u.mem_write(0x20002c88,bytes(4));u.reg_write(UC_ARM_REG_LR,0x801ff01)
     u.emu_start(syms[symbol] if source else native|1,0,count=200000);assert u.reg_read(UC_ARM_REG_PC)==0x801ff00
     return u.reg_read(UC_ARM_REG_R0)
    invoke(0x800ac84,'case_boot_scheduler_initialize',[])
    def word(a):return struct.unpack('<I',u.mem_read(a,4))[0]
    before=word(0x20000180);descriptor=0x20004000 if static else 0
    if descriptor:u.mem_write(descriptor,struct.pack('<IIII',0,0,0x20005000,44))
    target=syms[cb[1]] if source else (0x8000000+cb[0])|1
    obj=invoke(0x800aa48,'case_boot_transport_register',[target,mode,0x13579bdf,descriptor]);assert obj
    pair=word(obj+28);saved=bytes(u.mem_read(pair,8));allocated=word(0x20000180)
    assert invoke(0x800cd80,'case_policy_task_event_send',[obj,5,0,0])==1
    invoke(0x800b0fc,'case_boot_timer_expired',[])
    after=word(0x20000180);assert bytes(u.mem_read(pair,8))==saved and not called
    pair_header=word(pair-4);assert pair_header&0x80000000
    if static:assert after==allocated and bytes(u.mem_read(obj+40,1))[0]&2
    else:assert after>allocated
    results.append(dict(before_free_bytes=before,registered_free_bytes=allocated,deleted_free_bytes=after,callback_pair_still_allocated=True,pair_argument=struct.unpack('<II',saved)[1],callbacks_executed=0,bounded_stack_bytes=0x20002c88-low[0]))
   assert {k:v for k,v in results[0].items() if k!='bounded_stack_bytes'}=={k:v for k,v in results[1].items() if k!='bounded_stack_bytes'}
   rows.append(dict(callback_native=hex(0x8000000+cb[0]),mode=mode,static_object=static,native=results[0],source=results[1]))
(OUT/'verification.json').write_text(json.dumps(dict(status='PASS_24_REAL_REGISTER_SEND_DELETE_PAIRS',comparisons=rows,stock_behavior='Delete command frees dynamic timer object but leaves callback pair allocated; static object and pair remain. Preserve stock-compatible behavior; no upstream reclamation fix implemented.',limits=['Real scheduler queue, allocator, constructors, sender, receiver, consumer and free providers; no fabricated callbacks or helper returns','Synchronous valid delete; asynchronous reuse/race and running callback interleavings not proven','Retained callback pair is native behavior, not a recovered-C mismatch','No global stack bound or physical peripheral acceptance']),indent=2)+'\n');print('PASS',len(rows))
