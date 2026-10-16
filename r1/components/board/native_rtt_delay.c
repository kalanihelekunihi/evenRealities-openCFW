/* ARM primitive described by pinned nrfx_coredep.h::nrfx_coredep_delay_us.
 * Keep alignment/flags/loop timing explicit in compiler-supported assembly.
 * Source contains mnemonics, not an opaque executable-data array. */
#include <stdint.h>
__attribute__((naked,noinline,aligned(16)))
void r1_rtt_delay_cycles(uint32_t cycles __attribute__((unused)))
{
    __asm__ volatile("1: subs r0, #3\n"
                     "bhi 1b\n"
                     "bx lr\n");
}
