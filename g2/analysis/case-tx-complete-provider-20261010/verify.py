"""Exact stock weak TX-completion body and compiled source proof."""
from pathlib import Path
import hashlib,json,subprocess
from elftools.elf.elffile import ELFFile
D=Path(__file__).resolve().parent;R=D.parents[2]
source=R/'g2/components/case/source_candidate_20261010/tx_complete_provider.c'
firmware=R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin'
fw=firmware.read_bytes();fw_hash=hashlib.sha256(fw).hexdigest()
assert fw_hash=='36ca0c13558f252af286ae2b36b5e576d087d21d37b15d778e7da9f502a70374'
stock=fw[32+0x6776:32+0x6778]
assert stock==bytes.fromhex('7047')
obj=D/'tx_complete_provider.o'
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-mfloat-abi=soft','-std=c11','-Os','-ffreestanding','-fno-builtin','-ffunction-sections','-fdata-sections','-Wall','-Wextra','-Werror','-c',str(source),'-o',str(obj)],check=True)
with obj.open('rb') as f:
    e=ELFFile(f)
    section=e.get_section_by_name('.text.case_tx_complete_provider')
    assert section is not None
    compiled=section.data()
assert compiled==stock,(compiled.hex(),stock.hex())
out={'status':'PASS','stock_address':'0x08006776','stock_bytes':stock.hex(),'compiled_bytes':compiled.hex(),'firmware_sha256':fw_hash,'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'object_sha256':hashlib.sha256(obj.read_bytes()).hexdigest(),'body_contract':'weak no-op; R0 ignored; bx lr'}
(D/'results.json').write_text(json.dumps(out,indent=2)+'\n')
print('PASS exact 2-byte TX-completion stock/source body')
