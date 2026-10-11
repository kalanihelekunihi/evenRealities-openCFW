from pathlib import Path
import ctypes as C,hashlib,itertools,json,subprocess
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import UC_CPU_ARM_CORTEX_M4,UC_ARM_REG_SP,UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parent
raw=(ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(raw).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
source=ROOT/'g2/components/main/smp_ccb_candidates_20261010/ccb_lookup.c'
arm=HERE/'ccb_lookup.o';native=HERE/'ccb_lookup.dylib'
cmd=['clang','--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb','-std=c11','-Oz','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c',str(source),'-o',str(arm)]
subprocess.run(cmd,check=True)
subprocess.run(['clang','-dynamiclib','-std=c11','-O1','-Wall','-Wextra','-Werror',str(source),'-o',str(native)],check=True)
lib=C.CDLL(str(native))
GATE=C.CFUNCTYPE(C.c_uint32,C.c_uint32);COMPARE=C.CFUNCTYPE(C.c_uint32,C.c_uint32,C.c_uint32,C.c_uint32);FLAGS=C.CFUNCTYPE(C.c_uint32);EXT=C.CFUNCTYPE(None,*([C.c_uint32]*7));TRACE=C.CFUNCTYPE(None,*([C.c_uint32]*3))
class Provider(C.Structure):
    _fields_=[(x,C.c_uint32) for x in ['ccb_base','category','category_alt','source','function','file','err_text','smp_text','hci_text']]+[('log_gate',GATE),('compare',COMPARE),('log_flags',FLAGS),('log_extended',EXT),('trace',TRACE)]
lib.g2_smp_candidate_ccb_by_id.argtypes=[C.c_void_p,C.c_uint8];lib.g2_smp_candidate_ccb_by_id.restype=C.c_uint32
literal_slots={'ccb_base':0x537ebc,'category':0x537ea0,'category_alt':0x537eb0,'source':0x537eac,'function':0x537ec4,'file':0x537ec8}
lits={k:int.from_bytes(raw[a-0x438000:a-0x438000+4],'little') for k,a in literal_slots.items()}
lits.update(err_text=0x537864,smp_text=0x537868,hci_text=0x5379f0)
assert lits['ccb_base']==0x20070aec
# Event signatures are normalized to provider name plus R0-R3, and the three
# stack arguments for extended logging. Each provider returns scripted data.
def native_run(conn,gates,compares,flags):
    events=[];gi=ci=0
    def gate(carry):
        nonlocal gi
        events.append(('gate',carry));v=gates[gi];gi+=1;return v
    def compare(a,b,n):
        nonlocal ci
        events.append(('compare',a,b,n));v=compares[ci];ci+=1;return v
    def flag():events.append(('flags',));return flags
    def ext(*args):events.append(('extended',*args))
    def trace(*args):events.append(('trace',*args))
    callbacks=[GATE(gate),COMPARE(compare),FLAGS(flag),EXT(ext),TRACE(trace)]
    p=Provider(*[lits[k] for k in ['ccb_base','category','category_alt','source','function','file','err_text','smp_text','hci_text']],*callbacks)
    return lib.g2_smp_candidate_ccb_by_id(C.byref(p),conn&255),events

def original_run(conn,gates,compares,flags):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
    u.mem_map(0x438000,(len(raw)+4095)&~4095);u.mem_write(0x438000,raw)
    u.mem_map(0x20000000,0x80000)
    stop=0x100f00;u.mem_map(0x100000,0x2000);u.reg_write(UC_ARM_REG_SP,0x20010000);u.reg_write(UC_ARM_REG_LR,stop|1);u.reg_write(UC_ARM_REG_R0,conn)
    events=[];gi=ci=0
    address_kind={0x4c9c50:'gate',0x44b610:'compare',0x43d0ce:'flags',0x43d574:'extended',0x52a63c:'trace'}
    def hook(cpu,addr,size,_):
        nonlocal gi,ci
        if addr==stop:cpu.emu_stop();return
        kind=address_kind.get(addr)
        if kind is None:return
        r=[cpu.reg_read(x) for x in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]]
        if kind=='gate':events.append(('gate',r[0]));out=gates[gi];gi+=1
        elif kind=='compare':events.append(('compare',*r[:3]));out=compares[ci];ci+=1
        elif kind=='flags':events.append(('flags',));out=flags
        elif kind=='extended':
            sp=cpu.reg_read(UC_ARM_REG_SP);extra=[int.from_bytes(cpu.mem_read(sp+4*i,4),'little') for i in range(3)]
            events.append(('extended',*r,*extra));out=r[0]
        else:events.append(('trace',*r[:3]));out=r[0]
        cpu.reg_write(UC_ARM_REG_R0,out);cpu.reg_write(UC_ARM_REG_PC,cpu.reg_read(UC_ARM_REG_LR))
    u.hook_add(UC_HOOK_CODE,hook)
    u.emu_start(0x5375fd,stop,count=300)
    assert u.reg_read(UC_ARM_REG_PC)==stop and u.reg_read(UC_ARM_REG_SP)==0x20010000
    return u.reg_read(UC_ARM_REG_R0),events
count=0;paths=set()
for conn in [1,2,255,256,0x101]:
    a=original_run(conn,[0]*5,[0]*4,0);b=native_run(conn,[0]*5,[0]*4,0)
    assert a==b,(conn,a,b);count+=1
for gates in itertools.product([0,1],repeat=5):
    for compares in itertools.product([0,1],repeat=4):
        for flags in [0,2]:
            a=original_run(0,gates,compares,flags);b=native_run(0,gates,compares,flags)
            assert a==b,(gates,compares,flags,a,b)
            paths.add(tuple(e[0] for e in a[1]));count+=1
for gates,compares,flags in [
    ([7,0,0,0,0],[0,0,0,0],0xff),
    ([1,9,0,0,0],[0xffffffff,0,0,0],0),
    ([1,1,3,0,0],[0xffffffff,1,0,0],2),
    ([1,1,1,5,0],[1,1,0xffffffff,0],0xff),
    ([1,1,1,1,11],[1,1,1,0xffffffff],0),
    ([1,1,1,1,11],[1,1,1,0],0),
]:
    a=original_run(0,gates,compares,flags);b=native_run(0,gates,compares,flags)
    assert a==b,(gates,compares,flags,a,b)
    paths.add(tuple(e[0] for e in a[1]));count+=1
receipt={'status':'PASS','comparisons':count,'distinct_provider_traces':len(paths),'original':'0x5375fc..0x537742','raw_sha256':hashlib.sha256(raw).hexdigest(),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'arm_compile_command':cmd,'limits':['Original Thumb vs native compiled C with identical scripted provider callbacks.','Logging providers, initialized CCB state, and valid connection ID lifecycle remain separate.','Cortex-M55 source compile only; no compiled-byte equality or device behavior.']}
(HERE/'results.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps({'status':'PASS','comparisons':count,'distinct_provider_traces':len(paths)}))
