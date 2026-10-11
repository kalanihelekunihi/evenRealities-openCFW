#!/usr/bin/env python3
"""Compare an attributed LP context C initializer against authenticated reset bytes."""
from pathlib import Path
import hashlib,json,subprocess
ROOT=Path(__file__).resolve().parents[4]
HERE=Path(__file__).resolve().parent
OUT=ROOT/'g2/build/touch-reset-common-context-20261011';OUT.mkdir(exist_ok=True)
src=ROOT/'g2/components/touch/reset_layout_candidate_20261010/reset_common_context.c'
obj=OUT/'common.o';data=OUT/'common.bin'
argv=['clang','-target','armv6m-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Og','-ffreestanding','-Wall','-Wextra','-Werror','-c',str(src),'-o',str(obj)]
subprocess.run(argv,check=True)
subprocess.run(['arm-none-eabi-objcopy','--dump-section','.touch_init.common_context='+str(data),str(obj)],check=True)
firmware=ROOT/'g2/blobs/official/g2-2.2.6.10/firmware_touch.bin';blob=firmware.read_bytes()
assert hashlib.sha256(blob).hexdigest()=='0d13d8bb1337bf22989dc16143e3d5eca29a31cc1ed753ff624668750ea9470d'
expected=blob[32+0xb5f4-0x3300:32+0xb5f4-0x3300+32]
assert len(data.read_bytes())==32 and data.read_bytes()==expected
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
receipt={'status':'PASS_TYPED_RESET_CONTEXT_32_BYTES','firmware_sha256':sha(firmware),'source':str(src.relative_to(ROOT)),'source_sha256':sha(src),'object_sha256':sha(obj),'data_sha256':sha(data),'ram_address':'0x20000528','rom_address':'0xb5f4','bytes':32,'vendor_commit':'247a9a0f79eb976f144f5fbeb29488c1c2606517','vendor_header_sha256':sha(HERE/'capsense-v6-reference/cy_capsense_structure.h'),'native_consumers':['0x7e04 tuner/LP clear offsets2,6,22,28','ILO status offset8'],'aggregate_source_owned_reset_bytes':125,'remaining_reset_bytes':839,'limits':['Initializer byte identity only, not full image or physical touch proof.','32-byte ABI matches v4/v5/v6 LP definitions; producing SDK version not uniquely identified.','Other product contexts and pointer relocations remain open.']}
(HERE/'reset-common-context-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt,indent=2))
