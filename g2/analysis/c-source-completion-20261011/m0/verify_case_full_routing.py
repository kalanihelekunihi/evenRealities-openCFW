#!/usr/bin/env python3
"""Exhaustive opcode routing check of the new composition layer only."""
from pathlib import Path
import ctypes
import subprocess

HERE = Path(__file__).resolve().parent
SRC = HERE.parents[2] / 'components/case/legacy_default_candidate_20261010/full_command_candidate.c'
STUB = HERE / 'case_routing_stub.c'
STUB.write_text('''
#include <stdint.h>
#include <stdbool.h>
bool case_legacy_known_dispatch(const uint8_t *p,uint32_t n,uint32_t *r)
{(void)n;*r=0x10000u+p[0];return p[0]!=0xeeu&&p[0]!=0xffu;}
uint32_t case_legacy_ee_prefix(const uint8_t *p,uint32_t n)
{(void)p;(void)n;return 0xee00u;}
uint32_t case_legacy_ff_prefix(const uint8_t *p,uint32_t n)
{(void)p;(void)n;return 0xff00u;}
bool case_binary_known_dispatch(const uint8_t *p,uint32_t n,uint32_t m,uint32_t *r)
{(void)n;(void)m;*r=0x20000u+p[0];return p[2]!=2u||(p[0]!=0x06u&&p[0]!=0x41u);}
uint32_t case_binary_06_41_candidate(const uint8_t *p,uint32_t n)
{(void)n;return p[0]==0x06u?0xee00u:0xff00u;}
uint32_t case_binary_ack0641(uint32_t x){return x;}
''')
LIB = HERE / 'case_routing.so'
subprocess.run(['/usr/bin/clang', '-shared', '-fPIC', str(SRC), str(STUB),
                '-o', str(LIB)], check=True)
lib = ctypes.CDLL(str(LIB))
legacy = lib.case_legacy_command_candidate
binary = lib.case_binary_command_candidate
pointer = ctypes.POINTER(ctypes.c_uint8)
legacy.argtypes = [pointer, ctypes.c_uint32]
legacy.restype = ctypes.c_uint32
binary.argtypes = [pointer, ctypes.c_uint32, ctypes.c_uint32]
binary.restype = ctypes.c_uint32
for opcode in range(256):
    p = (ctypes.c_uint8 * 256)()
    p[0] = opcode
    expected = 0xee00 if opcode == 0xee else 0xff00 if opcode == 0xff else 0x10000+opcode
    assert legacy(p, 0) == expected
    for dest in range(256):
        p[2] = dest
        expected = (0xee00 if opcode == 0x06 else 0xff00) if dest == 2 and opcode in (0x06, 0x41) else 0x20000+opcode
        assert binary(p, 0, 0) == expected, (opcode, dest)
print('PASS_CASE_FULL_ROUTING', 256+256*256)
