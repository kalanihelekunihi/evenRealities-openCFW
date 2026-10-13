from pathlib import Path
import json,struct,random,hashlib
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
D=Path(__file__).resolve().parent;source=D.parent/'root-lvgl-content-sizing-round322/candidate-unadmitted.c';blob=Path('/tmp/opencfw-main-native.bin').read_bytes();assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob);u.mem_map(0x100000,0x200000);u.mem_map(0x20000000,0x100000)
with (D/'candidate-m4.elf').open('rb') as f:
 e=ELFFile(f)
 for sec in e.iter_sections():
  if sec['sh_flags']&2 and sec['sh_type']!='SHT_NOBITS':u.mem_write(sec['sh_addr'],sec.data())
 symbols={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
mapping=json.loads((D/'controlled-callees.json').read_text());targets={}
for name,address in mapping.items():targets[address]=name;targets[int(name.rsplit('_',1)[1],16)]=name;u.mem_write(address,b'\x70\x47')
OBJ=0x20005000;SPEC=0x20006000;ARRAY=0x20007000;CHILD=0x20008000
saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11];seeds=[0x12345000+i*0x101 for i in range(8)];case={};seen=[];counts={}
def word(address):return struct.unpack('<I',u.mem_read(address,4))[0]
def signed(value):return value if value<0x80000000 else value-0x100000000
def hook(uc,address,size,user):
 if address not in targets:return
 name=targets[address];a=uc.reg_read(UC_ARM_REG_R0);b=uc.reg_read(UC_ARM_REG_R1);index=(a-CHILD)//256 if CHILD<=a<CHILD+8*256 else -1
 row=case['children'][index] if index>=0 else None
 args=(a,)
 if 'obj_x_' in name:result=(0-word(SPEC+32))&0xffffffff if word(OBJ+8) else 0
 elif 'obj_y_' in name:result=(0-word(SPEC+36))&0xffffffff if word(OBJ+8) else 0
 elif 'child_count_' in name:result=len(case['children'])
 elif 'has_flag_any_' in name:args=(a,b);result=int(bool(row['flags']&b))
 elif 'layout_positioned_' in name:result=0 if row['flags']&0x60001 else row['positioned']
 elif 'self_width_' in name:result=case['self'][0]
 elif 'self_height_' in name:result=case['self'][1]
 elif 'style_x_' in name or 'style_y_' in name:args=(a,b);result=row['offset']
 elif 'style_align_' in name:args=(a,b);result=row['align']
 elif 'style_base_dir_' in name:args=(a,b);result=case['rtl']
 elif 'style_pad_' in name:
  args=(a,b);key=next(x for x in ['left','right','top','bottom'] if '_'+x+'_' in name);result=case['pads'][key]
 elif 'style_margin_' in name:
  args=(a,b);key=next(x for x in ['left','right','top','bottom'] if '_'+x+'_' in name);counter=(index,key);ordinal=counts.get(counter,0);counts[counter]=ordinal+1;result=(row['margins'][key]+ordinal*case['increment'])&0xffffffff
 elif 'area_width_' in name:result=(word(a+8)-word(a)+1)&0xffffffff
 elif 'area_height_' in name:result=(word(a+12)-word(a+4)+1)&0xffffffff
 else:raise AssertionError(name)
 seen.append((name,args,result,word(SPEC+32),word(SPEC+36)));uc.reg_write(UC_ARM_REG_R0,result);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
u.hook_add(UC_HOOK_CODE,hook)
def run(entry,initial):
 seen.clear();counts.clear();u.mem_write(OBJ,initial);u.reg_write(UC_ARM_REG_CPSR,0x33);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,OBJ)
 for r,v in zip(saved,seeds):u.reg_write(r,v)
 u.mem_write(0x200ff000,b'\xa5'*16);u.emu_start(entry|1,0x600000,count=5000)
 assert u.reg_read(UC_ARM_REG_PC)==0x600000 and u.reg_read(UC_ARM_REG_SP)==0x200ff000
 assert [u.reg_read(r) for r in saved]==seeds and bytes(u.mem_read(0x200ff000,16))==b'\xa5'*16
 return u.reg_read(UC_ARM_REG_R0),list(seen),bytes(u.mem_read(OBJ,0x4000))
rng=random.Random(323);total=0
for trial in range(768):
 count=[0,1,2,4,8][trial%5];case={'rtl':[0,1,2,255][trial%4],'self':[rng.getrandbits(32),rng.getrandbits(32)],'pads':{x:rng.getrandbits(32) for x in ['left','right','top','bottom']},'increment':[0,1,0x7fffffff][trial%3],'children':[]};initial=bytearray(rng.getrandbits(8) for _ in range(0x4000))
 def put(address,value):struct.pack_into('<I',initial,address-OBJ,value&0xffffffff)
 put(OBJ+8,0 if count==0 and trial%2==0 else SPEC);put(SPEC,ARRAY);put(SPEC+32,rng.getrandbits(32));put(SPEC+36,rng.getrandbits(32))
 for i in range(count):
  put(ARRAY+i*4,CHILD+i*256);case['children'].append({'flags':[0,1,0x40000,0x20000][rng.randrange(4)],'positioned':rng.randrange(2),'offset':[0,1,0xffffffff][rng.randrange(3)],'align':rng.choice([0,1,2,3,4,5,6,7,8,9,10,255]),'margins':{x:rng.getrandbits(32) for x in ['left','right','top','bottom']}})
 for native,name in [(0x440a3c,'audio_uart_lv_calc_content_width_440a3c'),(0x440c2e,'audio_uart_lv_calc_content_height_440c2e')]:
  expected=run(native,bytes(initial));actual=run(symbols[name],bytes(initial))
  if actual!=expected:
   (D/'mismatch.json').write_text(json.dumps({'trial':trial,'entry':hex(native),'case':case,'native_result':hex(expected[0]),'C_result':hex(actual[0]),'native_calls':expected[1],'C_calls':actual[1],'memory_equal':expected[2]==actual[2]},indent=2)+'\n');raise AssertionError((trial,hex(native),'see mismatch.json'))
  total+=1
receipt={'status':'PASS_PRELIMINARY_INTEGER_LOGIC_NATIVE_ORACLE','native_comparisons':total,'native_instruction_bytes_unchanged':True,'candidate_compiler_target':'Cortex-M4 research comparison of portable integer logic; actual Cortex-M55 compiler execution pending','controlled_child_targets':len(mapping),'checks':['R0bits','ordered child call inputs/outputs and scroll snapshots','entire16KiB object/spec/child region','SP/callee-saved seeds/caller guard'],'dynamic_margin_values':True,'candidate_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'selected':False,'limits':['All direct callees controlled; not connected child engine proof','M55 production compilation/ISA execution still required','No hardware/image qualification']};(D/'probe-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
