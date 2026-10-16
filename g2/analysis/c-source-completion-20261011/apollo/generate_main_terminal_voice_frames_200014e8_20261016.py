#!/usr/bin/env python3
"""Generate C assets for the 19 stock voice animation frames."""
import hashlib,struct
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/'g2'
PAYLOAD=G2/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
SOURCE=G2/'components/audio/uart_thread_source_candidate/terminal_voice_frames_200014e8.c'
PIN='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
FIRST_DESC=0x76bfb8;FIRST_PIXELS=0x6cd2b8;COUNT=19
def main():
 blob=PAYLOAD.read_bytes()[32:]
 if hashlib.sha256(blob).hexdigest()!=PIN:raise RuntimeError('Apollo payload changed')
 frames=[]
 for i in range(COUNT):
  desc=struct.unpack_from('<7I',blob,FIRST_DESC+i*28-0x438000)
  expected=(0x619,0x00100010,0x10,0x100,FIRST_PIXELS+i*256,0,0)
  if desc!=expected:raise RuntimeError(f'frame {i} descriptor changed: {desc}')
  pixels=blob[desc[4]-0x438000:desc[4]-0x438000+256]
  if len(pixels)!=256:raise RuntimeError('truncated pixels')
  frames.append(pixels)
 lines=['/* Exact 19-frame voice animation from pinned Apollo Main stock. */',
        '#include <stdint.h>',
        'struct terminal_voice_frame_descriptor {',
        '    uint32_t header, dimensions, stride, data_size;',
        '    const uint8_t *data;',
        '    uint32_t reserved0, reserved1;',
        '};',
        '_Static_assert(sizeof(struct terminal_voice_frame_descriptor)==28u,',
        '               "Apollo image descriptor size");',
        'const uint8_t audio_terminal_voice_frame_pixels_6cd2b8[19][256] = {']
 for frame in frames:
  lines.append('    {')
  lines.extend('        '+', '.join(f'0x{x:02x}' for x in frame[j:j+16])+',' for j in range(0,256,16))
  lines.append('    },')
 lines += ['};','const struct terminal_voice_frame_descriptor',
           'audio_terminal_voice_frame_descriptors_76bfb8[19] = {']
 lines.extend(f'    {{0x619u,0x00100010u,0x10u,0x100u,audio_terminal_voice_frame_pixels_6cd2b8[{i}],0u,0u}},' for i in range(COUNT))
 lines += ['};','const struct terminal_voice_frame_descriptor *',
           'audio_terminal_voice_style_200014e8[19]',
           '    __attribute__((section(".data.opencfw.terminal.voice_frames"),used,aligned(4))) = {']
 lines.extend(f'    &audio_terminal_voice_frame_descriptors_76bfb8[{i}],' for i in range(COUNT))
 lines += ['};']
 SOURCE.write_text('\n'.join(lines)+'\n')
 print(SOURCE.relative_to(ROOT),hashlib.sha256(SOURCE.read_bytes()).hexdigest())
if __name__=='__main__':main()
