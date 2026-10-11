from pathlib import Path
import hashlib,itertools,json,subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import UC_CPU_ARM_CORTEX_M4,UC_ARM_REG_SP,UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_PRIMASK
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parent
raw=(ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(raw).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
assert int.from_bytes(raw[0x52bab8-0x438000:0x52babc-0x438000],'little')==0x20075045
src=ROOT/'g2/components/main/wsf_queue_candidates_20261010/wsf_queue.c'
obj=HERE/'wsf_queue.o';elf=HERE/'wsf_queue.elf'
cmd=['clang','--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb','-std=c11','-Oz','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c',str(src),'-o',str(obj)]
subprocess.run(cmd,check=True);subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000','-e','g2_smp_candidate_message_dequeue',str(obj),'-o',str(elf)],check=True)
m4obj=HERE/'wsf_queue-m4.o';m4elf=HERE/'wsf_queue-m4.elf';cmd4=cmd.copy();cmd4[2]='-mcpu=cortex-m4';cmd4[-1]=str(m4obj)
subprocess.run(cmd4,check=True);subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000','-e','g2_smp_candidate_message_dequeue',str(m4obj),'-o',str(m4elf)],check=True)
with m4elf.open('rb') as f:
    e=ELFFile(f);segs=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
orig={'g2_wsf_candidate_cs_enter':0x52b8a4,'g2_wsf_candidate_cs_exit':0x52b8b6,'g2_wsf_candidate_queue_deq':0x538c4a,'g2_smp_candidate_message_dequeue':0x4bf9ec,'g2_smp_candidate_message_free':0x4bf9b0}
def case(name,original,chain,nest,primask):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
    u.mem_map(0x438000,(len(raw)+4095)&~4095);u.mem_write(0x438000,raw)
    u.mem_map(0x100000,0x20000)
    for a,data in segs:u.mem_write(a,bytes(data))
    u.mem_map(0x20000000,0x80000)
    q=0x20001000;h=0x20001100;id_addr=0x20001080;ctx=0x20001090
    nodes=[0x20001100+i*0x40 for i in range(chain)]
    u.mem_write(q,(nodes[0] if nodes else 0).to_bytes(4,'little')+(nodes[-1] if nodes else 0).to_bytes(4,'little'))
    for i,a in enumerate(nodes):u.mem_write(a,(nodes[i+1] if i+1<len(nodes) else 0).to_bytes(4,'little')+bytes([7+i,0,0,0])+bytes([0x80+i])*8)
    u.mem_write(id_addr,b'\xa5');u.mem_write(0x20075045,bytes([nest]));u.mem_write(ctx,(0x110e01).to_bytes(4,'little'))
    # The terminal allocator is deliberately observed, not reconstructed.
    free_args=[];stop=0x110f00
    u.reg_write(UC_ARM_REG_SP,0x20010000);u.reg_write(UC_ARM_REG_LR,stop|1);u.reg_write(UC_ARM_REG_PRIMASK,primask)
    if name=='g2_smp_candidate_message_dequeue':args=([q,id_addr] if original else [0,q,id_addr])
    elif name=='g2_smp_candidate_message_free':args=([h+8] if original else [ctx,h+8])
    elif name=='g2_wsf_candidate_queue_deq':args=[q]
    else:args=[]
    for reg,val in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2],args):u.reg_write(reg,val)
    def hook(cpu,address,size,_):
        if address==stop:cpu.emu_stop()
        elif address in (0x5304d4,0x110e00):
            free_args.append(cpu.reg_read(UC_ARM_REG_R0));cpu.reg_write(UC_ARM_REG_PC,cpu.reg_read(UC_ARM_REG_LR))
    u.hook_add(UC_HOOK_CODE,hook)
    u.emu_start((orig[name] if original else sym[name])|1,stop,count=100)
    assert u.reg_read(UC_ARM_REG_PC)==stop,(name,original,hex(u.reg_read(UC_ARM_REG_PC)))
    assert u.reg_read(UC_ARM_REG_SP)==0x20010000
    return {'ret':u.reg_read(UC_ARM_REG_R0) if name not in ('g2_wsf_candidate_cs_enter','g2_wsf_candidate_cs_exit','g2_smp_candidate_message_free') else None,'queue':bytes(u.mem_read(q,8)).hex(),'id':bytes(u.mem_read(id_addr,1)).hex(),'nest':bytes(u.mem_read(0x20075045,1)).hex(),'mask':u.reg_read(UC_ARM_REG_PRIMASK),'free':free_args,'nodes':[bytes(u.mem_read(a,16)).hex() for a in nodes]}
count=0
for name in orig:
    for chain,nest,mask in itertools.product([0,1,2,3],[0,1,2,255],[0,1]):
        a=case(name,True,chain,nest,mask);b=case(name,False,chain,nest,mask)
        assert a==b,(name,chain,nest,mask,a,b)
        count+=1
receipt={'status':'PASS','comparisons':count,'function_entries':{k:hex(v) for k,v in orig.items()},'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'raw_sha256':hashlib.sha256(raw).hexdigest(),'compile_command':cmd,'limits':['Lowest WsfBufFree allocator call intercepted at provider boundary on both sides.','Synthetic queue/hidden headers and nesting; no physical interrupt or concurrent execution.','Cortex-M55 compilation and Cortex-M4 Unicorn comparison; no byte identity.']}
(HERE/'results.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps({'status':'PASS','comparisons':count}))
