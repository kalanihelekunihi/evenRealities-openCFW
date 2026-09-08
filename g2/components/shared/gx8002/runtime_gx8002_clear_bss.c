/* SPDX-License-Identifier: MIT */
/* Reconstructed from CK804 startup's word-wise BSS clear. The linked bounds
 * are word aligned; the end is exclusive. Startup calls this before use. */
#include <stdint.h>
extern uint32_t open_cfw_gx8002_bss_start;
extern uint32_t open_cfw_gx8002_bss_end;

void open_cfw_gx8002_clear_bss(void)
{
    uintptr_t cursor = (uintptr_t)&open_cfw_gx8002_bss_start;
    const uintptr_t end = (uintptr_t)&open_cfw_gx8002_bss_end;
    while (cursor < end) {
        *(volatile uint32_t *)cursor = 0;
        cursor += sizeof(uint32_t);
    }
}
