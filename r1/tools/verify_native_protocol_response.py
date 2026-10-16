#!/usr/bin/env python3
"""Response allocation, encoder arguments, logging reloads, cleanup and status oracle."""
import hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-protocol-response';H=0x20002000;M=0x20003000;I=0x20004000;sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
P={'r1_authenticated_phone_connection_gate':0x4cbb0,'r1_peer_channel_b_valid':0x4cb40,'pvPortMalloc':0x855a0,'vPortFree':0x95d48,'r1_model_encode':0x82f9c,'r1_protocol_send_hook_call':0x827f8,'r1_structured_log_mode_get':0x914ec,'r1_structured_log_format':0x91638,'nrf_log_frontend_std_1':0x799c8,'nrf_log_frontend_std_2':0x799d6,'nrf_log_frontend_std_4':0x799f8}
SECTIONS={'alloc_ring':(0x82a28,43),'alloc_sdk':(0x82a54,37),'tx_ring':(0x82a7c,58),'tx_sdk':(0x82ab8,52),'send_ring':(0x82aec,53),'send_sdk':(0x82b24,47)}
def main():
 vp=OUT/'verification.json';vp.unlink(missing_ok=True);rp=OUT/'report.json';r=json.loads(rp.read_text());obj=OUT/'native_protocol_response.o';assert sha(obj)==r['units'][0]['object_sha256']
 for p,h in r['inputs'].items():assert sha(ROOT/p)==h,p
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';ah=sha(app);assert ah=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';evidence={}
 p=OUT/'rea-828b4.json';p.write_bytes((BASE/'native-battery-runtime/rea-next-828b4-body.json').read_bytes());q=json.loads(p.read_text());assert q['subject']['digest']['sha256']=='92c47a5cca2d71f9020e17693a0268c192677f00e3734c47e28f04d1f1b081e8' and q['normalized_result']['body']['total_bytes']==364;evidence[p.name]=sha(p)
 socket='/var/folders/mh/nz9vzlpn7kzff18f77pztg880000gn/T/ghidra-mcp-kalani/ghidra-11353.sock';raw=subprocess.check_output(['curl','-fsS','--max-time','20','--unix-socket',socket,'http://localhost/read_memory?program=stock-r1-native-analysis.elf&address=0x828b4&length=672']);assert bytes(json.loads(raw)['data'])==app.read_bytes()[0x828b4-0x27000:0x828b4-0x27000+672];p=OUT/'ghidra-body-data.json';p.write_bytes(raw);evidence[p.name]=sha(p)
 modes=[(i,) for i in range(8)]+[(0,4,2),(1,2),(4,0,7,0),(0,0,0,1,7),(0xffffffff,0)];machines=[];states={};counts={n:0 for n in P};outcomes={};comparisons=0;sections={}
 with tempfile.TemporaryDirectory() as directory:
  d=Path(directory);ld=d/'layout.ld';elf=d/'test.elf';binary=d/'text.bin';bindings={n:0x1100001+i*16 for i,n in enumerate(P)};ld.write_text('SECTIONS { '+''.join(f'.{n} 0x{a:x} : {{ *(.r1.protocol_response.{n}) }} ' for n,(a,z) in SECTIONS.items())+' .text 0x1000000 : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }');subprocess.run(['arm-none-eabi-ld','-T',str(ld),*['--defsym='+n+'='+hex(a) for n,a in bindings.items()],str(obj),'-o',str(elf)],check=True,capture_output=True);subprocess.run(['arm-none-eabi-objcopy','-j','.text','-O','binary',str(elf),str(binary)],check=True)
  for n,(a,z) in SECTIONS.items():
   p=d/(n+'.bin');subprocess.run(['arm-none-eabi-objcopy','-j','.'+n,'-O','binary',str(elf),str(p)],check=True);assert p.read_bytes()==app.read_bytes()[a-0x27000:a-0x27000+z];sections[n]={'address':a,'bytes':z,'sha256':sha(p)}
  syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3};kinds={a:n for n,a in P.items()};kinds.update({a&~1:n for n,a in bindings.items()});forms={a:n for n,(a,z) in SECTIONS.items()}
  def hook(u,a,size,_):
   if a not in kinds:
    if u is machines[1] and a<0x1000000 and a!=0x20000100:raise AssertionError(('source native provider',hex(a)))
    return
   f=states[id(u)];n=kinds[a];args=[u.reg_read(reg) for reg in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)];event=(n,);value=0
   if n=='r1_authenticated_phone_connection_gate':value=f['auth'];f['gate_a']+=1
   elif n=='r1_peer_channel_b_valid':value=f['peer'];f['gate_b']+=1
   elif n=='pvPortMalloc':assert args[0]==f['capacity'];event+=(args[0],);value=M if f['malloc'] else 0;f['allocations']+=1
   elif n=='vPortFree':assert args[0]==M;event+=(M,);f['frees']+=1
   elif n=='r1_model_encode':
    stack=struct.unpack('<5I',bytes(u.mem_read(u.reg_read(UC_ARM_REG_SP),20)));h=bytes(u.mem_read(H,8));assert args==[M,f['capacity'],h[1],h[2]] and stack==(h[3],h[0],struct.unpack_from('<H',h,4)[0],I,f['length']);event+=tuple(args)+stack;value=f['encode'];u.mem_write(M,bytes((i*17+11)&255 for i in range(64)));f['encodes']+=1
   elif n=='r1_protocol_send_hook_call':assert args[:3]==[f['handle'],M,f['capacity']];event+=tuple(args[:3]);value=f['send'];f['sends']+=1
   elif n=='r1_structured_log_mode_get':value=f['sequence'][f['mode_index']%len(f['sequence'])];f['mode_index']+=1;event+=(value,)
   else:
    form=forms[args[1]];event+=(form,);data=bytes(u.mem_read(M,8));command=(data[1]<<16)|(data[6]<<8)|data[7];h=bytes(u.mem_read(H,8));reverse=(h[2]<<8)|h[3]
    expected=[reverse,f['length']] if form.startswith('alloc') else [f['handle'],command,data[5],struct.unpack_from('<H',data,3)[0]] if form.startswith('tx') else [f['send']]
    if form.endswith('_ring'):
     header=0x04800000 if form.startswith('alloc') else 0x0d000000 if form.startswith('tx') else 0x04400000;assert n=='r1_structured_log_format' and args[:3]==[header,args[1],args[1]];actual=[args[3]]+list(struct.unpack('<'+str(len(expected)-1)+'I',bytes(u.mem_read(u.reg_read(UC_ARM_REG_SP),4*(len(expected)-1))))) if len(expected)>1 else [args[3]]
    else:
     assert args[0]==(0x001c0003 if form.startswith('tx') else 0x001c0001);actual=args[2:2+min(len(expected),2)]+list(struct.unpack('<2I',bytes(u.mem_read(u.reg_read(UC_ARM_REG_SP),8)))) if len(expected)==4 else args[2:2+len(expected)]
    assert actual==expected,(form,actual,expected);event+=tuple(actual)
   if f['mutation'] and n not in ('vPortFree','r1_protocol_send_hook_call'):
    data=bytearray(u.mem_read(H,8));data[2]=(data[2]+3)&255;data[4]=(data[4]+7)&255;u.mem_write(H,bytes(data));data=bytearray(u.mem_read(M,64));data[1]=(data[1]+1)&255;data[3]=(data[3]+2)&255;data[5]=(data[5]+3)&255;data[6]=(data[6]+4)&255;u.mem_write(M,bytes(data))
   f['trace'].append((event,bytes(u.mem_read(H,8)),bytes(u.mem_read(M,64))))
   u.reg_write(UC_ARM_REG_R0,value);u.reg_write(UC_ARM_REG_R1,0x12345678);u.reg_write(UC_ARM_REG_R2,0x76543210);u.reg_write(UC_ARM_REG_R3,0xdeadbeef);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  for _ in range(2):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,app.read_bytes());u.mem_map(0x1000000,65536);u.mem_write(0x1000000,binary.read_bytes());u.mem_map(0x1100000,4096);u.mem_map(0x20000000,0x40000);machines.append(u);u.hook_add(UC_HOOK_CODE,hook)
  saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
  cases=itertools.chain(((H,(1,0),True,7,0,length,(0,),False,0x12345678) for length in range(65536)),itertools.product((0,H),((0,0),(0,1),(1,0),(0xffffffff,0xffffffff)),(False,True),(0,0x80000007),(0,1,0xffffffff),(0,7,65523,65524,65535,65536,0xffffffff),modes,(False,True),(0xffff,0x12345678)))
  for pointer,gates,malloc,encode,send,length,sequence,mutation,handle in cases:
   expected=2 if not pointer else 5 if not gates[0] and not gates[1] else 3 if not malloc else encode if encode else 4 if send else 0;active=bool(pointer) and bool(gates[0] or gates[1]);allocated=active and malloc;results=[]
   for candidate,u in enumerate(machines):
    states[id(u)]={'auth':gates[0],'peer':gates[1],'malloc':malloc,'encode':encode,'send':send,'length':length,'capacity':(length+12)&65535,'sequence':sequence,'mutation':mutation,'handle':handle,'mode_index':0,'trace':[],'gate_a':0,'gate_b':0,'allocations':0,'encodes':0,'sends':0,'frees':0};u.mem_write(H,bytes.fromhex('a50112347856bcde'));u.mem_write(M,b'\x96'*64);u.mem_write(I,b'\x39'*16)
    for reg,value in [(UC_ARM_REG_R0,handle),(UC_ARM_REG_R1,pointer),(UC_ARM_REG_R2,I),(UC_ARM_REG_R3,length),(UC_ARM_REG_SP,0x2003f000),(UC_ARM_REG_LR,0x20000101)]:u.reg_write(reg,value)
    for i,reg in enumerate(saved):u.reg_write(reg,0x12345600+i)
    u.emu_start((syms['r1_protocol_send_response'] if candidate else 0x828b4)|1,0x20000100,count=5000)
    assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and [u.reg_read(reg) for reg in saved]==[0x12345600+i for i in range(8)]
    f=states[id(u)];assert u.reg_read(UC_ARM_REG_R0)==expected and f['gate_a']==int(bool(pointer)) and f['gate_b']==int(bool(pointer) and not gates[0]) and f['allocations']==int(active) and f['encodes']==f['frees']==int(allocated) and f['sends']==int(allocated and not encode);results.append((f['trace'],bytes(u.mem_read(H,8)),bytes(u.mem_read(M,64))))
   assert results[0]==results[1],(pointer,gates,malloc,encode,send,length,sequence,mutation,handle);comparisons+=1;outcomes[str(expected)]=outcomes.get(str(expected),0)+1
   for event in results[0][0]:counts[event[0][0]]+=1
 vp.write_text(json.dumps(dict(comparisons=comparisons,all_length_halfwords=True,allocation_wrap_bits=16,full_length_forwarded=True,mode_sequences=len(modes),provider_calls_per_side=counts,status_counts=outcomes,source_descriptor_sections=sections,report_sha256=sha(rp),object_sha256=sha(obj),driver_sha256=sha(Path(__file__)),application_sha256=ah,evidence=evidence,application_linked=False,instruction_identity=False,limitations=['Gates/allocator/encoder/send/logger endpoints are fixtures; actual lower composition remains open','Mapped buffers remain accessible for wrapped lengths; real encoder allocation bounds and physical memory safety are not established','Header/packet mutation and unaligned field reloads checked; physical interrupts/concurrency, full startup and original image identity remain gates']),indent=2)+'\n');print('Protocol response:',comparisons,counts,outcomes)
if __name__=='__main__':main()
