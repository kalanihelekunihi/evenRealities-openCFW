#!/usr/bin/env python3
"""Bounded stock/source entry oracle; lower-cut branches are reported separately."""
import hashlib, json, pathlib, struct, sys
from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn import arm_const as A

ROOT = pathlib.Path(__file__).resolve().parents[4]
BLOB = ROOT / 'g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin'
HASH = 'f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5'
ENTRY = 0x426536
STOP = 0x600000

def load_elf(path):
    with open(path, 'rb') as f:
        elf = ELFFile(f)
        segments = [(s['p_vaddr'], s.data()) for s in elf.iter_segments()
                    if s['p_type'] == 'PT_LOAD' and s.data()]
        names = {}
        for section in elf.iter_sections():
            if section.header.sh_type == 'SHT_SYMTAB':
                names.update({s.name: s['st_value'] for s in section.iter_symbols()})
        return segments, names

def run(blob, segments, entry, handle, status, words, source, cuts, error=False, callback=False,
        descriptor_callback=False, lower_failure=None):
    uc = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
    for base, size in ((0x400000,0x50000),(0x500000,0x10000),
                       (0x600000,0x1000),(0x20000000,0x30000),
                       (0x40060000,0x10000)):
        uc.mem_map(base,size)
    uc.mem_write(0x410000,blob)
    for base,data in segments:
        if 0x500000 <= base < 0x510000: uc.mem_write(base,data)
    state=bytearray(0x8d0)
    for off,value in words.items(): struct.pack_into('<I',state,off,value)
    uc.mem_write(0x20010000,bytes(state))
    uc.mem_write(0x20018000,b'\0'*0x100)
    if descriptor_callback:
        uc.mem_write(0x20018010,struct.pack('<II',0x600101,0x20018100))
    uc.mem_write(0x2001d2c8,struct.pack('<I',0x20019000))
    uc.reg_write(A.UC_ARM_REG_R0,handle)
    uc.reg_write(A.UC_ARM_REG_R1,status)
    uc.reg_write(A.UC_ARM_REG_SP,0x2002f000)
    uc.reg_write(A.UC_ARM_REG_LR,STOP|1)
    uc.reg_write(A.UC_ARM_REG_XPSR,0x01000000)
    visited=set(); done=[]; callbacks=[]
    def hook(cpu,address,size,_):
        if address==STOP: done.append(True); cpu.emu_stop()
        elif address == 0x600100:
            callbacks.append((cpu.reg_read(A.UC_ARM_REG_R0),cpu.reg_read(A.UC_ARM_REG_R1)))
            cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
        elif address in cuts:
            if address == 0x427a56 or (source and address == (names_for_cuts['opencfw_boot_mspi_cmdq_get_status'] & ~1)):
                payload=bytearray(16)
                if callback: struct.pack_into('<I',payload,0,1)
                if error: payload[14]=1
                cpu.mem_write(cpu.reg_read(A.UC_ARM_REG_R1),bytes(payload))
            result = 0
            if lower_failure and address == lower_failure[0]: result=lower_failure[1]
            cpu.reg_write(A.UC_ARM_REG_R0,result)
            cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
        elif not source and ENTRY <= address < 0x426800:
            visited.update(range(address,address+size))
    uc.hook_add(UC_HOOK_CODE,hook)
    uc.emu_start(entry|1,STOP+2,count=100000)
    assert done,(hex(entry),hex(uc.reg_read(A.UC_ARM_REG_PC)))
    return (uc.reg_read(A.UC_ARM_REG_R0),bytes(uc.mem_read(0x20010000,0x8d0)),
            bytes(uc.mem_read(0x20018000,0x20)),callbacks),visited

def main():
    blob=BLOB.read_bytes(); assert hashlib.sha256(blob).hexdigest()==HASH
    elf=pathlib.Path(sys.argv[1]); segments,names=load_elf(elf)
    global names_for_cuts
    names_for_cuts=names
    stock_cuts={0x427a56,0x423fac,0x427b38,0x423f8e,0x42403e,0x422364}
    source_cuts={names[n] & ~1 for n in (
        'opencfw_boot_mspi_cmdq_get_status','opencfw_hal_mspi_cq_disable',
        'opencfw_boot_mspi_cmdq_error_resume','opencfw_boot_mspi_cq_enable',
        'opencfw_boot_mspi_program_dma','clock_release')}
    cases=[
        ('null',0,0,{}),
        ('invalid-prefix',0x20010000,0,{0:0}),
        ('idle',0x20010000,0x24,{0:0x01bebebe,4:0,0x20:0}),
        ('idle-other-module',0x20010000,0x1880,{0:0x01bebebe,4:2,0x20:0}),
        ('hp-no-completion',0x20010000,0,{0:0x01bebebe,4:1,0x83c:1,0x840:1}),
        ('hp-complete',0x20010000,0x40,{0:0x01bebebe,4:1,0x83c:1,0x840:1,0x848:1,0x854:0x20018000,0x20:1}),
        ('hp-complete-clock-release',0x20010000,0x40,{0:0x01bebebe,4:1,0x83c:1,0x840:1,0x848:1,0x854:0x20018000,0x20:0}),
        ('cq-status-idle',0x20010000,0x40,{0:0x01bebebe,4:0,0x20:1}),
        ('cq-status-error',0x20010000,0x1880,{0:0x01bebebe,4:0,0x20:1}),
        ('cq-one-callback',0x20010000,0,{0:0x01bebebe,4:0,0x20:1,0x2c:0x600101,0x42c:0x20018000}),
        ('hp-descriptor-callback',0x20010000,0x40,{0:0x01bebebe,4:1,0x83c:1,0x840:1,0x848:1,0x854:0x20018000,0x20:1}),
        ('cq-status-failure',0x20010000,0x40,{0:0x01bebebe,4:0,0x20:1}),
        ('cq-disable-failure',0x20010000,0x1880,{0:0x01bebebe,4:0,0x20:1}),
        ('hp-clock-release-failure',0x20010000,0x40,{0:0x01bebebe,4:1,0x83c:1,0x840:1,0x848:1,0x854:0x20018000,0x20:0}),
    ]
    visited=set(); results=[]
    for label,handle,status,words in cases:
        lower={
            'cq-status-failure':(0x427a56,names['opencfw_boot_mspi_cmdq_get_status']&~1,6),
            'cq-disable-failure':(0x423fac,names['opencfw_hal_mspi_cq_disable']&~1,4),
            'hp-clock-release-failure':(0x422364,names['clock_release']&~1,6),
        }.get(label)
        kw={'error':label in ('cq-status-error','cq-disable-failure'),
            'callback':label=='cq-one-callback',
            'descriptor_callback':label=='hp-descriptor-callback'}
        original,seen=run(blob,segments,ENTRY,handle,status,words,False,stock_cuts,
                          lower_failure=(lower[0],lower[2]) if lower else None,**kw)
        candidate,_=run(blob,segments,names['am_hal_mspi_interrupt_service'],handle,status,words,True,source_cuts,
                        lower_failure=(lower[1],lower[2]) if lower else None,**kw)
        assert original==candidate,(label,original[0],candidate[0],
                                    [(i,original[1][i],candidate[1][i]) for i in range(0x8d0) if original[1][i]!=candidate[1][i]][:16],
                                    original[3],candidate[3])
        visited|=seen; results.append(label)
    receipt={'status':'PASS','original_sha256':HASH,'candidate_elf_sha256':hashlib.sha256(elf.read_bytes()).hexdigest(),
             'cases':results,'stock_bytes_visited':len(visited),
             'limits':['Cortex-M33 recompilation; selected Cortex-M55 object not executed.',
                       'Invalid-handle, idle CQ, HP completion, descriptor callback, CQ status/error, active CQ callback, and three nonzero child results. Lower calls are controlled cuts with explicit status output.',
                       'Synthetic RAM/MMIO; hardware effects and liveness not established.']}
    pathlib.Path(__file__).with_name('mspi-service-oracle-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(receipt))

if __name__=='__main__': main()
