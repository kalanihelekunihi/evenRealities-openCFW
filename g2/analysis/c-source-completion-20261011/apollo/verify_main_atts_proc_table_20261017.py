#!/usr/bin/env python3
"""Match source-owned Cordio ATTS table to authenticated Main low-RAM words."""
import hashlib,subprocess,tempfile,sys,re,json
from pathlib import Path
from elftools.elf.elffile import ELFFile
ROOT=Path(__file__).resolve().parents[4]
SOURCE=ROOT/'g2/components/audio/uart_thread_source_candidate/display_ble_atts_proc_table_2000045c_20261017.c'
VENDOR=ROOT/'third-party/upstream/cordio/ble-host/sources/stack/att/atts_main.c'
DECODE=ROOT/'g2/analysis/c-source-completion-20261011/apollo/decode_main_low_ram_20261016.py'
OUT=ROOT/'g2/build/c-firmware/20261017/main-atts-proc-table/oracle-receipt.json'
NAMES=[None,'attsProcMtuReq','attsProcFindInfoReq','attsProcFindTypeReq',
       'attsProcReadTypeReq','attsProcReadReq','attsProcReadBlobReq',
       'attsProcReadMultReq','attsProcReadGroupTypeReq','attsProcWrite',
       'attsProcWrite','attsProcPrepWriteReq','attsProcExecWriteReq',None,None,
       'attsProcValueCnf','attsProcReadMultiVarReq',None]
ADDR=[0,0x56c6fd,0x56c931,0x56dc05,0x56dd9d,0x56caa9,0x56da9f,
      0x56e0df,0x56e26d,0x5a5e3b,0x5a5e3b,0x5a5fc3,0x5a6171,0,0,
      0x533dd9,0x56cbcb,0]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
sys.path.insert(0,str(DECODE.parent))
from decode_main_low_ram_20261016 import decode
low=decode();stock=[int.from_bytes(low[0x45c+4*i:0x460+4*i],'little') for i in range(18)]
assert stock==ADDR
vendor=VENDOR.read_text();block=vendor.split('attsProcFcn_t attsProcFcnTbl[',1)[1].split('};',1)[0]
rows=[]
for line in block.splitlines():
    match=re.match(r'^\s*(NULL|attsProc\w+)\s*,?\s*(?:/\*.*)?$',line)
    if match:rows.append(None if match.group(1)=='NULL' else match.group(1))
assert rows==NAMES,(rows,NAMES)
with tempfile.TemporaryDirectory() as td:
    elf=Path(td)/'table.elf'
    args=['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11',
          '-O2','-Wall','-Wextra','-Werror','-ffreestanding','-fno-builtin',
          '-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,0']
    args += [f'-Wl,--defsym={name}=0x{ADDR[NAMES.index(name)]:x}' for name in dict.fromkeys(x for x in NAMES if x)]
    subprocess.run([*args,str(SOURCE),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
    with elf.open('rb') as f:
        e=ELFFile(f);section=e.get_section_by_name('.g2_ram_2000045c')
        assert section is not None and section['sh_size']==72
        built=[int.from_bytes(section.data()[4*i:4*i+4],'little') for i in range(18)]
    assert built==stock,(built,stock)
rec={'status':'PASS_MAIN_ATTS_PROC_TABLE_SOURCE_MATCH','entries':18,
     'unique_provider_symbols':len(set(x for x in NAMES if x)),
     'stock_low_ram_sha256':hashlib.sha256(low).hexdigest(),
     'source_sha256':sha(SOURCE),'vendor_sha256':sha(VENDOR),
     'provider_order':NAMES,'stock_words':[f'0x{x:08x}' for x in stock],
     'scope':'Cordio vendor row order, exact stock initialized words after symbolic link, duplicate/null topology',
     'remaining_gate':'Thirteen handler bodies and final RAM relocation/startup remain separate.'}
OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text(json.dumps(rec,indent=2,sort_keys=True)+'\n')
print(rec['status'],rec['entries'],rec['unique_provider_symbols'],sha(OUT))
