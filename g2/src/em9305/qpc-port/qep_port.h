/* SPDX-License-Identifier: GPL-3.0-or-later
 * QP/C 6.5.1 QEP port for the EM9305 (ARC EM, 32-bit, little endian).
 * Written for this project against the unmodified upstream headers pinned at
 * third-party/upstream/qpc (Quantum Leaps QP/C 6.5.1, commit 416dcec8).
 * Q_SIGNAL_SIZE 2 and 16-bit signals follow the stock QEvt layout (sig u16,
 * poolId_ u8, refCtr_ u8; stock QActive_post_ reads refCtr_ at +3).
 */
#ifndef qep_port_h
#define qep_port_h

#include <stdint.h>
#include <stdbool.h>

/* Stock "fast" types: uint_fast8_t is a byte (QF_maxPool_ is a byte load/store, 0x3111b0 ldb,
 * 0x311026 stb) and uint_fast16_t is a full register (QActive_post_ compares the whole margin
 * register with 0xffff, 0x310e4c brne r15,0xffff, no halfword extension). */
#define uint_fast8_t  uint8_t
#define uint_fast16_t uint32_t

/* Stock Q_onAssert is the returning dispatcher at 0x3117d8 (assert.c). */
void Q_onAssert(char const * const module, int location)
    __asm__("opencfw_em9305_assert");

#include "qep.h"

#endif /* qep_port_h */
