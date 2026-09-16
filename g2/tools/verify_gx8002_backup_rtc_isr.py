# SPDX-License-Identifier: MIT
"""Decoded backup RTC callback/acknowledgement regression."""
import itertools,json,subprocess
from build_gx8002_backup_rtc_isr import build,ROOT,Elf32,IMAGE_SHA,sha
from verify_gx8002_rtc_isr import execute,expected
from verify_gx8002_memcpy_source import decode


def verify():
    build();wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf'
    elf=Elf32(wrapper.read_bytes(),'stock');assert sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))==IMAGE_SHA
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    old=decode(subprocess.check_output([pre,'-D','--start-address=0x4111c','--stop-address=0x41140',str(wrapper)],text=True))
    new=decode((ROOT/'build/gx8002-backup-rtc-isr/device.disassembly.txt').read_text());count=0
    for args in itertools.product((0,4,31,0x80000000,0xffffffff),(0,0x10020000,0x10021000),(0,0x20040000,0xffffffff),(0,1,0x80000000,0xffffffff),(0,1,0xffffffff)):
        assert execute(old,0x4111c,*args,state=0x200176d0)==execute(new,0x100087dc,*args,state=0x200176d0)==expected(*args,state=0x200176d0)
        count+=1
    report={'cases':count,'differences':0,'limits':['Callback return/clobbers and acknowledgement value modeled. Checks read ordering, callback arguments, result and preserved registers; hardware acknowledgement and concurrency remain unqualified.']}
    (ROOT/'docs/research/gx8002-backup-rtc-isr-verification.json').write_text(json.dumps(report,indent=2)+'\n');return report


if __name__=='__main__':print(verify())
