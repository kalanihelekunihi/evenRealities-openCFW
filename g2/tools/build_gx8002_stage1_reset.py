# SPDX-License-Identifier: MIT
"""Build authenticated upstream SPL reset/vector assembly on macOS."""
import json,subprocess,struct
from build_gx8002_stage1_platform_gate import build as authenticate,ROOT,SDK_COMMIT,authenticated_blob,sha,Elf32
from build_gx8002_backup_cfft import IMAGE,IMAGE_SHA


def build():
    evidence=authenticate();sdk=ROOT/'build/upstream-nationalchip-lvp-kws'
    rel='arch/cpu/csky/ck804/spl_start.S'
    blob=subprocess.check_output(['git','-C',str(sdk),'rev-parse',SDK_COMMIT+':'+rel],text=True).strip()
    source=authenticated_blob(sdk/rel,blob)
    out=ROOT/'build/gx8002-stage1-reset';out.mkdir(exist_ok=True)
    (out/'spl_start.S').write_bytes(source)
    (out/'autoconf.h').write_text('#define CONFIG_STAGE1_STACK 0x20002ffc\n')
    (out/'board_config.h').write_text('/* Configuration supplied by autoconf.h. */\n')
    (out/'soc.h').write_text('#define NR_IRQS 32\n')
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    subprocess.run([pre+'gcc','-mcpu=ck804ef','-mhard-float','-I',str(out),'-c',str(out/'spl_start.S'),'-o',str(out/'reset.o')],check=True)
    subprocess.run([pre+'objcopy','--set-section-flags=.spl.vectors=alloc,load,readonly,data',str(out/'reset.o')],check=True)
    ld='''SECTIONS {
.vectors 0x10000000 : { *(.spl.vectors) }
.reset 0x10000100 : { *(.text) }
}
spl_board_init_r = 0x10000df0;
reset_handler = 0x10003100;
'''
    (out/'reset.ld').write_text(ld);path=out/'reset.elf'
    subprocess.run([pre+'ld','-T',str(out/'reset.ld'),str(out/'reset.o'),'-o',str(path)],check=True)
    elf=Elf32(path.read_bytes(),'reset');stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    assert not any(s['name'] and s['section']==0 for s in elf.symbols())
    assert not any(elf.relocations(s['index']) for s in elf.sections)
    vectors=next(s for s in elf.sections if s['name']=='.vectors');reset=next(s for s in elf.sections if s['name']=='.reset')
    assert elf.contents(vectors)==struct.pack('<64I',0x10000100,*([0x10000130]*63))==stock[0x38954:0x38a54]
    assert reset['size']==54 and elf.contents(reset)==stock[0x38a54:0x38a8a]
    (out/'reset.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(path)],text=True))
    report={'upstream_evidence':evidence,'upstream_commit':SDK_COMMIT,'upstream_path':rel,'upstream_blob':blob,'source_sha256':sha(source),'elf_sha256':sha(path.read_bytes()),'vectors_bytes':256,'reset_bytes':54,'stock_byte_exact':True,'source_admitted':False,'limits':['Unmodified authenticated upstream assembly with recovered IRQ count and stack configuration. All vector/reset/default/empty-hook bytes match stock. Dispatcher and later-image reset are explicit absolute link dependencies here. Hardware processor control, fallback-image lifetime and full firmware admission remain pending.']}
    (ROOT/'docs/research/gx8002-stage1-reset.json').write_text(json.dumps(report,indent=2)+'\n');return report


if __name__=='__main__':print(build()['stock_byte_exact'])
