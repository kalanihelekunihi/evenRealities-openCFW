"""Authenticate buffer initialization and enumerate corpus-bound static references."""
from pathlib import Path
import sys,json,hashlib,struct,subprocess
sys.path.insert(0,'/tmp/mspi-enable-python-deps')
from unicorn import *
from unicorn.arm_const import *
from capstone import Cs,CS_ARCH_ARM,CS_MODE_THUMB
from capstone.arm import ARM_OP_MEM,ARM_REG_PC
D=Path(__file__).resolve().parent;R=next(p for p in D.parents if (p/'g2/workflow/target.json').exists());raw=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes();sha=lambda b:hashlib.sha256(b).hexdigest()
assert sha(raw)=='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863';base=0x437fe0;buf=0x20074150
assert sha(raw[0x4b4c8a-base:0x4b4cb2-base])=='db6ec37887401e6aa5d37c1308fccca367048a6306546127f427a3cf75898ec8'
assert struct.unpack_from('<I',raw,0x4b4dc0-base)[0]==buf
ledger=R/'g2/research/corpus/apollo-main/ghidra/open-2026-09-29/functions-000.jsonl';funcs=[json.loads(s) for s in ledger.read_text().splitlines()]
md=Cs(CS_ARCH_ARM,CS_MODE_THUMB);md.detail=True
literal_matches=[]
for off in range(0,len(raw)-3,2):
    v=struct.unpack_from('<I',raw,off)[0]
    if buf-64<=v<buf+64:literal_matches.append({'address':hex(base+off),'value':hex(v)})
refs=[];exact=0;decoded=0;movt=[]
for f in funcs:
    for a,b in f['ranges']:
        lo,hi=int(a,16),int(b,16)+1
        if lo<base or hi>base+len(raw):continue
        for i in md.disasm(raw[lo-base:hi-base],lo):
            decoded+=1
            if i.mnemonic in ['movw','movt'] and ('#0x4150' in i.op_str or '#0x2007' in i.op_str):movt.append({'function':f['entry'],'address':hex(i.address),'instruction':i.mnemonic+' '+i.op_str})
            if i.mnemonic.startswith('ldr'):
                for op in i.operands:
                    if op.type==ARM_OP_MEM and op.mem.base==ARM_REG_PC:
                        literal=((i.address+4)&~3)+op.mem.disp
                        if base<=literal<=base+len(raw)-4:
                            v=struct.unpack_from('<I',raw,literal-base)[0]
                            if buf-64<=v<buf+64:refs.append({'function':f['entry'],'name':f['name'],'site':hex(i.address),'literal':hex(literal),'value':hex(v),'instruction':i.mnemonic+' '+i.op_str})
elf=D.parent/'main-analysis-only.elf'
for a,b,name in [(0x4b4c8a,0x4b4cb2,'command'),(0x52b84c,0x52b87a,'vendor-copy'),(0x5fa01e,0x5fa054,'zero-initializer'),(0x4b4c00,0x4b4dc4,'nearby-owners'),(0x597c6c,0x597cde,'indexed-neighbor-bound'),(0x456280,0x4562da,'heap-neighbor')]:
    (D/(name+'-gnu.txt')).write_text(subprocess.check_output(['/opt/homebrew/bin/arm-none-eabi-objdump','-D','-M','force-thumb',f'--start-address={a}',f'--stop-address={b}',str(elf)],text=True))
u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x438000,0x360000);u.mem_write(0x438000,raw[32:]);u.mem_map(0x20000000,0x100000);u.mem_map(0x100000,0x1000);u.mem_write(0x20004558,b'\xa5'*0x70af0);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_R0,0x75d3cc)
phase='zero';stopped=[];writes=[];args=[]
def hook(uc,pc,size,user):
    if phase=='zero' and pc==0x5fa024 and uc.reg_read(UC_ARM_REG_R0)==0x75d3d8:stopped.append('before-next-scatter-row');uc.emu_stop()
    if phase=='command' and pc==0x52b84c:args.append([uc.reg_read(r) for r in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2]]);uc.emu_stop()
    if phase=='copy' and pc==0x100000:uc.emu_stop()
def write(uc,access,a,size,value,user):
    if a<buf+8 and a+size>buf:writes.append({'phase':phase,'pc':hex(uc.reg_read(UC_ARM_REG_PC)),'address':hex(a),'size':size,'value':hex(value)})
u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_MEM_WRITE,write);u.emu_start(0x5fa01f,0,count=1000000)
assert stopped and bytes(u.mem_read(0x20004558,0x70af0))==bytes(0x70af0)
zero=bytes(u.mem_read(buf,8));phase='command';u.reg_write(UC_ARM_REG_SP,0x200ff000);u.emu_start(0x4b4c8b,0,count=100)
assert args==[[0xfff2,8,buf]];initialized=bytes(u.mem_read(buf,8));assert initialized==bytes.fromhex('ff7c010fb8190000')
# Independent arbitrary-state counterexample proves command does not itself own tail.
u.mem_write(buf+6,bytes.fromhex('a55a'));u.reg_write(UC_ARM_REG_SP,0x200ff000);u.emu_start(0x4b4c8b,0,count=100)
counterexample=bytes(u.mem_read(buf,8));assert counterexample==bytes.fromhex('ff7c010fb819a55a')
copy_record=next(f for f in funcs if f['entry']=='00439be4');copy_bytes=raw[0x439be4-base:0x439c8a-base];assert sha(copy_bytes)==copy_record['body_sha256']
phase='copy';copies=[]
for payload in [initialized,counterexample]:
    u.mem_write(buf,payload);u.mem_write(0x20090000,b'\xa5'*16)
    for r,v in [(UC_ARM_REG_R0,0x20090003),(UC_ARM_REG_R1,buf),(UC_ARM_REG_R2,8),(UC_ARM_REG_SP,0x200ff000),(UC_ARM_REG_LR,0x100001)]:u.reg_write(r,v)
    u.emu_start(0x439be5,0,count=200)
    copied=bytes(u.mem_read(0x20090003,8));assert copied==payload and bytes(u.mem_read(buf,8))==payload
    assert bytes(u.mem_read(0x20090000,3))==b'\xa5'*3 and bytes(u.mem_read(0x2009000b,5))==b'\xa5'*5
    copies.append(copied.hex())
(D/'results.json').write_text(json.dumps({'stock_sha256':sha(raw),'ledger_sha256':sha(ledger.read_bytes()),'function_count':len(funcs),'decoded_instruction_count':decoded,'pointer_literal_scan_stride':2,'nearby_pointer_literals':literal_matches,'corpus_pc_relative_refs':refs,'candidate_movw_movt':movt,'zero_initialized_buffer':zero.hex(),'command_arguments':args,'initialized_payload':initialized.hex(),'arbitrary_tail_counterexample':counterexample.hex(),'original_memcpy_outputs':copies,'buffer_writes':writes,'unicorn_version':__import__('unicorn').__version__,'limits':'Known corpus Thumb ranges and two-byte-aligned static pointer literals; indirect/calculated pointers, unknown executable spans, ROM and DMA writers not exhaustively excluded. Zero record, command prefix and authenticated memcpy executed; vendor allocation/send not executed.'},indent=2)+'\n')
print(json.dumps({'nearby_literals':literal_matches,'pc_relative_refs':refs,'initialized':initialized.hex(),'counterexample':counterexample.hex()},indent=2))
