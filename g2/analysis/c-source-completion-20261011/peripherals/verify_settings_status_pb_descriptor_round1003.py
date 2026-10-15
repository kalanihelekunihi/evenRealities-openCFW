#!/usr/bin/env python3
"""Check the compiled settings-status nanopb graph against every native node."""
from pathlib import Path
import hashlib, importlib.util, json, struct, subprocess, tempfile
from elftools.elf.elffile import ELFFile

root = Path(__file__).resolve().parents[3]
out = root / 'build/c-firmware/settings-status-pb-descriptor-round1003'
out.mkdir(parents=True, exist_ok=True)
generator = root / 'analysis/c-source-completion-20261011/peripherals/generate_settings_status_pb_descriptor.py'
spec = importlib.util.spec_from_file_location('terminal_descriptor_generator', generator)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
nodes = mod.nodes
src = root / 'components/audio/uart_thread_source_candidate/settings_status_pb_descriptor.c'
base = root / 'build/c-firmware/td-record-build-round1001/apollo-main-td-record-build.o'
obj = out / 'settings_status_pb_descriptor.o'
linked = out / 'apollo-main-settings-status-pb-descriptor.o'
flags = ['clang', '--target=arm-none-eabi', '-mcpu=cortex-m55', '-mthumb',
         '-fshort-enums', '-fno-builtin', '-O2', '-Wall', '-Wextra', '-Werror']
subprocess.run(flags + ['-c', str(src), '-o', str(obj)], check=True)
with tempfile.TemporaryDirectory() as td:
    elf = Path(td) / 'graph.elf'
    subprocess.run(flags[:4] + ['-O2', '-nostdlib', '-Wl,-Ttext=0x100000',
                    '-Wl,-e,audio_settings_status_pb_descriptor', str(src), '-o', str(elf)], check=True)
    with elf.open('rb') as f:
        e = ELFFile(f)
        segs = [(s['p_vaddr'], s.data()) for s in e.iter_segments() if s['p_type'] == 'PT_LOAD']
        symbols = {s.name: s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
    def read(addr, n):
        for start, data in segs:
            if start <= addr and addr + n <= start + len(data):
                return data[addr-start:addr-start+n]
        raise AssertionError((hex(addr), n))
    def u32(addr): return struct.unpack('<I', read(addr, 4))[0]
    def u16(addr): return struct.unpack('<H', read(addr, 2))[0]
    pending = [(0x77772c, symbols['audio_settings_status_pb_descriptor'])]
    seen = set()
    while pending:
        native, compiled = pending.pop(0)
        if native in seen: continue
        seen.add(native)
        count, largest, words, children = nodes[native]
        field_ptr, sub_ptr, default, callback = (u32(compiled + i*4) for i in range(4))
        assert default == callback == 0
        assert (u16(compiled+16), u16(compiled+18), u16(compiled+20)) == (count,0,largest)
        assert [u32(field_ptr + i*4) for i in range(len(words)+1)] == words+[0]
        compiled_children = [u32(sub_ptr + i*4) for i in range(len(children)+1)]
        assert compiled_children[-1] == 0
        assert all(compiled_children[:-1])
        pending.extend(zip(children, compiled_children[:-1]))
    assert len(seen) == len(nodes) == 19
subprocess.run(['arm-none-eabi-ld', '-r', str(base), str(obj), '-o', str(linked)], check=True)
def imports(path):
    return {line.split()[-1] for line in subprocess.check_output(
        ['arm-none-eabi-nm', '-u', str(path)], text=True).splitlines()}
before, after = imports(base), imports(linked)
assert before - after == {'audio_settings_status_pb_descriptor'} and not after - before
receipt = {'round': 1003, 'status': 'PASS_SETTINGS_STATUS_PB_DESCRIPTOR_GRAPH',
           'component': 'Apollo settings status nanopb descriptor graph rooted 0x77772c',
           'source': str(src.relative_to(root)),
           'source_sha256': hashlib.sha256(src.read_bytes()).hexdigest(),
           'generator': str(generator.relative_to(root)),
           'official_image_sha256': hashlib.sha256(mod.blob).hexdigest(),
           'nodes': len(seen),
           'validation': 'M55 strict compile; every compiled descriptor field word, edge, and ABI count matches native graph',
           'linked_object': str(linked.relative_to(root)),
           'linked_sha256': hashlib.sha256(linked.read_bytes()).hexdigest(),
           'unresolved_before': len(before), 'unresolved_after': len(after),
           'whole_image_complete': False, 'hardware_proof': False,
           'gates': ['Absolute ROM/RAM placement and whole-image firmware rebuild remain open',
                     'Native encoder behavior depends on lower selected nanopb and BLE providers']}
(out / 'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
print(receipt['status'], len(seen), len(before), len(after), receipt['linked_sha256'])
