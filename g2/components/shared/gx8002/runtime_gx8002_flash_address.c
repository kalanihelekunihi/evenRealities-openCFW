/* SPDX-License-Identifier: MIT */
/* Recovered address-byte encoder at image-A 0x15ba0. CK804 LSR uses
 * the low six shift-count bits and yields zero for counts 32..63.
 * Express that behavior without an undefined C shift (width 3 writes a
 * trailing zero at byte 4). Width is deliberately reloaded four times. */
#include <stdint.h>
void open_cfw_gx8002_flash_encode_address(const volatile uint32_t *width,
                                         unsigned address, uint8_t *command)
{
    for (unsigned i=1; i<=4; ++i) {
        unsigned shift=((*width-i)*8u)&63u;
        command[i]=shift<32u ? (uint8_t)(address>>shift) : 0;
    }
}
