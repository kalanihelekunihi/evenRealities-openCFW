# SPDX-License-Identifier: MIT
"""Build authenticated backup-image startup and vectors without binary input code."""
import json,subprocess,struct
from build_gx8002_stage1_platform_gate import build as authenticate,ROOT,SDK_COMMIT,authenticated_blob,sha,Elf32
from build_gx8002_backup_cfft import IMAGE,IMAGE_SHA


def build():
    evidence=authenticate();sdk=ROOT/'build/upstream-nationalchip-lvp-kws';rel='arch/cpu/csky/ck804/start.S'
    blob=subprocess.check_output(['git','-C',str(sdk),'rev-parse',SDK_COMMIT+':'+rel],text=True).strip();source=authenticated_blob(sdk/rel,blob)
    out=ROOT/'build/gx8002-backup-reset';out.mkdir(exist_ok=True)
    (out/'start.S').write_bytes(source)
    (out/'autoconf.h').write_text('#define CONFIG_STAGE2_STACK 0x2002fffc\n')
    for name in ('csi_config.h','board_config.h'):(out/name).write_text('/* No additional configuration required. */\n')
    (out/'soc.h').write_text('#define NR_IRQS 32\n')
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    subprocess.run([pre+'gcc','-mcpu=ck804ef','-mhard-float','-I',str(out),'-c',str(out/'start.S'),'-o',str(out/'reset.o')],check=True)
    subprocess.run([pre+'objcopy','--set-section-flags=.vectors=alloc,load,readonly,data',str(out/'reset.o')],check=True)
    ld='''SECTIONS {
.vectors 0x10003000 : { *(.vectors) }
.reset 0x10003100 : { *(.text) }
}
system_init = 0x1000314c;
main = 0x10015cfc;
Default_Handler = 0x10003240;
tspend_handler = Default_Handler;
gx_irq_handler = 0x10004880;
_start_bss_ = 0x20017090;
_end_bss_ = 0x2002d79c;
ENTRY(reset_handler)
'''
    (out/'reset.ld').write_text(ld);path=out/'reset.elf'
    subprocess.run([pre+'ld','-T',str(out/'reset.ld'),str(out/'reset.o'),'-o',str(path)],check=True)
    elf=Elf32(path.read_bytes(),'backup reset');stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    assert not any(s['name'] and s['section']==0 for s in elf.symbols())
    assert not any(elf.relocations(s['index']) for s in elf.sections)
    vectors=next(s for s in elf.sections if s['name']=='.vectors');reset=next(s for s in elf.sections if s['name']=='.reset')
    expected=struct.pack('<64I',0x10003100,*([0x10003240]*31),*([0x10004880]*32))
    assert elf.contents(vectors)==expected==stock[0x3b940:0x3ba40]
    assert reset['size']==76 and elf.contents(reset)==stock[0x3ba40:0x3ba8c]
    (out/'reset.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(path)],text=True))
    report={'upstream_evidence':evidence,'upstream_commit':SDK_COMMIT,'upstream_path':rel,'upstream_blob':blob,'source_sha256':sha(source),'elf_sha256':sha(path.read_bytes()),'vectors_bytes':256,'reset_and_bss_bytes':76,'stock_byte_exact':True,'source_admitted':False,'limits':['Unmodified authenticated upstream assembly, recovered stack/IRQ/BSS configuration and callback bindings. Startup, return loop and BSS-clear bytes match stock. System initialization, main and exception/IRQ callbacks remain absolute dependencies here. Physical processor and loaded-image lifetime remain unqualified.']}
    (ROOT/'docs/research/gx8002-backup-reset.json').write_text(json.dumps(report,indent=2)+'\n');return report


if __name__=='__main__':print(build()['stock_byte_exact'])
