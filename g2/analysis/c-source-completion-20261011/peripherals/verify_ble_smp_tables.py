#!/usr/bin/env python3
"""Pinned Cordio table rows/action names versus authenticated native interfaces."""
from pathlib import Path
import re,subprocess,tempfile
from elftools.elf.elffile import ELFFile
R=Path(__file__).resolve().parents[3]
BASE=0x438000
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
V=R.parent/'third-party/local-vendor/sources/AmbiqSuite_R3.2.0/third_party/cordio'
D=R/'research/corpus/apollo-main/ghidra/open-2026-09-29/decomp'
OPTIONS=[('-I'+str(V/'ble-host/include')),('-I'+str(V/'ble-host/sources/stack/smp')),
         ('-I'+str(V/'ble-host/sources/stack/cfg')),('-I'+str(V/'wsf/include')),
         ('-I'+str(V/'wsf/sources')),('-I'+str(V/'wsf/sources/port/freertos'))]
ITEMS=[('smpi_sm.c','smpiStateTbl','smpiStateTblCommon','smpiActionTbl',0x78c344),
       ('smpi_sc_sm.c','smpiScStateTbl','smpiScStateTblCommon','smpiScActionTbl',0x78c320),
       ('smpr_sm.c','smprStateTbl','smprStateTblCommon','smprActionTbl',0x78c4ac),
       ('smpr_sc_sm.c','smprScStateTbl','smprScStateTblCommon','smprScActionTbl',0x78c470)]
def word(a):return int.from_bytes(B[a-BASE:a-BASE+4],'little')
rows=actions=0
with tempfile.TemporaryDirectory() as td:
 for filename,table_name,common_name,action_name,interface in ITEMS:
  obj=Path(td)/(filename+'.o')
  subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2',
                  '-Wall','-Wextra','-Werror',*OPTIONS,'-c',
                  str(V/'ble-host/sources/stack/smp'/filename),'-o',str(obj)],check=True)
  with obj.open('rb') as f:
   elf=ELFFile(f);symbols=elf.get_section_by_name('.symtab')
   by_name={s.name:s for s in symbols.iter_symbols()}
   table,common,action=[by_name[x] for x in (table_name,common_name,action_name)]
   ro=elf.get_section(table['st_shndx']).data()
   rel=next(s for s in elf.iter_sections() if s.name=='.rel.rodata')
   names={r['r_offset']:symbols.get_symbol(r['r_info_sym']).name for r in rel.iter_relocations()}
   stock_rows,stock_actions,stock_common=[word(interface+4*i) for i in range(3)]
   local=ro[common['st_value']:common['st_value']+common['st_size']]
   assert local==B[stock_common-BASE:stock_common-BASE+len(local)],(filename,'common')
   for i in range(table['st_size']//4):
    offset=int.from_bytes(ro[table['st_value']+4*i:table['st_value']+4*i+4],'little')
    row=next((s for s in symbols.iter_symbols() if s['st_shndx']==table['st_shndx'] and
              s['st_value']==offset and s['st_size']>0),None)
    assert row is not None,(filename,i,'row symbol')
    native=word(stock_rows+4*i)
    local=ro[offset:offset+row['st_size']]
    assert local==B[native-BASE:native-BASE+len(local)],(filename,i,'row mismatch')
    rows+=1
   for i in range(action['st_size']//4):
    expected=names[action['st_value']+4*i]
    address=word(stock_actions+4*i)&~1
    source=(D/f'{address:08x}.c').read_text().split('{',1)[0]
    found=re.findall(r'([A-Za-z_][A-Za-z_0-9]*)\s*\(',source)
    assert found and found[-1]==expected,(filename,i,expected,found)
    actions+=1
print(f'PASS_BLE_SMP_TABLES_NAMED {rows} rows {actions} actions 4 common tables')
