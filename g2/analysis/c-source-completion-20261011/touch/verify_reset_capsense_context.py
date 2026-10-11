#!/usr/bin/env python3
"""Bounded LP32 typed context pointer table and stock reset-copy comparison."""
from pathlib import Path
import hashlib,json,subprocess,tempfile
ROOT=Path(__file__).resolve().parents[4]
HERE=Path(__file__).resolve().parent
SRC=ROOT/'g2/components/touch/reset_layout_candidate_20261010/reset_capsense_context.c'
FIRMWARE=ROOT/'g2/blobs/official/g2-2.2.6.10/firmware_touch.bin'
LOCKED='0d13d8bb1337bf22989dc16143e3d5eca29a31cc1ed753ff624668750ea9470d'
blob=FIRMWARE.read_bytes();assert hashlib.sha256(blob).hexdigest()==LOCKED
image=blob[32:]
symbols={
 'touch_generated_common_config':0xb2a8,
 'touch_reset_common':0x20000528,
 'touch_generated_internal_context':0x20000c50,
 'touch_generated_widget_config':0xb0f8,
 'touch_reset_widgets':0x20000548,
 'touch_generated_pin_config':0xb34c,
 'touch_shield_pins_rom_b33c':0xb33c,
 'touch_generated_active_scan_sns':0x20000c38,
 'touch_generated_base_frame_context':0x20000b38,
 'touch_generated_sensor_frame_context':0x20000aac,
 'touch_generated_lp_sensor_frame_context':0x200009fc,
 'touch_reset_active_descriptors':0x20000818,
 'touch_reset_lp_descriptors':0x20000808,
 'touch_generated_lp_history':0x2000065e,
}
with tempfile.TemporaryDirectory(prefix='touch-context-') as tmp:
 d=Path(tmp);obj=d/'context.o';pmobj=d/'pm.o';elf=d/'context.elf';raw=d/'context.bin'
 subprocess.run(['clang','--target=armv6m-none-eabi','-mcpu=cortex-m0plus','-mthumb','-ffreestanding','-fno-builtin','-std=c11','-Wall','-Wextra','-Werror','-ffunction-sections','-fdata-sections','-c',str(SRC),'-o',str(obj)],check=True)
 subprocess.run(['clang','--target=armv6m-none-eabi','-mcpu=cortex-m0plus','-mthumb','-ffreestanding','-fno-builtin','-std=c11','-Wall','-Wextra','-Werror','-ffunction-sections','-fdata-sections','-c',str(ROOT/'g2/components/touch/reset_layout_candidate_20261010/reset_app_pm.c'),'-o',str(pmobj)],check=True)
 args=['arm-none-eabi-ld','--gc-sections','-T',str(HERE/'reset_capsense_alignment.ld'),str(obj),str(pmobj),'-o',str(elf)]
 for name,value in symbols.items():args+=['--defsym',f'{name}={value:#x}']
 subprocess.run(args,check=True)
 subprocess.run(['arm-none-eabi-objcopy','--dump-section',f'.touch_init.app_context={raw}',str(elf)],check=True)
 data=raw.read_bytes();expected=image[0xb5b4-0x3300:0xb5b4-0x3300+64]
 assert len(data)==64 and data==expected,(data.hex(),expected.hex())
 report={'status':'PASS_BOUNDED_TYPED_CONTEXT','firmware_sha256':LOCKED,'source_sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),'context_bytes':60,'natural_alignment_bytes':2,'newly_attributed_pointer_bytes':52,'existing_selected_slot_pointer_bytes':8,'external_pointees':symbols,'limits':['Pointer values and 15-field layout match stock using authenticated fixed-address fixture symbols. Pointee bodies/configuration and final relocation are not source-owned by this test.','Two padding bytes at RAM0x200004ea are produced by natural four-byte alignment after the already selected threshold; the 426-byte history allocation extent remains unowned.','This experimental whole-table unit overlaps two selected slot-link definitions and is not integrated into the current Touch candidate.']}
 (HERE/'reset-capsense-context-receipt.json').write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps({'status':report['status'],'context_bytes':60,'newly_attributed_pointer_bytes':52,'alignment_bytes':2}))
