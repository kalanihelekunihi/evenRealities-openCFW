from pathlib import Path
import hashlib,itertools,json,subprocess,sys
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parent
raw=(ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(raw).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
dirs=['extended_log_smp_onebit_candidates_20261010/onebit.c','extended_log_postformat_candidates_20261010/postformat.c','extended_log_append_candidates_20261010/append.c','extended_log_smp_format_candidates_20261010/smp_format.c','extended_log_memory_candidates_20261010/memory.c','extended_log_time_candidates_20261010/time.c','extended_log_token_candidates_20261010/token.c','extended_log_module_policy_candidates_20261010/module_policy.c','smp_provider_candidates_20261010/compare.c','extended_log_smp_abi_candidates_20261010/abi.c']
paths=[ROOT/'g2/components/main'/x for x in dirs]
base=['clang','--target=arm-none-eabi','-mthumb','-std=c11','-Oz','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror']
for cpu,suffix in [('cortex-m55',''),('cortex-m4','-m4')]:
    objs=[]
    for path in paths:
        obj=HERE/(path.parent.name+suffix+'.o');objs.append(obj)
        subprocess.run(base[:2]+['-mcpu='+cpu]+base[2:]+['-c',str(path),'-o',str(obj)],check=True)
    subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000','-e','g2_log_candidate_smp_onebit',*map(str,objs),'-o',str(HERE/('onebit'+suffix+'.elf'))],check=True)
with (HERE/'onebit-m4.elf').open('rb') as f:
    elf=ELFFile(f);segs=[(s['p_vaddr'],s.data()) for s in elf.iter_segments() if s['p_type']=='PT_LOAD'];symbols={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
STATE=0x20070be8;BUF=0x2006bd30;CTX=0x20001000;STOP=0x110f00;SP=0x20010000;ARGS=0x20004000
def run(original,bit,color,token,level=1,fmt=0x77bf14,policy_kind=0,module_filter=0):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
    u.mem_map(0x438000,(len(raw)+4095)&~4095);u.mem_write(0x438000,raw)
    u.mem_map(0x100000,0x20000)
    for x,data in segs:u.mem_write(x,bytes(data))
    u.mem_map(0x20000000,0x80000)
    u.mem_write(STATE,bytes([5]));u.mem_write(STATE+241,b'\1');u.mem_write(STATE+245,bytes([color]))
    if module_filter:u.mem_write(STATE+1,(b'SMP' if module_filter==1 else b'NOPE')+b'\0')
    if policy_kind:
        u.mem_write(STATE+240,b'\1')
        u.mem_write(STATE+49+33*2,bytes([0 if policy_kind==1 else 3]))
        u.mem_write(STATE+50+33*2,(b'BAD' if policy_kind==3 else b'SMP')+b'\0')
        u.mem_write(STATE+81+33*2,b'\1')
    u.mem_write(STATE+216+4*level,bit.to_bytes(4,'little'))
    if token:u.mem_write(STATE+32,(b'evt=' if token==1 else b'NOPE')+b'\0')
    u.mem_write(BUF,b'Z'*1040)
    for addr,s in [(0x20003000,b'event'),(0x20003100,b'state'),(0x20003200,b'DATE'),(0x20003300,b'TIME'),(0x20003400,b'TICK'),(0x20003500,b'LEVEL'),(0x20003600,b'COLOR')]:u.mem_write(addr,s+b'\0')
    for i in range(6):u.mem_write(0x20000974+4*i,(0x20003500).to_bytes(4,'little'))
    for i in range(8):u.mem_write(0x2000098c+4*i,(0x20003600).to_bytes(4,'little'))
    arg0,arg1=(0x20003000,0x20003100) if fmt==0x77bf14 else (17,4)
    line=852 if fmt==0x77bf14 else 855
    u.mem_write(ARGS,arg0.to_bytes(4,'little')+arg1.to_bytes(4,'little'))
    provider=[symbols['g2_log_candidate_smp_format'],symbols['g2_log_candidate_find_token'],0x110d20,0x110d40,0x110d60,0x110d80,0x110da0,0x110dc0]
    u.mem_write(CTX,b''.join((v|1).to_bytes(4,'little') for v in provider))
    if '--abi' in sys.argv:u.mem_write(symbols['bound_providers']&~1,CTX.to_bytes(4,'little'))
    u.reg_write(UC_ARM_REG_SP,SP);u.reg_write(UC_ARM_REG_LR,STOP|1)
    if original or '--abi' in sys.argv:
        u.mem_write(SP,line.to_bytes(4,'little')+fmt.to_bytes(4,'little')+arg0.to_bytes(4,'little')+arg1.to_bytes(4,'little'))
        for reg,val in [(UC_ARM_REG_R0,level),(UC_ARM_REG_R1,0x56f148),(UC_ARM_REG_R2,0x6e1994),(UC_ARM_REG_R3,0x789060)]:u.reg_write(reg,val)
    else:
        u.mem_write(SP,(0x789060).to_bytes(4,'little')+line.to_bytes(4,'little')+fmt.to_bytes(4,'little')+ARGS.to_bytes(4,'little'))
        for reg,val in [(UC_ARM_REG_R0,CTX),(UC_ARM_REG_R1,level),(UC_ARM_REG_R2,0x56f148),(UC_ARM_REG_R3,0x6e1994)]:u.reg_write(reg,val)
    events=[]
    names={0x43d416:'lock',0x43d438:'unlock',0x44aa80:'output',0x44aaa8:'date',0x44ab14:'time',0x44ab1c:'tick',0x110d60:'lock',0x110d40:'unlock',0x110d20:'output',0x110d80:'date',0x110da0:'time',0x110dc0:'tick'}
    def hook(cpu,addr,size,_):
        name=names.get(addr)
        if name is None:return
        if name=='output':events.append((name,cpu.reg_read(UC_ARM_REG_R0),cpu.reg_read(UC_ARM_REG_R1),cpu.reg_read(UC_ARM_REG_R2)))
        else:events.append((name,))
        if name in ('date','time','tick'):cpu.reg_write(UC_ARM_REG_R0,{'date':0x20003200,'time':0x20003300,'tick':0x20003400}[name])
        cpu.reg_write(UC_ARM_REG_PC,cpu.reg_read(UC_ARM_REG_LR))
    u.hook_add(UC_HOOK_CODE,hook)
    try:u.emu_start((0x43d574 if original else symbols['g2_log_candidate_smp_stock_abi'] if '--abi' in sys.argv else symbols['g2_log_candidate_smp_onebit'])|1,STOP,count=50000)
    except Exception as exc:raise RuntimeError((original,bit,color,token,level,hex(fmt),policy_kind,module_filter,hex(u.reg_read(UC_ARM_REG_PC)),events)) from exc
    assert u.reg_read(UC_ARM_REG_PC)==STOP and u.reg_read(UC_ARM_REG_SP)==SP,(original,bit,color,token,level,hex(fmt),hex(u.reg_read(UC_ARM_REG_PC)),hex(u.reg_read(UC_ARM_REG_SP)),events)
    return events,bytes(u.mem_read(BUF,1040))
count=0;shapes=set()
masks=range(256) if '--all-masks' in sys.argv else ([0,255] if '--policy' in sys.argv else [0,1,2,3,7,31,63,127,255] if '--levels' in sys.argv else [0,1,2,4,8,16,32,64,128])
levels=[1,3,5] if '--policy' in sys.argv else range(6) if '--levels' in sys.argv else [1]
formats=[0x77bf14,0x765710] if '--levels' in sys.argv or '--policy' in sys.argv else [0x77bf14]
tokens=[0,2] if '--policy' in sys.argv else [0,1,2]
policies=range(4) if '--policy' in sys.argv else [0]
module_filters=range(3) if '--policy' in sys.argv else [0]
for bit,color,token,level,fmt,policy_kind,module_filter in itertools.product(masks,[0,1],tokens,levels,formats,policies,module_filters):
    a=run(True,bit,color,token,level,fmt,policy_kind,module_filter);b=run(False,bit,color,token,level,fmt,policy_kind,module_filter)
    assert a==b,(bit,color,token,level,hex(fmt),policy_kind,module_filter,a[0],b[0],a[1][:160],b[1][:160])
    shapes.add(tuple(e[0] for e in a[0]));count+=1
receipt={'status':'PASS','comparisons':count,'call_shapes':len(shapes),'source_sha256':hashlib.sha256(paths[0].read_bytes()).hexdigest(),'abi_source_sha256':hashlib.sha256(paths[-1].read_bytes()).hexdigest(),'raw_sha256':hashlib.sha256(raw).hexdigest(),'domain':('stock eight-argument ABI with all 256 category masks' if '--abi' in sys.argv and '--all-masks' in sys.argv else 'stock eight-argument ABI with selected policy matrix' if '--abi' in sys.argv else 'policy and module-filter matrix' if '--policy' in sys.argv else 'all 256 category masks' if '--all-masks' in sys.argv else 'selected combined masks across six levels and both SMP literals' if '--levels' in sys.argv else 'one category bit or zero')+', synthetic RAM color/policy tables','limits':['Level-six fatal/recursion and general formatter outside this adapter.','Initialized production logger state not established.']}
(HERE/('abi_policy_results.json' if '--abi' in sys.argv and '--policy' in sys.argv else 'abi_all_masks_results.json' if '--abi' in sys.argv and '--all-masks' in sys.argv else 'abi_results.json' if '--abi' in sys.argv else 'policy_results.json' if '--policy' in sys.argv else 'all_masks_results.json' if '--all-masks' in sys.argv else 'levels_results.json' if '--levels' in sys.argv else 'onebit_results.json')).write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps({'status':'PASS','comparisons':count,'call_shapes':len(shapes)}))
