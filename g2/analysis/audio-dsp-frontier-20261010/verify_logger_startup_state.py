#!/usr/bin/env python3
"""Bounded stock reset-constructor oracle for short logger RAM state."""
from pathlib import Path
import hashlib, json, struct
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_MEM_WRITE
from unicorn.arm_const import UC_ARM_REG_R0, UC_ARM_REG_R9, UC_ARM_REG_SP, UC_ARM_REG_LR, UC_ARM_REG_PC

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
IMAGE = ROOT / 'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
blob = IMAGE.read_bytes()
assert hashlib.sha256(blob).hexdigest() == '36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863'
def word_at(addr):
    return struct.unpack_from('<I', blob, addr - 0x437fe0)[0]
assert word_at(0x438004) == 0x5e4233
assert [(hex(a), hex(word_at(a))) for a in (0x75d3c8, 0x75d3e0, 0x75d3f0, 0x75d400)] == [
    ('0x75d3c8', '0xffe9cc57'), ('0x75d3e0', '0xffcdcd3f'),
    ('0x75d3f0', '0xffcdcd2f'), ('0x75d400', '0xffcdcd1f')]
assert tuple(word_at(a) for a in (0x75d3cc, 0x75d3d0, 0x75d3d4, 0x75d3d8, 0x75d3dc)) == (
    0x70af0, 0x20004558, 0x240fd4, 0x2013be70, 0)
assert tuple(word_at(a) for a in (0x75d3f4, 0x75d3f8, 0x75d3fc)) == (0x344aa, 0x54e0, 0x20000000)
assert tuple(word_at(a) for a in (0x75d404, 0x75d408, 0x75d40c)) == (0x322f3, 0x434e, 0x20080000)

u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
u.mem_map(0x437000, ((len(blob) + 0xfe0 + 0xfff) // 0x1000) * 0x1000)
u.mem_write(0x437fe0, blob)
u.mem_map(0x10000000, 0x1000)
u.mem_map(0x20000000, 0x4000000)
u.reg_write(UC_ARM_REG_SP, 0x203ff000)
u.reg_write(UC_ARM_REG_R9, 0)
u.reg_write(UC_ARM_REG_LR, 0x10000001)
u.mem_write(0x200004c8, b'\xa5' * 16)
u.mem_write(0x20074f9f, b'\xa5')
u.mem_write(0x20074fa1, b'\xa5')
u.mem_write(0x20075048, b'\xa5')
u.mem_write(0x2037ce44, b'\xa5')

def invoke(pc, descriptor, count):
    writes = []
    def hook(_emu, access, address, size, value, _user):
        writes.append((address, size))
    handle = u.hook_add(UC_HOOK_MEM_WRITE, hook)
    u.reg_write(UC_ARM_REG_R0, descriptor)
    u.reg_write(UC_ARM_REG_LR, 0x10000001)
    u.emu_start(pc | 1, 0x10000000, count=count)
    u.hook_del(handle)
    assert u.reg_read(UC_ARM_REG_PC) == 0x10000000
    return u.reg_read(UC_ARM_REG_R0), writes

zero_next, zero_writes = invoke(0x5fa01e, 0x75d3cc, 15_000_000)
assert zero_next == 0x75d3e0
assert u.mem_read(0x20074f9f, 1) == b'\0'
assert u.mem_read(0x20074fa1, 1) == b'\0'
assert u.mem_read(0x200004c8, 16) == b'\xa5' * 16
assert u.mem_read(0x20075048, 1) == b'\xa5'
assert u.mem_read(0x2037ce44, 1) == b'\xa5'

copy_next, copy_writes = invoke(0x43a11e, 0x75d3f4, 20_000_000)
assert copy_next == 0x75d400
ring = bytes(u.mem_read(0x200004c8, 16))
assert ring == bytes.fromhex('d8cb0c20008000000000000000000000')
assert u.mem_read(0x20074f9f, 1) == b'\0'
low_writes = [(a, n) for a, n in copy_writes if 0x20000000 <= a < 0x20010000]
assert min(a for a, _ in low_writes) == 0x20000000
assert max(a + n for a, n in low_writes) == 0x20004558
low_sha = hashlib.sha256(bytes(u.mem_read(0x20000000, 0x4558))).hexdigest()
u.mem_write(0x200ccbd8, b'\xa5' * 0x8000)
shared_next, shared_writes = invoke(0x43a11e, 0x75d404, 30_000_000)
assert shared_next == 0x75d410
assert bytes(u.mem_read(0x200ccbd8, 0x8000)) == bytes(0x8000)
assert bytes(u.mem_read(0x200004c8, 16)) == ring
receipt = {
    'status': 'PASS', 'image_sha256': hashlib.sha256(blob).hexdigest(),
    'reset_vector': '0x5e4233', 'constructor_table': '0x75d3c8',
    'zero': {'entry': '0x5fa01e', 'descriptor': '0x75d3cc', 'next': hex(zero_next),
             'ranges': [['0x20004558', '0x20075048'], ['0x2013be70', '0x2037ce44']],
             'sequence_0x20074f9f': 0, 'policy_0x20074fa1': 0,
             'low_ring_unchanged': True, 'write_count': len(zero_writes)},
    'low_ram_decompress': {'entry': '0x43a11e', 'descriptor': '0x75d3f4',
                           'next': hex(copy_next), 'source_offset': '0x344aa',
                           'encoded_length': '0x54e0', 'destination': '0x20000000',
                           'written_range': ['0x20000000', '0x20004558'],
                           'output_sha256': low_sha, 'write_count': len(copy_writes)},
    'ring_descriptor_0x200004c8': {'base': '0x200ccbd8', 'capacity': 32768,
                                   'read': 0, 'write': 0, 'raw_hex': ring.hex()},
    'shared_ram_decompress': {'entry': '0x43a11e', 'descriptor': '0x75d404',
                              'next': hex(shared_next), 'destination': '0x20080000',
                              'ring_storage': ['0x200ccbd8', '0x200d4bd8'],
                              'ring_storage_zeroed': True,
                              'write_count': len(shared_writes)},
    'limits': 'Stock constructor execution proves runtime bytes, not source ownership of the compressed initialized payload or complete boot ordering.'
}
(HERE / 'logger-startup-state-receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
print('PASS', receipt['ring_descriptor_0x200004c8'], low_sha)
