# SPDX-License-Identifier: MIT
"""Native macOS cross-build of the recovered OTP-dependent low-power entry."""
import json,subprocess
from verify_gx8002_analog_source import FLAGS
from build_transparent_image import Elf32
from analyze_gx8002_upstream_objects import ROOT,sha,IMAGE,IMAGE_SHA


def build(extra_flags=()):
    out=ROOT/'build/gx8002-board';out.mkdir(parents=True,exist_ok=True)
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    source=ROOT/'components/shared/gx8002/runtime_gx8002_otp_lowpower_enter.c'
    flags=['-Os',*FLAGS[1:],*extra_flags]
    subprocess.run([pre+'gcc',*flags,'-c',str(source),'-o',str(out/'otp-lowpower-enter.o')],check=True)
    script=out/'otp-lowpower-enter.ld';script.write_text('SECTIONS { .text 0x100248cc : { *(.text.open_cfw_gx8002_otp_lowpower_enter) } }\nopen_cfw_gx8002_flash_otp_configuration = 0x10025d04;\nopen_cfw_gx8002_clock_switch_1m = 0x10025a14;\n')
    path=out/'otp-lowpower-enter.elf'
    subprocess.run([pre+'ld','-T',str(script),str(out/'otp-lowpower-enter.o'),'-o',str(path)],check=True)
    elf=Elf32(path.read_bytes(),str(path));section=next(s for s in elf.sections if s['name']=='.text');data=elf.contents(section)
    assert sha(IMAGE.read_bytes())==IMAGE_SHA and not elf.relocations(section['index'])
    assert not any(s['name'] and s['section']==0 for s in elf.symbols())
    assert {s['name'] for s in elf.sections if s['size'] and s['flags']&2}=={'.text'}
    (out/'otp-lowpower-enter.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(path)],text=True))
    report={'flags':flags,'source_sha256':sha(source.read_bytes()),'compiled_bytes':len(data),'compiled_sha256':sha(data),'package_offset':0x168e0,'envelope_bytes':116,'fits':len(data)<=116,'source_admitted':False,'limits':['Build-only reconstruction; decoded behavior and caller integration pending. Explicit architectural sync/doze assembly remains visible source.']}
    (ROOT/'docs/research/gx8002-otp-lowpower-enter-candidate.json').write_text(json.dumps(report,indent=2)+'\n')
    return report
if __name__=='__main__':print(json.dumps(build(),indent=2))
