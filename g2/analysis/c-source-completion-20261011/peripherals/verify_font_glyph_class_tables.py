"""Native ROM class slots against target C constant records and relocations."""
from pathlib import Path
import subprocess,tempfile,struct
from elftools.elf.elffile import ELFFile
ROOT=Path(__file__).resolve().parents[3]
source=ROOT/'components/audio/uart_thread_source_candidate/display_font_freetype_glyph_classes.c'
blob=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
base=0x438000
names=[
 ('audio_uart_font_bitmap_glyph_class',0x7601b0),
 ('audio_uart_font_outline_glyph_class',0x7601d0)]
with tempfile.TemporaryDirectory() as d:
    obj=Path(d)/'classes.o'
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb','-O2','-Wall','-Wextra','-Werror','-c',str(source),'-o',str(obj)],check=True)
    with obj.open('rb') as file:
        elf=ELFFile(file);symtab=elf.get_section_by_name('.symtab')
        syms={s.name:s for s in symtab.iter_symbols()}
        ro=elf.get_section_by_name('.rodata').data()
        rel=elf.get_section_by_name('.rel.rodata')
        rels={r['r_offset']:symtab.get_symbol(r['r_info_sym']).name for r in rel.iter_relocations()}
        for name,addr in names:
            offset=syms[name]['st_value'];native=struct.unpack('<8I',blob[addr-base:addr-base+32]);candidate=struct.unpack('<8I',ro[offset:offset+32])
            for i,(a,b) in enumerate(zip(native,candidate)):
                key=offset+i*4
                if 0x520000<=(a&~1)<=0x590000:
                    assert key in rels,(name,i,'missing relocation')
                    assert (a&1)==1,(name,i,'not Thumb')
                    assert rels[key].startswith('audio_uart_font_'),(name,i,rels[key])
                else:assert a==b,(name,i,hex(a),hex(b))
            print('PASS',name,'native',hex(addr),'relocations',sum(offset<=r<offset+32 for r in rels))
        assert len(rels)==10,len(rels)
