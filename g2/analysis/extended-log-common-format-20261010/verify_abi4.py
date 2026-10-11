from pathlib import Path
import hashlib, itertools, json, subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *

ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parent
raw=(ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(raw).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
assert raw[0x709f64-0x438000:0x709f64-0x438000+65].startswith(b'_log get all buffer: read=%u, write=%u, capacity=%u, length=%u\0')
assert raw[0x72d3e8-0x438000:0x72d3e8-0x438000+58].startswith(b'Image data[%d]=0x%08X, length=%d, address=0x%08X\0')
names=['extended_log_smp_onebit_candidates_20261010/onebit.c','extended_log_postformat_candidates_20261010/postformat.c','extended_log_append_candidates_20261010/append.c','extended_log_common_format_candidates_20261010/common_format.c','extended_log_memory_candidates_20261010/memory.c','extended_log_time_candidates_20261010/time.c','extended_log_token_candidates_20261010/token.c','extended_log_module_policy_candidates_20261010/module_policy.c','smp_provider_candidates_20261010/compare.c','extended_log_smp_abi_candidates_20261010/abi.c']
paths=[ROOT/'g2/components/main'/n for n in names]
for cpu,suffix in [('cortex-m55',''),('cortex-m4','-m4')]:
    objs=[]
    for path in paths:
        obj=HERE/(path.parent.name+'-abi4'+suffix+'.o');objs.append(obj)
        subprocess.run(['clang','--target=arm-none-eabi','-mcpu='+cpu,'-mthumb','-std=c11','-Oz','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c',str(path),'-o',str(obj)],check=True)
    subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000','-e','g2_log_candidate_four_word_stock_abi',*map(str,objs),'-o',str(HERE/('abi4'+suffix+'.elf'))],check=True)
with (HERE/'abi4-m4.elf').open('rb') as f:
    elf=ELFFile(f);segs=[(s['p_vaddr'],s.data()) for s in elf.iter_segments() if s['p_type']=='PT_LOAD']
    symbols={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
STATE=0x20070be8;BUF=0x2006bd30;CTX=0x20001000;STOP=0x110f00;SP=0x20010000
def run(original,fmt,adapter,line,level,arguments,enabled,limit):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
    u.mem_map(0x438000,(len(raw)+4095)&~4095);u.mem_write(0x438000,raw)
    u.mem_map(0x100000,0x20000)
    for a,data in segs:u.mem_write(a,bytes(data))
    u.mem_map(0x20000000,0x80000)
    u.mem_write(STATE,bytes([limit]));u.mem_write(STATE+241,bytes([enabled]))
    u.mem_write(BUF,b'Z'*1040)
    providers=[symbols['g2_log_candidate_common_format'],symbols['g2_log_candidate_find_token'],0x110d20,0x110d40,0x110d60,0x110d80,0x110da0,0x110dc0]
    u.mem_write(CTX,b''.join((v|1).to_bytes(4,'little') for v in providers))
    u.mem_write(symbols['bound_providers']&~1,CTX.to_bytes(4,'little'))
    u.mem_write(SP,b''.join(x.to_bytes(4,'little') for x in (line,fmt,*arguments)))
    for reg,val in [(UC_ARM_REG_R0,level),(UC_ARM_REG_R1,0x78d1ec),(UC_ARM_REG_R2,0x6e2b18),(UC_ARM_REG_R3,0x77e988)]:u.reg_write(reg,val)
    u.reg_write(UC_ARM_REG_SP,SP);u.reg_write(UC_ARM_REG_LR,STOP|1)
    events=[]
    callbacks={0x43d416:'lock',0x43d438:'unlock',0x44aa80:'output',0x110d60:'lock',0x110d40:'unlock',0x110d20:'output'}
    def hook(cpu,addr,size,_):
        name=callbacks.get(addr)
        if not name:return
        events.append((name,cpu.reg_read(UC_ARM_REG_R0),cpu.reg_read(UC_ARM_REG_R1),cpu.reg_read(UC_ARM_REG_R2)) if name=='output' else (name,))
        cpu.reg_write(UC_ARM_REG_PC,cpu.reg_read(UC_ARM_REG_LR))
    u.hook_add(UC_HOOK_CODE,hook)
    entry=0x43d574 if original else symbols[adapter]
    u.emu_start(entry|1,STOP,count=50000)
    assert u.reg_read(UC_ARM_REG_PC)==STOP and u.reg_read(UC_ARM_REG_SP)==SP
    return events,bytes(u.mem_read(BUF,1040))
count=0
four=[(0,0,0,0),(1,2,3,4),(0xffffffff,0x80000000,1000,42),(123456789,10,4096,0)]
one=[(0,),(1,),(0x41,),(0xffffffff,)]
three=[(0,0,0),(1,0,500),(0xffffffff,0xffffffff,500),(0,0x80000000,1)]
cases=[(0x709f64,'g2_log_candidate_four_word_stock_abi',122,four,'0x43c922'),
       (0x72d3e8,'g2_log_candidate_four_word_stock_abi',319,four,'0x52fa9c'),
       (0x783550,'g2_log_candidate_one_word_stock_abi',365,one,'0x4afa4e'),
       (0x718b44,'g2_log_candidate_one_word_stock_abi',261,one,'0x4d6626'),
       (0x7258e8,'g2_log_candidate_three_word_stock_abi',1185,three,'0x4f624c')]
for fmt,adapter,line,vectors,caller in cases:
    for level,args,enabled,limit in itertools.product(range(6),vectors,[0,1],[0,3,5]):
        a=run(True,fmt,adapter,line,level,args,enabled,limit)
        b=run(False,fmt,adapter,line,level,args,enabled,limit)
        assert a==b,(hex(fmt),level,args,enabled,limit,a[0],b[0],a[1][:160],b[1][:160])
        count+=1
receipt={'status':'PASS','comparisons':count,'formats':[hex(c[0]) for c in cases],'callers':[c[4] for c in cases],'source_sha256':hashlib.sha256(paths[3].read_bytes()).hexdigest(),'abi_source_sha256':hashlib.sha256(paths[-1].read_bytes()).hexdigest(),'image_sha256':hashlib.sha256(raw).hexdigest(),'limit':'Five exact 1-, 3-, or 4-word caller ABIs and synthetic quiet logger state; no general varargs claim'}
(HERE/'abi4_results.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps({'status':'PASS','comparisons':count}))
