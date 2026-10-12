#!/usr/bin/env python3
"""Bound startup GPIO callback roots through the 97 stock/source descriptors."""
from pathlib import Path
import hashlib,json,struct
from elftools.elf.elffile import ELFFile

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
STOCK=ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin'
SOURCE=ROOT/'g2/components/bootloader/initializer_callbacks/gpio_descriptor_data.c'
REGISTRAR=ROOT/'g2/components/bootloader/initializer_callbacks/gpio_descriptors.c'
ELF=HERE/'boot-coplacement-spot-callback-identity-round/boot.elf'
stock=STOCK.read_bytes()[0x42f674-0x410000:][:97*12]
with ELF.open('rb') as stream:
 elf=ELFFile(stream)
 symbol=next(s for s in elf.get_section_by_name('.symtab').iter_symbols()
             if s.name=='opencfw_boot_gpio_descriptors')
 assert symbol['st_size']==97*12
 segment=next(s for s in elf.iter_segments() if s['p_type']=='PT_LOAD' and
              s['p_vaddr']<=symbol['st_value']<s['p_vaddr']+s['p_filesz'])
 source=segment.data()[symbol['st_value']-segment['p_vaddr']:][:97*12]
assert source==stock
rows=[struct.unpack_from('<IBBBBI',stock,12*i) for i in range(97)]
nonzero_modes=[i for i,row in enumerate(rows) if row[3]]
nonzero_callbacks=[i for i,row in enumerate(rows) if row[5]]
assert not nonzero_modes and not nonzero_callbacks
registrar=REGISTRAR.read_text()
assert 'if(rows[i].interrupt_mode && rows[i].callback)' in registrar
assert '(void)opencfw_boot_gpio_callback_register(0,pin,rows[i].callback,0)' in registrar
receipt={
 'status':'PASS_BOUNDED_GPIO_STARTUP_INDIRECT_ROOT_ABSENCE',
 'descriptor_count':97,'descriptor_bytes':len(stock),
 'stock_descriptor_sha256':hashlib.sha256(stock).hexdigest(),
 'source_elf_descriptor_sha256':hashlib.sha256(source).hexdigest(),
 'source_descriptor_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
 'selected_registrar_sha256':hashlib.sha256(REGISTRAR.read_bytes()).hexdigest(),
 'selected_elf_sha256':hashlib.sha256(ELF.read_bytes()).hexdigest(),
 'nonzero_interrupt_mode_rows':nonzero_modes,
 'nonzero_callback_rows':nonzero_callbacks,
 'startup_registration_predicate':'interrupt_mode && callback',
 'limits':['The stock 97-record descriptor initialization causes no GPIO callback registrations in the selected startup registrar.',
           'External callers may later register runtime GPIO callbacks; this does not enumerate those values or prove interrupt delivery.',
           'Stock/source descriptor bytes and selected C predicate establish only this initialized startup path.'],
}
out=HERE/'boot-gpio-startup-indirect-roots.json'
out.write_text(json.dumps(receipt,indent=2)+'\n')
print(receipt['status'],receipt['descriptor_bytes'])
