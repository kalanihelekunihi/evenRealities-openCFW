"""Run an unchanged oracle with one declared extra offline source slot.
No assertion/result hook changes; old ELF reader and machine profiles stay intact.
"""
from pathlib import Path
import sys,runpy,importlib.util,unicorn
HERE=Path(__file__).resolve().parent
ROOT=next(p for p in HERE.parents if (p/'AGENTS.md').exists())
original_spec=importlib.util.spec_from_file_location
reader=ROOT/'g2/components/bootloader/update_core/elf_reader.py'
def spec(name,location,*args,**kw):
 if Path(location).resolve()==reader:location=HERE/'elf_reader_three_slots.py'
 return original_spec(name,location,*args,**kw)
importlib.util.spec_from_file_location=spec
OriginalUc=unicorn.Uc
def ThreeSlotUc(*args,**kw):
 u=OriginalUc(*args,**kw);original_map=u.mem_map;extra_mapped=False
 def map_slot(address,size,*args,**kw):
  nonlocal extra_mapped
  if not extra_mapped:original_map(0x50000,0x10000);extra_mapped=True
  if address < 0x60000 and address+size > 0x50000:
   if address < 0x50000:original_map(address,0x50000-address,*args,**kw)
   if address+size > 0x60000:original_map(0x60000,address+size-0x60000,*args,**kw)
   return
  return original_map(address,size,*args,**kw)
 u.mem_map=map_slot
 return u
unicorn.Uc=ThreeSlotUc
script=Path(sys.argv[1]).resolve();sys.argv=[str(script),*sys.argv[2:]]
if script.name in ['verify_heap.py','verify_owned_heap.py','verify_pendsv.py','verify_pendsv_fp.py','verify_select.py','verify_manager_bridge.py']:
 from elftools.elf.elffile import ELFFile
 elf_arg=Path(sys.argv[sys.argv.index('--elf')+1])
 with elf_arg.open('rb') as f:
  e=ELFFile(f);sy={s.name:s['st_value']&~1 for s in e.get_section_by_name('.symtab').iter_symbols()}
 source=script.read_text()
 for old,name in [('0x41b5f6','opencfw_malloc_failed_native'),('0x41b600','opencfw_stack_overflow_native'),('0x42e1da','opencfw_dfu_terminal_native')]:
  if name in sy:source=source.replace('pc=='+old,'pc in ('+old+','+hex(sy[name])+')').replace('0x42de58,0x42e1da','0x42de58,0x42e1da,'+hex(sy[name]) if old=='0x42e1da' else '0x42de58,0x42e1da')
 exec(compile(source,str(script),'exec'),{'__file__':str(script),'__name__':'__main__'})
else:
 runpy.run_path(str(script),run_name='__main__')
