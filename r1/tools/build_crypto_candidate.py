#!/usr/bin/env python3
"""Compile/link recovered R1 two-pass policy against pinned upstream AES."""
import hashlib
import json
from pathlib import Path
import subprocess

ROOT=Path(__file__).resolve().parents[2]
PIN='e72b6eff0884673997d0ca6385169bbd9b31936d'


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    aes=ROOT/'third-party/upstream/tiny-aes-c'
    assert (aes/'.git').exists()
    assert subprocess.check_output(['git','-C',str(aes),'rev-parse','HEAD'],text=True).strip()==PIN
    assert not subprocess.check_output(['git','-C',str(aes),'status','--porcelain'],text=True).strip()
    output=ROOT/'r1/research/source-build/crypto';output.mkdir(parents=True,exist_ok=True)
    for name in ('report.json','two-pass.elf','two-pass.bin','aes.o','stock_two_pass.o'):
        (output/name).unlink(missing_ok=True)
    flags=['--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-mfloat-abi=hard','-mfpu=fpv4-sp-d16',
           '-std=c11','-ffreestanding','-fno-strict-aliasing','-Os','-Wall','-Wextra','-Werror',
           '-isystem',str(ROOT/'vendor-cache/r1/gcc-arm-none-eabi-9-2020-q2-update/arm-none-eabi/include'),
           '-DECB=1','-DCBC=0','-DCTR=0','-I'+str(aes)]
    sources=[aes/'aes.c',ROOT/'r1/components/crypto/stock_two_pass.c']
    rows=[];objects=[]
    for source in sources:
        obj=output/(source.stem+'.o');command=['clang',*flags,'-c',str(source),'-o',str(obj)]
        subprocess.run(command,check=True);objects.append(obj)
        rows.append(dict(source=str(source.relative_to(ROOT)),source_sha256=sha(source),command=command,object_sha256=sha(obj)))
    elf=output/'two-pass.elf';binary=output/'two-pass.bin'
    command=['arm-none-eabi-ld','-Ttext=0x01000000','--entry=r1_stock_two_pass_callback',
             *map(str,objects),'-o',str(elf)]
    subprocess.run(command,check=True)
    undefined=subprocess.check_output(['arm-none-eabi-nm','-u',str(elf)],text=True)
    assert not undefined.strip()
    subprocess.run(['arm-none-eabi-objcopy','-O','binary',str(elf),str(binary)],check=True)
    symbols=subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True)
    addresses={line.split()[-1]:int(line.split()[0],16) for line in symbols.splitlines() if len(line.split())==3}
    report=dict(schema=1,upstream_pin=PIN,units=rows,compiled=2,total=2,component_linked=True,
                image_linked=False,byte_identity_proven=False,link_command=command,
                compiler_version=subprocess.check_output(['clang','--version'],text=True),
                elf_sha256=sha(elf),binary_sha256=sha(binary),binary_bytes=binary.stat().st_size,
                undefined_symbols=undefined,symbols=addresses,
                headers={str(p.relative_to(ROOT)):sha(p) for p in [aes/'aes.h',ROOT/'r1/components/crypto/stock_two_pass.h']})
    (output/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(f'Two-pass crypto component compiled and linked: 2/2 units, {binary.stat().st_size} bytes, no unresolved symbols')


if __name__=='__main__':main()
