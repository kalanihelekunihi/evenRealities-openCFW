from pathlib import Path
import hashlib,itertools,json,subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import UC_CPU_ARM_CORTEX_M4,UC_ARM_REG_SP,UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_PRIMASK
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parent
raw=(ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(raw).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
for lit,val in [(0x530514,0x20074eec),(0x530518,0x20075044),(0x530534,0xfaabd00d),(0x52bab8,0x20075045)]:
    assert int.from_bytes(raw[lit-0x438000:lit-0x438000+4],'little')==val
src=ROOT/'g2/components/main/wsf_buffer_candidates_20261010/buffer_free.c'
cs=ROOT/'g2/components/main/wsf_queue_candidates_20261010/wsf_queue.c'
flags=['--target=arm-none-eabi','-mthumb','-std=c11','-Oz','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror']
for cpu,suffix in [('cortex-m55',''),('cortex-m4','-m4')]:
    objs=[]
    for source,stem in [(src,'buffer_free'),(cs,'wsf_queue')]:
        obj=HERE/(stem+suffix+'.o');subprocess.run(['clang',*flags[:1],'-mcpu='+cpu,*flags[1:],'-c',str(source),'-o',str(obj)],check=True);objs.append(obj)
    elf=HERE/('buffer_free'+suffix+'.elf')
    subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000','-e','g2_smp_candidate_buffer_free',*map(str,objs),'-o',str(elf)],check=True)
with (HERE/'buffer_free-m4.elf').open('rb') as f:
    e=ELFFile(f);segs=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD'];entries={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
base=0x20002000;starts=[0x20003000,0x20003100,0x20003200,0x20003300];blocks=[0x20002f00,starts[0],0x20003080,starts[1],0x20003380]
def run(original,count,block,occupied,nest,mask,adapter=False,message_chain=False):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
    u.mem_map(0x438000,(len(raw)+4095)&~4095);u.mem_write(0x438000,raw)
    u.mem_map(0x100000,0x20000)
    for a,data in segs:u.mem_write(a,bytes(data))
    u.mem_map(0x20000000,0x80000)
    u.mem_write(0x20074eec,base.to_bytes(4,'little'));u.mem_write(0x20075044,bytes([count]));u.mem_write(0x20075045,bytes([nest]))
    for i,s in enumerate(starts):
        free=(0x20004000+i*0x20) if occupied else 0
        row=(0x20+i*0x10).to_bytes(2,'little')+bytes([i+1,0])+s.to_bytes(4,'little')+free.to_bytes(4,'little')
        u.mem_write(base+12*i,row)
    u.mem_write(block,b'\xcc'*8)
    ctx=0x20001000
    u.mem_write(ctx,(entries['g2_wsf_candidate_buffer_free_word']|1).to_bytes(4,'little'))
    # Full relevant before/after domain; includes all candidate target blocks.
    stop=0x110f00;u.reg_write(UC_ARM_REG_SP,0x20010000);u.reg_write(UC_ARM_REG_LR,stop|1);u.reg_write(UC_ARM_REG_PRIMASK,mask)
    if message_chain:
        if original:u.reg_write(UC_ARM_REG_R0,block+8)
        else:u.reg_write(UC_ARM_REG_R0,ctx);u.reg_write(UC_ARM_REG_R1,block+8)
    elif original:u.reg_write(UC_ARM_REG_R0,block)
    elif adapter:u.reg_write(UC_ARM_REG_R0,block)
    else:u.reg_write(UC_ARM_REG_R0,0);u.reg_write(UC_ARM_REG_R1,block)
    u.hook_add(UC_HOOK_CODE,lambda cpu,address,size,_:cpu.emu_stop() if address==stop else None)
    target=(0x4bf9b0 if original else entries['g2_smp_candidate_message_free']) if message_chain else (0x5304d4 if original else entries['g2_wsf_candidate_buffer_free_word' if adapter else 'g2_smp_candidate_buffer_free'])
    u.emu_start(target|1,stop,count=200)
    assert u.reg_read(UC_ARM_REG_PC)==stop and u.reg_read(UC_ARM_REG_SP)==0x20010000
    return {'table':bytes(u.mem_read(base,48)).hex(),'block':bytes(u.mem_read(block,8)).hex(),'nest':bytes(u.mem_read(0x20075045,1)).hex(),'mask':u.reg_read(UC_ARM_REG_PRIMASK)}
count_cases=0
for count,block,occupied,nest,mask in itertools.product([0,1,2,4],blocks,[False,True],[0,1,255],[0,1]):
    a=run(True,count,block,occupied,nest,mask)
    for adapter in (False,True):
        b=run(False,count,block,occupied,nest,mask,adapter)
        assert a==b,(count,hex(block),occupied,nest,mask,adapter,a,b)
        count_cases+=1
    a=run(True,count,block,occupied,nest,mask,message_chain=True)
    b=run(False,count,block,occupied,nest,mask,message_chain=True)
    assert a==b,(count,hex(block),occupied,nest,mask,'message_chain',a,b)
    count_cases+=1
receipt={'status':'PASS','comparisons':count_cases,'original':'0x5304d4..0x530512','source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'cs_source_sha256':hashlib.sha256(cs.read_bytes()).hexdigest(),'raw_sha256':hashlib.sha256(raw).hexdigest(),'limits':['Synthetic pool descriptors and blocks; no initialized stock pool state or allocation history.','Original/source behavioral equivalence includes lower-bound selection and invalid high/low pointers, not memory safety or ownership.','Cortex-M55 compilation and Cortex-M4 Unicorn execution; no byte identity or hardware proof.']}
(HERE/'results.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps({'status':'PASS','comparisons':count_cases}))
