from pathlib import Path
import sys,struct,json,hashlib,itertools
from unicorn import *
from unicorn.arm_const import *
from elftools.elf.elffile import ELFFile
D=Path(__file__).resolve().parent;R=D.parents[2];previous=R/'g2/analysis/audio-platform-callbacks-closure-2026-10-08';sys.path.insert(0,str(previous))
from itcm_record import decode_itcm
from startup_evidence import initialized_record
blob=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes();assert hashlib.sha256(blob).hexdigest()=='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863';raw=blob[32:];itcm=decode_itcm(raw);startup=initialized_record(raw)
elf=Path('/tmp/opencfw-transition-producers/producers.elf');segments=[]
with elf.open('rb') as f:
 e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
 for s in e.iter_segments():
  if s['p_type']=='PT_LOAD':segments.append((s['p_vaddr'],s.data()))
def w(u,a,v):u.mem_write(a,struct.pack('<I',v&0xffffffff))
def word(u,a):return struct.unpack('<I',u.mem_read(a,4))[0]
def machine():
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M33)
 for a,n in [(0x438000,(len(raw)+4095)&~4095),(0x20000000,0x80000),(0x100000,0x10000),(0,0x1000),(0x40020000,0x2000),(0x40008000,0x1000),(0x40004000,0x1000),(0xe000e000,0x2000),(0x47ff0000,0x1000)]:u.mem_map(a,n)
 u.mem_write(0x438000,raw);u.mem_write(0x20000000,bytes(startup));u.mem_write(0x40,itcm)
 for a,b in segments:u.mem_write(a,b)
 w(u,0xe000ed88,0xf00000);u.reg_write(UC_ARM_REG_SP,0x2007e000);u.reg_write(UC_ARM_REG_LR,0x2007f001);return u
entries={'stop':(0x4802ce,'pcm22_timer_stop'),'complete2':(0x5a23f8,'pcm22_sequence_2_complete'),'complete7':(0x5a2b14,'pcm22_sequence_7_complete'),'dispatch':(0x5a40ca,'pcm22_boost_completion'),'start2':(0x5a22c0,'pcm22_sequence_2'),'complete21':(0x5a3e24,'pcm22_sequence_21_complete'),'post':(0x5a40b6,'pcm22_post_low_to_high')}
def run(native,kind,sequence=2,initial=0,clock=0,ready=0,cache=0,mask=0,next=1,old=5,ton=0,trim=0,enabled=0,intstat=0,continue_flag=1,clock_clients=0,clock_allowed=0,icache=0,cache_power=0,finish=0,baseline=None,new_vddf=None,current_profile=None,lv_trims=0,last_state=255,callback_enabled=1):
 u=machine();u.mem_map(0xe001e000,0x1000);w(u,0xe001e300,cache_power);w(u,0xe000ed14,icache)
 for a in [0x40020044,0x40020048,0x4002004c,0x40020080,0x4002037c,0x40020344,0x40020358,0x400083e0,0x40008010,0x40008068]:w(u,a,initial)
 w(u,0x400083e0,(initial&~1)|enabled);w(u,0x40008064,intstat);w(u,0x40021000,clock);w(u,0x40004044,cache);w(u,0x40004030,ready);w(u,0x400204e8,0x140)
 u.mem_write(0x20004536,bytes([clock_allowed]));w(u,0x20073348,clock_clients);u.mem_write(0x20004540,bytes([sequence]));u.mem_write(0x20074f60,b'\xa5'*32);u.mem_write(0x20074f77,bytes([continue_flag]));w(u,0x200002a0,next)
 for a,v in [(0x200742d4,trim&127),(0x200742d8,(trim>>7)&127),(0x200742dc,(trim>>14)&1023),(0x200742e0,(trim>>24)&15)]:w(u,a,v)
 for i in range(20):w(u,0x20056660+i*4,(trim+(i*0x0212048b))&0xffffffff)
 w(u,0x200566ac,trim);w(u,0x200566b0,trim);w(u,0x200566b4,trim);w(u,0x200566b8,trim);w(u,0x200566bc,trim)
 w(u,0x200002a4,last_state)
 w(u,0x200566c0,lv_trims)
 if baseline is not None: w(u,0x20056664,(word(u,0x20056664)&~127)|baseline)
 if new_vddf is not None: w(u,0x20056660+next*4,(word(u,0x20056660+next*4)&~127)|new_vddf)
 if kind in ['irq','registered_irq']:w(u,0x2007329c,(sym['pcm22_boost_completion']|1 if native else 0x5a40cb) if callback_enabled else 0)
 if kind=='registered_post':w(u,0x20073298,(sym['pcm22_post_low_to_high']|1 if native else 0x5a40b7) if callback_enabled else 0)
 writes=[];calls=[]
 def write(u,access,a,n,v,d):writes.append([hex(a),n,v])
 for a,b in [(0x40020000,0x40021fff),(0x40008000,0x40008fff),(0x40004000,0x40004fff),(0xe000e100,0xe000e2ff),(0xe000ed14,0xe000ed17),(0xe000ef50,0xe000ef53)]:u.hook_add(UC_HOOK_MEM_WRITE,write,begin=a,end=b)
 def hook(u,a,n,d):
  if a==sym['pcm22_ton_adjust']&~1:calls.append(['0x5a423c',u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_R1)])
  cache_aliases={0x474eb4:'0x474eb4',0x474efa:'0x474efa',sym['pcm22_icache_enable']&~1:'0x474eb4',sym['pcm22_icache_disable']&~1:'0x474efa'}
  if a in cache_aliases:calls.append([cache_aliases[a]])
  if a in [0x4807a0,0x480240,0x4c4530,0x5a423c,0x4807fc]:calls.append([hex(a),*[u.reg_read(r) for r in ([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3] if a==0x4807fc else [UC_ARM_REG_R0,UC_ARM_REG_R1] if a in [0x4c4530,0x5a423c] else [UC_ARM_REG_R0])]])
 u.hook_add(UC_HOOK_CODE,hook);u.reg_write(UC_ARM_REG_PRIMASK,mask)
 for reg,v in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],[next,old,ton,0xabcdef01]):u.reg_write(reg,v)
 if kind=='ton_adjust':u.reg_write(UC_ARM_REG_R0,ton);u.reg_write(UC_ARM_REG_R1,next)
 entry=sym[entries[kind][1]] if native else entries[kind][0];u.emu_start(entry|1,0x2007f000,count=500000)
 assert u.reg_read(UC_ARM_REG_PC)==0x2007f000,(kind,hex(u.reg_read(UC_ARM_REG_PC)))
 if kind in ['cache_enable','cache_disable']:assert u.reg_read(UC_ARM_REG_R0)==(1 if cache_power&0x300 else 0)
 if finish:
  if kind=='start7':target=sym['pcm22_boost_completion'] if native else 0x5a40ca
  else:
   w(u,0x200002a0,next if current_profile is None else current_profile);target=sym['pcm22_post_low_to_high'] if native else 0x5a40b6
  u.reg_write(UC_ARM_REG_SP,0x2007e000);u.reg_write(UC_ARM_REG_LR,0x2007f001);u.emu_start(target|1,0x2007f000,count=500000);assert u.reg_read(UC_ARM_REG_PC)==0x2007f000
 if kind in ['post','registered_post']:assert u.reg_read(UC_ARM_REG_R0)==0
 return dict(icache_final=word(u,0xe000ed14),cache_return=u.reg_read(UC_ARM_REG_R0) if kind in ['cache_enable','cache_disable'] else None,continuation_flag=bytes(u.mem_read(0x20074f77,1)).hex(),writes=writes,calls=calls,trim_globals=bytes(u.mem_read(0x200742d4,24)).hex(),sequence=bytes(u.mem_read(0x20004540,1)).hex(),last_state=word(u,0x200002a4),clock_clients=bytes(u.mem_read(0x20073324,56)).hex(),primask=u.reg_read(UC_ARM_REG_PRIMASK))

entries.update(start7=(0x5a29a0,'pcm22_sequence_7'),start21=(0x5a3cc6,'pcm22_sequence_21'),cache_enable=(0x474eb4,'pcm22_icache_enable'),cache_disable=(0x474efa,'pcm22_icache_disable'),start8=(0x5a2c30,'pcm22_sequence_8'),start9=(0x5a2d24,'pcm22_sequence_9'),start20=(0x5a3bcc,'pcm22_sequence_20'),start10=(0x5a2e10,'pcm22_sequence_10'),start12=(0x5a3122,'pcm22_sequence_12'),start14=(0x5a34ca,'pcm22_sequence_14'),start15=(0x5a35a4,'pcm22_sequence_15'),start16=(0x5a36ac,'pcm22_sequence_16'),start17=(0x5a3798,'pcm22_sequence_17'),start19=(0x5a3ab0,'pcm22_sequence_19'),start0=(0x5a1f04,'pcm22_sequence_0'),start1=(0x5a20e8,'pcm22_sequence_1'),start3=(0x5a2462,'pcm22_sequence_3'),start4=(0x5a2586,'pcm22_sequence_4'),start5=(0x5a26be,'pcm22_sequence_5'),start6=(0x5a28c0,'pcm22_sequence_6'),start11=(0x5a2eea,'pcm22_sequence_11'),start13=(0x5a326c,'pcm22_sequence_13'),start18=(0x5a38ce,'pcm22_sequence_18'),start22=(0x5a3e80,'pcm22_sequence_22'),start23=(0x5a3fe8,'pcm22_sequence_23'),start24=(0x5a40b0,'pcm22_sequence_24'),start25=(0x5a40b2,'pcm22_sequence_25'),start26=(0x5a40b4,'pcm22_sequence_26'),irq=(0x4d58a6,'pcm22_timer15_vector_handler'),registered_irq=(0x48039a,'pcm22_registered_timer_service'),registered_post=(0x4803dc,'pcm22_registered_post_low_to_high'),ton_adjust=(0x5a423c,'pcm22_ton_adjust'))
rows=[];cases=[]
for kind,cache,power,mask in itertools.product(['cache_enable','cache_disable'],[0,0x20000,0xa5a5a5a5],[0,0x100,0x200,0x300],[0,1]):
 cases.append(dict(kind=kind,icache=cache,cache_power=power,mask=mask))
for next,old,ton,trim,mask,enabled,intstat,seq,finish in itertools.product([0,8,19],[0,5,19],[0,7],[0,0x12345678,0xffffffff],[0,1],[0,1],[0,0x40000000],[2,7,26],[0,1]):
 if not enabled and (intstat or seq!=26):continue
 cases.append(dict(kind='start7',next=next,old=old,ton=ton,trim=trim,mask=mask,enabled=enabled,intstat=intstat,sequence=seq,clock=0,ready=0x1000000,cache=0x20,finish=finish))
for baseline,nf,clock,ready,cache in itertools.product([0,50,127],[0,49,50,51,63,64,126,127],[0,2],[0,0x1000000],[0,0x20]):
 cases.append(dict(kind='start7',next=8,old=5,baseline=baseline,new_vddf=nf,clock=clock,ready=ready,cache=cache,finish=1,clock_allowed=1))
for old,trim,mask,enabled,intstat,seq,icache,power,finish in itertools.product([0,5,19],[0,0x12345678,0xffffffff],[0,1],[0,1],[0,0x40000000],[2,7,26],[0,0x20000],[0,0x100],[0,1]):
 if not enabled and (intstat or seq!=26):continue
 cases.append(dict(kind='start21',next=8,old=old,ton=7,trim=trim,mask=mask,enabled=enabled,intstat=intstat,sequence=seq,icache=icache,cache_power=power,finish=finish))
for current in [0,1,8,19]:cases.append(dict(kind='start21',next=8,old=0,ton=7,trim=0x12345678,finish=1,current_profile=current,icache=0x20000))
for kind,next,old,ton,trim,mask,enabled,intstat,seq in itertools.product(['start8','start9','start20'],[0,8,19],[0,5],[0,7],[0,0xffffffff],[0,1],[0,1],[0,0x40000000],[2,7,26]):
 if not enabled and (intstat or seq!=26):continue
 cases.append(dict(kind=kind,next=next,old=old,ton=ton,trim=trim,mask=mask,enabled=enabled,intstat=intstat,sequence=seq))
for kind,next,old,ton,trim,mask,enabled,intstat,seq in itertools.product(['start10','start12','start14','start15','start16','start17','start19'],[0,8,19],[0,5],[0,7],[0,0xffffffff],[0,1],[0,1],[0,0x40000000],[2,7,26]):
 if not enabled and (intstat or seq!=26):continue
 cases.append(dict(kind=kind,next=next,old=old,ton=ton,trim=trim,mask=mask,enabled=enabled,intstat=intstat,sequence=seq,initial=0xa5a5a5a5,lv_trims=0x07e07f80))
for kind,next,old,lv in itertools.product(['start15','start16','start17','start19'],range(4),range(4),[0,0x0fffffff,0x07e07f80]):
 cases.append(dict(kind=kind,next=next,old=old,lv_trims=lv,initial=0xa5a5a5a5,trim=0x12345678))
for kind,next,old,ton,trim,mask,enabled,intstat,seq in itertools.product(['start0','start1','start3','start4','start5','start6','start11','start13','start18','start22','start23'],[0,8,19],[0,5],[0,7],[0,0xffffffff],[0,1],[0,1],[0,0x40000000],[2,7,26]):
 if not enabled and (intstat or seq!=26):continue
 cases.append(dict(kind=kind,next=next,old=old,ton=ton,trim=trim,mask=mask,enabled=enabled,intstat=intstat,sequence=seq,initial=0xa5a5a5a5,lv_trims=0x07e07f80))
for kind,next,old in itertools.product(['start24','start25','start26'],[0,1,8,19],[0,5,19]):cases.append(dict(kind=kind,next=next,old=old))
for next,seq,trim,mask,clients in itertools.product([0,8,19],[2,7,26],[0,0x12345678],[0,1],[0,0x20000]):
 cases.append(dict(kind='start0',next=next,last_state=next,old=5,enabled=1,sequence=seq,trim=trim,mask=mask,clock_clients=clients))
for kind,clock,ready,cache,mask in itertools.product(['start5','start11','start13'],[0,2,6],[0,0x1000000],[0,0x20],[0,1]):
 cases.append(dict(kind=kind,next=8,old=0,trim=0x12345678,clock=clock,ready=ready,cache=cache,mask=mask,initial=0xa5a5a5a5))
for kind,icache,power,mask,trim in itertools.product(['start0','start1'],[0,0x20000],[0,0x100,0x200,0x300],[0,1],[0,0x12345678]):
 cases.append(dict(kind=kind,next=8,old=0,icache=icache,cache_power=power,mask=mask,trim=trim))
for nf,base in itertools.product([0,49,50,51,127],[0,50,127]):
 cases.append(dict(kind='start13',next=8,old=5,new_vddf=nf,baseline=base,ready=0x1000000,cache=0x20))
for kind,seq,clients,mask,on in itertools.product(['irq','registered_irq'],[2,7,26],[0,0x20000,0x20001],[0,1],[0,1]):
 cases.append(dict(kind=kind,sequence=seq,clock_clients=clients,mask=mask,callback_enabled=on,trim=0x12345678))
for next,flag,on,trim in itertools.product([0,8,19],[0,1],[0,1],[0,0xffffffff]):
 cases.append(dict(kind='registered_post',next=next,continue_flag=flag,callback_enabled=on,trim=trim))
for ton,profile,trim,initial in itertools.product(list(range(10))+[0x100,0xffffffff],[0,7,8,19],[0,0x12345678,0xffffffff],[0,0xa5a5a5a5]):
 cases.append(dict(kind='ton_adjust',ton=ton,next=profile,trim=trim,initial=initial))
for case in cases:
 o=run(False,**case);n=run(True,**case);assert o==n,(case,o,n);rows.append(dict(inputs=case,**o))
(D/'results.json').write_text(json.dumps(dict(status='PASS',cases=len(rows),elf_sha256=hashlib.sha256(elf.read_bytes()).hexdigest(),comparisons=rows,limits=['Synthetic calibration and passive MMIO/CCR/cache-power status; authentic trim values and asynchronous IRQ/cache effects unverified.','Explicit producer→completion calls are synthetic sequential composition, not observed IRQ scheduling.','Actual shared delay/ITCM/timer-start/TON/status/clock code executes without successful-return stubs.','Native cache routines independently reproduce stock instructions; M33-compatible instruction subset, not physical cache/barrier semantics.','Void transition return registers are not treated as success contracts.']),separators=(',',':'))+'\n');print('PASS',len(rows),'producer/cache/composition comparisons')
