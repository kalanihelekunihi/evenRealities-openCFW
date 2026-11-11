/* SPDX-License-Identifier: GPL-3.0-or-later
 * QP/C 6.5.1 QF port for the EM9305 (ARC EM, preemptive QK kernel).
 * Stock evidence: QF_MAX_ACTIVE 16 (QK_activate_ asserts next >= 17, ready set is a
 * halfword), critical section is "clri r18; sync" ... "seti r18" with the status kept in a
 * callee-saved register (stock 0x310e40/0x310eac), QF_INT_ENABLE/DISABLE are seti 0 / clri 0.
 * QF_LOG2 is the vendor extension instruction log2p1 (major 7, minor 0; vendor
 * apexextensions.s), see qpc-scheduler/log2p1_port.c.
 */
#ifndef qf_port_h
#define qf_port_h

#include <stdint.h>

#define QF_MAX_ACTIVE        16
/* Stock QF_poolInit asserts maxPool < 2 (0x3111b8 brlo r3,2) and sizeof(QMPool) = 20 (mpyuw 0x14);
 * QF_pool_ at 0x801368 ends where QK_attr_ (0x801394) begins. */
#define QF_MAX_EPOOL         2

#define QF_INT_DISABLE()     __asm__ volatile ("clri 0\n\tsync" ::: "memory")
#define QF_INT_ENABLE()      __asm__ volatile ("seti 0" ::: "memory")

#define QF_CRIT_STAT_TYPE    uint32_t
#define QF_CRIT_ENTRY(stat_) __asm__ volatile ("clri %0\n\tsync" : "=r"(stat_) :: "memory")
#define QF_CRIT_EXIT(stat_)  __asm__ volatile ("seti %0" :: "r"(stat_) : "memory")

#ifdef OPENCFW_QEMU_SOFT_LOG2
/* Test-harness only (.waves/qrun.py): QEMU-ARC does not implement the vendor log2p1 extension,
 * so the harness substitutes the arithmetic it is believed to perform (bit length of n). */
static inline uint_fast8_t opencfw_em9305_qf_log2(uint32_t n)
{
    uint_fast8_t r = 0U;
    while (n != 0U) { n >>= 1; ++r; }
    return r;
}
#else
__asm__(".extInstruction log2p1,7,0,SUFFIX_NONE,SYNTAX_2OP");
static inline uint_fast8_t opencfw_em9305_qf_log2(uint32_t n)
{
    uint32_t r;
    __asm__ volatile ("log2p1 %0, %1" : "=r"(r) : "r"(n));
    return (uint_fast8_t)r;
}
#endif
#define QF_LOG2(n_)          opencfw_em9305_qf_log2((uint32_t)(n_))

#include "qep_port.h"
#include "qk_port.h"
#include "qf.h"

#endif /* qf_port_h */
