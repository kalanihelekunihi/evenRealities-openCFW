#!/usr/bin/env python3
"""Execute locked claim/transaction instructions against the shared source ELF.

Lower power/clock/CQ/wait APIs are explicit deterministic call cuts in this
direct suite; shared integration separately runs the native power/clock code.
"""
import argparse, hashlib, importlib.util, itertools, json, struct
from pathlib import Path
from unicorn import arm_const as a
HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('interrupt_profile', HERE/'verify_context_interrupt.py')
v = importlib.util.module_from_spec(spec); spec.loader.exec_module(v)
POOL, STRIDE, OUT = 0x2001455c, 0x8a8, 0x20003000
ENTRIES = {'claim': ('opencfw_boot_context_claim', 0x42c4c6),
           'transaction': ('opencfw_boot_context_transaction', 0x42c988),
           'interrupt': ('opencfw_boot_context_interrupt_enable', 0x42c63a)}
CALLS = {'opencfw_bl_mspi_mode_enter': (0x41bf84, 'mode-enter', 1),
         'opencfw_bl_mspi_mode_leave': (0x41c17a, 'mode-leave', 1),
         'clock_request': (0x4222f0, 'clock-request', 2),
         'clock_release': (0x422364, 'clock-release', 2),
         'opencfw_boot_iom_cq_enable': (0x42c420, 'cq-enable', 1),
         'opencfw_boot_iom_cq_disable': (0x42c44e, 'cq-disable', 1),
         'opencfw_hal_status_poll': (0x41d246, 'status-poll', 5)}
REGISTERS = [0x104,0x118,0x11c,0x228,0x22c,0x234,0x23c,0x240,
             0x244,0x280,0x2c0,0x200,0x210,0x248]
class Machine(v.Machine):
    def __init__(self, source, segments, symbols):
        super().__init__(source, segments, symbols)
        self.cpu.mem_map(v.IRQ+0x4000,0x4000)
        self.cuts = {(symbols[name]&~1 if source else pc):(label,arity)
                     for name,(pc,label,arity) in CALLS.items()}
        self.events, self.state_writes = [], []
        self.clock_status, self.lower_status = 0, 0
    def code(self,uc,pc,size,user):
        if pc in self.cuts:
            label,arity=self.cuts[pc]
            args=[uc.reg_read(r) for r in (a.UC_ARM_REG_R0,a.UC_ARM_REG_R1,
                                         a.UC_ARM_REG_R2,a.UC_ARM_REG_R3)]
            if arity==5: args.append(struct.unpack('<I',uc.mem_read(uc.reg_read(a.UC_ARM_REG_SP),4))[0])
            result=self.clock_status if label.startswith('clock-') else self.lower_status
            self.events.append([label,*args[:arity],result])
            uc.reg_write(a.UC_ARM_REG_R0,result)
            uc.reg_write(a.UC_ARM_REG_PC,uc.reg_read(a.UC_ARM_REG_LR));return
        super().code(uc,pc,size,user)
    def memwrite(self,uc,access,address,size,value,user):
        super().memwrite(uc,access,address,size,value,user)
        if v.IRQ+0x4000<=address<v.IRQ+0x8000:
            self.writes.append([address,size,value&((1<<(size*8))-1)])
        if POOL<=address<POOL+8*STRIDE or OUT<=address<OUT+4:
            self.state_writes.append([address,size,value&((1<<(size*8))-1)])
    def reset(self):
        self.events.clear();self.state_writes.clear();self.writes.clear()
        self.cpu.mem_write(POOL,bytes((i*13+7)&255 for i in range(8*STRIDE)))
        self.cpu.mem_write(OUT,struct.pack('<I',0xdeadbeef))
        self.cpu.mem_write(v.IRQ,b'\0'*0x8000)
        for module in range(8):
            for offset in REGISTERS:
                self.cpu.mem_write(v.IRQ+module*0x1000+offset,
                                   struct.pack('<I',0x82000000+offset+module*16))
    def call(self,entry,args):
        self.done=False
        for reg,value in zip((a.UC_ARM_REG_R0,a.UC_ARM_REG_R1,a.UC_ARM_REG_R2,a.UC_ARM_REG_R3),list(args)+[0]*4):
            self.cpu.reg_write(reg,value)
        self.cpu.reg_write(a.UC_ARM_REG_SP,v.SP);self.cpu.reg_write(a.UC_ARM_REG_LR,v.STOP|1)
        pc=self.symbols[ENTRIES[entry][0]]&~1 if self.source else ENTRIES[entry][1]
        self.cpu.emu_start(pc|1,v.STOP+2,count=100000);assert self.done
        return self.cpu.reg_read(a.UC_ARM_REG_R0)
    def observation(self,status):
        return dict(status=status,output=bytes(self.cpu.mem_read(OUT,4)).hex(),
                    pool_sha256=hashlib.sha256(self.cpu.mem_read(POOL,8*STRIDE)).hexdigest(),
                    mmio_sha256=hashlib.sha256(self.cpu.mem_read(v.IRQ,0x8000)).hexdigest(),
                    events=list(self.events),state_writes=list(self.state_writes),
                    mmio_writes=list(self.writes))
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--elf',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
    blob=v.BLOB.read_bytes();assert hashlib.sha256(blob).hexdigest()==v.LOCKED_SHA
    _,segments,symbols=v.elf.elf_info(args.elf)
    assert symbols['opencfw_boot_iom_contexts']==POOL
    machines=[Machine(False,segments,symbols),Machine(True,segments,symbols)];cases=[]
    def compare(kind,parameters,prepare,sequence):
        observations=[]
        for m in machines:
            m.reset();prepare(m);statuses=[m.call(e,values) for e,values in sequence];observations.append(m.observation(statuses))
        assert observations[0]==observations[1],(kind,parameters,observations)
        cases.append(dict(kind=kind,parameters=parameters,observation=observations[0]))
        return observations[0]
    for module,out,flags in itertools.product(range(11),(0,OUT),(0,0x02000000,0x800abcde,0x01000000,0xfe123456)):
        def prepare(m):
            for i in range(8):m.cpu.mem_write(POOL+i*STRIDE,struct.pack('<I',flags))
        result=compare('claim',[module,out,flags],prepare,[('claim',[module,out])])
        expected=5 if module>=8 else 6 if out==0 else 7 if flags&0x01000000 else 0
        assert result['status']==[expected]
        if expected:assert not result['state_writes'] and result['output']=='efbeadde'
    for module,command,retain,scenario in itertools.product((0,4,7),(0,1,2,3,0x100,0x102),(0,1,0x100,0x101),range(5)):
        handle=POOL+module*STRIDE
        def prepare(m):
            flags=0x01123456|(0x02000000 if scenario in (2,3,4) else 0)
            m.cpu.mem_write(handle,struct.pack('<II',flags,module))
            m.cpu.mem_write(handle+0x24,struct.pack('<I',1 if scenario==3 else 0))
            m.cpu.mem_write(handle+0x868,bytes([0 if scenario==0 else 1]))
            m.cpu.mem_write(handle+0x87c,struct.pack('<I',1 if scenario==4 else 0))
            m.cpu.mem_write(v.IRQ+module*0x1000+0x228,struct.pack('<I',1 if scenario==4 else 0))
            m.cpu.mem_write(v.IRQ+module*0x1000+0x248,struct.pack('<I',2 if scenario==2 else 4))
            m.clock_status=7 if scenario==4 else 0;m.lower_status=9
        compare('transaction',[module,command,retain,scenario],prepare,[('transaction',[handle,command,retain])])
    for handle in (0,POOL):
        compare('invalid-transaction',[handle],lambda m:None,[('transaction',[handle,0,0])])
    for module,mask in itertools.product(range(8),(2,4,0xff)):
        handle=POOL+module*STRIDE
        def prepare(m):
            m.cpu.mem_write(handle,struct.pack('<I',0));m.clock_status=0;m.lower_status=0
        result=compare('claim-config-powerdown-reclaim',[module,mask],prepare,
                       [('claim',[module,OUT]),('transaction',[handle,0,0]),
                        ('interrupt',[handle,mask]),('transaction',[handle,1,0]),
                        ('claim',[module,OUT])])
        assert result['status']==[0,0,6 if mask&2 else 0,0,7]
    trace={hex(pc):raw for pc,raw in machines[0].trace.items()};used={int(pc,0)+i for pc,raw in trace.items() for i in range(len(bytes.fromhex(raw)))}
    report=dict(status='PASS',cases=len(cases),elf_sha256=hashlib.sha256(args.elf.read_bytes()).hexdigest(),
                original_sha256=v.LOCKED_SHA,original_trace=trace,distinct_original_trace_bytes=len(used),
                source_sha256={str(p.relative_to(v.ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in (HERE/'context_claim.c',HERE/'context_claim.h',HERE/'context_transaction.c',Path(__file__))},
                comparisons=cases,limits=['MMIO is Unicorn RAM. Lower power/clock/CQ/wait calls have controlled return values; no physical timing or lower-call implementation proof from this direct suite.',
                'Static slot claim performs no heap allocation. Failure preserves output/pool; transaction powerdown retains claim bit and duplicate claim still returns7. No uninitialize/release implementation is invented.',
                'Only the listed modules/arguments/snapshot/busy/status combinations are exercised.'])
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:report[k] for k in ('status','cases','distinct_original_trace_bytes','elf_sha256')}))
if __name__=='__main__':main()
