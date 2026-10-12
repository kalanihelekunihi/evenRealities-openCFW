#!/usr/bin/env python3
"""Check native ADR/literal loads behind corrected CASE logger callsites."""
from pathlib import Path
import hashlib, json

H = Path(__file__).resolve().parent
R = H.parents[3]
firmware = (R / 'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()
assert hashlib.sha256(firmware).hexdigest() == '36ca0c13558f252af286ae2b36b5e576d087d21d37b15d778e7da9f502a70374'
payload = firmware[32:]
manifest = {int(r['native_address'], 16): r for r in json.loads((H / 'case-semantic-strings.json').read_text())['rows']}
def half(address): return int.from_bytes(payload[address - 0x08000000:address - 0x08000000 + 2], 'little')
def word(address): return int.from_bytes(payload[address - 0x08000000:address - 0x08000000 + 4], 'little')
def adr(address):
    instruction = half(address)
    assert instruction & 0xff00 == 0xa000, (hex(address), hex(instruction))
    return ((address + 4) & ~3) + (instruction & 255) * 4
def ldr(address):
    instruction = half(address)
    assert instruction & 0xff00 == 0x4800, (hex(address), hex(instruction))
    pool = ((address + 4) & ~3) + (instruction & 255) * 4
    return word(pool)
binds = [
    ('adr', 0x08007fac, 0x080081a0, 'application_boot_transport_cb_7f2c_candidate.c'),
    ('ldr', 0x08007ff8, 0x0800d7b8, 'application_boot_transport_cb_7f2c_candidate.c'),
    ('ldr', 0x08008026, 0x0800d828, 'application_boot_transport_cb_7f2c_candidate.c'),
    ('adr', 0x0800804e, 0x080081cc, 'application_boot_transport_cb_7f2c_candidate.c'),
    ('adr', 0x0800807c, 0x080081f4, 'application_boot_transport_cb_7f2c_candidate.c'),
    ('adr', 0x080080b6, 0x0800822c, 'application_boot_transport_cb_7f2c_candidate.c'),
    ('adr', 0x08008122, 0x08008254, 'application_boot_transport_cb_7f2c_candidate.c'),
    ('adr', 0x08008158, 0x08008274, 'application_boot_transport_cb_7f2c_candidate.c'),
    ('adr', 0x0800817e, 0x080082b4, 'application_boot_transport_cb_7f2c_candidate.c'),
    ('adr', 0x08006fb8, 0x08007148, 'application_boot_transport_cb_6e1c_candidate.c'),
    ('adr', 0x08006fd6, 0x08007160, 'application_boot_transport_cb_6e1c_candidate.c'),
    ('adr', 0x08006ffe, 0x08007180, 'application_boot_transport_cb_6e1c_candidate.c'),
    ('adr', 0x0800707e, 0x08007194, 'application_boot_transport_cb_6e1c_candidate.c'),
    ('adr', 0x080070be, 0x080071b4, 'application_boot_transport_cb_6e1c_candidate.c'),
    ('adr', 0x080070da, 0x080071d4, 'application_boot_transport_cb_6e1c_candidate.c'),
    ('ldr', 0x080021d6, 0x0800d648, 'record_dispatch_candidate.c'),
]
for kind, instruction, expected, filename in binds:
    actual = adr(instruction) if kind == 'adr' else ldr(instruction)
    assert actual == expected, (hex(instruction), hex(actual), hex(expected))
    assert expected in manifest, hex(expected)
    source = (R / 'g2/components/case/startup_candidate_20261011' / filename).read_text()
    assert f'CASE_STRING_ADDR({expected:08x})' in source, (filename, hex(expected))
print('PASS_CASE_LOGGER_LITERAL_BINDINGS', len(binds))
