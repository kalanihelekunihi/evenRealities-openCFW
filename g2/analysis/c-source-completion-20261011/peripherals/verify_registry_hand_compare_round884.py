#!/usr/bin/env python3
"""Compare Apollo 0x46636c with host C over the same record/context pairs."""
from pathlib import Path
import ctypes, hashlib, json, random, subprocess, tempfile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS
from unicorn import arm_const as A

root = Path(__file__).resolve().parents[3]
out = root / 'build/c-firmware/registry-hand-compare-round884'
out.mkdir(parents=True, exist_ok=True)
src = root / 'components/audio/uart_thread_source_candidate/registry_hand_compare_46636c.c'
obj = out / 'registry_hand_compare_46636c.o'
subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m55', '-mthumb',
                '-fshort-enums', '-std=c11', '-ffreestanding', '-fno-builtin', '-O2',
                '-Wall', '-Wextra', '-Werror', '-c', str(src), '-o', str(obj)], check=True)
imports = {line.split()[-1] for line in subprocess.check_output(
    ['arm-none-eabi-nm', '-u', str(obj)], text=True).splitlines()}
assert imports == {'audio_uart_hand_context', 'g2_lfs_memcmp'}, imports
blob = (root / 'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(blob).hexdigest() == '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
native = blob[0x46636c - 0x438000:0x466412 - 0x438000]
assert native[:2].hex() == '38b5' and native[-2:].hex() == '32bd'
assert int.from_bytes(blob[0x4667ec-0x438000:0x4667f0-0x438000], 'little') == 0x200736d4

with tempfile.TemporaryDirectory() as td:
    shim = Path(td) / 'shim.c'
    shim.write_text('#include <stdint.h>\n'
                    'const volatile uint8_t *const audio_uart_hand_context=(void *)0x1;\n'
                    'int32_t g2_lfs_memcmp(const void *a,const void *b,uint32_t n){'
                    'const uint8_t *x=a,*y=b;for(uint32_t i=0;i<n;i++)'
                    'if(x[i]!=y[i])return (int32_t)x[i]-(int32_t)y[i];return 0;}\n')
    # A writable pointer cell lets the verifier bind each host context fixture.
    shim.write_text(shim.read_text().replace('const volatile uint8_t *const audio_uart_hand_context=(void *)0x1;',
                                         'const volatile uint8_t *audio_uart_hand_context;'))
    host = Path(td) / 'host.dylib'
    subprocess.run(['clang', '-shared', '-fPIC', '-std=c11', '-O2', str(src), str(shim),
                    '-o', str(host)], check=True)
    lib = ctypes.CDLL(str(host))
    cell = ctypes.c_void_p.in_dll(lib, 'audio_uart_hand_context')
    fun = lib.audio_uart_registry_hand_compare_46636c
    fun.argtypes = [ctypes.c_void_p]
    fun.restype = ctypes.c_uint32
    rng = random.Random(0x46636c)
    cases = []
    for changed in [None, 3, 4, 5, 6, 7, 10, 13, 14, 20, 21, 28, 31, 32, 40, 44, 45]:
        saved = bytearray(rng.randbytes(48))
        record = bytearray(rng.randbytes(48))
        for a,b,n in ((3,1,4),(7,5,3),(10,8,3),(13,11,1),(14,12,6),
                      (20,18,2),(28,24,4),(32,28,2),(40,36,4),(44,40,2)):
            record[a:a+n] = saved[b:b+n]
        if changed is not None: record[changed] ^= 0x5a
        c_saved=(ctypes.c_uint8*48).from_buffer_copy(saved)
        c_record=(ctypes.c_uint8*48).from_buffer_copy(record)
        cell.value=ctypes.addressof(c_saved)
        actual_c=fun(ctypes.addressof(c_record))
        uc=Uc(UC_ARCH_ARM, UC_MODE_THUMB|UC_MODE_MCLASS)
        uc.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
        uc.mem_map(0x438000,(len(blob)+0xfff)&~0xfff)
        uc.mem_write(0x438000,blob)
        uc.mem_map(0x20000000,0x80000)
        uc.mem_write(0x200736d4,bytes(saved))
        uc.mem_write(0x20074000,bytes(record))
        uc.reg_write(A.UC_ARM_REG_R0,0x20074000)
        uc.reg_write(A.UC_ARM_REG_SP,0x2007f000)
        uc.reg_write(A.UC_ARM_REG_LR,0x466415)
        uc.emu_start(0x46636d,0x466414,count=10000)
        native_result=uc.reg_read(A.UC_ARM_REG_R0)
        assert actual_c==native_result, (changed,actual_c,native_result)
        cases.append({'changed_offset':changed,'result':native_result})

base=root/'build/c-firmware/registry-ring-child-round883/apollo-main-registry-ring-child.o'
linked=out/'apollo-main-registry-hand-compare.o'
subprocess.run(['arm-none-eabi-ld','-r',str(base),str(obj),'-o',str(linked)],check=True)
before={x.split()[-1] for x in subprocess.check_output(['arm-none-eabi-nm','-u',str(base)],text=True).splitlines()}
after={x.split()[-1] for x in subprocess.check_output(['arm-none-eabi-nm','-u',str(linked)],text=True).splitlines()}
assert not after-before
assert len(after)==len(before)
receipt={'round':884,'status':'PASS_NATIVE_REGISTRY_HAND_COMPARE',
         'component':'Apollo registry hand comparison',
         'source':str(src.relative_to(root)),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),
         'official_image_sha256':hashlib.sha256(blob).hexdigest(),
         'native_body_sha256':hashlib.sha256(native).hexdigest(),
         'cases':cases,'unresolved_before':len(before),'unresolved_after':len(after),
         'linked_object':str(linked.relative_to(root)),
         'linked_sha256':hashlib.sha256(linked.read_bytes()).hexdigest(),
         'whole_image_complete':False,'hardware_proof':False,
         'gates':['Parent callback child 0x466412 and saved hand context ownership remain open',
                  'Final image placement and hardware execution remain unverified']}
(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print('PASS_REGISTRY_HAND_COMPARE',len(cases),len(after))
