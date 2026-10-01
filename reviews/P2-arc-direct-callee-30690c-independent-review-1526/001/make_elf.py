#!/usr/bin/env python3
"""Build ARCv2 EM disassembly carrier ELF and assign the authenticated load VMA."""
from pathlib import Path
import argparse,struct,subprocess
here=Path(__file__).resolve().parent
repo=Path('/Users/kalani/Repo/evenRealities-openCFW')
campaign=repo/'g2/build/pseudocode-first/20260930T190500Z'
as_tool=campaign/'tools/arc-binutils-001/prefix/bin/arc-elf32-as'
def make(binary_name, elf_name, address):
    source=here/(Path(elf_name).stem+'.s')
    stem=Path(elf_name).stem.replace('-','_')
    source.write_text(f'.section .firmware,"ax"\n.global {stem}_entry\n{stem}_entry:\n.incbin "{binary_name}"\n')
    subprocess.run([str(as_tool),'-mcpu=em','-EL','-o',str(here/elf_name),str(source)],cwd=here,check=True)
    elf=bytearray((here/elf_name).read_bytes())
    shoff=struct.unpack_from('<I',elf,32)[0]; entsize=struct.unpack_from('<H',elf,46)[0]
    nsections=struct.unpack_from('<H',elf,48)[0]; shstrndx=struct.unpack_from('<H',elf,50)[0]
    stroff,strlen=struct.unpack_from('<II',elf,shoff+shstrndx*entsize+16); names=elf[stroff:stroff+strlen]
    for i in range(nsections):
        off=shoff+i*entsize; no=struct.unpack_from('<I',elf,off)[0]
        if no and names[no:names.find(b'\0',no)].decode() == '.firmware':
            struct.pack_into('<I',elf,off+12,address); break
    else: raise RuntimeError('missing .firmware section')
    (here/elf_name).write_bytes(elf)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('binary');p.add_argument('elf');p.add_argument('address',type=lambda x:int(x,0));a=p.parse_args();make(a.binary,a.elf,a.address)
