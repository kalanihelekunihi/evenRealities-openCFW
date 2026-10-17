#!/usr/bin/env python3
"""Authenticate C title/icon data and descriptor pointer relocation."""
import hashlib,json,struct,subprocess
from pathlib import Path
from elftools.elf.elffile import ELFFile
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/'g2';OUT=G2/'build/c-firmware/20261016/main-conversate-prep-icon-76a47c'
SOURCE=G2/'components/audio/uart_thread_source_candidate/conversate_prep_icon_76a47c.c'
STOCK=G2/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
PAYLOAD_SHA='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 OUT.mkdir(parents=True,exist_ok=True);payload=STOCK.read_bytes()[32:]
 assert hashlib.sha256(payload).hexdigest()==PAYLOAD_SHA
 obj=OUT/'oracle.o'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-O2','-Wall','-Wextra','-Werror','-ffreestanding','-fno-builtin','-c',str(SOURCE),'-o',str(obj)],check=True)
 with obj.open('rb') as stream:
  elf=ELFFile(stream)
  pix=elf.get_section_by_name('.g2_conversate_prep_icon_pixels_6aca80').data()
  icon=elf.get_section_by_name('.g2_conversate_prep_icon_76a47c').data()
  title=elf.get_section_by_name('.g2_conversate_title_label_5b3334').data()
  rel=elf.get_section_by_name('.rel.g2_conversate_prep_icon_76a47c')
  sym=elf.get_section_by_name('.symtab')
  reloc=[(r['r_offset'],r['r_info_type'],sym.get_symbol(r['r_info_sym']).name) for r in rel.iter_relocations()]
 expected_icon=payload[0x76a47c-0x438000:0x76a47c-0x438000+28]
 expected_pix=payload[0x6aca80-0x438000:0x6aca80-0x438000+0x240]
 expected_title=payload[0x5b3334-0x438000:0x5b3338-0x438000]
 if pix!=expected_pix or len(pix)!=0x240 or title!=expected_title or len(title)!=4 or len(icon)!=28 or icon[:16]!=expected_icon[:16] or icon[20:]!=expected_icon[20:] or reloc!=[(16,2,'audio_conversate_prep_icon_pixels_6aca80')]:raise RuntimeError('icon/title fields, pixels or pointer relocation differ from stock')
 record={'status':'PASS_MAIN_CONVERSATE_PREP_ICON_SOURCE_DATA','stock_payload_sha256':PAYLOAD_SHA,'native_icon':'0x76a47c..0x76a497','native_pixels':'0x6aca80..0x6accbf','native_title':'0x5b3334..0x5b3337','source':str(SOURCE.relative_to(ROOT)),'source_sha256':sha(SOURCE),'object':str(obj.relative_to(ROOT)),'object_sha256':sha(obj),'pixel_sha256':sha_bytes(pix),'pointer_relocation':{'offset':16,'type':'R_ARM_ABS32','target':'audio_conversate_prep_icon_pixels_6aca80'},'source_complete':False,'flashable':False,'hardware_proof':False,'limits':['Final absolute placement and whole-image byte equality remain open.']}
 path=OUT/'oracle-receipt.json';path.write_text(json.dumps(record,indent=2,sort_keys=True)+'\n')
 print(record['status'],hashlib.sha256(path.read_bytes()).hexdigest())
def sha_bytes(data):return hashlib.sha256(data).hexdigest()
if __name__=='__main__':main()
