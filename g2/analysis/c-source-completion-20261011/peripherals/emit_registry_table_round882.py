#!/usr/bin/env python3
"""Emit symbolic C for the authenticated 43-row Apollo UI registry."""
from pathlib import Path
import hashlib,struct
root=Path(__file__).resolve().parents[3]
image=root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
blob=image.read_bytes()[32:]
assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
begin,end=0x6a44b0,0x6a4760
assert (end-begin)==43*16
rows=[struct.unpack_from('<4I',blob,begin-0x438000+i*16) for i in range(43)]
callbacks=sorted({v&~1 for row in rows for v in row[1:3] if v})
contexts=sorted({row[3] for row in rows if row[3]})
assert len(callbacks)==64
lines=['/* Authenticated Apollo UI registry 0x6a44b0..0x6a475f.\n'
       ' * Function declarations provide address relocations only; callback ABI\n'
       ' * and RAM context ownership must be established per entry. */',
       '#include <stdint.h>','',
       'struct audio_uart_ui_registry_row {',
       '    uint32_t id; uintptr_t primary; uintptr_t secondary; uintptr_t context;',
       '};',
       '_Static_assert(sizeof(struct audio_uart_ui_registry_row)==16u,"registry row ABI");','']
for addr in callbacks:lines.append(f'extern uint32_t audio_uart_registry_callback_{addr:x}();')
lines.append('')
for addr in contexts:lines.append(f'extern uint8_t audio_uart_registry_context_{addr:08x};')
lines.extend(['','const struct audio_uart_ui_registry_row audio_uart_display_registry_begin[43]={'])
def cb(value):return f'(uintptr_t)&audio_uart_registry_callback_{value&~1:x}' if value else '0u'
def ctx(value):return f'(uintptr_t)&audio_uart_registry_context_{value:08x}' if value else '0u'
for index,(id_,primary,secondary,context) in enumerate(rows):
 lines.append(f'    /* {index:02d} native 0x{begin+index*16:06x} */ '
              f'{{0x{id_:x}u,{cb(primary)},{cb(secondary)},{ctx(context)}}},')
lines.extend(['};',
              '_Static_assert(sizeof(audio_uart_display_registry_begin)==43u*16u,"registry byte count");',
              '/* One-past-end section-relative alias; a linker absolute defsym',
              ' * would lose the table relocation in the final image. */',
              '__asm__(".globl audio_uart_display_registry_end\\n"',
              '        ".set audio_uart_display_registry_end, audio_uart_display_registry_begin + 688");',
              ''])
target=root/'components/audio/uart_thread_source_candidate/ui_registry_table.c'
target.write_text('\n'.join(lines))
print('EMITTED_SYMBOLIC_UI_REGISTRY',len(rows),len(callbacks),len(contexts),target.relative_to(root))
