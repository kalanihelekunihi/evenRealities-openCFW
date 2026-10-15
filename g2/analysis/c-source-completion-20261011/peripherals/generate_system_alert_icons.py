#!/usr/bin/env python3
"""Generate source-owned system-alert LVGL icon data from authenticated ROM."""
from pathlib import Path
import hashlib,struct

root=Path(__file__).resolve().parents[3]
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
def span(address,length):return blob[address-0x438000:address-0x438000+length]
assets=(('disconnect',0x7747e4,0x6bb6c0),('connect',0x772928,0x6ba700))
lines=['/* Generated from authenticated Apollo s200 2.2.6.10 ROM. */',
       '#include <stdint.h>',
       'struct g2_icon_descriptor {',
       '    uint32_t header, dimensions, stride, data_size;',
       '    const uint8_t *data;',
       '    uint32_t reserved0, reserved1;',
       '};',
       '_Static_assert(sizeof(struct g2_icon_descriptor)==28,"Apollo icon descriptor size");']
for name,descriptor,data in assets:
    words=struct.unpack('<7I',span(descriptor,28))
    assert words==(0x619,0x00180018,0x18,0x240,data,0,0),(name,words)
    pixel=span(data,0x240)
    assert len(pixel)==0x240
    pixname=f'audio_system_alert_pixels_{name}_{data:06x}'
    dscname=f'audio_system_alert_icon_{name}_{descriptor:06x}'
    lines += [f'const uint8_t {pixname}[0x240]',
              f'    __attribute__((section(".g2.rom.system_alert_pixels_{name}"),used,aligned(4))) = {{']
    for i in range(0,len(pixel),16):
        lines.append('    '+', '.join(f'0x{x:02x}' for x in pixel[i:i+16])+',')
    lines += ['};',f'const struct g2_icon_descriptor {dscname}',
              f'    __attribute__((section(".g2.rom.system_alert_icon_{name}"),used,aligned(4))) = {{',
              f'    0x619u, 0x00180018u, 0x18u, 0x240u, {pixname}, 0u, 0u',
              '};']
source=root/'components/audio/uart_thread_source_candidate/system_alert_icons.c'
source.write_text('\n'.join(lines)+'\n')
print(source,hashlib.sha256(source.read_bytes()).hexdigest())
