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
runpy.run_path(str(script),run_name='__main__')
