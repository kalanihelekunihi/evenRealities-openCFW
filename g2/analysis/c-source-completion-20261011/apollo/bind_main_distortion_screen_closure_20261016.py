#!/usr/bin/env python3
"""Bind verified distortion UI C, six style wrappers, and authenticated assets."""
import hashlib
import json
import subprocess
from pathlib import Path

from elftools.elf.elffile import ELFFile
from elftools.elf.relocation import RelocationSection

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / 'g2'
SOURCES = (
    G2 / 'components/audio/uart_thread_source_candidate/display_distortion_style_wrappers.c',
    G2 / 'components/audio/uart_thread_source_candidate/distortion_screen_event_5cf330.c',
    G2 / 'components/audio/uart_thread_source_candidate/distortion_screen_assets.c',
)
HEADER = G2 / 'components/audio/uart_thread_source_candidate/distortion_screen_assets.h'
BASE = G2 / 'build/c-firmware/20261015/main-test-screen-registry-context-min/apollo-main-test-screen-registry-context-min.o'
CALLBACK_ORACLE = G2 / 'build/c-firmware/20261016/main-distortion-screen-event-5cf330/oracle-receipt.json'
STYLE_ORACLE = G2 / 'build/c-firmware/20261016/main-distortion-style-wrappers/oracle-receipt.json'
PAYLOAD = G2 / 'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
PAYLOAD_SHA = '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
OUT = G2 / 'build/c-firmware/20261016/main-distortion-screen-closure'
OWNED = {f'audio_uart_page_{a:x}' for a in (0x441246, 0x441254, 0x44130c,
                                                0x44142e, 0x48ba78, 0x48ba92)} | {
    'audio_uart_registry_callback_5cf330',
    'audio_uart_distortion_asset_769f58',
    'audio_uart_distortion_text_736af4',
    'audio_uart_distortion_text_736b24',
    'audio_uart_distortion_root_2007487c',
}

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def symbols(path, flag):
    return {line.split()[-1] for line in subprocess.check_output(
        ['arm-none-eabi-nm', '-g', flag, str(path)], text=True).splitlines()}

def symbol_bytes(elf, name):
    symtab = elf.get_section_by_name('.symtab')
    sym = next(s for s in symtab.iter_symbols() if s.name == name)
    section = elf.get_section(sym['st_shndx'])
    return section.data()[sym['st_value']:sym['st_value'] + sym['st_size']], sym

def verify_assets(obj, image):
    with obj.open('rb') as f:
        elf = ELFFile(f)
        descriptor, d = symbol_bytes(elf, 'audio_uart_distortion_asset_769f58')
        pixels, p = symbol_bytes(elf, 'distortion_screen_pixels')
        first, t1 = symbol_bytes(elf, 'audio_uart_distortion_text_736af4')
        second, t2 = symbol_bytes(elf, 'audio_uart_distortion_text_736b24')
        root, r = symbol_bytes(elf, 'audio_uart_distortion_root_2007487c')
        stock_descriptor = image[0x769f58 - 0x438000:0x769f58 - 0x438000 + 28]
        stock_pixels = image[0x6abac0 - 0x438000:0x6abac0 - 0x438000 + 576]
        if len(descriptor) != 28 or descriptor[:16] != stock_descriptor[:16] or \
                descriptor[20:] != stock_descriptor[20:] or len(pixels) != 576 or \
                pixels != stock_pixels or len(first) != 47 or len(second) != 47 or \
                first != image[0x736af4-0x438000:0x736af4-0x438000+47] or \
                second != image[0x736b24-0x438000:0x736b24-0x438000+47] or \
                r['st_size'] != 4 or r['st_info']['type'] != 'STT_OBJECT':
            raise RuntimeError('source-owned distortion asset bytes or RAM cell changed')
        relocs = [s for s in elf.iter_sections() if isinstance(s, RelocationSection)
                  and s['sh_info'] == d['st_shndx']]
        # The only pointer field in the descriptor targets the local pixel array.
        if len(relocs) != 1:
            raise RuntimeError('distortion descriptor relocation section changed')
        offsets = [r['r_offset'] for r in relocs[0].iter_relocations()]
        if offsets != [d['st_value'] + 16] or int.from_bytes(descriptor[16:20], 'little') != p['st_value']:
            raise RuntimeError('distortion pixel pointer relocation changed')
        return {'descriptor_stock_sha256': hashlib.sha256(stock_descriptor).hexdigest(),
                'pixel_bytes': 576, 'pixel_sha256': hashlib.sha256(pixels).hexdigest(),
                'string_stock_sha256': [hashlib.sha256(first).hexdigest(),
                                        hashlib.sha256(second).hexdigest()],
                'root_observed_bytes': 4}

def main():
    image = PAYLOAD.read_bytes()[32:]
    if hashlib.sha256(image).hexdigest() != PAYLOAD_SHA:
        raise RuntimeError('stock Apollo main payload changed')
    callback = json.loads(CALLBACK_ORACLE.read_text())
    style = json.loads(STYLE_ORACLE.read_text())
    if callback['status'] != 'PASS_NATIVE_MAIN_DISTORTION_SCREEN_EVENT_5CF330' or \
            callback['cases'] != 28 or callback['source_sha256'] != sha(SOURCES[1]) or \
            style['status'] != 'PASS_NATIVE_MAIN_DISTORTION_STYLE_WRAPPERS' or \
            style['cases'] != 48 or style['source_sha256'] != sha(SOURCES[0]):
        raise RuntimeError('native/C distortion or style evidence changed')
    OUT.mkdir(parents=True, exist_ok=True)
    objects = []
    for source in SOURCES:
        obj = OUT / (source.stem + '.o')
        subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4', '-mthumb',
                        '-std=c11', '-ffreestanding', '-fno-builtin', '-O2', '-Wall',
                        '-Wextra', '-Werror', '-c', str(source), '-o', str(obj)], check=True)
        objects.append(obj)
    asset = verify_assets(objects[2], image)
    defined = set().union(*(symbols(obj, '--defined-only') for obj in objects))
    if defined != OWNED:
        raise RuntimeError(f'distortion source ownership changed: {defined ^ OWNED}')
    before = symbols(BASE, '-u')
    if len(before) != 183 or 'audio_uart_registry_callback_5cf330' not in before:
        raise RuntimeError('Apollo main base frontier changed')
    linked = OUT / 'apollo-main-distortion-screen-closure.o'
    subprocess.run(['arm-none-eabi-ld', '-r', str(BASE), *(str(o) for o in objects),
                    '-o', str(linked)], check=True)
    after = symbols(linked, '-u')
    if before - after != {'audio_uart_registry_callback_5cf330'} or after - before or len(after) != 182:
        raise RuntimeError('Apollo main distortion link frontier changed')
    receipt = {'status': 'PASS_EXPERIMENTAL_MAIN_DISTORTION_SCREEN_C_CLOSURE',
               'source_files': [{'path': str(s.relative_to(ROOT)), 'sha256': sha(s)} for s in SOURCES],
               'header': str(HEADER.relative_to(ROOT)), 'header_sha256': sha(HEADER),
               'official_payload_sha256': PAYLOAD_SHA,
               'callback_oracle': str(CALLBACK_ORACLE.relative_to(ROOT)),
               'callback_oracle_sha256': sha(CALLBACK_ORACLE),
               'style_oracle': str(STYLE_ORACLE.relative_to(ROOT)),
               'style_oracle_sha256': sha(STYLE_ORACLE),
               'asset': asset,
               'source_owned_symbols': sorted(OWNED),
               'objects': [{'path': str(o.relative_to(ROOT)), 'sha256': sha(o)} for o in objects],
               'base_object': str(BASE.relative_to(ROOT)), 'base_sha256': sha(BASE),
               'linked_object': str(linked.relative_to(ROOT)), 'linked_sha256': sha(linked),
               'unresolved_before': 183, 'unresolved_after': 182,
               'imports_resolved': ['audio_uart_registry_callback_5cf330'], 'imports_added': [],
               'source_complete': False, 'full_payload_linked': False, 'hardware_proof': False,
               'limits': ['Lower page/style calls were controlled in native comparisons.',
                          'The 24x24 asset and two strings match authenticated stock data, with relocatable pixel pointer.',
                          'Final RAM placement, complete UI state, whole-image layout and hardware behavior remain open.']}
    path = OUT / 'receipt.json'
    path.write_text(json.dumps(receipt, indent=2) + '\n')
    print(receipt['status'], 183, 182, sha(path))

if __name__ == '__main__': main()
