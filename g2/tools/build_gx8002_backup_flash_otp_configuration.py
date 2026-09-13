# SPDX-License-Identifier: MIT
"""Compile backup flash identification routine using recovered helper ABI."""
import json,subprocess
from build_gx8002_backup_platform_config import ROOT,IMAGE,IMAGE_SHA,sha,Elf32,FLAGS
BINDINGS={'open_cfw_gx8002_clock_frequency':0x10003cf0,
          'open_cfw_gx8002_flash_otp_probe':0x20016d80,
          'open_cfw_gx8002_flash_otp_read_api':0x1000802c,
          'printf':0x10009934,'strncmp':0x10009998,'strlen':0x100099bc,
          'open_cfw_gx8002_flash_otp_error':0x10012a8c,
          'open_cfw_gx8002_flash_otp_signature':0x10012aa4}

def build():
    out=ROOT/'build/gx8002-backup-flash-otp-configuration';out.mkdir(exist_ok=True)
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    source=ROOT/'components/shared/gx8002/runtime_gx8002_backup_flash_otp_configuration.c'
    subprocess.run([pre+'gcc',*FLAGS,'-fno-shrink-wrap','-c',str(source),'-o',str(out/'configuration.o')],check=True)
    (out/'configuration.ld').write_text('SECTIONS { .text 0x100156d4 : { *(.text.open_cfw_gx8002_flash_otp_configuration) } }\n'+''.join(f'{k} = {v:#x};\n' for k,v in BINDINGS.items()))
    path=out/'configuration.elf'
    subprocess.run([pre+'ld','-T',str(out/'configuration.ld'),str(out/'configuration.o'),'-o',str(path)],check=True)
    elf=Elf32(path.read_bytes(),'backup OTP');s=next(s for s in elf.sections if s['name']=='.text');body=elf.contents(s)
    assert not elf.relocations(s['index']) and not any(s['name'] and s['section']==0 for s in elf.symbols())
    stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    (out/'configuration.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(path)],text=True))
    report={'source_sha256':sha(source.read_bytes()),'bindings':BINDINGS,'compiled_bytes':len(body),'compiled_sha256':sha(body),
            'envelope_bytes':118,'fits':len(body)<=118,'source_admitted':False,'hardware_qualified':False,
            'limits':['Candidate only. Backup retains explicit strlen before bounded comparison; helper behavior and pool/layout qualification pending.']}
    (ROOT/'docs/research/gx8002-backup-flash-otp-configuration-candidate.json').write_text(json.dumps(report,indent=2)+'\n')
    return report
if __name__=='__main__':print(json.dumps(build(),indent=2))
