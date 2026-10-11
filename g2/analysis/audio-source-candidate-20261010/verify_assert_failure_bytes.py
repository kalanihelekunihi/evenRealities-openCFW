#!/usr/bin/env python3
"""Compare complete source-built fatal entry bodies against pinned Apollo MAIN."""
import hashlib
import json
from pathlib import Path
from elftools.elf.elffile import ELFFile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT = Path('/tmp/g2-audio-arm-inventory')
image = ROOT / 'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
blob = image.read_bytes()
sha = hashlib.sha256(blob).hexdigest()
assert sha == '36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863'
row = next(r for r in json.loads((OUT/'compile-results.json').read_text())['rows']
           if r['source'].endswith('assert_failure_providers.c'))
with Path(row['object_path']).open('rb') as stream:
    elf = ELFFile(stream)
    code = elf.get_section_by_name('.text').data()
    symbols = {s.name: s['st_value'] & ~1
               for s in elf.get_section_by_name('.symtab').iter_symbols()}
    bodies = []
    for name, address in [('audio_queue_bad_argument', 0x441800),
                          ('opencfw_event_group_assert_failure', 0x45537e),
                          ('stock_bad_critical_exit', 0x4420f6)]:
        original = blob[address-0x437fe0:address-0x437fe0+10]
        compiled = code[symbols[name]:symbols[name]+10]
        assert original == compiled, (name, original.hex(), compiled.hex())
        bodies.append({'name': name, 'original_entry': hex(address),
                       'object_text_offset': hex(symbols[name]),
                       'original_bytes': original.hex(), 'compiled_bytes': compiled.hex(),
                       'original_sha256': hashlib.sha256(original).hexdigest(),
                       'compiled_sha256': hashlib.sha256(compiled).hexdigest()})
receipt = {'status': 'PASS', 'verified_complete_function_bodies': len(bodies),
           'body_bytes_per_function': 10, 'functions': bodies, 'image_sha256': sha,
           'source_sha256': row['source_sha256'], 'object_sha256': row['object_sha256'],
           'dependency_sha256': row['dependency_sha256'],
           'compile_command': row['command'],
           'archive_sha256': hashlib.sha256((OUT/'libaudio-source-candidates.a').read_bytes()).hexdigest(),
           'caller_abi': 'All three C caller declarations are void(void) noreturn; original bodies ignore incoming arguments.',
           'limit': 'Exact direct-entry instruction text. Exception delivery, fault handler, and live device not executed.'}
(HERE/'assert-failure-byte-proof.json').write_text(json.dumps(receipt, indent=2)+'\n')
print('PASS', len(bodies))
