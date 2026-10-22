/* SPDX-License-Identifier: MIT
 * Image-A initialized clock-source records at 0x10026904 and 0x10026954.
 * Native clock initialization reads each 8-byte {selector, value} record
 * through runtime 0x2002xxxx aliases and passes it to source-select.
 */
#include <stdint.h>

struct gx8002_clock_source_record {
    uint32_t selector;
    uint32_t value;
};
_Static_assert(sizeof(struct gx8002_clock_source_record) == 8,
               "native clock source record ABI");

/* Stock 0x10026904 (gx8002_clock_init_pointer_osc) */
const struct gx8002_clock_source_record gx8002_clock_osc_sources_26904[10]
    __attribute__((section(".gx8002.clock_sources.26904"), used,
                   aligned(4))) = {
    {15,0}, {27,0}, {28,0}, {29,0}, {26,0},
    {16,0}, {17,0}, {18,1}, {0,1}, {14,0},
};

/* Stock 0x10026954 (gx8002_clock_init_pointer_xtal) */
const struct gx8002_clock_source_record gx8002_clock_xtal_sources_26954[10]
    __attribute__((section(".gx8002.clock_sources.26954"), used,
                   aligned(4))) = {
    {15,0}, {27,0}, {28,0}, {29,0}, {26,1},
    {16,1}, {17,0}, {18,1}, {0,0}, {14,0},
};
