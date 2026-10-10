from pathlib import Path
import ctypes as C,struct,json,hashlib,sys
sys.path.insert(0,'/tmp/mspi-enable-python-deps')
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
D=Path(__file__).resolve().parent;R=next(p for p in D.parents if (p/'g2/blobs').exists())
raw=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()
sha=lambda b:hashlib.sha256(b).hexdigest()
assert sha(raw)=='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863'
assert sha(raw[0x537d0c-0x437fe0:0x537e9e-0x437fe0])=='c6c182f8937a91efc42995289820d0589b5ae839960cde0d83aec3f40ba0dbba'
vals=[struct.unpack_from('<I',raw,a-0x437fe0)[0] for a in [0x537ea0,0x537eb0,0x537eac,0x537ee0,0x537ee4,0x537ee8]]
class Literals(C.Structure):_fields_=[(x,C.c_uint32) for x in ['category','comparison3','source','format','file','aes_queue']]
# Explicit callback signatures mirror only observed argument use, not guesses
# about full providers' inferred prototypes.
u=C.c_uint32;v=C.c_void_p;b=C.c_uint8
signatures=[('database',None,[]),('buffer_free',None,[u]),('lookup',v,[b]),('state',None,[v,v]),('gate',u,[u]),('compare',u,[u,u,u]),('flags',u,[]),('extended',None,[u]*8),('fallback',None,[u]*4),('dequeue',u,[u,v]),('free',None,[u])]
types={k:C.CFUNCTYPE(ret,v,*args) for k,ret,args in signatures}
class Providers(C.Structure):_fields_=[('context',v)]+[(k,types[k]) for k,ret,args in signatures]
lib=C.CDLL(str(D/'candidate.dylib'));lib.g2_candidate_smp_handler.argtypes=[b,v,C.POINTER(Literals),C.POINTER(Providers)]
M=0x20081000;CCB=0x20080000;SP=0x200ff000
cases=[]
for event in [0,11,28,32,255]:
 for conn in [0,1]:
  for plain in ([0,0x20083000] if event==28 else [0]):
   cases.append(dict(name=f'event-{event}-conn-{conn}-plain-{plain}',event=event,conn=conn,plain=plain,token=7,status=7,gates=[0]*5,compares=[1]*4,flags=0,nodes=0,null=False))
for level in range(1,6):
 for flags in [0,2,0x80000002]:
  for nodes in [0,3]:
   gates=[0]*5;gates[level-1]=1
   cases.append(dict(name=f'log-{level}-flags-{flags}-nodes-{nodes}',event=11,conn=1,plain=0,token=7,status=6,gates=gates,compares=[0]*4,flags=flags,nodes=nodes,null=False))
for finalcmp in [0,1]:
 cases.append(dict(name=f'all-compare-fail-final-{finalcmp}',event=11,conn=1,plain=0,token=255,status=0,gates=[1,1,1,0,1],compares=[3,5,7,finalcmp],flags=0,nodes=2,null=False))
cases.append(dict(name='null-message-event-255',event=255,conn=1,plain=0,token=7,status=6,gates=[],compares=[],flags=0,nodes=0,null=True))
results=[];seen_sites=set();seen_instructions=set()
for case in cases:
 msg=bytearray(struct.pack('<HBB',0xab01,case['event'],case['status'])+bytes(12));struct.pack_into('<I',msg,8,case['plain'])
 ccb=bytearray(80);ccb[61]=case['conn'];ccb[65]=case['token']
 def scenario(native):
  transcript=[];gi=ci=di=0;uarm=None
  cbuf=(C.c_uint8*80).from_buffer_copy(ccb);mbuf=(C.c_uint8*16).from_buffer_copy(msg)
  def invoke(kind,args):
   nonlocal gi,ci,di
   if kind=='lookup':transcript.append([kind,*args]);return C.addressof(cbuf) if native else CCB
   if kind=='state':transcript.append([kind]);return
   if kind=='database':transcript.append([kind]);return
   if kind=='dequeue':
    address,out=args
    old=C.c_uint8.from_address(out).value if native else bytes(uarm.mem_read(out,1))[0]
    transcript.append([kind,address,old]);res=0 if di==case['nodes'] else 0x20082008+64*di
    if res:
     if native:C.c_uint8.from_address(out).value=di+1
     else:uarm.mem_write(out,bytes([di+1]))
     di+=1
    return res
   transcript.append([kind,*args])
   if kind=='gate':res=case['gates'][gi];gi+=1;return res
   if kind=='compare':res=case['compares'][ci];ci+=1;return res
   if kind=='flags':return case['flags']
  if native:
   callbacks=[types[k](lambda ctx,*args,k=k:invoke(k,list(args))) for k,ret,args in signatures]
   providers=Providers(None,*callbacks);lit=Literals(*vals)
   lib.g2_candidate_smp_handler(255,None if case['null'] else C.addressof(mbuf),C.byref(lit),C.byref(providers))
  else:
   uarm=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);uarm.mem_map(0x438000,0x360000);uarm.mem_write(0x438000,raw[32:]);uarm.mem_map(0x20000000,0x100000);uarm.mem_map(0x100000,0x1000)
   uarm.mem_write(M,bytes(msg));uarm.mem_write(CCB,bytes(ccb))
   saved={r:0xabc000+k for k,r in enumerate([UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7])}
   for r,val in saved.items():uarm.reg_write(r,val)
   for r,val in [(UC_ARM_REG_R0,255),(UC_ARM_REG_R1,0 if case['null'] else M),(UC_ARM_REG_SP,SP),(UC_ARM_REG_LR,0x100001)]:uarm.reg_write(r,val)
   addresses={0x542960:('database',0),0x5304d4:('buffer_free',1),0x5375fc:('lookup',1),0x56ee62:('state',2),0x4c9c50:('gate',1),0x44b610:('compare',3),0x43d0ce:('flags',0),0x43d574:('extended',8),0x52a63c:('fallback',4),0x4bf9ec:('dequeue',2),0x4bf9b0:('free',1)}
   def hook(uc,a,size,user):
    if a==0x100000:uc.emu_stop();return
    if 0x537d0c<=a<0x537e9e:
     seen_instructions.add(a);return
    assert a in addresses,hex(a)
    seen_sites.add((uc.reg_read(UC_ARM_REG_LR)&~1)-4)
    k,n=addresses[a];args=[uc.reg_read(r) for r in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]][:n]
    if n>4:args+=list(struct.unpack('<4I',bytes(uc.mem_read(uc.reg_read(UC_ARM_REG_SP),16))))
    result=invoke(k,args)
    if result is not None:uc.reg_write(UC_ARM_REG_R0,result)
    uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   uarm.hook_add(UC_HOOK_CODE,hook);uarm.emu_start(0x537d0d,0,count=3000)
   assert uarm.reg_read(UC_ARM_REG_PC)==0x100000 and uarm.reg_read(UC_ARM_REG_SP)==SP
   assert all(uarm.reg_read(r)==val for r,val in saved.items())
   assert bytes(uarm.mem_read(M,16))==msg and bytes(uarm.mem_read(CCB,80))==ccb
  return transcript
 original=scenario(False);native=scenario(True);assert original==native,(case,original,native)
 results.append(dict(case=case,transcript=original,agreement=True,stock_abi_preserved=True))
assert len(seen_sites)==24
assert len(seen_instructions)==161
obj=(D/'candidate.o').read_bytes();header=struct.unpack_from('<16sHHIIIIIHHHHHH',obj)
secs=[struct.unpack_from('<IIIIIIIIII',obj,header[6]+i*header[11]) for i in range(header[12])]
names=secs[header[13]];strings=obj[names[4]:names[4]+names[5]]
textsec=next(s for s in secs if strings[s[0]:].split(b'\0')[0]==b'.text')
text=obj[textsec[4]:textsec[4]+textsec[5]]
arm_object=dict(sha256=sha(obj),text_bytes=len(text),text_sha256=sha(text),stock_body_bytes=402,byte_identical=False,reason='Explicit callback context and source decomposition change ABI/codegen; no linked fixed-address production image')
(D/'results.json').write_text(json.dumps(dict(count=len(results),cases=results,literals=vals,call_sites=[hex(x) for x in sorted(seen_sites)],executed_instruction_count=len(seen_instructions),main_sha256=sha(raw),arm_object=arm_object,scope='Original 402-byte handler versus native compiled C; all external providers replaced by identical scripted callbacks'),indent=2)+'\n')
print('PASS',len(results),'original-byte/native-C fixtures')
