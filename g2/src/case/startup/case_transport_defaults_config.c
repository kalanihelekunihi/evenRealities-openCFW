/* SPDX-License-Identifier: MIT
 * CASE transport mode at RAM 0x200000fb = device[7] relative to 0x200000f4.
 * Native callback 0x9684 dispatches modes 1/2/4 and returns for initial 3;
 * native aging begin 0x1334 subsequently selects 4.
 */
#include <stdint.h>

void case_crt_init_transport_mode(void)
{
    *(volatile uint8_t *)(uintptr_t)0x200000fbu=3u;
}
