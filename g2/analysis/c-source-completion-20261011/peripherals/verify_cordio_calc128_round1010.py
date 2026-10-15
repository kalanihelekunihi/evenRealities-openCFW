#!/usr/bin/env python3
"""Build pinned upstream Cordio Calc128 source into the selected Apollo graph."""
from pathlib import Path
import hashlib,json,subprocess

root=Path(__file__).resolve().parents[3]
repo=root.parent
cordio=repo/'third-party/upstream/cordio'
out=root/'build/c-firmware/cordio-calc128-round1010';out.mkdir(parents=True,exist_ok=True)
src=cordio/'wsf/sources/util/calc128.c'
shim=root/'config-recovered/cordio/g2-compat-include'
base=root/'build/c-firmware/ble-hci-reset-masks-round1009/apollo-main-ble-hci-reset-masks.o'
pin=subprocess.check_output(['git','-C',str(cordio),'rev-parse','HEAD'],text=True).strip()
assert pin=='3656312d6b73e2a2c1c8b33ee0385bc199dd97e6'
obj=out/'calc128.o';linked=out/'apollo-main-cordio-calc128.o'
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb',
                '-fshort-enums','-fno-builtin','-O2','-Wall','-Wextra','-Werror',
                '-I',str(shim),'-I',str(cordio/'wsf/include'),
                '-c',str(src),'-o',str(obj)],check=True)
subprocess.run(['arm-none-eabi-ld','-r',str(base),str(obj),'-o',str(linked)],check=True)
def imports(path):return {line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','-u',str(path)],text=True).splitlines()}
before,after=imports(base),imports(linked)
assert before-after=={'Calc128Cpy','Calc128Cpy64','calc128Zeros'}
assert not after-before
sym=subprocess.check_output(['arm-none-eabi-nm','-S',str(obj)],text=True)
assert any(line.endswith(' calc128Zeros') and int(line.split()[1],16)==16 for line in sym.splitlines())
receipt={'round':1010,'status':'PASS_PINNED_CORDIO_CALC128_BINDING',
         'component':'Apollo BLE 128-bit copy helpers and zero constant',
         'upstream_submodule':'third-party/upstream/cordio','upstream_commit':pin,
         'source':str(src.relative_to(repo)),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),
         'compat_header':str((shim/'string.h').relative_to(repo)),
         'validation':'Pinned upstream source, strict M55 compile, three selected import bindings, no new imports',
         'linked_object':str(linked.relative_to(root)),'linked_sha256':hashlib.sha256(linked.read_bytes()).hexdigest(),
         'unresolved_before':len(before),'unresolved_after':len(after),
         'whole_image_complete':False,'hardware_proof':False,
         'gates':['Native equivalence beyond the inspected copy lengths remains to be compared',
                  'Full image layout and hardware proof remain open']}
(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(receipt['status'],len(before),len(after),receipt['linked_sha256'])
