#!/usr/bin/env python3
"""Execute actual adapter/retry/recovery/frame/wire source; GPIO and disabled logger boundaries remain explicit."""
import hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-stacmd-stage';C=0x200075c4;B=0x20003000
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
ENTRIES={'r1_stacmd_read_frame_native':0x28bb0,'r1_stacmd_write_frame_native':0x28c6c,'r1_stacmd_drive_bit_native':0x5cbe4,'r1_stacmd_write_bits_native':0x5cc68,'r1_stacmd_idle_native':0x5cccc,'r1_stacmd_parity_native':0x968a8,'r1_stacmd_read_bit_native':0x87b30,'r1_stacmd_read_bit_adapter_native':0x969ec,'r1_stacmd_recovery_delay_native':0x5c0fa}
ENTRIES.update(r1_stacmd_read=0x56590,r1_stacmd_write=0x5660c,r1_stacmd_write_retry_native=0x35698,r1_stacmd_bus_recovery_native=0x5cc8c)
ENTRIES.update(r1_yhm2710_stacmd_binding_configuration=0x565f4,r1_stock_registry_register=0x85d58,strcmp=0x277fe,r1_stock_dispatch_08=0x85d1a,r1_stock_dispatch_0c=0x85cba,r1_stock_dispatch_10=0x85d2c,r1_stock_dispatch_14=0x85da8,r1_stacmd_open=0x5657c,r1_stacmd_close=0x56568)
def main():
 vp=OUT/'registry-integration-verification.json';vp.unlink(missing_ok=True);objects=[];provider_reports={};provider_objects={}
 for module in ('native-stacmd-frames','native-stacmd-transmit','native-stacmd-receive','native-stacmd-delay','native-stacmd-operations','native-stacmd-write-retry','native-stacmd-recovery','native-stacmd-state'):
  report=BASE/module/'report.json';r=json.loads(report.read_text());u=r['units'][0];obj=BASE/module/(module.replace('-','_')+'.o');assert sha(obj)==u['object_sha256']
  for p,h in r['inputs'].items():assert sha(ROOT/p)==h,p
  objects.append(obj);provider_reports[module+'/report.json']=sha(report);provider_objects[str(obj.relative_to(BASE))]=sha(obj)
 registration_report=BASE/'native-stacmd-registration/report.json';registration=json.loads(registration_report.read_text());registration_object=registration_report.parent/'stacmd-registration.o';assert sha(registration_object)==registration['selected_object_sha256'];objects.append(registration_object);provider_reports['native-stacmd-registration/report.json']=sha(registration_report);provider_objects[str(registration_object.relative_to(BASE))]=sha(registration_object)
 for module,source,filename in [('i2c5','r1/components/registry/stock_registry.c','stock_registry.o'),('runtime','third-party/upstream/musl-memory-1.2.5/strcmp.c','strcmp.o')]:
  report=BASE/module/'report.json';r=json.loads(report.read_text());unit=next(u for u in r['units'] if u['source']==source);obj=report.parent/filename;assert sha(obj)==unit['object_sha256'] and sha(ROOT/source)==unit['source_sha256'];objects.append(obj);provider_reports[module+'/report.json']=sha(report);provider_objects[str(obj.relative_to(BASE))]=sha(obj)
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';app_hash=sha(app);assert app_hash=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
 stock_init=Uc(UC_ARCH_ARM,UC_MODE_THUMB);stock_init.mem_map(0x20000,0xc0000);stock_init.mem_write(0x27000,app.read_bytes());stock_init.mem_map(0x20000000,0x40000);stock_init.mem_write(0x20000000,b'\xa5'*0x40000);stock_init.reg_write(UC_ARM_REG_SP,0x2003f000);stock_init.emu_start(0x283a1,0x27208,count=2000000);assert stock_init.reg_read(UC_ARM_REG_PC)==0x27208;native_initial=bytes(stock_init.mem_read(C-4,112));assert native_initial[:4]==bytes(4)
 counts={side:{n:0 for n in ENTRIES} for side in ('native','source')};nops={'native':0,'source':0};gpio_counts={'native':0,'source':0};case_counts={'read':0,'write':0};outcomes={'success':0,'failure':0}
 with tempfile.TemporaryDirectory() as directory:
  d=Path(directory);ld=d/'layout.ld';elf=d/'test.elf';binary=d/'text.bin';ld.write_text('SECTIONS { .registry_head 0x20007680 (NOLOAD) : { *(.r1.registry.head) } .counter 0x200075c0 : { *(.r1.stacmd.failed_transactions) } .configuration 0x200075c4 : { *(.r1.stacmd.configuration) } .name 0xc07c8 : { *(.r1.stacmd.name) } .text 0x1000000 : { *(.text*) *(.rodata*) *(.r1.stacmd_retry.*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }');subprocess.run(['arm-none-eabi-ld','-T',str(ld),'--defsym=r1_twi_gpio_low=0x1100001','--defsym=r1_twi_gpio_high=0x1100011','--defsym=r1_twi_gpio_output=0x1100021','--defsym=r1_twi_gpio_input=0x1100031','--defsym=r1_twi_gpio_read=0x1100041','--defsym=r1_twi_gpio_release=0x1100071','--defsym=r1_rtt_delay_cycles=0x1100211','--defsym=r1_structured_log_mode_get=0x1100101','--defsym=r1_structured_log_format=0x1100111','--defsym=nrf_log_frontend_std_1=0x1100121',*map(str,objects),'-o',str(elf)],check=True,capture_output=True);subprocess.run(['arm-none-eabi-objcopy','-j','.text','-O','binary',str(elf),str(binary)],check=True)
  syms={v[2]:int(v[0],16) for l in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=l.split())==3};image=binary.read_bytes();assert len(image)<65536;machines=[];states={};addresses=[{a:n for n,a in ENTRIES.items()},{syms[n]:n for n in ENTRIES}]
  from verify_native_device_registrars import STACMD_POINTERS
  compiled_sections={}
  for section,address,size in [('counter',C-4,4),('configuration',C,108),('name',0xc07c8,14)]:
   file=d/(section+'.bin');subprocess.run(['arm-none-eabi-objcopy','-j','.'+section,'-O','binary',str(elf),str(file)],check=True);contents=file.read_bytes();assert len(contents)==size;compiled_sections[section]={'address':address,'bytes':size,'sha256':sha(file),'data':contents}
  assert compiled_sections['counter']['data']==bytes(4) and compiled_sections['name']['data']==b'device_stacmd\0'
  source_initial=compiled_sections['counter']['data']+compiled_sections['configuration']['data']
  def normalize(data,candidate):
   data=bytearray(data)
   for offset,name,native in STACMD_POINTERS:
    value=struct.unpack_from('<I',data,4+offset)[0]
    if candidate and value==(syms[name]|1):struct.pack_into('<I',data,4+offset,native|1)
   return bytes(data)
  assert normalize(source_initial,True)==native_initial
  native_gpio={0x791e4:0x1100000,0x794ac:0x1100010,0x7910c:0x1100020,0x790aa:0x1100030,0x79408:0x1100040,0x7902c:0x1100070}
  def hook(u,a,size,_):
   candidate=int(id(u)==id(machines[1]));side='source' if candidate else 'native';f=states[id(u)]
   if a in addresses[candidate]:
    name=addresses[candidate][a];counts[side][name]+=1
    if name in ('r1_stacmd_read_frame_native','r1_stacmd_write_frame_native'):
     f['frame_index']+=1;f['episode']=-1;f['poll']=0;f['stream']=list(f['base_stream'])
     f['fault']='header_timeout' if f['plan']=='always_timeout' else 'header_parity' if f['plan']=='always_parity' or (f['plan']=='fail_first_then_success' and f['frame_index']==1) else 'none'
     if f['fault']=='header_parity':f['stream'][0]^=1
   if f.get('phase')=='wire' and bytes(u.mem_read(a,2))==b'\x00\xbf':nops[side]+=1;f['nops']+=1
   r=[u.reg_read(reg) for reg in (UC_ARM_REG_R0,UC_ARM_REG_R1)]
   a=native_gpio.get(a,a)
   if a in (0x914ec,0x1100100):
    f['mode_calls']+=1;u.reg_write(UC_ARM_REG_R0,0);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR));return
   if a in (0x91638,0x799c8,0x1100110,0x1100120):raise AssertionError('unexpected enabled log in mode0')
   if a in (0x1100000,0x1100010,0x1100020):event=('line',a,r[0]);value=0xffffffff
   elif a==0x1100030:
    event=('input',r[0],r[1]);f['episode']+=1;f['poll']=0;value=0xffffffff
   elif a in (0x1100040,0x1100060):
    episode=f['episode'];index=f['poll'];f['poll']+=1;bit=f['stream'][episode] if episode<len(f['stream']) else 0
    falling=(f['fault']=='header_timeout' and episode==0) or (f['fault']=='data_timeout' and episode==(3 if f['reading'] else 1));rising=f['fault']=='rising_timeout' and episode==0;first_calls=1000 if falling else 1
    if index<first_calls:value=1 if falling else 0
    elif index==first_calls:value=1-bit
    else:value=0 if rising else 1
    event=('read',a,r[0],value)
   else:
    if candidate and a<0x1000000 and a!=0x20000100:raise AssertionError(('source executed native provider',hex(a)))
    return
   gpio_counts[side]+=1;f['trace'].append(event)
   if f['mutation']:
    index=len(f['trace']);u.mem_write(C+4,b'\0');u.mem_write(C+12,struct.pack('<I',0x80000000+index));u.mem_write(C+32,bytes([index&255]));u.mem_write(C+40,struct.pack('<I',0x1100061))
   u.reg_write(UC_ARM_REG_R0,value);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  for _ in range(2):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,app.read_bytes());u.mem_map(0x1000000,65536);u.mem_write(0x1000000,image);u.mem_map(0x1100000,4096);u.mem_map(0x20000000,0x40000);machines.append(u);u.hook_add(UC_HOOK_CODE,hook)
  saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
  status_counts={}
  for reading,opened,null_request,length,plan,mutation in itertools.product((False,True),(0,1),(False,True),(0,1,3),('success','fail_first_then_success','always_parity','always_timeout'),(False,True)):
   command=0x44;reg=2;fault='none'
   payload=bytes((0x00,0xa5,0xff,0x81));header=((command&0xf0)+reg)&255;parity=lambda x:(x&255).bit_count()&1;stream=[parity((header<<1)+int(reading))]
   if length<0x80000000:
    if reading:stream += [(byte>>bit)&1 for byte in payload[:length] for bit in range(7,-1,-1)]
    else:stream += [parity(byte) for byte in payload[:length]]
   if fault=='header_parity':stream[0]^=1
   name='r1_stacmd_read' if reading else 'r1_stacmd_write';results=[]
   for candidate,u in enumerate(machines):
    states[id(u)]={'trace':[],'nops':0,'episode':-1,'poll':0,'stream':stream,'reading':reading,'fault':fault,'mutation':mutation,'frame_index':0,'base_stream':stream,'plan':plan,'mode_calls':0,'phase':'setup'};u.mem_write(C-4,b'\x96'*116);u.mem_write(C-4,source_initial if candidate else native_initial);u.mem_write(0xc07c8,compiled_sections['name']['data']);u.mem_write(B-4,b'\xa5'*4+payload+b'\x69'*4)
    u.mem_write(0x20007680,bytes(4))
    def invoke(entry,args):
     for register,value in zip((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3),args):u.reg_write(register,value)
     u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101)
     for index,register in enumerate(saved):u.reg_write(register,0x12345600+index)
     u.emu_start(entry|1,0x20000100,count=10000)
     assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and [u.reg_read(register) for register in saved]==[0x12345600+index for index in range(8)]
     return u.reg_read(UC_ARM_REG_R0)
    registrar='r1_yhm2710_stacmd_binding_configuration';entry=syms[registrar] if candidate else ENTRIES[registrar]
    assert invoke(entry,())==1 and invoke(entry,())==0
    assert struct.unpack('<I',bytes(u.mem_read(0x20007680,4)))[0]==C+48
    operation='r1_stock_dispatch_08' if opened else 'r1_stock_dispatch_0c'
    assert invoke(syms[operation] if candidate else ENTRIES[operation],(C+48,))==0
    assert u.mem_read(C+4,1)==bytes([opened])
    states[id(u)]['phase']='wire'
    request=bytearray(20);request[0]=reg;request[8]=length;request[16]=length;struct.pack_into('<I',request,4,B);struct.pack_into('<I',request,12,B);u.mem_write(0x20002000,bytes(request))
    for r,v in [(UC_ARM_REG_R0,C+48),(UC_ARM_REG_R1,0xffffffff),(UC_ARM_REG_R2,0 if null_request else 0x20002000),(UC_ARM_REG_R3,0),(UC_ARM_REG_SP,0x2003f000),(UC_ARM_REG_LR,0x20000101)]:u.reg_write(r,v)
    for i,r in enumerate(saved):u.reg_write(r,0x12345600+i)
    dispatch='r1_stock_dispatch_10' if reading else 'r1_stock_dispatch_14';u.emu_start((syms[dispatch] if candidate else ENTRIES[dispatch])|1,0x20000100,count=1500000)
    assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and [u.reg_read(r) for r in saved]==[0x12345600+i for i in range(8)]
    results.append((u.reg_read(UC_ARM_REG_R0),states[id(u)]['trace'],states[id(u)]['nops'],normalize(bytes(u.mem_read(C-4,116)),candidate),bytes(u.mem_read(B-4,12)),states[id(u)]['frame_index'],states[id(u)]['mode_calls'],bytes(u.mem_read(0x20007680,4))))
   assert results[0]==results[1],(reading,opened,null_request,length,plan,mutation,{'returns':[x[0] for x in results],'trace_equal':results[0][1]==results[1][1],'nops':[x[2] for x in results],'context_equal':results[0][3]==results[1][3],'buffer_equal':results[0][4]==results[1][4]})
   expected=11 if null_request else (29 if reading else 27) if not opened else (31 if reading else 30) if plan in ('always_parity','always_timeout') else 0
   status_counts[str(expected)]=status_counts.get(str(expected),0)+1
   expected_frames=0 if null_request or not opened else 1 if plan=='success' else 2 if plan=='fail_first_then_success' else 9
   assert results[0][5]==results[1][5]==expected_frames
   assert results[0][6]==results[1][6]
   assert results[0][0]==expected,(reading,opened,null_request,length,plan,results[0][0]);outcomes['success' if expected==0 else 'failure']+=1;case_counts['read' if reading else 'write']+=1
 assert counts['native']==counts['source'] and nops['native']==nops['source'] and gpio_counts['native']==gpio_counts['source']
 vp.write_text(json.dumps(dict(comparisons=sum(case_counts.values()),counts=case_counts,outcomes=outcomes,status_counts=status_counts,logging_mode=0,registration_calls_per_case=2,source_owned_sections={name:{k:v for k,v in row.items() if k!='data'} for name,row in compiled_sections.items()},source_owned_counter_initial_value=0,provider_reports=provider_reports,provider_objects=provider_objects,executed_provider_entry_counts=counts,total_nops=nops,gpio_callback_counts=gpio_counts,driver_sha256=sha(Path(__file__)),application_sha256=app_hash,provider_interception=False,application_linked=False,instruction_identity=False,limitations=['GPIO callbacks and disabled logger-mode boundary are fixtures; all selected adapter/retry/recovery/frame/wire bodies execute','Compiled registration and cold counter sections are installed; GPIO addresses and logging endpoints remain fixtures','Actual registry/adapter/wire graph does not establish higher transport or canonical integration','NOP counts match; physical timing/cycle scheduling and whole-image byte identity remain open']),indent=2)+'\n');print('STACMD registry/state/wire graph:',case_counts,outcomes,counts,nops,gpio_counts)
if __name__=='__main__':main()
