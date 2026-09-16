# SPDX-License-Identifier: MIT
"""Composed decoded stock 512-point FFT arithmetic for processing comparison."""
import subprocess
from analyze_gx8002_upstream_objects import ROOT,IMAGE,IMAGE_SHA,sha
from verify_gx8002_memcpy_source import decode
from verify_gx8002_backup_radix4_stock_host import execute as radix
from verify_gx8002_backup_split_stock_host import execute as split
from verify_gx8002_backup_radix4_by2_host import s16
from generate_gx8002_backup_math_tables import coefficients

def make_fft():
    assert sha(IMAGE.read_bytes())==IMAGE_SHA
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf'
    from build_transparent_image import Elf32
    elf=Elf32(wrapper.read_bytes(),'stock')
    assert elf.contents(next(s for s in elf.sections if s['name']=='.data'))==IMAGE.read_bytes()
    codes={}
    for inverse in (False,True):
        ranges=((0x47f50,0x48164),(0x479a8,0x47a00)) if inverse else ((0x47d3c,0x47f50),(0x47914,0x479a8))
        codes[inverse]=[(start,decode(subprocess.check_output([pre,'-D',f'--start-address={start:#x}',f'--stop-address={end:#x}',str(wrapper)],text=True))) for start,end in ranges]
    complex_coeff=coefficients(complex_fft=True)[0];real_coeff=coefficients()[0]
    def reverse(values):return tuple(values[2*int(f'{i:08b}'[::-1],2)+j] for i in range(256) for j in (0,1))
    def execute(values,inverse):
        (rstart,rc),(sstart,sc)=codes[inverse]
        assert len(values)==(514 if inverse else 512)
        if inverse:
            intermediate=split(sc,sstart,values,real_coeff,256,1,True)
            transformed=reverse(radix(rc,rstart,intermediate,complex_coeff,1))
            return tuple(values),tuple(s16(v*2) for v in transformed)
        updated=reverse(radix(rc,rstart,values,complex_coeff,1))
        return updated,split(sc,sstart,updated,real_coeff,256,1,False)
    return execute
