from pathlib import Path
# Reuse only pinned image/ELF loader and machine helper, not registration test execution.
exec(Path(__file__).with_name('verify.py').read_text().split('# Independent expected registration model')[0].replace('UC_CPU_ARM_CORTEX_M4','UC_CPU_ARM_CORTEX_M33'))

def run(native,gate,signature,action,enable,metadata,old,mask,profile=3,companion=0):
 u=machine();u.mem_map(0x40008000,0x1000);u.mem_map(0xe000e000,0x2000);w(u,0xe000ed88,0xf00000)
 w(u,0x40021108,gate<<4);w(u,0x2005665c,signature)
 for a,v in [(0x40021008,0x40000),(0x40021010,0x80),(0x40021018,0x12345678),(0x40021028,0x87654321),(0x200742b0,0xabcdef00),(0x200002a0,profile),(0x20000314,0)]:w(u,a,v)
 u.mem_write(0x20074f60,b'\xa5'*32);u.mem_write(0x20074f60,b'\x00');u.mem_write(0x20074f78,bytes([2,old]));u.mem_write(0x20004539,b'\xa5');u.mem_write(0x20004540,bytes([companion]));m=0 if metadata is None else 0x20006000
 w(u,0x20006000,0 if metadata is None else metadata);w(u,0x20006004,0xa5a5a5a5);w(u,0x20006008,0xa5a5a5a5);boundary=[];plan_inputs=[];writes=[]
 def hook(u,a,n,d):
  if a in [0x5a45d0,sym['audio_platform_plan']&~1]:plan_inputs.append(bytes(u.mem_read(u.reg_read(UC_ARM_REG_R0),19)).hex())
  if a in [0x5a453c,sym['audio_platform_apply']&~1]:
   row=dict(address='0x5a453c')
   if a in [0x5a453c,sym['audio_platform_apply']&~1]:row['arguments']=[u.reg_read(r) for r in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]]
   boundary.append(row);u.emu_stop()
 def write(u,access,a,n,v,d):writes.append([hex(a),n,v])
 u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_MEM_WRITE,write,begin=0x40020000,end=0x40021fff)
 u.reg_write(UC_ARM_REG_R0,action);u.reg_write(UC_ARM_REG_R1,enable);u.reg_write(UC_ARM_REG_R2,m);u.reg_write(UC_ARM_REG_PRIMASK,mask);u.emu_start((sym['audio_platform_newer_control'] if native else 0x5a490c)|1,0x2007f000,count=100000)
 assert boundary or u.reg_read(UC_ARM_REG_PC)==0x2007f000
 rv=None if boundary else u.reg_read(UC_ARM_REG_R0)
 if gate!=3:assert rv==0 and not boundary and not plan_inputs and u.reg_read(UC_ARM_REG_PRIMASK)==mask
 elif signature!=0x1f01600d:assert rv==1 and not boundary and not plan_inputs and u.reg_read(UC_ARM_REG_PRIMASK)==mask
 elif action&255 not in range(7):assert rv==6 and u.reg_read(UC_ARM_REG_PRIMASK)==mask
 elif metadata is None and (action&255 in [0,1,2,5] or ((action&255 in [3,4,6]) and enable&255)):assert rv==6 and u.reg_read(UC_ARM_REG_PRIMASK)==mask
 assert not writes
 return dict(return_value=rv,boundary=boundary,plan_inputs=plan_inputs,metadata_after=bytes(u.mem_read(0x20006000,12)).hex(),globals_after=bytes(u.mem_read(0x20074f60,32)).hex(),classification_flag=bytes(u.mem_read(0x20004539,1)).hex(),selected_pair=[word(u,0x200002a0),word(u,0x20000314)],primask=u.reg_read(UC_ARM_REG_PRIMASK))
rows=[]
cases=[]
for gate,sig,action,metadata,mask in itertools.product([0,1,2,3],[0,0x1f01600d],[0,2,7],[None,0],[0,1]):
 if gate==3 and sig==0x1f01600d:continue
 cases.append((gate,sig,action,1,metadata,2,mask))
for action,enable,metadata,old,mask in itertools.product([0,1,2,3,4,5,6,7,256,259],[0,1],[None,0,1,2,3,4],[0,1,2,3,4],[0,1]):cases.append((3,0x1f01600d,action,enable,metadata,old,mask))
for bits in [0xc3960000,0xc3888000,0xc1b00000,0xc1a00000,0xc0000000,0xbf800000,0,0x42400000,0x42480000,0x447a0000,0x7fc00000,0x7f800000,0xff800000]:
 cases.append((3,0x1f01600d,2,1,bits,2,0))
for profile,companion,mask in itertools.product([0,8,9,10,11,12,0xffffffff],[6,7,8],[0,1]):
 cases.append((3,0x1f01600d,0,1,2,0,mask,profile,companion))
for case in cases:
 o=run(False,*case);n=run(True,*case);assert o==n,(case,o,n);rows.append(dict(gate=case[0],signature=hex(case[1]),action=case[2],enable=case[3],metadata_word=case[4],old_state=case[5],initial_primask=case[6],initial_profile=case[7] if len(case)>7 else 3,companion_flag=case[8] if len(case)>8 else 0,**o))
(D/'newer-results.json').write_text(json.dumps(dict(status='PASS',cases=len(rows),comparisons=rows,elf_sha256=hashlib.sha256(elf.read_bytes()).hexdigest(),limits=['Independent first-party control, float classifier, planner, prepare flag and state-flag setter.','Passive MMIO and synthetic gate/signature/state. Initialization reachability and physical effects unverified.','Stop before real apply child; no successful child returns fabricated.','M33-compatible ARMv8-M FPU profile for selected M55 instruction subset, not full M55 emulation.']),indent=2)+'\n');print('PASS',len(rows),'newer-control comparisons')
