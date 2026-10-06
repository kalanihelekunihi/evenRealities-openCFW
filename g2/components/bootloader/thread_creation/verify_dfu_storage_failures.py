#!/usr/bin/env python3
"""Malformed-DFU task paths through source guarded MRAM bridge and reset store.

The source machine contains no locked executable image.  The absent ROM call at
0x0200ff20 is a named status callback; all surrounding source/stock code runs.
NOR/filesystem and MMIO are offline fixture models, never device writes.
"""
import argparse, importlib.util, json, struct, hashlib, zlib
from pathlib import Path
from unicorn import UC_HOOK_MEM_WRITE

HERE=Path(__file__).resolve().parent; ROOT=HERE.parents[3]
spec=importlib.util.spec_from_file_location('storage',HERE/'verify_dfu_storage.py')
s=importlib.util.module_from_spec(spec); spec.loader.exec_module(s)
v=s.v; c=s.c; fs=s.fs; NOR=s.NOR; SIZE=s.SIZE
spec=importlib.util.spec_from_file_location('runtime',HERE/'verify_dfu_runtime.py')
r=importlib.util.module_from_spec(spec); spec.loader.exec_module(r)
ENABLE=0x200271a7; STATUS=0x40021018; REQUEST=0x40021014
ROM=0x0200ff20; LOG=0x08002130; CONTROL_LOG=0x08002130

def make_disk(seed_elf, vector, scenario):
    _,segs,syms=v.elf.elf_info(seed_elf); m=fs.Source(segs,syms); cfg=syms['opencfw_boot_lfs_config']
    image=bytearray(32+256); image[32:40]=vector
    for i in range(40,len(image)):image[i]=(i*37)&255
    struct.pack_into('<I',image,0,len(image)|(1<<26));struct.pack_into('<I',image,20,0x438000)
    struct.pack_into('<I',image,4,zlib.crc32(image[8:]) ^ (1 if scenario=='bad-crc' else 0))
    if scenario=='short-header':image=image[:19]
    m.cpu.mem_write(fs.PATH,b'ota\0');assert m.call('lfs_format',[fs.FS,cfg])==0
    assert m.call('lfs_mount',[fs.FS,cfg])==0;assert m.call('lfs_mkdir',[fs.FS,fs.PATH])==0
    path=b'ota/other.bin\0' if scenario=='missing-file' else b'ota/s200_firmware_ota.bin\0'
    m.cpu.mem_write(fs.PATH,path);m.cpu.mem_write(fs.IMAGE,bytes(image))
    assert m.call('lfs_file_open',[fs.FS,fs.FILE,fs.PATH,0x502])==0
    assert m.call('lfs_file_write',[fs.FS,fs.FILE,fs.IMAGE,len(image)])==len(image)
    assert m.call('lfs_file_close',[fs.FS,fs.FILE])==0
    assert m.call('lfs_unmount',[fs.FS])==0
    return bytes(m.cpu.mem_read(NOR,SIZE)),v.sha(seed_elf)

class FailureMachine(s.Machine):
    def __init__(self,*args,**kw):
        super().__init__(*args,**kw)
        self.cpu.mem_map(0x40000000,0x1000); self.cpu.mem_map(0x40014000,0x1000); self.cpu.mem_map(0x0200f000,0x1000)
        self.storage=True; self.executed.update((self.symbols[n]&~1) if self.source else a for n,a in s.FILES.items())
        self.rom_status=0; self.guard_events=[]; self.rom_events=[]; self.control_logs=[]
        self.scenario=''
        self.guard_active=False
        self.in_failure=False
        self.mram_cleanup=[]; self.reset_events=[]; self.mmio_writes=[]; self.power_calls=[]
        self.failure_entry=(self.symbols['opencfw_boot_dfu_error_transaction']&~1) if self.source else 0x42de0e
        self.guard_begin=(self.symbols['opencfw_boot_control_guard_begin']&~1) if self.source else 0x41bd92
        self.guard_end=(self.symbols['opencfw_boot_control_guard_end']&~1) if self.source else 0x41bde4
        if self.source:
            self.executed.update(self.symbols[n]&~1 for n in ['opencfw_boot_control_guard_begin','opencfw_boot_control_guard_end','opencfw_boot_control_mram','opencfw_boot_dfu_error_transaction','opencfw_boot_control_critical_save'])
        self.cpu.hook_add(UC_HOOK_MEM_WRITE,self.memwrite)
    def drive(self):
        try:return super().drive()
        except AssertionError:
            if self.reason=='terminal-reset-store':return
            raise
    def memwrite(self,uc,access,address,size,value,user):
        if address in (0x40000004,0x40000008,0x40014008,0x40014024,REQUEST):
            self.mmio_writes.append([address,size,value & 0xffffffff])
        if address==REQUEST and self.guard_active and not (value&0x20):
            self.w(STATUS,self.u(STATUS)&~0x80)
    def code(self,uc,pc,size,user):
        if self.in_failure and (self.u(0x40000008)==0xd4 or self.u(0x40000004)==0x1b):
            self.reset_events.append(['terminal-reset-store',self.u(0x40000004),self.u(0x40000008)])
            self.stop('terminal-reset-store'); return
        if pc==self.failure_entry:
            self.in_failure=True
            self.boundary_events.append(['dfu-error-transaction-entry',hex(pc)])
            self.guard_active=True;self.w(ENABLE,1);self.w(STATUS,0)
            if not self.source:
                # Let pinned stock transaction instructions continue; the
                # inherited storage verifier's early boundary is bypassed.
                r.code(self,uc,pc,size,user); return
        if self.in_failure and pc==self.guard_begin:
            self.guard_events.append(['guard-begin',hex(pc)])
        if self.in_failure and pc==self.guard_end:self.guard_events.append(['guard-end',hex(pc)])
        if self.in_failure and pc==self.guard_end:
            self.w(STATUS,self.u(STATUS)&~0x80);self.guard_active=False
        if self.source and pc in (0x41f8ba,0x41ba80,0x41c990):
            self.boundary_events.append(['startup-control-provider',hex(pc),self.args()[0]])
            self.ret(0);return
        if pc==0x41cd1a and self.guard_active:
            a,b,p,_=self.args(); config=self.u(p); self.power_calls.append([a,b,config])
            if b==1:self.w(STATUS,self.u(STATUS)|0x80)
            else:self.guard_active=False
            self.ret(0); return
        if pc==ROM and self.in_failure:
            key,operation,source,word_offset=self.args(); words=self.u(uc.reg_read(v.a.UC_ARM_REG_SP))
            payload=bytes(uc.mem_read(source,words*4)) if words<=16 else b''
            self.rom_events.append([key,operation,hex(source),word_offset,words,payload.hex(),self.rom_status])
            self.ret(self.rom_status); return
        if self.in_failure and pc in (0x40014008,0x40014024):
            self.mram_cleanup.append([pc,self.args()[0]])
        if pc==CONTROL_LOG and self.in_failure:
            level,line,*_=self.args(); self.control_logs.append([level,line]); self.ret(); return
        if pc==0x4176ce and self.args()[1]==0x433fe0:
            self.task_events.append(['dfu-log',self.args()[0],self.u(uc.reg_read(v.a.UC_ARM_REG_SP))]); self.ret(); return
        if pc==0x4176ce and self.cstr(self.args()[1])=='file_system':self.ret();return
        if pc==self.failure_entry and self.source:
            pass
        super().code(uc,pc,size,user)

def setup(m,disk,blob,reset,vector):
    m.cpu.mem_write(NOR,disk);m.application_reset=reset;m.cpu.mem_map(reset&~4095,4096)
    m.cpu.mem_map(0x438000,4096);m.cpu.mem_write(0x438000,vector)
    m.cpu.mem_map(0x7fe000,4096);m.w(0x7fe000,0x55555555)
    m.apply_status=0;m.transition_status=0;m.query_status=0;m.query_result=0;m.finish_status=0
    if m.source:m.cpu.mem_write(v.BASE,blob[:4])
    m.stage_status={};m.init_status=0;m.read_status=0;m.mode_result=0;m.created_handle=0x20026ac0
    m.w(c.SLOT,c.SLOT_SENTINEL)
    for address,length in c.INIT_REGIONS:m.cpu.mem_write(address,b'\xcc'*length)
    m.cpu.reg_write(v.a.UC_ARM_REG_R9,0);c.seed_source_inputs(m,blob)
    for module in range(4):m.w(0x40060000+(module<<12)+0x14,0x00563412);m.w(0x40060000+(module<<12)+0x1c,1)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--elf',type=Path,required=True);ap.add_argument('--seed-elf',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args()
    assert v.sha(v.BLOB)==v.SHA;_,segs,syms=v.elf.elf_info(a.elf);blob=v.BLOB.read_bytes()
    app=ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'; assert v.sha(app)=='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863'
    vector=app.read_bytes()[32:40];reset=struct.unpack('<2I',vector)[1]&~1;cases=[];trace={}
    for scenario,status in [('missing-file',0),('short-header',7),('bad-crc',0x55)]:
        disk,seedhash=make_disk(a.seed_elf,vector,scenario);pair=[FailureMachine(),FailureMachine(True,segs,syms)]
        result=[]
        for m in pair:
            setup(m,disk,blob,reset,vector);m.rom_status=status;m.scenario=scenario
            try:m.drive()
            except Exception as exc:
                print('OBSERVED-STOP',scenario,'source',m.source,'pc',hex(m.cpu.reg_read(v.a.UC_ARM_REG_PC)),type(exc).__name__)
                result.append(dict(run='stopped-before-terminal',exception=type(exc).__name__,pc=hex(m.cpu.reg_read(v.a.UC_ARM_REG_PC)),arguments=m.args(),trace_tail=list(m.trace.items())[-12:],boundary=m.boundary_events,task_events=m.task_events,file_calls=m.file_calls,rom_events=m.rom_events))
            else:
                assert m.reason=='terminal-reset-store', (scenario,m.source,m.reason,hex(m.cpu.reg_read(v.a.UC_ARM_REG_PC)))
                assert len(m.rom_events)==1 and m.rom_events[0][0:5]==[0x12344321,1,m.rom_events[0][2],0xff800,4]
                assert m.rom_events[0][5]=='ffffffffffffffffffffffffffffffff'
                assert m.reset_events==[['terminal-reset-store',0,0xd4]]
                assert [x[0] for x in m.guard_events]==['guard-begin','guard-end']
                result.append(dict(run='terminal-reset-store',boundary=m.boundary_events,task_events=m.task_events,control_logs=m.control_logs,guard_events=m.guard_events,power_calls=m.power_calls,rom_events=m.rom_events,mram_cleanup=m.mram_cleanup,mmio_writes=m.mmio_writes,reset_events=m.reset_events,PRIMASK=m.cpu.reg_read(v.a.UC_ARM_REG_PRIMASK),file_calls=m.file_calls))
        trace.update(pair[0].trace)
        cases.append(dict(scenario=scenario,synthetic_rom_status=status,seed_nor_sha256=hashlib.sha256(disk).hexdigest(),seed_elf_sha256=seedhash,original=result[0],source=result[1]))
    all_match=all(c['original']==c['source'] for c in cases)
    used={int(pc,0)+i for pc,raw in trace.items() for i in range(len(bytes.fromhex(raw)))}
    completed=all(x['original'].get('run')=='terminal-reset-store' and x['source'].get('run')=='terminal-reset-store' for x in cases)
    report=dict(status='PASS' if all_match and completed else 'PARTIAL',all_original_source_match=all_match,cases=len(cases),distinct_original_trace_bytes=len(used),original_sha256=v.SHA,application_sha256=v.sha(app),elf_sha256=v.sha(a.elf),seed_elf_sha256=v.sha(a.seed_elf),source_sha256={str(p.relative_to(ROOT)):v.sha(p) for folder in ['startup','thread_creation','manager_task','dfu_task','update_core','filesystem','platform_control','nor_init','nor_mspi_init'] for p in (ROOT/'g2/components/bootloader'/folder).iterdir() if p.is_file() and p.suffix in ['.c','.h','.S','.ld','.py']},original_trace=trace,comparisons=cases,limits=['Source machine loads only ELF source executable segments and the first four locked bytes used as an initializer fixture; it never maps locked executable firmware. Original side executes pinned firmware. The missing ROM body at 0x0200ff20 is a synthetic callback returning the per-case status; source/stock MRAM bridge cleanup and terminal transaction code execute around it.','Synthetic littlefs-backed NOR supplies a nonempty directory containing a different file for the missing-name case, a 19-byte short-file case and a bad-CRC case. These exact fixtures only are tested. MMIO, guard power acknowledgement, filesystem allocator/mutex/NOR providers and ROM status are modeled.','Only successful task error-path runs justify the four-FFFFFFFF-word/0x7fe000/cleanup/reset-store outcome. Stopped runs report exact PC/arguments and do not imply that the stock failure transaction completed. Harness terminal-store observation is not a silicon reset.','No cancellation API was introduced or exercised. The test does not establish behavior if power fails during ROM programming or terminal reset before/after the store; the external ROM implementation and physical power-fail atomicity remain outside the boundary.','No complete source closure, byte identity, SBL/ROM implementation, peripheral timing or hardware write/reset claim.'])
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'status':report['status'],'cases':report['cases'],'original_bytes':report['distinct_original_trace_bytes']}))
if __name__=='__main__':main()
